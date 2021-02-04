from inspect import signature, Parameter
from collections import defaultdict

from ordered_set import OrderedSet

from plums.commons.path import Path
from plums.commons.data import DataPoint
from .base import SizedDataset
from ..utils.cache import DatasetCache, NotInCacheError
from ..utils.path import PathResolver


def _check_driver(fn, name):
    """Validate a driver callable to ensure it is a callable with the correct signature.

    Such a sanity check is not strictly required as the :term:`EAFP` coding style would be a far more natural fit for
    this particular instance. However, this would delay the exception raise to the first
    :meth:`~PatternDataset.__getitem__` call which would be confusing for the user, hence Plums going out of its way
    to reassure the user on its driver compatibility preemptively, that is, when the |PatternDataset| is *actually*
    instantiated.

    Note that the return "signature" can not be inspected beforehand and that its validity check will thus be delayed.

    Args:
        fn (Callable): A driver callable to inspect.
        name (str): The driver scope (Tile or Annotation) to customise the exception message in case of failure.

    Raises:
        TypeError: If the provided callable is not driver-compatible.

    """
    try:
        fn_signature = signature(fn)
    except TypeError:
        raise TypeError('Invalid {} driver: Expected a callable, got {}.'.format(name, fn.__class__.__name__))

    parameter_kinds = tuple(parameter.kind for parameter in fn_signature.parameters.values())
    if len(parameter_kinds) != 2 or parameter_kinds != (Parameter.POSITIONAL_OR_KEYWORD, Parameter.VAR_KEYWORD):
        raise TypeError('Invalid {} driver: '
                        'Expected function(path_tuple, **matched_groups), got function{}.'.format(name, fn_signature))


