from warnings import warn

import numpy as np

from plums.commons.path import Path
from plums.commons.data import (
    TileCollection,
    Annotation,
    MaskCollection,
    VectorMask,
    RecordCollection,
    Record,
    Taxonomy,
    Label,
    DataPoint
)
from .pattern import PatternDataset
from ..utils.cache import DatasetCache
from ..io import Tile, RGB, load
from ..utils.path import PathResolver


class TileDriver:
    """A basic driver to open `Intelligence Playground`_ tiles as |TileIO| instance.

    It provides a basic level of customisation but heavy modification will require either subclassing and overriding or
    writing a new driver altogether.

    Args:
        *names (str): Optional. If provided, it will be used a keys in the |TileCollection| returned by the driver.
        ptype (|ptype|): Optional. Default to ``RGB``. The image pixel-type (e.g. RGB, BGR or Grey).
        dtype (:class:`~numpy.dtype`): Optional. Default to :class:`~numpy.uint8`.
            The internal :class:`~numpy.ndarray` storage data type.
        fetch_ordering (bool): If ``True``, tiles will be ordered using the information stored in the dataset summary
            provided as a *JSON* file alongside each exports.

            .. warning::

                    If ``False`` the |TileCollection| ordering will be entirely **filesystem dependent** which is no
                    better than random.

    .. _Intelligence Playground: https://playground.intelligence-airbusds.com/

    """

    def __init__(self, *names, ptype=RGB, dtype=np.dtype('u1'), fetch_ordering=True):
        # Tile format configuration
        self._names = names
        self._explicit = bool(names)
        self._ptype = ptype
        self._dtype = dtype

        # Tile ordering configuration
        self._summaries = None
        self._summary_resolver = None
        if fetch_ordering:
            self._summary_resolver = PathResolver('{dataset_id}/dataset_summary.json')

    def __call__(self, path_tuple, **matched_groups):
        """Open a set of tiles in a |TileCollection|.

        Args:
            path_tuple (Tuple[PathLike]): A tuple of paths pointing to the tiles to open.
            **matched_groups (str): A  ``group_name: value`` mapping of the *path pattern* group match in the paths.

        Returns:
            |TileCollection|: A |TileCollection| with the opened tiles. If names where provided in the constructor,
            they are used as key in the collection, otherwise, the default applies.

        Raises:
            ValueError: If the number of names provided in the constructor and the number of retrieved tiles mismatch.

        """
        # If need be resolve and load summaries
        if self._summaries is None and self._summary_resolver is not None:
            root = path_tuple[0].root_to_anchor(matched_groups['dataset_id'])

            def _make_order_index(path):
                """Construct a ``zone_id: (image_id, )`` mapping from a dataset summary.

                Args:
                    path (Path): A path to a *JSON* dataset summary file.

                Returns:
                    dict: A ``zone_id: (image_id, )`` mapping where ``(image_id, )`` is an **ordered** tuple of image
                    identifiers.

                """
                summary = load(path)
                return {zone_id: tile_ids for zone_id, tile_ids in zip(summary['zoneIds'], summary['imageIds'])}

            self._summaries = \
                {path.match['dataset_id']: _make_order_index(path) for path in self._summary_resolver.find(root)}

            if not self._summaries:
                raise FileNotFoundError('Invalid dataset: No file summaries could be found.')

        # Reorder path tuple if need be
        if self._summaries is not None:
            dataset_id = matched_groups['dataset_id']
            zone_id = matched_groups['zone_id']

            try:
                order = {image_id: i for i, image_id in enumerate(self._summaries[dataset_id][zone_id])}
            except KeyError:
                raise ValueError('Invalid dataset: Some zones or datasets seem to be missing from the summaries.')

            try:
                path_tuple = tuple(sorted(path_tuple, key=lambda path: order[path[-2]]))
            except KeyError:
                raise ValueError('Invalid dataset: Some images seem to be missing from the summaries.')

        # Load tiles
        tiles = [Tile(path, ptype=self._ptype, dtype=self._dtype, **getattr(path, 'match', {})) for path in path_tuple]
        if self._explicit:
            if len(tiles) != len(self._names):
                raise ValueError('The number of tiles is incompatible with the provided number '
                                 'of names: {} != {}.'.format(len(tiles), len(self._names)))
            return TileCollection(*((name, tile) for name, tile in zip(self._names, tiles)))

        return TileCollection(*tiles)


