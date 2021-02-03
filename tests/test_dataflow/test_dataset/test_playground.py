import pytest
import numpy as np

from playground_plums.commons.path import Path
from playground_plums.commons.data import Taxonomy, Label, TileCollection
from playground_plums.dataflow.io import dump, RGB, BGR, Tile
from playground_plums.dataflow.io.tile._backend import Image
from playground_plums.dataflow.dataset.playground import PlaygroundDataset, TaxonomyReader, TileDriver, AnnotationDriver


@pytest.fixture()
def reference_image():
    return np.array(Image.load(Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'))


def test_taxonomy_reader(tmp_path):
    # Prepare taxonomy
    taxonomy_file = tmp_path / 'taxonomy.json'
    dump({'some_label': {'child': {},
                         'other': {'nested': {}}},
          'root': {}}, taxonomy_file)
    nested = Label('nested')
    other = Label('other', children=(nested, ))
    child = Label('child')
    some_label = Label('some_label', children=(child, other))
    root = Label('root')
    taxonomy_reference = Taxonomy(some_label, root)

    # Assert equal
    reader = TaxonomyReader()
    assert reader(tmp_path) == taxonomy_reference


def test_annotation_driver(tmp_path, json_feature_collection):  # noqa: R701
    annotation_path = tmp_path / 'annotation.json'
    annotation_path.write_text(json_feature_collection)

    # +-> Error
    driver = AnnotationDriver()
    with pytest.raises(ValueError, match='More than one annotation file was provided'):
        _ = driver((annotation_path, annotation_path), group='value')

    # +-> Base
    driver = AnnotationDriver()
    annotation = driver((annotation_path, ), group='value')
    assert len(annotation.record_collection) == 1
    assert annotation.record_collection[0].labels == ('tag', 'class')
    assert annotation.record_collection[0].confidence is None
    assert annotation.record_collection[0].dataset_id == 'f16fff43-2535-4e34-afec-6404dcdcd545'
    assert annotation.record_collection[0].zone_id == '10187fa3-30df-4eb4-a1e9-6b1dcdc79951'
    assert annotation.record_collection[0].id == '6e73eff2-06f3-11ea-976a-b2cdca212bc0'
    assert \
        annotation.mask_collection['zone_footprint'].coordinates == [[[0, 0], [0, 256], [256, 256], [256, 0], [0, 0]]]
    assert (annotation_path, ) not in driver._memcache
    # +--> Reopen
    assert driver((annotation_path, ), group='value') is not annotation

    # +-> Confidence
    driver = AnnotationDriver(confidence_key='surface')
    annotation = driver((annotation_path, ), group='value')
    assert len(annotation.record_collection) == 1
    assert annotation.record_collection[0].labels == ('tag', 'class')
    assert annotation.record_collection[0].confidence - 64.2146176930851 <= 1e-4
    assert annotation.record_collection[0].dataset_id == 'f16fff43-2535-4e34-afec-6404dcdcd545'
    assert annotation.record_collection[0].zone_id == '10187fa3-30df-4eb4-a1e9-6b1dcdc79951'
    assert annotation.record_collection[0].id == '6e73eff2-06f3-11ea-976a-b2cdca212bc0'
    assert \
        annotation.mask_collection['zone_footprint'].coordinates == [[[0, 0], [0, 256], [256, 256], [256, 0], [0, 0]]]

    # +-> Id
    driver = AnnotationDriver(record_id_key='owner_id')
    annotation = driver((annotation_path, ), group='value')
    assert len(annotation.record_collection) == 1
    assert annotation.record_collection[0].labels == ('tag', 'class')
    assert annotation.record_collection[0].confidence is None
    assert annotation.record_collection[0].dataset_id == 'f16fff43-2535-4e34-afec-6404dcdcd545'
    assert annotation.record_collection[0].zone_id == '10187fa3-30df-4eb4-a1e9-6b1dcdc79951'
    assert annotation.record_collection[0].id == '35e370a9-6b76-4ac6-a3d5-1eeb983c3dc7'
    assert \
        annotation.mask_collection['zone_footprint'].coordinates == [[[0, 0], [0, 256], [256, 256], [256, 0], [0, 0]]]

    # +-> Cache
    driver = AnnotationDriver(cache=True)
    annotation = driver((annotation_path, ), group='value')
    assert len(annotation.record_collection) == 1
    assert annotation.record_collection[0].labels == ('tag', 'class')
    assert annotation.record_collection[0].confidence is None
    assert annotation.record_collection[0].dataset_id == 'f16fff43-2535-4e34-afec-6404dcdcd545'
    assert annotation.record_collection[0].zone_id == '10187fa3-30df-4eb4-a1e9-6b1dcdc79951'
    assert annotation.record_collection[0].id == '6e73eff2-06f3-11ea-976a-b2cdca212bc0'
    assert \
        annotation.mask_collection['zone_footprint'].coordinates == [[[0, 0], [0, 256], [256, 256], [256, 0], [0, 0]]]
    assert driver._memcache[(annotation_path, )] is annotation
    # +--> Reopen
    assert driver((annotation_path, ), group='value') is annotation


def test_tile_driver(reference_image):  # noqa: R701
    # +-> Base
    driver = TileDriver(fetch_ordering=False)
    tiles = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')
    assert isinstance(tiles, TileCollection)
    assert len(tiles) == 3
    assert all(isinstance(tile, Tile) for tile in tiles.values())
    assert all(name == 'tile_{}'.format(i) for i, name in enumerate(tiles.keys()))
    assert all(tile.ptype == RGB for tile in tiles.values())
    assert all(tile.dtype == np.uint8 for tile in tiles.values())
    assert all(np.array_equal(reference_image, tile) for tile in tiles.values())

    # +-> PType
    driver = TileDriver(ptype=BGR, fetch_ordering=False)
    tiles = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')
    assert isinstance(tiles, TileCollection)
    assert len(tiles) == 3
    assert all(isinstance(tile, Tile) for tile in tiles.values())
    assert all(name == 'tile_{}'.format(i) for i, name in enumerate(tiles.keys()))
    assert all(tile.ptype == BGR for tile in tiles.values())
    assert all(tile.dtype == np.uint8 for tile in tiles.values())
    assert all(np.array_equal(reference_image, tile.astype(ptype=RGB)) for tile in tiles.values())

    # +-> DType
    driver = TileDriver(dtype=np.float64, fetch_ordering=False)
    tiles = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')
    assert isinstance(tiles, TileCollection)
    assert len(tiles) == 3
    assert all(isinstance(tile, Tile) for tile in tiles.values())
    assert all(name == 'tile_{}'.format(i) for i, name in enumerate(tiles.keys()))
    assert all(tile.ptype == RGB for tile in tiles.values())
    assert all(tile.dtype == np.float64 for tile in tiles.values())
    assert all(np.array_equal(reference_image, tile.astype(dtype=np.uint8)) for tile in tiles.values())

    # +-> Names
    with pytest.raises(ValueError, match='The number of tiles is incompatible with the provided number'):
        driver = TileDriver('not', 'enough', fetch_ordering=False)
        _ = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')

    with pytest.raises(ValueError, match='The number of tiles is incompatible with the provided number'):
        driver = TileDriver('too', 'many', 'names', 'provided', fetch_ordering=False)
        _ = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')

    names = ['some', 'tile', 'set']
    driver = TileDriver(*names, fetch_ordering=False)
    tiles = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')
    assert isinstance(tiles, TileCollection)
    assert len(tiles) == 3
    assert all(isinstance(tile, Tile) for tile in tiles.values())
    assert all(name == names[i] for i, name in enumerate(tiles.keys()))
    assert all(tile.ptype == RGB for tile in tiles.values())
    assert all(tile.dtype == np.uint8 for tile in tiles.values())
    assert all(np.array_equal(reference_image, tile.astype(dtype=np.uint8)) for tile in tiles.values())

    # +-> All
    driver = TileDriver(*names, ptype=BGR, dtype=np.float64, fetch_ordering=False)
    tiles = driver((Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg',
                    Path(__file__)[:-1] / '..' / 'test_io' / 'test_tile' / '_data' / 'test_jpg.jpg'), group='value')
    assert isinstance(tiles, TileCollection)
    assert len(tiles) == 3
    assert all(isinstance(tile, Tile) for tile in tiles.values())
    assert all(name == names[i] for i, name in enumerate(tiles.keys()))
    assert all(tile.ptype == BGR for tile in tiles.values())
    assert all(tile.dtype == np.float64 for tile in tiles.values())
    assert all(np.array_equal(reference_image, tile.astype(ptype=RGB, dtype=np.uint8)) for tile in tiles.values())


def test_base(playground_tree, reference_image):
    root, paths = playground_tree
    dataset = PlaygroundDataset(root, use_taxonomy=False)

    assert len(dataset) == 5

    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       '2411dbb6-e7bf-41fd-8898-83325a9c6e5a',
                                       '4a8a08f09d37b73795649038408b5f33')
    assert dataset._group_index[1] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       'c3e8b68b-f862-41bd-848c-6e2df28e4dd8',
                                       '92eb5ffee6ae2fec3ad71c777531578b')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[3] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')
    assert dataset._group_index[4] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')

    assert len(dataset[0].tiles) == 2
    assert len(dataset[1].tiles) == 1
    assert len(dataset[2].tiles) == 1
    assert len(dataset[3].tiles) == 1
    assert len(dataset[4].tiles) == 2
    assert np.array_equal(reference_image, dataset[0].tiles.iloc[0])

    # Test ordering
    assert tuple(tile.image_id for tile in dataset[0].tiles.values()) == ("4e15b4a3-ee52-4382-b8a8-7d492fb1a6ed",
                                                                          "5562b632-72c3-4c21-b24e-e0536d8b20c8")
    assert tuple(tile.image_id for tile in dataset[4].tiles.values()) == ("f9525e3bfbd081cd545261b3b5414eb88f689005",
                                                                          "75ad128196254e711ef7c9b129d1c59153098b18")

    assert len(dataset[0].annotation.record_collection) == 1
    assert dataset[0].annotation.record_collection[0].labels == ('tag', 'class')
    assert dataset[0].annotation.record_collection[0].dataset_id == 'f16fff43-2535-4e34-afec-6404dcdcd545'
    assert dataset[0].annotation.record_collection[0].zone_id == '10187fa3-30df-4eb4-a1e9-6b1dcdc79951'
    assert dataset[0].annotation.record_collection[0].id == '6e73eff2-06f3-11ea-976a-b2cdca212bc0'
    assert dataset[0].annotation.mask_collection['zone_footprint'].coordinates \
        == [[[0, 0], [0, 256], [256, 256], [256, 0], [0, 0]]]


