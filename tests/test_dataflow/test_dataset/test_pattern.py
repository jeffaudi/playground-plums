import pathlib

import pytest
import numpy as np

from playground_plums.commons.data import TileWrapper, Record, RecordCollection, DataPoint
from playground_plums.dataflow.dataset import PatternDataset


def _dummy_tile_driver(paths, **matches):
    paths = sorted(paths, key=str, reverse=True)

    print(paths)
    print(matches)

    return TileWrapper(np.zeros((12, 12, 3)), filename=paths[0], **matches)


def _invalid_return_tile_driver(paths, **matches):
    print(paths)
    print(matches)

    return np.zeros((12, 12, 3))


def _invalid_paths_signature_tile_driver(*paths, **matches):
    print(paths)
    print(matches)

    return TileWrapper(np.zeros((12, 12, 3)), filename=paths[0], **matches)


def _invalid_matches_signature_tile_driver(*paths, matches=None):
    print(paths)
    print(matches)

    return TileWrapper(np.zeros((12, 12, 3)), filename=paths[0], **matches)


def _invalid_extra_signature_tile_driver(*paths, degenerate=False, **matches):
    print(paths)
    print(degenerate)
    print(matches)

    return TileWrapper(np.zeros((12, 12, 3)), filename=paths[0], **matches)


def _dummy_annotation_driver(paths, **matches):
    print(paths)
    print(matches)

    record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('label', ), paths=paths, **matches)
    return RecordCollection(record)


def _invalid_return_annotation_driver(paths, **matches):
    print(paths)
    print(matches)

    return matches


def _invalid_paths_signature_annotation_driver(*paths, **matches):
    print(paths)
    print(matches)

    record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('label', ), paths=paths, **matches)
    return RecordCollection(record)


def _invalid_matches_signature_annotation_driver(*paths, matches=None):
    print(paths)
    print(matches)

    record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('label', ), paths=paths, **matches)
    return RecordCollection(record)


def _invalid_extra_signature_annotation_driver(*paths, degenerate=False, **matches):
    print(paths)
    print(degenerate)
    print(matches)

    record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('label', ), paths=paths, **matches)
    return RecordCollection(record)


class TestSignature:
    def test_type_tile_signature(self):
        with pytest.raises(TypeError, match='Invalid Tile driver: Expected a callable'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               None, _dummy_annotation_driver)

    def test_invalid_paths_tile_signature(self):
        with pytest.raises(TypeError, match='Invalid Tile driver: Expected function'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _invalid_paths_signature_tile_driver, _dummy_annotation_driver)

    def test_invalid_matches_tile_signature(self):
        with pytest.raises(TypeError, match='Invalid Tile driver: Expected function'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _invalid_matches_signature_tile_driver, _dummy_annotation_driver)

    def test_invalid_extra_tile_signature(self):
        with pytest.raises(TypeError, match='Invalid Tile driver: Expected function'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _invalid_extra_signature_tile_driver, _dummy_annotation_driver)

    def test_type_annotation_signature(self):
        with pytest.raises(TypeError, match='Invalid Annotation driver: Expected a callable'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _dummy_tile_driver, None)

    def test_invalid_paths_annotation_signature(self):
        with pytest.raises(TypeError, match='Invalid Annotation driver: Expected function'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _dummy_tile_driver, _invalid_paths_signature_annotation_driver)

    def test_invalid_matches_annotation_signature(self):
        with pytest.raises(TypeError, match='Invalid Annotation driver: Expected function'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _dummy_tile_driver, _invalid_matches_signature_annotation_driver)

    def test_invalid_extra_annotation_signature(self):
        with pytest.raises(TypeError, match='Invalid Annotation driver: Expected function'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _dummy_tile_driver, _invalid_extra_signature_annotation_driver)


