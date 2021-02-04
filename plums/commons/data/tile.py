from sys import version_info
from collections import OrderedDict

try:
    import PIL.ImageFile
    import PIL.Image
    HAS_PILLOW = True
except ImportError:
    PIL = None
    HAS_PILLOW = False

from .base import _Array, ArrayInterfaced
from .mixin import PropertyContainer


class TileCollection(OrderedDict):
    """An *ordered dictionary*-like collection of |Tile|.

    It is effectively a subclass of :class:`~collections.OrderedDict` with a friendlier constructor.

    Named |Tile| can be added either as item tuples (in an ordered dictionary fashion) or as keyword argument, note that
    ordered keyword arguments where introduced in python 3.6 and using those in python 3.5 would result in a random
    ordering. Thus, to avoid hard to track mistake, a :exc:`ValueError` will be raised if one attempts to do so.

    Anonymous |Tile| can be added as position arguments, in which case a ``tile_<n>`` name will be added to fit in the
    dictionary, where *n* is the current |Tile| index position.

    Args:
        *tiles (Tile, Tuple[str, Tile]): Either a |Tile|, in which case a default name is used, or a tuple
            ``(name, Tile)`` where the name will be used as the tile's key.
        **named_tiles (Tile): A |Tile| to add to the collection, as the keyword's entry.

    Raises:
        ValueError: If attempting to use keyword arguments on python :math:`<=` 3.5.
        TypeError: If any provided tile in not a |Tile|-like object.

    """

    def __init__(self, *tiles, **named_tiles):
        if version_info[1] <= 5 and named_tiles:
            raise ValueError('Ordered keyword argument were introduced in Python 3.6 and can not be used for '
                             'instantiating a tile collection in previous python version.')

        tiles = tuple(('tile_{}'.format(i), item) if isinstance(item, Tile) else item for i, item in enumerate(tiles))
        tiles += tuple(named_tiles.items())

        # Tile-like sanity check
        try:
            not_tiles = any(not isinstance(tile, Tile) for name, tile in tiles)
        except TypeError:
            not_tiles = True
        if not_tiles:
            raise TypeError('Expected each tiles to expose the __array_interface__ attribute, along with "filename", '
                            '"size", "width" and "height"')

        super(TileCollection, self).__init__(tiles)

    @property
    def iloc(self):
        """Access stored tiles through their insert positions."""
        class _PositionIndexer:
            def __init__(self, *tiles):
                self._tiles = tiles

            def __getitem__(self, item):
                return self._tiles[item]

        return _PositionIndexer(*self.values())


class Tile(ArrayInterfaced):
    """Utility class which wraps an |ArrayInterfaced| and forward its :data:`__array_interface__`.

    It is not intended to be instantiated as such but rather subclassed (like |TileWrapper|) or used to check whether
    an particular instance validates as a |Tile|.

    Because it registers :class:`PIL.Image.Image` as a virtual subclasses, this implies that only subclasses of
    |Tile| (such as |TileWrapper|) or **Pillow** :class:`~PIL.Image.Image` are considered valid |Tile|.

    Args:
        array_data (|ArrayInterfaced|): An |ArrayInterfaced| instance to wrap.

    """

    def __init__(self, array_data):
        super(Tile, self).__init__()
        if not isinstance(array_data, ArrayInterfaced):
            raise TypeError('Tile expect an object which exposes the __array_interface__')

        self._array_data = array_data

    @property
    def __array_interface__(self):  # noqa: D401
        """dict: The stored |ArrayInterfaced| :data:`__array_interface__` property."""
        return self._array_data.__array_interface__


if HAS_PILLOW:
    Tile.register(PIL.ImageFile.ImageFile)
    Tile.register(PIL.Image.Image)


class TileWrapper(PropertyContainer, Tile):
    """A wrapper around a **Numpy** :class:`~numpy.ndarray` which forwards its :data:`__array_interface__`.

    It accepts any instance which have an :data:`__array_interface__` and a shape property as a valid
    :class:`~numpy.ndarray` (see |_Array|).

    The properties it exposes mimic some **Pillow** :class:`~PIL.Image.Image` properties which make this class useful
    to wrap images opened with different library (like **OpenCV**) and make them usable in places where one would
    expect a **Pillow** :class:`~PIL.Image.Image` with useful metadata.

    Transformation into an actual **Pillow** :class:`~PIL.Image.Image` can be done with:

    .. code-block:: python

        def as_pillow_image(tile_wrapper):
            pillow_image = PIL.Image.fromarray(np.asarray(tile_wrapper))
            pillow_image.filename = tile_wrapper.filename
            pillow_image.info.update(tile_wrapper.info)

            return pillow_image

    Args:
        array_data (:class:`~numpy.ndarray`): The image data
        filename (str): Optional. Default to None. The filename from where the image was read (if any).
        **properties (Any): Additional properties to store alongside the image.

    Attributes:
        filename (str): The image filename or ``None``.
        properties (dict): Properties provided as kwargs in the constructor.

    """

    def __init__(self, array_data, filename=None, **properties):
        if not isinstance(array_data, _Array):
            raise TypeError('TileWrapper expect a ndarray-like object, got: {}'.format(array_data.__class__.__name__))

        if len(array_data.shape) != 3:
            raise ValueError('TileWrapper expect a 3-dim ndarray, got: {}'.format(len(array_data.shape)))

        if array_data.shape[0] <= array_data.shape[2] or array_data.shape[1] <= array_data.shape[2]:
            raise ValueError('TileWrapper expect a HWC formatted image')

        super(TileWrapper, self).__init__(array_data, **properties)
        self.filename = filename

    @property
    def size(self):
        """tuple: The stored image size as a ``(width, height)`` tuple."""
        return tuple(reversed(self._array_data.shape[:2]))

    @property
    def width(self):
        """float: The stored image width."""
        return self._array_data.shape[1]

    @property
    def height(self):
        """float: The stored image height."""
        return self._array_data.shape[0]

    @property
    def info(self):  # noqa: D401
        """dict: Additional properties stored alongside the image."""
        return self.properties

    @property
    def data(self):
        """:class:`~numpy.ndarray`: The stored image data."""
        return self._array_data
