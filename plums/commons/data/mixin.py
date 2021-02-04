import uuid
from abc import ABCMeta
from copy import deepcopy


class SlottedDictMeta(ABCMeta):
    """Add the attribute `__all_slots__` to a class.

    `__all_slots__`  is a set that contains all unique slots of a class,
    including the ones that are inherited from parents.

    """

    def __init__(cls, name, bases, dictionary):
        super(SlottedDictMeta, cls).__init__(name, bases, dictionary)
        slots_iterator = (getattr(c, '__slots__', ()) for c in cls.__mro__)
        # `__slots__` might only be a single string,
        # so we need to put the strings into a tuple.
        slots_converted = ((slots,) if isinstance(slots, str) else slots for slots in slots_iterator)
        cls.__all_slots__ = set()
        cls.__all_slots__.update(*slots_converted)


class SlottedDict(object, metaclass=SlottedDictMeta):
    """Base class which enables both :any:`__slots__` and :attr:`~object.__dict__` for mix-in classes."""

    __slots__ = '__dict__'

    @staticmethod
    def _is_dunder(name):
        return name[:2] == '__' and name[-2:] == '__'

    def _get_slot(self, name):
        if name[:2] == '__' and not name[-2:] == '__':  # Beware, name mangling here
            return getattr(self, '_{}{}'.format(self.__class__.__name__, name))
        return getattr(self, name)

    def __copy__(self):
        """Construct a shallow copy of a :class:`SlottedDict`."""
        cls = self.__class__
        result = cls.__new__(cls)
        result.__setstate__(self.__getstate__())
        return result

    def __deepcopy__(self, memo=None):
        """Construct a deep copy of a :class:`SlottedDict`."""
        memo = {} if memo is None else memo

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.__setstate__(deepcopy(self.__getstate__(), memo))

        return result

    def __getstate__(self):
        """Return a dictionary of all slotted and in dictionary attributes."""
        dct = {key: value for key, value in self.__dict__.items()}

        for key in self.__all_slots__:
            if self._is_dunder(key):
                continue
            dct[key] = self._get_slot(key)

        return dct

    def __setstate__(self, state):
        """Set attributes values from a dictionary of all slotted and in dictionary attributes."""
        for key, value in state.items():
            setattr(self, key, value)


class IdentifiedMixIn(SlottedDict):
    """Mix In class to add a unique identifier and the ability to manually provide it in the constructor.

    Args:
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.

    Attributes:
        id (str): The instance *uuid*.

    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        # Init id
        id = kwargs.pop('id', None)
        if hasattr(self.__class__, 'id'):
            self._id = id or str(uuid.uuid4())
        else:
            self.id = id or str(uuid.uuid4())
        super(IdentifiedMixIn, self).__init__(*args, **kwargs)


class PropertyContainer(SlottedDict):
    """Utility class which swallows every key-word arguments provided and exposes them as attributes.

    Args:
        **properties (Any): Properties which are stored in :attr:`properties` and exposed as attributes.

    """

    __slots__ = '_properties'

    def __init__(self, *args, **properties):
        id = properties.pop('id', None)
        self._properties = properties
        if id is not None:
            super(PropertyContainer, self).__init__(*args, id=id)
        else:
            super(PropertyContainer, self).__init__(*args)

    @property
    def properties(self):  # noqa: D401
        """dict: Properties provided as kwargs in the constructor."""
        return self.__getattribute__('_properties')

    @properties.setter
    def properties(self, value):
        super(PropertyContainer, self).__setattr__('_properties', value)

    def __getattribute__(self, key):
        """Get an attribute or a property value."""
        try:
            return super(PropertyContainer, self).__getattribute__(key)
        except AttributeError as error:
            if key in ('properties', '_properties'):
                raise error

            try:
                return self.properties[key]
            except KeyError:
                raise error

    def __setattr__(self, key, value):
        """Add or set an attribute or a property."""
        if key == '_properties':
            super(PropertyContainer, self).__setattr__(key, value)
            return

        try:
            if key in self._properties.keys():
                self._properties[key] = value
            else:
                super(PropertyContainer, self).__setattr__(key, value)
        except AttributeError:
            super(PropertyContainer, self).__setattr__(key, value)

    def __delattr__(self, key):
        """Delete an attribute or a property."""
        try:
            del self._properties[key]
        except (KeyError, AttributeError):
            super(PropertyContainer, self).__delattr__(key)

    def __dir__(self):
        """Return the standard dir with :attr:`properties` added."""
        return list(super(PropertyContainer, self).__dir__()) + list(self.properties.keys())
