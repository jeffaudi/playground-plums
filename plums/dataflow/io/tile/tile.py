import numpy as np

from plums.commons.data import Tile as CommonsTile
from plums.commons.data import PropertyContainer
from ._format import rgb, RGB, rgba, RGBA, bgr, BGR, bgra, BGRA, grey, GREY, y, Y, ptype
from ._backend import Image


class Tile(PropertyContainer, CommonsTile):
    """Load and manipulate images through a high level interface.

    The |TileIO| class acts as a "concrete" counterpart to the *representational* |Tile| class defined in the *Plums*
    data-model.

    It necessarily stems from an actual image file **on-disk** and it additionally encloses 2 *type* information:

    * The *data-type* which is nothing more than the native numpy *dtype* and indicate the actual numeric type
      used (e.g. *uint8*, *float32*...).
    * The *pixel-type* which indicates the way a given pixel is stored as a vector of *channel* values
      (e.g. *RGB*, *BGR*, *HSL*, *XYZ* etc...).

    Args:
        filename (PathLike): The filename from where the image will be read.
        ptype (|ptype|): Optional. Default to ``RGB``. The image pixel-type (e.g. RGB, BGR or Grey).
        dtype (:class:`~numpy.dtype`): Optional. Default to :class:`~numpy.uint8`.
            The internal :class:`~numpy.ndarray` storage data type.
        **properties (Any): Additional properties to store alongside the image.

    Attributes:
        filename (PathLike): The filename from where the image was read.

    """

    def __init__(self, filename, ptype=RGB, dtype=np.dtype('u1'), **properties):
        # Developer pass-through to allow seamless tile copy without reading from disk every time.
        # +-> For array data (and dtype)
        if properties.get('__array__', None) is None:
            array = np.asarray(Image.load(filename))
        else:
            array = properties.pop('__array__')

        # +-> For ptype
        if properties.get('__ptype__', None) is None:
            initial_ptype = None
        else:
            initial_ptype = properties.pop('__ptype__')

        # Actual __init__ is beginning here.
        super(Tile, self).__init__(array, **properties)
        self._ptype = RGB if initial_ptype is None else initial_ptype
        self.filename = filename
        self.totype(ptype=ptype, dtype=dtype)

    @property
    def ptype(self):  # noqa: F811
        """|ptype|: The image pixel-type.

        In a similar fashion as data-type, the pixel-type encodes the way a particular pixel vector can be interpreted
        as actual data carried by the tile.

        """
        return self._ptype

    @ptype.setter
    def ptype(self, new_ptype):
        self.totype(ptype=new_ptype)

    @property
    def dtype(self):
        """:class:`~numpy.dtype`: The internal :class:`~numpy.ndarray` storage data type.

        Warnings:
            Modifying the :attr:`dtype` will only modify the storage :class:`~numpy.ndarray`'s data type. No domain
            conversion logic is applied, that is to say that, for example, converting a :class:`~numpy.uint8` |TileIO|
            to :class:`~numpy.float64` will effectively change the underlying array's type but the data will still be
            between 0 and 255.

        """
        return self._array_data.dtype

    @dtype.setter
    def dtype(self, new_dtype):
        self.totype(dtype=new_dtype)

    @property
    def shape(self):
        """tuple: The internal :class:`~numpy.ndarray` storage shape."""
        return self._array_data.shape

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

    def save(self, filepath, ptype=RGB):
        """Save the |TileIO| as a image on disk.

        Args:
            ptype (|ptype|): If provided, the |ptype| into which to save the |TileIO|.
            filepath (|Path|): The path where to save the image.

        Raises:
            ValueError: If ``filepath`` refers to un unsupported image type.
            TypeError: If ``ptype`` is not **RGB** as it is the only supported save format for now.

        """
        if ptype not in (rgb, ):
            raise TypeError('Invalid ptype provided: Only RGB is supported for save operation for now.')
        Image(self.astype(ptype=ptype, dtype=np.uint8).data).save(filepath)

    def clone(self):
        """Create a copy of the |TileIO| in a new memory location.

        Returns:
            |TileIO|: A new |TileIO| instance.

        """
        array_data = np.array(self._array_data, copy=True, dtype=self.dtype)
        return Tile(self.filename, ptype=self.ptype, dtype=self.dtype, __array__=array_data, __ptype__=self.ptype)

    def totype(self, ptype=None, dtype=None):
        """Convert the |TileIO| storage format in-place to a new pixel-type or a new data-type.

        Args:
            ptype (|ptype|): If provided, the |ptype| into which to convert the |TileIO|.
            dtype (:class:`~numpy.dtype`): If provided, it must be a valid numpy data-type into which the internal
                :class:`~numpy.ndarray` storage will be converted.

        """
        if ptype is not None and ptype != self.ptype:
            self._array_data = self._ptype.get_conversion_fn_to(ptype)(self._array_data)
            self._ptype = ptype

        if dtype is not None and dtype != self.dtype:
            self._array_data = self._array_data.astype(dtype)

    def astype(self, ptype=None, dtype=None):
        """Convert the |TileIO| to a new pixel-type or a new data-type in a new |TileIO|.

        Args:
            ptype (|ptype|): If provided, the |ptype| into which to convert the |TileIO|.
            dtype (:class:`~numpy.dtype`): If provided, it must be a valid numpy data-type into which the internal
                :class:`~numpy.ndarray` storage will be converted.

        Returns:
            |TileIO|: A new converted |TileIO|.

        """
        tile = self.clone()
        tile.totype(ptype=ptype, dtype=dtype)
        return tile