class AnnotationDriver:
    """A basic driver to open `Intelligence Playground`_ annotation GeoJSON **FeatureCollection**  as |Annotation|.

    It provides a basic level of customisation but heavy modification will require either subclassing and overriding or
    writing a new driver altogether.

    Args:
        record_id_key (str): The key used to find a record's unique identifier in its ``properties`` mapping.
        confidence_key (str): The key used to find a record's confidence score in its ``properties`` mapping.
        taxonomy (Taxonomy): If provided, a |Taxonomy| against which all records' labels will be validated.
        cache (bool): Optional. Default to ``False``. If ``True``, all constructed |Annotation| will be cached in
            memory to speed up future retrieval.


    .. _Intelligence Playground: https://playground.intelligence-airbusds.com/

    """

    def __init__(self, record_id_key='record_id', confidence_key='confidence', taxonomy=None, cache=False):
        self.taxonomy = taxonomy
        self._record_id_key = record_id_key
        self._confidence_key = confidence_key
        self._cache = cache
        self._memcache = {}

    @staticmethod
    def _cleanup(feature, key):
        if key in feature['properties']:  # Cleanup properties
            feature['properties'].pop(key)

    def __call__(self, path_tuple, **matched_groups):
        """Open a *Playground* annotation GeoJSON file as an |Annotation|.

        Args:
            path_tuple (Tuple[PathLike]): A tuple containing a single path pointing to a valid GeoJSON file.
            **matched_groups (str): A  ``group_name: value`` mapping of the *path pattern* group match in the paths.

        Returns:
            |Annotation|: An |Annotation| with |Record| in the tile and a |VectorMask| corresponding to the *zone*
            footprint in the tile.

        Raises:
            ValueError: If no valid |Annotation| could be constructed from the opened JSON file.
            ValueError: If more than one path was provided.

        """
        if len(path_tuple) >= 2:
            raise ValueError('More than one annotation file was provided.')

        # If cache is enabled, try retrieving from cache
        if self._cache:
            annotation = self._memcache.get(path_tuple, None)
            if annotation is not None:
                return annotation

        # Load annotation
        feature_collection = load(path_tuple[0])

        # +-> Prepare defaults values
        data_mask = VectorMask([[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]], 'zone_footprint', mask=True)
        record_collection = RecordCollection(taxonomy=self.taxonomy)

        # +-> Iterate over features
        for feature in feature_collection['features']:
            # +-> If found, retrieve zone footprint mask
            if feature['properties'].get('mask') is not None:
                data_mask = VectorMask(feature['geometry']['coordinates'], 'zone_footprint', mask=True)
                continue

            # +-> Get record coordinates
            coordinates = feature['geometry']['coordinates']

            # +-> Get record labels
            labels = feature['properties'].pop('tags')

            # +-> Get record confidence
            confidence = feature['properties'].pop(self._confidence_key, None)

            # +-> Get record identifier
            id_ = feature['properties'].pop(self._record_id_key, None)

            # Cleanup
            self._cleanup(feature, 'coordinates')
            self._cleanup(feature, 'labels')
            self._cleanup(feature, 'confidence')
            self._cleanup(feature, 'id')
            self._cleanup(feature, 'taxonomy')

            record_collection.append(Record(coordinates, labels, confidence, id_, **feature['properties']))

        annotation = Annotation(record_collection, mask_collection=MaskCollection(data_mask), filename=path_tuple[0])

        # If cache is enabled, store annotation in cache
        if self._cache:
            self._memcache[path_tuple] = annotation

        return annotation


class TaxonomyReader:
    """A callable class which loads and constructs a |Taxonomy| when provided with a valid Playground dataset path."""

    def _make_tree(self, root, tree_descriptor):
        """Recursively descend a dictionary tree and create a tree.

        Args:
            root (Label): The current tree root.
            tree_descriptor (dict): The current dictionary tree.

        Returns:
            Label: The current tree root |Label|.

        """
        for leaf, value in tree_descriptor.items():
            leaf = Label(leaf)
            root.add(leaf)
            if value is not None:
                self._make_tree(leaf, value)

        return root

    def __call__(self, path):
        """Construct a |Taxonomy| from the exported dataset `taxonomy.json` file.

        Args:
            path (PathLike): A path to a single Playground dataset.

        Returns:
            Taxonomy: The dataset taxonomy.

        """
        path = Path(path)

        taxonomy_descriptor = load(path / 'taxonomy.json')

        taxonomy = Taxonomy()
        self._make_tree(taxonomy.root, taxonomy_descriptor)

        return taxonomy


