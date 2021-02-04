import numpy as np

from .utils import on_slice, on_index, max_value

channels_register = {}


def new_channel(x):
    """Create and return a new channel frame with the same spatial dimension as the input array.

    Args:
        x (:class:`~numpy.ndarray`): An array which serves as a reference to create a channel frame.

    Returns:
        :class:`~numpy.ndarray`: A new array, with the same spatial shape as the input array and filled with the
        maximum allowed value for the input array data-type.

    """
    return np.ones((x.shape[0], x.shape[1]), dtype=x.dtype) * max_value(x.dtype)


def identity(x):
    """Perform an identity operation on a given :class:`~numpy.ndarray`.

    Args:
        x (:class:`~numpy.ndarray`): An array on which to perform identity.

    Returns:
        :class:`~numpy.ndarray`: The input array, identical.

    """
    return x


def linear_combination_factory(*factors):
    """Construct a conversion function which applies a linear combination of components.

    Args:
        *factors (int, float): A collections of linear combination scalar factors.

    Returns:
        callable: A conversion functions which makes a linear combination of image channels.

    """
    vector = np.array([[factor] for factor in factors])

    def linear_combination(array):
        """Compute a linear combination of image channels.

        Args:
            array (:class:`~numpy.ndarray`): The input image as a HWC ndarray.

        Returns:
            :class:`~numpy.ndarray`: The resulting image channel, as computed from the input image channels.

        """
        return array.dot(vector).squeeze(axis=-1)

    return linear_combination


class MetaRegister(type):
    """A meta-class which add a registration logic where all classes call a :meth:`register` method when created."""

    def __new__(mcs, name, bases, dct):  # noqa: N804
        """Construct a |Registered| class with a :meth:`register` call on class creation."""
        new_cls = super(MetaRegister, mcs).__new__(mcs, name, bases, dct)
        for b in bases:
            if hasattr(b, 'register'):
                b.register(new_cls)
        new_cls.__id__ = hash(getattr(new_cls, '__full_name__', None))
        return new_cls


class Registered(object, metaclass=MetaRegister):
    """A class with auto-registration logic, implemented in the :meth:`register` method called upon class creation."""

    @classmethod
    def register(cls, new_cls):
        """Register the class in the :data:`channels_register` dictionary.

        Args:
            new_cls (|Channel|): The class to register by its short name, along with its lower-cased and long aliases.

        """
        channels_register[new_cls.__short_name__] = new_cls
        channels_register[new_cls.__short_name__.lower()] = new_cls
        channels_register[new_cls.__full_name__] = new_cls


class Channel(Registered):
    """Base class for all image channels.

    It acts as an *unknown* channels itself, that is to say a channel on which we have no knowledge of any sort.

    Args:
        conversions (dict): A mapping between a tuple of |Channel| and a conversion function.

    """

    __short_name__ = 'X'
    __full_name__ = 'UNKNOWN'

    def __init__(self, conversions=None):
        self.__conversion__ = conversions if conversions is not None else {}

    def get_conversion_fn_from(self, pixel_type):
        """Return a conversion function on a slice in the channel dimension to make self from a given |ptype|.

        Args:
            pixel_type (|ptype|): A |ptype| from which to construct self.

        Returns:
            callable: A conversion function which acts on a channel slice.

        """
        if self in pixel_type:
            return on_slice(pixel_type.slice(self), identity)

        for channels, conversion_fn in self.__conversion__.items():
            if channels in pixel_type:
                # If sub-vector, use conversion function
                return on_slice(pixel_type.slice(channels), conversion_fn)
            if pixel_type.contains(channels):
                # If sub-set, define a new function which reorders then uses the real conversion function
                return on_index(pixel_type.index(channels), conversion_fn)

        return new_channel

    def __str__(self):
        """Return a human readable representation of a |Channel|."""
        return self.__full_name__

    def __repr__(self):
        """Return a pythonic representation of a |Channel|."""
        return 'Channel({})'.format(self.__full_name__)

    def __eq__(self, other):
        """Return whether two |Channel| are identical, *i.e.* if they have the same name."""
        try:
            return self.__id__ == other.__id__
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        """Return whether two |Channel| do not have the same name."""
        return not self == other

    def __hash__(self):
        """Return the python hash of the |Channel| name."""
        return self.__id__


class Red(Channel):
    """A 'red' image channel class."""

    __short_name__ = 'R'
    __full_name__ = 'RED'

    def __init__(self):
        super(Red, self).__init__({
            (Grey, ): identity,
        })


class Green(Channel):
    """A 'green' image channel class."""

    __short_name__ = 'G'
    __full_name__ = 'GREEN'

    def __init__(self):
        super(Green, self).__init__({
            (Grey, ): identity,
        })


class Blue(Channel):
    """A 'blue' image channel class."""

    __short_name__ = 'B'
    __full_name__ = 'BLUE'

    def __init__(self):
        super(Blue, self).__init__({
            (Grey, ): identity,
        })


class Grey(Channel):
    """A 'grey' image channel class (*i.e.* luminance channel)."""

    __short_name__ = 'Y'
    __full_name__ = 'GRAY'

    def __init__(self):
        super(Grey, self).__init__({
            (Red, Green, Blue): linear_combination_factory(0.299, 0.587, 0.114),
        })


class Alpha(Channel):
    """An 'alpha' image channel class."""

    __short_name__ = 'A'
    __full_name__ = 'Alpha'
