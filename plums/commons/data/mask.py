from .base import GeoInterfaced, _Array
from .mixin import IdentifiedMixIn, PropertyContainer


class MaskCollection(object):
    """Data model class which aggregates multiple |Mask| together.

    It also implement a index and name handy access to stored |Mask|.

    Examples:
        >>> rm = RasterMask(image, 'raster-data')
        >>>  vm = VectorMask([[[0, 0], [0, 1], [1, 1], [0, 0]]], 'vector-data')
        >>> mc = MaskCollection(rm, vm)
        >>> mc[0] == rm
        True
        >>> mc[1] == vm
        True
        >>> mc['vector-data'] == vm
        True
        >>> mc['raster-data'] == rm
        True

    Args:
        *masks (|Mask|): |Mask| instances to aggregate.

    Attributes:
        masks (tuple): Stored |Mask| instances.

    """

    def __init__(self, *masks):
        super(MaskCollection, self).__init__()
        self.masks = masks
        self._name_map = {self.masks[index].name: index for index in range(len(self.masks))}

    def __getitem__(self, key):
        """Get a stored |Mask| from its name or its index position.

        Returns:
            |Mask|: The specified |Mask| instance.

        Raises:
            IndexError: If ``key`` does not correspond to any |Mask|.

        """
        try:
            return self.masks[self._name_map[key]]
        except KeyError:
            return self.masks[key]


class Mask(PropertyContainer, IdentifiedMixIn):
    """Utility class which implements a generic template of a |Mask|.

    It is not intended to be instantiated as such but rather subclassed (like |VectorMask| or |RasterMask|) or to
    type-test.

    Args:
        name (str): The |Mask| name.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |Mask|.

    Attributes:
        name (str): The |Mask| name.
        id (str): The instance *uuid*.
        properties (dict): Properties provided as kwargs in the constructor.

    """

    def __init__(self, name, *args, **properties):
        super(Mask, self).__init__(*args, **properties)
        self.properties['mask'] = True
        self.name = name


class VectorMask(GeoInterfaced, Mask):
    """Data model class which represents a |VectorMask|.

    It implements the :data:`__geo_interface__` and represents itself as a GeoJSON *Feature*.

    Args:
        coordinates (list, tuple): A GeoJSON-valid coordinate sequence describing the |VectorMask| shape.
        name (str): The |VectorMask| name.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |VectorMask|.

    Attributes:
        name (str): The |Mask| name.
        id (str): The instance *uuid*.
        coordinates (list, tuple): A GeoJSON-valid coordinate sequence describing the |VectorMask| shape.
        properties (dict): Properties provided as kwargs in the constructor.

    """

    def __init__(self, coordinates, name, id=None, **properties):
        super(VectorMask, self).__init__(name=name, id=id, **properties)
        self.coordinates = coordinates

    def to_geojson(self):
        """Implement the object conversion into a valid GeoJSON mapping.

        Returns:
            dict: The GeoJSON representation of the |VectorMask|.

        """
        prop_dict = {"name": self.name}
        prop_dict.update(self.properties)

        return {
            'type': 'Feature',
            'geometry': {
                'type': "Polygon",
                'coordinates': self.coordinates
            },
            'properties': prop_dict
        }


class RasterMask(Mask):
    """Data model class which represents a |RasterMask|.

    It forwards the stored array's  :data:`__array_interface__` and exposes useful properties in a similar fashion
    as |TileWrapper|.

    Args:
        data (:class:`~numpy.ndarray`): The |RasterMask| raster data.
        name (str): The |RasterMask| name.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |RasterMask|.

    Attributes:
        name (str): The |Mask| name.
        id (str): The instance *uuid*.
        properties (dict): Properties provided as kwargs in the constructor.

    """

    def __init__(self, data, name, id=None, **properties):
        super(RasterMask, self).__init__(name=name, id=id, **properties)

        if not isinstance(data, _Array):
            raise TypeError('RasterMask expect a ndarray-like object, got: {}'.format(data.__class__.__name__))

        self._array_data = data

    @property
    def size(self):
        """tuple: The stored mask size as a ``(width, height)`` tuple."""
        return tuple(reversed(self._array_data.shape[:2]))

    @property
    def width(self):
        """float: The stored mask width."""
        return self._array_data.shape[1]

    @property
    def height(self):
        """float: The stored mask height."""
        return self._array_data.shape[0]

    @property
    def data(self):  # noqa: D401
        """:class:`~numpy.ndarray`: The stored mask data."""
        return self._array_data

    @property
    def __array_interface__(self):  # noqa: D401
        """dict: The stored |ArrayInterfaced| :data:`__array_interface__` property."""
        return self._array_data.__array_interface__
