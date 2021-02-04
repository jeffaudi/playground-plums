import abc

import geojson

from .mixin import IdentifiedMixIn


def _check_methods(cls, *methods):
    mro = cls.__mro__
    for method in methods:
        for base_cls in mro:
            if method in base_cls.__dict__:
                if base_cls.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True


class ArrayInterfaced(object, metaclass=abc.ABCMeta):
    """Abstract base class which checks for the :data:`__array_interface__` property.

    Implement a subclass hook to check for the presence of the :data:`__array_interface__` property and mark as a
    virtual subclass of |ArrayInterfaced| classes which implement the interface.

    Examples:
        >>> class MockArrayInterfaced(object):
        ...     @property
        ...     def __array_interface__(self):
        ...         # This passes the inheritance test although this
        ...         # __array_interface__ implementation is invalid
        ...         return None
        >>> isinstance(MockArrayInterfaced(), ArrayInterfaced)
        True

    """

    @classmethod
    def __subclasshook__(cls, subclass):
        """Check for the presence of the :data:`__array_interface__` property in potential virtual subclasses."""
        if cls is ArrayInterfaced:
            return _check_methods(subclass,
                                  "__array_interface__")
        return NotImplemented


class GeoInterfaced(IdentifiedMixIn, metaclass=abc.ABCMeta):
    """Abstract class which checks for the :data:`__geo_interface__` property and provides a :data:`__geo_interface__`.

    Implement a subclass hook to check for the presence of the :data:`__geo_interface__` property and mark as a virtual
    subclass of |GeoInterfaced| classes which implement the interface.

    Args:
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.

    Examples:
        >>> class MockGeoInterfaced(object):
        ...     @property
        ...     def __geo_interface__(self):
        ...         # This actually is a valid GeoJSON mapping
        ...         return {'type': 'FeatureCollection', 'features': []}
        >>> isinstance(MockGeoInterfaced(), GeoInterfaced)
        True

    Attributes:
        id (str): The instance *uuid*.

    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(GeoInterfaced, self).__init__(*args, **kwargs)

    @property
    def is_valid(self):
        """bool: Return ``True`` if the :data:`__geo_interface__` returns a valid GeoJSON object."""
        geo_object = geojson.GeoJSON.to_instance(self.to_geojson())
        return geo_object.is_valid

    @property
    def __geo_interface__(self):  # noqa: D401
        """dict: A GeoJSON valid mapping."""
        return self.to_geojson()

    @abc.abstractmethod
    def to_geojson(self):
        """Abstract method which implements the object conversion into a valid GeoJSON mapping.

        Subclasses must override this method in order to be instantiable.

        Returns:
            dict: The GeoJSON representation of the |GeoInterfaced|.

        """
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, subclass):
        """Check for the presence of the :data:`__geo_interface__` property in potential virtual subclasses."""
        if cls is GeoInterfaced:
            return _check_methods(subclass,
                                  "__geo_interface__")
        return NotImplemented


class _Array(object, metaclass=abc.ABCMeta):
    """Abstract base class which checks for both the :data:`__array_interface__` and the shape properties.

    Implement a subclass hook to check for the presence of the :data:`__array_interface__` and the shape properties
    and mark as a virtual subclass of |_Array| classes which implement the interface.

    Examples:
        >>> class MockArray(object):
        ...     @property
        ...     def __array_interface__(self):
        ...         # This passes the inheritance test although this
        ...         # __array_interface__ implementation is invalid
        ...         return None
        ...
        ...     @property
        ...     def shape(self):
        ...         # This passes the inheritance test although this
        ...         # shape implementation is invalid
        ...         return None
        >>> isinstance(MockArray(), _Array)
        True

    """

    @classmethod
    def __subclasshook__(cls, subclass):
        """Check for the :data:`__array_interface__` and shape properties in potential virtual subclasses."""
        if cls is _Array:
            return _check_methods(subclass,
                                  "__array_interface__",
                                  "shape")
        return NotImplemented