class PatternDataset(SizedDataset):
    """A |SizedDataset| of which tile/annotation pairs are globed from a pair of matching dataset path patterns.

    A path pattern is provided using a micro-language as described bellow:

    * A dataset pattern is a path-like string where path elements may be either "*components*" or "*groups*".
    * A *component* designate an entity which value is fixed, *e.g.* in ``/some/pattern``, ``some`` and ``pattern`` are
      components. Components define exact-matches where the name of the element to match is known in advance.
    * A *group* designate a named-entity whose value is unknown. They are delimited by curly braces *{* and *}*, *e.g.*
      in ``/some/pattern/{with}/some/{groups}``, ``{with}`` and ``{groups}`` are groups, and may additionally define
      constraints to limit or expand the group match capability. The text consequential to the opening bracket is the
      group's name and must be unique to the pattern. A forward-slash */* following the group name indicates a
      *recursive* group, which is a group which might span over multiple folders. If one wishes to constraint the group
      match, a colon *:* after the group name (or recursive slash) is used to add a *regex* on which all candidate
      entities will be matched (note that for recursive groups, the regex will apply on each of the path entity, not on
      the whole group).
    * The last group or component of the pattern must be a file, indicated by an *extension* added at the end. Multiple
      extension *alternatives* may be provided, using brackets *[* and *]* delimiters and separating each alternative
      with a pipe *|* alternator.

    In a more formal manner, the *path pattern* language
    `EBNF <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_ grammar might look something like:

    .. code-block:: ebnf

        pattern = [ absolute ], { folder }, file ;
        absolute = SEPARATOR ;
        folder = entry, SEPARATOR ;
        file = entry, ".", extension ;
        entry = FSNAME | "{" IDENTIFIER, [ SEPARATOR ], [ ":", REGEX ], "}" ;
        extension = EXTENSION | "[", EXTENSION, { "|", EXTENSION }, "]" ;
        IDENTIFIER = ( "_" | LETTER ), { "_" | LETTER | NUMBER } ;
        FSNAME = { LETTER | NUMBER | "_" | "-" | " " } ;

    .. hint::
        The annotation path pattern may be degenerate (*i.e.* point to a single, non variable file) in which case the
        path matching every tile path will be the degenerate annotation path. A degenerate flag set to ``True`` is
        passed to the enclosed annotation driver called to allow for caching mechanism and reduce the file load overhead
        in this case.

    The |PatternDataset| also expects a pair of callable, called the **drivers** which will be fed a tuple of path and
    the path pattern named-group match ``name: value`` pairs. It should returns objects compatible with the Plums
    data-model, *i.e.* a |Tile|-like object for tiles and an |Annotation|-like object for annotations.

    See Also:
        The |TileIO| and |load|/|dump| helpers provided in the ``plums.dataflow.io`` module.

    Args:
        tile_pattern (str): The path pattern corresponding to the dataset tiles.
        annotation_pattern (str): The path pattern corresponding to the dataset annotations.
        tile_driver (callable): A ``function(path_tuple, **matched_groups)`` callable which return a
            |TileCollection|-like object.
        annotation_driver (callable): A ``function(path_tuple, **matched_groups)`` callable which return an
            |Annotation|-like object.
        path (PathLike): If the tile and annotation path pattern a relative, a folder from which to start discovering
            tile/annotation file pairs.
        sort_key (callable): Optional. If provided, it must be function of one match group which return a sorting key
            used to sort tile/annotation pairs.

            .. warning::

                    Although the data points will be sorted, the matched file paths ordering will be entirely
                    **filesystem dependent** which is no better than random.

        strict (bool): If ``False``, solitary tiles or annotations will be silently dropped instead of raising.
        cache (bool): If ``True``, the dataset will be looked-up in the user's cache directory and if found loaded from
            there instead of walking the file-system. Note that although this could speedup dataset loading multiple
            fold for big datasets, one may load stale data when using the cache.

    Raises:
        ValueError: If the provided tile path pattern is degenerate.
        ValueError: If the provided tile path pattern have no named group in common with the provided annotation
            path pattern.
        ValueError: If tile could not be matched to an annotation and ``strict`` is ``True``.
        ValueError: If no tile/annotation pair could be found.

    """

    _cache = DatasetCache('pattern')  # For easy subclass prefix selection.

    def __init__(self, tile_pattern, annotation_pattern, tile_driver, annotation_driver, path=None, sort_key=None,
                 strict=True, cache=False):
        # Handle PathLike path
        path = Path(path) if path is not None else None

        # Initialize resolvers
        self._tile_resolver = PathResolver(tile_pattern)
        _check_driver(tile_driver, 'Tile')
        self._tile_driver = tile_driver
        self._annotation_resolver = PathResolver(annotation_pattern, reserved=('degenerate', ))
        _check_driver(annotation_driver, 'Annotation')
        self._annotation_driver = annotation_driver
        # +-> Cache key parameters
        self._keys = (tile_pattern, annotation_pattern, '' if path is None else str(path))

        # Degeneracy sanity checks
        if self._tile_resolver.degenerate:
            raise ValueError('Invalid tile path pattern: Tile pattern degeneracy is not supported.')
        # +-> Compute groups found in both patterns (used to match files)
        if self._annotation_resolver.degenerate:
            self._matching_groups = self._tile_resolver.group_names
        else:
            self._matching_groups = \
                tuple(OrderedSet(self._tile_resolver.group_names) & OrderedSet(self._annotation_resolver.group_names))
        if not self._matching_groups:
            raise ValueError('Invalid path pattern pair: No common group could be found in between patterns.')

        # Cache init sequence branching
        if cache:
            try:
                # Retrieve entry from cache
                data = self._cache.retrieve(*self._keys)
            except NotInCacheError:
                # If not in cache, continue startup sequence normally
                data = None

            if data is not None:
                # If in cache, load from cached data and exit.
                self._deserialize(data)
                return

        # Glob and resolve paths
        # +-> Initialise attributes
        self._tiles_index = {}
        self._tiles_database = defaultdict(tuple)
        self._annotations_index = {}
        self._annotations_database = defaultdict(tuple)
        # +-> Glob
        tile_generator = self._tile_resolver.find(path=path)
        annotation_generator = self._annotation_resolver.find(path=path)
        # +-> Compute databases
        for tile_path in tile_generator:
            group = tuple(tile_path.match[key] for key in self._matching_groups)
            self._tiles_index[tile_path] = group
            self._tiles_database[group] += (tile_path, )

        for annotation_path in annotation_generator:
            if self._annotation_resolver.degenerate:
                group = ()
            else:
                group = tuple(annotation_path.match[key] for key in self._matching_groups)
            self._annotations_index[annotation_path] = group
            self._annotations_database[group] += (annotation_path, )

        # Compute index, assert matches, sort and compute length
        self._group_index = []
        for key, paths in self._tiles_database.items():
            if not self._annotation_resolver.degenerate and key not in self._annotations_database:
                if strict:
                    raise ValueError('Invalid dataset: {} does not have a matching annotation.'.format(paths))
                continue
            self._group_index.append(key)
        if not self._group_index:
            raise ValueError('Invalid dataset: No matches where found between tiles and annotation.')

        if sort_key is not None:
            self._group_index = sorted(self._group_index, key=sort_key)

        # Store dataset index in cache.
        self._cache.cache(self._serialize(), *self._keys)

    def __getitem__(self, item):
        """Read and return the i-th |DataPoint| of the |PatternDataset|.

        Args:
            item (int): The |DataPoint| index in the dataset.

        Returns:
            DataPoint: The dataset i-th entry.

        """
        # Fetch group
        group = self._group_index[item]
        match = {name: value for name, value in zip(self._matching_groups, group)}

        # Fetch tiles through driver
        tiles = self._tile_driver(self._tiles_database[group], **match)

        # Fetch annotation through driver
        annotation_path_tuple = self._annotations_database[group] \
            if not self._annotation_resolver.degenerate else self._annotations_database[()]
        annotation = \
            self._annotation_driver(annotation_path_tuple, degenerate=self._annotation_resolver.degenerate, **match)

        # Return DataPoint
        return DataPoint(tiles, annotation)

    def __len__(self):
        """Return the dataset's number of tile/annotation pair groups."""
        return len(self._group_index)

    def _serialize(self):
        """Construct a JSON serializable version of the dataset."""
        tile_database = {str(group): {'group': group,
                                      'paths': tuple({'path': str(path),
                                                      'match': path.match} for path in paths)}
                         for group, paths in self._tiles_database.items()}
        annotations_database = {str(group): {'group': group,
                                             'paths': tuple({'path': str(path),
                                                             'match': getattr(path, 'match', {})} for path in paths)}
                                for group, paths in self._annotations_database.items()}
        return {'tile': tile_database, 'annotation': annotations_database, 'group_index': self._group_index}

    def _deserialize(self, data):
        """Update internals from a JSON serialized data dictionary."""
        # Initialize structures
        self._tiles_index = {}
        self._tiles_database = defaultdict(tuple)
        self._annotations_index = {}
        self._annotations_database = defaultdict(tuple)

        # Deserialize tiles database and index
        for path_dict in data['tile'].values():
            group = tuple(path_dict['group'])
            for path in path_dict['paths']:
                tile_path = Path(path['path'])
                tile_path.match = path['match']
                self._tiles_index[tile_path] = group
                self._tiles_database[group] += (tile_path, )

        # Deserialize annotation database and index
        for path_dict in data['annotation'].values():
            group = tuple(path_dict['group'])
            for path in path_dict['paths']:
                annotation_path = Path(path['path'])
                annotation_path.match = path['match']
                self._annotations_index[annotation_path] = group
                self._annotations_database[group] += (annotation_path, )

        # Deserialize group index
        self._group_index = [tuple(group) for group in data['group_index']]
