try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

from .utils import ConversionFunction
from .channels import channels_register, Channel


class ptype(object):  # noqa: N801
    """The *pixel-type* of a given image: A representation of its spectral base.

    As each actual pixel are stored as vectors, understanding of the base used is compulsory to decode a given pixel
    vector, the *pixel-type* class describes the way a given pixel is stored as a vector of *channel* values
    (e.g. *RGB*, *BGR*, *HSL*, *XYZ* etc...).

    Args:
        string (str): A string description of the *pixel-type* as a list of channel characters (*e.g.* ``'RGB'``,
            ``'rgY'``, ``'bgr'``, ``'y'``...).

    """

    def __init__(self, string):
        self._channels = tuple(channels_register[item]() for item in string)

    def __repr__(self):
        """Return a pythonic representation or a *pixel-type*."""
        return 'ptype(\'{}\')'.format(''.join(channel.__short_name__ for channel in self._channels))

    def __str__(self):
        """Return a human readable representation or a *pixel-type*."""
        return ''.join(channel.__short_name__ for channel in self._channels)

    def __hash__(self):
        """Compute the *pixel-type* python hash as the has of its |Channel| vector."""
        return hash(self._channels)

    def __getitem__(self, index):
        """Get the i-th |Channel| from the *pixel-type* |Channel| vector."""
        return self._channels[index]

    def __len__(self):
        """Get the dimension number of the |Channel| space of the *pixel-type*."""
        return len(self._channels)

    def __eq__(self, other):
        """Return whether 2 |ptype| instances have the same |Channel| vector, thus describing the same *pixel-type*."""
        try:
            return self._channels == tuple(channel for channel in other)
        except TypeError:
            return NotImplemented

    def __ne__(self, other):
        """Return whether 2 |ptype| do not have the same |Channel| vector, thus not describing the same *pixel-type*."""
        return not self == other

    @staticmethod
    def _find_secondary_in_primary(secondary_list, primary_list):
        len_primary, len_secondary = len(primary_list), len(secondary_list)
        i, last = 0, len_primary - len_secondary + 1
        while True:
            try:
                found = primary_list.index(secondary_list[0], i, last)  # find first elem in secondary_list
            except ValueError:
                return None
            if primary_list[found:found + len_secondary] == secondary_list:
                return found, found + len_secondary
            else:
                i = found + 1

    def __contains__(self, channels):
        """Return whether the *pixel-type* |Channel| vector contains a given |Channel| or |Channel| "sub-vector"."""
        return self.slice(channels) is not None

    def contains(self, channels):
        """Return whether the *pixel-type* |Channel| vector contains a given |Channel| or |Channel| "sub-set"."""
        return self.index(channels) is not None

    def slice(self, channels):
        """Compute the *pixel-type* |channel| vector slice of a given sub-vector.

        Args:
            channels (tuple, |Channel|): Either a single |Channel| or a tuple of |Channel| assumed to be a sub-vector of
                the *pixel-type* |Channel| vector.

        Returns:
            (int, int) or ``None``: The slice of the |Channel| vector corresponding to the input or ``None`` if it is
            not contained in the |Channel| vector.

        """
        if isinstance(channels, Channel):
            channels = channels,
        return self._find_secondary_in_primary(channels, self._channels)

    def index(self, channels):
        """Compute the *pixel-type* |channel| indices of a given sub-set.

        Args:
            channels (tuple, |Channel|): Either a single |Channel| or a tuple of |Channel| assumed to be a sub-set of
                the *pixel-type* |Channel| vector.

        Returns:
            (int, ) or ``None``: The indices of the |Channel| corresponding to the input or ``None`` if it is
            not contained in the |Channel| vector.

        """
        if isinstance(channels, Channel):
            channels = channels,
        try:
            return tuple(self._channels.index(channel) for channel in channels)
        except ValueError:
            return None

    @lru_cache(maxsize=10)
    def get_conversion_fn_to(self, destination_ptype):
        """Compute the conversion function from self to another ptype.

        Args:
            destination_ptype (|ptype|): The destination ptype object.

        Returns:
            callable: A conversion function to move from one ptype to another.

        """
        return ConversionFunction(self, destination_ptype)


RGB = rgb = ptype('RGB')  # Pixel stored as *Red*-*Green*-*Blue* channels.
RGBA = rgba = ptype('RGBA')   # Pixel stored as *Red*-*Green*-*Blue*-*Alpha* channels.
BGR = bgr = ptype('BGR')  # Pixel stored as *Blue*-*Green*-*Red* channels.
BGRA = bgra = ptype('BGRA')  # Pixel stored as *Blue*-*Green*-*Red*-*Alpha* channels.
GREY = grey = Y = y = ptype('Y')   # Pixel stored as a single *Grey* channels.
