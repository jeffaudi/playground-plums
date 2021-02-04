from functools import wraps

import numpy as np


def max_value(dtype):
    """Compute the maximum allowed value for a given integer data-type, or 1 for floating point data-type.

    Args:
        dtype (numpy.dtype): A valid numpy data type.

    Returns:
        int, float: The maximum allowed value for the provided data-type.

    Raises:
        ValueError: If the data-type is complex or invalid.

    """
    try:
        return np.iinfo(dtype).max
    except ValueError:
        try:
            # Assert floating point
            _ = np.finfo(dtype).max  # noqa: F841
            # Ok means return 1.0
            return 1.0
        except ValueError:
            raise ValueError('No maximum value could be computed for the data-type {}'.format(dtype))


def on_slice(channel_slice, function):
    """Wrap a numpy ufunc to only apply it on a given slice in the image channel dimension.

    Args:
        channel_slice (tuple): A channel dimension slice on which to limit the function application.
        function (callable): The function to wrap.

    Returns:
        callable: The wrapped function.

    """
    @wraps(function)
    def on_slice_callable(array):
        return function(np.squeeze(array[..., slice(channel_slice[0], channel_slice[1])]))

    return on_slice_callable


def on_index(channel_index, function):
    """Wrap a numpy ufunc to only apply it on a given slice in the image channel dimension.

    Args:
        channel_index (tuple): A channel dimension index tuple on which to aplly the function application.
        function (callable): The function to wrap.

    Returns:
        callable: The wrapped function.

    """
    @wraps(function)
    def on_index_callable(array):
        return function(np.squeeze(array[..., channel_index]))

    return on_index_callable


class ConversionFunction(object):
    """Make a *pixel-type* conversion function.

    Args:
        origin_ptype (|ptype|): The *pixel-type* from which to convert the |TileIO|.
        destination_ptype (|ptype|): The *pixel-type* into which to convert the |TileIO|.

    """

    def __init__(self, origin_ptype, destination_ptype):
        self._origin = origin_ptype
        self._destination = destination_ptype

    def __repr__(self):
        """Return a human readable name from the conversion function."""
        return '{}To{}()'.format(self._origin, self._destination)

    __str__ = __repr__

    def __call__(self, image_array):
        """Convert a given HWC :class:`~numpy.ndarray` from one *pixel-type* to another.

        Args:
            image_array (:class:`~numpy.ndarray`): A HWC image array in the original |ptype|.

        Returns:
            image_array (:class:`~numpy.ndarray`): A converted HWC image array in the destination |ptype|.

        Raises:
            ValueError: If the input image array channel dimension shape is inconsistent with the assumed original
                |ptype|.

        """
        if image_array.shape[2] != len(self._origin):
            raise ValueError('Inconsistent shape: '
                             'Expected {} channels but got {}.'.format(len(self._origin), image_array.shape[2]))

        out_array = [None] * len(self._destination)
        for i, channel in enumerate(self._destination):
            out_array[i] = channel.get_conversion_fn_from(self._origin)(image_array)

        return np.stack(out_array, axis=-1)