def test_select_exclude(playground_tree):  # noqa: R701
    root, paths = playground_tree

    # Dataset:
    # +-> Select:
    dataset = PlaygroundDataset(root, use_taxonomy=False, select_datasets=('63d0da07-0a4b-4ffd-844f-af75c02288e0', ))
    assert len(dataset) == 3
    assert dataset._group_index[0] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')

    # +-> Exclude:
    dataset = PlaygroundDataset(root, use_taxonomy=False, exclude_datasets=('1af6c4c5-278d-40ae-9e32-dc8192f8402a', ))
    assert len(dataset) == 3
    assert dataset._group_index[0] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')

    # +-> Both:
    with pytest.raises(ValueError, match='Invalid dataset: No matches where found between tiles and annotation'):
        _ = PlaygroundDataset(root, use_taxonomy=False,
                              select_datasets=('63d0da07-0a4b-4ffd-844f-af75c02288e0', ),
                              exclude_datasets=('63d0da07-0a4b-4ffd-844f-af75c02288e0', ))

    # Zone:
    # +-> Select:
    dataset = PlaygroundDataset(root, use_taxonomy=False, select_zones=('b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                                                        'c3e8b68b-f862-41bd-848c-6e2df28e4dd8'))
    assert len(dataset) == 3
    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       'c3e8b68b-f862-41bd-848c-6e2df28e4dd8',
                                       '92eb5ffee6ae2fec3ad71c777531578b')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')

    # +-> Exclude:
    dataset = PlaygroundDataset(root, use_taxonomy=False, exclude_zones=('b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                                                         'c3e8b68b-f862-41bd-848c-6e2df28e4dd8'))
    assert len(dataset) == 2
    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       '2411dbb6-e7bf-41fd-8898-83325a9c6e5a',
                                       '4a8a08f09d37b73795649038408b5f33')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')

    # +-> Both:
    dataset = PlaygroundDataset(root, use_taxonomy=False,
                                select_zones=('b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                              'c3e8b68b-f862-41bd-848c-6e2df28e4dd8'),
                                exclude_zones=('c3e8b68b-f862-41bd-848c-6e2df28e4dd8', ))
    assert len(dataset) == 2
    assert dataset._group_index[0] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')

    # Image:
    # +-> Select:
    dataset = PlaygroundDataset(root, use_taxonomy=False,
                                select_images=('S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548',
                                               'f9525e3bfbd081cd545261b3b5414eb88f689005'))
    assert len(dataset) == 2
    assert dataset._group_index[0] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')
    assert len(dataset[0].tiles) == 1
    assert len(dataset[1].tiles) == 1

    # +-> Exclude:
    dataset = PlaygroundDataset(root, use_taxonomy=False,
                                exclude_images=('S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548',
                                                'f9525e3bfbd081cd545261b3b5414eb88f689005'))
    assert len(dataset) == 4
    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       '2411dbb6-e7bf-41fd-8898-83325a9c6e5a',
                                       '4a8a08f09d37b73795649038408b5f33')
    assert dataset._group_index[1] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       'c3e8b68b-f862-41bd-848c-6e2df28e4dd8',
                                       '92eb5ffee6ae2fec3ad71c777531578b')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[3] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')
    assert len(dataset[0].tiles) == 2
    assert len(dataset[1].tiles) == 1
    assert len(dataset[2].tiles) == 1
    assert len(dataset[3].tiles) == 1

    # +-> Both:
    dataset = PlaygroundDataset(root, use_taxonomy=False,
                                select_images=('S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548',
                                               'f9525e3bfbd081cd545261b3b5414eb88f689005',
                                               '75ad128196254e711ef7c9b129d1c59153098b18'),
                                exclude_images=('S2B_MSIL1C_20200212T025609_N0209_R003_T47DMH_20200212T054548',
                                                '75ad128196254e711ef7c9b129d1c59153098b18', ))
    assert len(dataset) == 1
    assert dataset._group_index[0] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')
    assert len(dataset[0].tiles) == 1

    # Tile:
    # +-> Select:
    dataset = PlaygroundDataset(root, use_taxonomy=False, select_tiles=('4a8a08f09d37b73795649038408b5f33',
                                                                        '0cc175b9c0f1b6a831c399e269772661',
                                                                        '7c47df1097b349278c052e93e1d1903a'))
    assert len(dataset) == 3
    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       '2411dbb6-e7bf-41fd-8898-83325a9c6e5a',
                                       '4a8a08f09d37b73795649038408b5f33')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')

    # +-> Exclude:
    dataset = PlaygroundDataset(root, use_taxonomy=False, exclude_tiles=('92eb5ffee6ae2fec3ad71c777531578b', ))
    assert len(dataset) == 4
    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       '2411dbb6-e7bf-41fd-8898-83325a9c6e5a',
                                       '4a8a08f09d37b73795649038408b5f33')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')
    assert dataset._group_index[2] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '453e41d218e071ccfb2d1c99ce23906a')
    assert dataset._group_index[3] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')

    # +-> Both:
    dataset = PlaygroundDataset(root, use_taxonomy=False,
                                select_tiles=('4a8a08f09d37b73795649038408b5f33',
                                              '0cc175b9c0f1b6a831c399e269772661',
                                              '7c47df1097b349278c052e93e1d1903a'),
                                exclude_tiles=('7c47df1097b349278c052e93e1d1903a', ))
    assert len(dataset) == 2
    assert dataset._group_index[0] == ('1af6c4c5-278d-40ae-9e32-dc8192f8402a',
                                       '2411dbb6-e7bf-41fd-8898-83325a9c6e5a',
                                       '4a8a08f09d37b73795649038408b5f33')
    assert dataset._group_index[1] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'b4d9ffe3-ab2d-4f18-b1c5-b4c3d9b2f6f7',
                                       '0cc175b9c0f1b6a831c399e269772661')