class PlaygroundDataset(PatternDataset):
    """A |Dataset| as exported by the `Intelligence Playground`_ which loads data in the *Plums* data model.

    A |PlaygroundDataset| has the following file structure:

    ::

        ├── <dataset_id_1>
        │   ├── samples
        │   │   ├── <zone_id_1>
        │   │   │   ├── <image_id_1>
        │   │   │   │   ├── <tile_id>.jpg
        │   │   │   │   └── ...
        │   │   │   ├── <image_id_2>
        │   │   │   │   ├── <tile_id>.jpg
        │   │   │   │   └── ...
        │   │   │   └── ...
        │   │   ├── <zone_id_2>
        │   │   │   ├── samples
        │   │   │   └── ...
        │   │   └── ...
        │   └── labels
        │       ├── <zone_id_1>
        │       │   ├── <tile_id>.json
        │       │   └── ...
        │       ├── <zone_id_2>
        │       │   ├── <tile_id>.json
        │       │   └── ...
        │       └── ...
        ├── <dataset_id_2>
        │   └── ...
        └── ...

    Where samples are projected jpg tiles of imagery and annotation are a *geojson* **FeatureCollection**.

    .. hint::
        The constructor arguments allows for explicit selection of *datasets*, *zones*, *images* or *tiles* and explicit
        exclusion of *datasets*, *zones*, *images* or *tiles* by providing list of identifiers to select or exclude. If
        no such sequence or provided, valid data point will be automatically discovered from the filesystem.

    Args:
        path (PathLike): The path path to the dataset root, it may be either absolute or relative to the current
            working directory.
        select_datasets (Sequence[str]): Optional. If provided, it must be a sequence of uuid used to select the
            datasets in which data points will be fetched.
        exclude_datasets (Sequence[str]): Optional. If provided, it must be a sequence of uuid used to excludes
            datasets from the data point search.
        select_zones (Sequence[str]): Optional. If provided, it must be a sequence of uuid used to select the zones
            in which data points will be fetched.
        exclude_zones (Sequence[str]): Optional. If provided, it must be a sequence of uuid used to excludes
            zones from the data point search.
        select_images (Sequence[str]): Optional. If provided, it must be a sequence of identifiers used to select the
            images in which data points will be fetched.
        exclude_images (Sequence[str]): Optional. If provided, it must be a sequence of identifiers used to excludes
            images from the data point search.
        select_tiles (Sequence[str]): Optional. If provided, it must be a sequence of identifiers used to select the
            tiles which will be fetched.
        exclude_tiles (Sequence[str]): Optional. If provided, it must be a sequence of identifiers used to excludes
            tiles from the data point search.
        tile_driver (callable): Optional. Default to a |TileDriver|. A ``function(path_tuple, **matched_groups)``
            callable which return a |TileCollection|-like object called for each data point (see :ref:`drivers`).
        annotation_driver (callable): Optional. Default to a |AnnotationDriver|. A
            ``function(path_tuple, **matched_groups)`` callable which return an |Annotation|-like object called for
            each data point (see :ref:`drivers`).
        use_taxonomy (bool): Optional. Default to ``True``. If ``False``, the global taxonomy will not be passed to
            the annotation driver and implicit taxonomies for each annotation files, with no interplay guarantee.
        strict (bool): If ``False``, solitary tiles or annotations will be silently dropped instead of raising.
        cache (bool): If ``True``, the dataset will be looked-up in the user's cache directory and if found loaded from
            there instead of walking the file-system. Note that although this could speedup dataset loading multiple
            fold for big datasets, one may load stale data when using the cache.

    Warnings:
        If providing a custom annotation driver, the ``use_taxonomy`` flag is not guaranteed to work and it is up to the
        provided driver to handle dataset taxonomies if needed (See also the |TaxonomyReader| helper class).

    Raises:
        ValueError: If the requested playground datasets have mismatching taxonomies and global |Taxonomy| usage was
            requested.
        ValueError: If tile could not be matched to an annotation and ``strict`` is ``True``.
        ValueError: If no tile/annotation pair could be found.

    Warns:
        UserWarning: If the requested playground datasets have mismatching taxonomies and global |Taxonomy| usage was
            not requested.

    .. _Intelligence Playground: https://playground.intelligence-airbusds.com/

    """

    _cache = DatasetCache('playground')  # For easy subclass prefix selection.

    def __init__(self, path, select_datasets=(), select_zones=(), select_images=(), select_tiles=(),
                 exclude_datasets=(), exclude_zones=(), exclude_images=(), exclude_tiles=(), tile_driver=None,
                 annotation_driver=None, use_taxonomy=True, strict=True, cache=False):
        # Build eventual regular expressions from include and exclude sequences
        # +-> Dataset:
        dataset_regex = r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'

        if select_datasets:
            dataset_regex = r'(?:{})'.format('|'.join(select_datasets))

        if exclude_datasets:
            dataset_regex = '{exclude}{regex}'.format(exclude=r'(?!{})'.format('|'.join(exclude_datasets)),
                                                      regex=dataset_regex)
        # +-> Zone:
        zone_regex = r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'

        if select_zones:
            zone_regex = r'(?:{})'.format('|'.join(select_zones))

        if exclude_zones:
            zone_regex = '{exclude}{regex}'.format(exclude=r'(?!{})'.format('|'.join(exclude_zones)),
                                                   regex=zone_regex)
        # +-> Image:
        image_regex = r'[^/]+'

        if select_images:
            image_regex = r'(?:{})'.format('|'.join(select_images))

        if exclude_images:
            image_regex = '{exclude}{regex}'.format(exclude=r'(?!{})'.format('|'.join(exclude_images)),
                                                    regex=image_regex)
        # +-> Tile:
        tile_regex = r'[0-9a-f]{32}'

        if select_tiles:
            tile_regex = r'(?:{})'.format('|'.join(select_tiles))

        if exclude_tiles:
            tile_regex = '{exclude}{regex}'.format(exclude=r'(?!{})'.format('|'.join(exclude_tiles)),
                                                   regex=tile_regex)

        # Build path patterns
        # +-> Tile:
        tile_pattern = '{{dataset_id:{dataset_regex}}}/' \
                       'samples/' \
                       '{{zone_id:{zone_regex}}}/' \
                       '{{image_id:{image_regex}}}/' \
                       '{{tile_id:{tile_regex}}}.jpg'.format(dataset_regex=dataset_regex,
                                                             zone_regex=zone_regex,
                                                             image_regex=image_regex,
                                                             tile_regex=tile_regex)

        # +-> Annotation:
        annotation_pattern = '{{dataset_id:{dataset_regex}}}/' \
                             'labels/' \
                             '{{zone_id:{zone_regex}}}/' \
                             '{{tile_id:{tile_regex}}}.json'.format(dataset_regex=dataset_regex,
                                                                    zone_regex=zone_regex,
                                                                    tile_regex=tile_regex)

        # Initialize dataset
        super(PlaygroundDataset, self).__init__(tile_pattern=tile_pattern, annotation_pattern=annotation_pattern,
                                                tile_driver=TileDriver() if tile_driver is None else tile_driver,
                                                annotation_driver=AnnotationDriver()
                                                if annotation_driver is None else annotation_driver,
                                                path=path, strict=strict, sort_key=lambda group: group, cache=cache)

        # Load taxonomies and attach it to the annotation driver if needed
        path = Path(path)
        taxonomy_reader = TaxonomyReader()
        reference_taxonomy = None
        reference_dataset = None
        for dataset_id in {group[0] for group in self._group_index}:
            try:
                taxonomy = taxonomy_reader(path / dataset_id)
            except FileNotFoundError:
                raise FileNotFoundError('Invalid dataset: No taxonomy could be found in {}.'.format(path / dataset_id))

            if reference_taxonomy is None:
                reference_dataset = dataset_id
                reference_taxonomy = taxonomy

            if reference_taxonomy != taxonomy:
                if use_taxonomy:
                    raise ValueError('Some datasets have mismatching taxonomies:\n'
                                     'Dataset {}:\n'
                                     '{}\n'
                                     'is different from\n'
                                     'Dataset {}:\n'
                                     '{}'.format(reference_dataset, reference_taxonomy, dataset_id, taxonomy))
                else:
                    warn('Some datasets have mismatching taxonomies:\n'
                         'Dataset {}:\n'
                         '{}\n'
                         'is different from\n'
                         'Dataset {}:\n'
                         '{}'.format(reference_dataset, reference_taxonomy, dataset_id, taxonomy), UserWarning)

        if use_taxonomy:
            self._annotation_driver.taxonomy = reference_taxonomy

    def __getitem__(self, item):
        """Read and return the i-th |DataPoint| of the |PlaygroundDataset|.

        Args:
            item (int): The |DataPoint| index in the dataset.

        Returns:
            DataPoint: The dataset i-th entry.

        """
        # Fetch match
        group = self._group_index[item]
        match = {name: value for name, value in zip(self._matching_groups, group)}

        # Fetch data point
        data_point = super(PlaygroundDataset, self).__getitem__(item)
        data_point.dataset_id = match['dataset_id']
        data_point.zone_id = match['zone_id']
        data_point.tile_id = match['tile_id']

        return data_point