class TestPairMatch:
    def test_strict(self, strict_pattern_tree):
        root, path_list = strict_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                 'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=str(root))
        assert len(dataset) == 8
        assert dataset._matching_groups == ('dataset', 'aoi', 'type', 'tile')
        assert set(dataset._group_index) == {('dataset_1', 'aoi_0', 'simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_0', 'simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_0', 'labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_0', 'labeled', 'tile_01'),
                                             ('dataset_1', 'aoi_3', 'simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_3', 'simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_3', 'labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_3', 'labeled', 'tile_01')}

    def test_sort(self, strict_pattern_tree):
        root, path_list = strict_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                 'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root,
                                 sort_key=lambda x: tuple(reversed(x)))
        assert len(dataset) == 8
        assert dataset._matching_groups == ('dataset', 'aoi', 'type', 'tile')
        assert dataset._group_index == [
            ('dataset_1', 'aoi_0', 'labeled', 'tile_00'),
            ('dataset_1', 'aoi_3', 'labeled', 'tile_00'),
            ('dataset_1', 'aoi_0', 'simulated', 'tile_00'),
            ('dataset_1', 'aoi_3', 'simulated', 'tile_00'),
            ('dataset_1', 'aoi_0', 'labeled', 'tile_01'),
            ('dataset_1', 'aoi_3', 'labeled', 'tile_01'),
            ('dataset_1', 'aoi_0', 'simulated', 'tile_01'),
            ('dataset_1', 'aoi_3', 'simulated', 'tile_01'),
        ]

    def test_cache(self, strict_pattern_tree):
        root, path_list = strict_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                 'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver,
                                 path=root)
        cached = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                                _dummy_tile_driver, _dummy_annotation_driver,
                                path=root, cache=True)

        assert dataset._tiles_database == cached._tiles_database
        assert dataset._tiles_index == cached._tiles_index
        assert dataset._annotations_database == cached._annotations_database
        assert dataset._annotations_index == cached._annotations_index
        assert dataset._matching_groups == cached._matching_groups
        assert dataset._group_index == cached._group_index

    def test_cache_miss(self, strict_pattern_tree):
        root, path_list = strict_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{type}/{tile}.jpg',
                                 'data/labels/{dataset}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver,
                                 path=pathlib.Path(str(root)), cache=True)
        assert len(dataset) == 2
        assert dataset._matching_groups == ('dataset', 'type', 'tile')
        assert set(dataset._group_index) == {('dataset_0', 'labeled', 'tile_00'),
                                             ('dataset_0', 'labeled', 'tile_01')}

    def test_strict_recursive(self, strict_pattern_tree):
        root, path_list = strict_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{aoi/}/{tile}.jpg',
                                 'data/labels/{dataset}/{aoi/}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root)
        assert len(dataset) == 10
        assert dataset._matching_groups == ('dataset', 'aoi', 'tile')
        assert set(dataset._group_index) == {('dataset_0', 'labeled', 'tile_00'),
                                             ('dataset_0', 'labeled', 'tile_01'),
                                             ('dataset_1', 'aoi_0/simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_0/simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_0/labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_0/labeled', 'tile_01'),
                                             ('dataset_1', 'aoi_3/simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_3/simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_3/labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_3/labeled', 'tile_01')}

    def test_tile_degeneracy_fail(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        with pytest.raises(ValueError, match='Tile pattern degeneracy is not supported'):
            _ = PatternDataset('data/images/tile.jpg',
                               'data/labels/{dataset_id}/{aoi_id}/{type_id}/{tile_id}.json',
                               _dummy_tile_driver, _dummy_annotation_driver, path=root)

    def test_no_common_group_fail(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        with pytest.raises(ValueError, match='No common group could be found in between patterns'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset_id}/{aoi_id}/{type_id}/{tile_id}.json',
                               _dummy_tile_driver, _dummy_annotation_driver, path=root)

    def test_no_match_fail(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        with pytest.raises(ValueError, match='No matches where found between tiles and annotation'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.JSON',
                               _dummy_tile_driver, _dummy_annotation_driver, path=root, strict=False)

    def test_loose_fail(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        with pytest.raises(ValueError, match='does not have a matching annotation'):
            _ = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                               'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                               _dummy_tile_driver, _dummy_annotation_driver, path=root)

    def test_loose(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                 'data/labels/{dataset}/{aoi}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root, strict=False)
        assert len(dataset) == 6
        assert dataset._matching_groups == ('dataset', 'aoi', 'type', 'tile')
        assert set(dataset._group_index) == {('dataset_1', 'aoi_0', 'simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_0', 'simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_3', 'simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_3', 'simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_3', 'labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_3', 'labeled', 'tile_01')}

    def test_loose_alternative(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                 'data/images/{dataset}/{aoi}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root, strict=False)
        assert len(dataset) == 1
        assert dataset._matching_groups == ('dataset', 'aoi', 'type', 'tile')
        assert set(dataset._group_index) == {('dataset_1', 'aoi_0', 'labeled', 'tile_00')}

        dataset = PatternDataset('data/images/{dataset}/{aoi}/{type}/{tile}.jpg',
                                 'data/images/{dataset}/{aoi}/{type}/{tile}.[json|geojson]',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root, strict=False)
        assert len(dataset) == 2
        assert set(dataset._group_index) == {('dataset_1', 'aoi_0', 'labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_0', 'labeled', 'tile_01')}

    def test_loose_duplicate(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        with pytest.raises(ValueError, match='does not have a matching annotation'):
            _ = PatternDataset('data/images/{dataset}/{type}/{prior}/{tile}.jpg',
                               'data/labels/{dataset}/{type}/{tile}.json',
                               _dummy_tile_driver, _dummy_annotation_driver, path=root)

        dataset = PatternDataset('data/images/{dataset}/{type}/{prior}/{tile}.jpg',
                                 'data/labels/{dataset}/{type}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root, strict=False)
        assert len(dataset) == 2
        assert dataset._matching_groups == ('dataset', 'type', 'tile')
        assert set(dataset._group_index) == {('dataset_0', 'labeled', 'tile_00'),
                                             ('dataset_0', 'labeled', 'tile_01')}

        assert len(dataset._tiles_database[('dataset_0', 'labeled', 'tile_00')]) == 2
        assert len(dataset._tiles_database[('dataset_0', 'labeled', 'tile_01')]) == 2

        assert len(dataset._annotations_database[('dataset_0', 'labeled', 'tile_00')]) == 1
        assert len(dataset._annotations_database[('dataset_0', 'labeled', 'tile_01')]) == 1

    def test_degenerate(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{type}/{prior}/{tile}.jpg',
                                 'data/images.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root)
        assert len(dataset) == 12
        assert dataset._matching_groups == ('dataset', 'type', 'prior', 'tile')
        assert set(dataset._group_index) == {('dataset_0', 'labeled', 'prior', 'tile_00'),
                                             ('dataset_0', 'labeled', 'prior', 'tile_01'),
                                             ('dataset_0', 'labeled', 'posterior', 'tile_00'),
                                             ('dataset_0', 'labeled', 'posterior', 'tile_01'),
                                             ('dataset_1', 'aoi_0', 'simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_0', 'simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_0', 'labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_0', 'labeled', 'tile_01'),
                                             ('dataset_1', 'aoi_3', 'simulated', 'tile_00'),
                                             ('dataset_1', 'aoi_3', 'simulated', 'tile_01'),
                                             ('dataset_1', 'aoi_3', 'labeled', 'tile_00'),
                                             ('dataset_1', 'aoi_3', 'labeled', 'tile_01')}


class TestDriver:
    def test_call_argument(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{nature}/{prior}/{tile}.jpg',
                                 'data/labels/{dataset}/{nature}/{tile}.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root,
                                 strict=False, sort_key=lambda x: x)

        assert isinstance(dataset[0], DataPoint)
        assert dataset[0].tiles.iloc[0].filename == root / 'data/images/dataset_0/labeled/prior/tile_00.jpg'
        assert dataset[0].tiles.iloc[0].dataset == 'dataset_0'
        assert dataset[0].tiles.iloc[0].nature == 'labeled'
        assert dataset[0].tiles.iloc[0].tile == 'tile_00'
        assert not hasattr(dataset[0].tiles.iloc[0], 'prior')

        assert dataset[0].annotation[0].paths == (root / 'data/labels/dataset_0/labeled/tile_00.json', )
        assert dataset[0].annotation[0].dataset == 'dataset_0'
        assert dataset[0].annotation[0].nature == 'labeled'
        assert dataset[0].annotation[0].tile == 'tile_00'
        assert not hasattr(dataset[0].annotation[0], 'prior')

    def test_degenerate_call_argument(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{nature}/{prior}/{tile}.jpg',
                                 'data/images.json',
                                 _dummy_tile_driver, _dummy_annotation_driver, path=root,
                                 sort_key=lambda x: x)

        assert isinstance(dataset[0], DataPoint)
        assert dataset[0].tiles.iloc[0].filename == root / 'data/images/dataset_0/labeled/posterior/tile_00.jpg'
        assert dataset[0].tiles.iloc[0].dataset == 'dataset_0'
        assert dataset[0].tiles.iloc[0].nature == 'labeled'
        assert dataset[0].tiles.iloc[0].prior == 'posterior'
        assert dataset[0].tiles.iloc[0].tile == 'tile_00'

        assert dataset[0].annotation[0].paths == (root / 'data/images.json', )
        assert dataset[0].annotation[0].dataset == 'dataset_0'
        assert dataset[0].annotation[0].nature == 'labeled'
        assert dataset[0].annotation[0].prior == 'posterior'
        assert dataset[0].annotation[0].tile == 'tile_00'

    def test_call_invalid_tile_type(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{nature}/{prior}/{tile}.jpg',
                                 'data/labels/{dataset}/{nature}/{tile}.json',
                                 _invalid_return_tile_driver, _dummy_annotation_driver, path=root, strict=False)

        with pytest.raises(TypeError):
            _ = dataset[0]

    def test_call_invalid_annotation_type(self, loose_pattern_tree):
        root, path_list = loose_pattern_tree
        dataset = PatternDataset('data/images/{dataset}/{nature}/{prior}/{tile}.jpg',
                                 'data/labels/{dataset}/{nature}/{tile}.json',
                                 _dummy_tile_driver, _invalid_return_annotation_driver, path=root, strict=False)

        with pytest.raises(TypeError):
            _ = dataset[0]