def test_select_exclude_composition(playground_tree):
    root, paths = playground_tree
    dataset = PlaygroundDataset(root, use_taxonomy=False,
                                exclude_datasets=('1af6c4c5-278d-40ae-9e32-dc8192f8402a', ),
                                select_zones=('fa719db8-31e9-49d1-9344-d4608ef6417e', ),
                                exclude_images=('f9525e3bfbd081cd545261b3b5414eb88f689005', ))

    assert len(dataset) == 1
    assert dataset._group_index[0] == ('63d0da07-0a4b-4ffd-844f-af75c02288e0',
                                       'fa719db8-31e9-49d1-9344-d4608ef6417e',
                                       '7c47df1097b349278c052e93e1d1903a')
    assert len(dataset[0].tiles) == 1


def test_pass_taxonomy(playground_tree):
    root, paths = playground_tree
    dataset = PlaygroundDataset(root, use_taxonomy=True)
    with pytest.raises(ValueError):
        _ = dataset[0]


def test_taxonomy_conflict_raise(playground_tree_conflict):
    root, paths = playground_tree_conflict
    with pytest.raises(ValueError, match='Some datasets have mismatching taxonomies'):
        _ = PlaygroundDataset(root, use_taxonomy=True)


def test_taxonomy_conflict_warn(playground_tree_conflict):
    root, paths = playground_tree_conflict
    with pytest.warns(UserWarning, match='Some datasets have mismatching taxonomies'):
        _ = PlaygroundDataset(root, use_taxonomy=False)


def test_fetch_ordering_missing_image(playground_tree_summary_missing_image):
    root, paths = playground_tree_summary_missing_image

    dataset = PlaygroundDataset(root, use_taxonomy=False)
    with pytest.raises(ValueError, match='Invalid dataset: Some images seem to be missing from the summaries'):
        _ = dataset[5]

    dataset = PlaygroundDataset(root, use_taxonomy=False, tile_driver=TileDriver(fetch_ordering=False))
    assert isinstance(dataset[5].tiles.iloc[0], Tile)


def test_fetch_ordering_missing_zone(playground_tree_summary_missing_zone):
    root, paths = playground_tree_summary_missing_zone

    dataset = PlaygroundDataset(root, use_taxonomy=False)
    with pytest.raises(ValueError, match='Invalid dataset: Some zones or datasets seem to be '
                                         'missing from the summaries'):
        _ = dataset[1]

    dataset = PlaygroundDataset(root, use_taxonomy=False, tile_driver=TileDriver(fetch_ordering=False))
    assert isinstance(dataset[1].tiles.iloc[0], Tile)


def test_fetch_ordering_missing_dataset(playground_tree_summary_missing_dataset):
    root, paths = playground_tree_summary_missing_dataset

    dataset = PlaygroundDataset(root, use_taxonomy=False)
    with pytest.raises(ValueError, match='Invalid dataset: Some zones or datasets seem to be '
                                         'missing from the summaries'):
        _ = dataset[0]

    dataset = PlaygroundDataset(root, use_taxonomy=False, tile_driver=TileDriver(fetch_ordering=False))
    assert isinstance(dataset[0].tiles.iloc[0], Tile)


def test_fetch_ordering_missing_summaries(playground_tree_summary_missing_summaries):
    root, paths = playground_tree_summary_missing_summaries

    dataset = PlaygroundDataset(root, use_taxonomy=False)
    with pytest.raises(FileNotFoundError, match='Invalid dataset: No file summaries could be found'):
        _ = dataset[0]

    dataset = PlaygroundDataset(root, use_taxonomy=False, tile_driver=TileDriver(fetch_ordering=False))
    assert isinstance(dataset[0].tiles.iloc[0], Tile)
