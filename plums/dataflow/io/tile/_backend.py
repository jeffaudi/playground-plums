import imghdr

import numpy as np

from plums.commons.path import Path

# Image backends import
try:
    import PIL.Image
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False

try:
    from ._vendor.turbojpeg import TurboJPEG, TJPF
    turbo_jpeg_handler = TurboJPEG()
    _HAS_TURBO_JPEG = True
except ImportError:
    turbo_jpeg_handler = None
    _HAS_TURBO_JPEG = False

try:
    import lycon
    _HAS_LYCON = True
except ImportError:
    _HAS_LYCON = False

try:
    import cv2
    _HAS_CV2 = True
except ImportError:
    _HAS_CV2 = False

# Backend import sanity check
if not _HAS_TURBO_JPEG and not _HAS_LYCON and not _HAS_CV2 and not _HAS_PILLOW:
    raise ImportError('Error importing plums.dataflow.io: No suitable image backend where found. '
                      'For more information, please refer to the documentation.')


# Image IO operation per type
def _load_jpg(filepath):
    """Open a JPG image as an RGB :class:`~numpy.ndarray`.

    Args:
        filepath (|Path|): The path to the image file on disk.

    Returns:
        :class:`~numpy.ndarray`: The image an HWC array of value.

    """
    # Backend selection (Fastest to slowest).
    if _HAS_TURBO_JPEG:
        with open(str(filepath), 'rb') as f:
            data = turbo_jpeg_handler.decode(f.read(), pixel_format=TJPF.RGB)
        return data
    elif _HAS_LYCON:
        return lycon.load(str(filepath))
    elif _HAS_CV2:
        return cv2.cvtColor(cv2.imread(str(filepath)), cv2.COLOR_BGR2RGB)
    elif _HAS_PILLOW:
        with PIL.Image.open(str(filepath)) as image:
            return np.asarray(image)
    else:
        raise RuntimeError('No backend available to open JPG image.')


def _dump_jpg(filepath, data):
    """Save a JPG image from an RGB :class:`~numpy.ndarray`.

    Args:
        filepath (|Path|): The path to the image file on disk.
        data (:class:`~numpy.ndarray`): The image an HWC array of value.

    """
    # Backend selection (Fastest to slowest).
    if _HAS_TURBO_JPEG:
        with open(str(filepath), 'wb') as f:
            f.write(turbo_jpeg_handler.encode(data, pixel_format=TJPF.RGB))
    elif _HAS_LYCON:
        lycon.save(str(filepath), data)
    elif _HAS_CV2:
        cv2.imwrite(str(filepath), cv2.cvtColor(data, cv2.COLOR_RGB2BGR))
    elif _HAS_PILLOW:
        PIL.Image.fromarray(data).save(str(filepath))
    else:
        raise RuntimeError('No backend available to save JPG image.')


def _load_png(filepath):
    """Open a PNG image as an RGB :class:`~numpy.ndarray`.

    Args:
        filepath (|Path|): The path to the image file on disk.

    Returns:
        :class:`~numpy.ndarray`: The image an HWC array of value.

    """
    # Backend selection (Fastest to slowest).
    if _HAS_LYCON:
        return lycon.load(str(filepath))
    elif _HAS_CV2:
        return cv2.cvtColor(cv2.imread(str(filepath)), cv2.COLOR_BGR2RGB)
    elif _HAS_PILLOW:
        with PIL.Image.open(str(filepath)) as image:
            return np.asarray(image)
    else:
        raise RuntimeError('No backend available to open PNG image.')


def _dump_png(filepath, data):
    """Save a PNG image from an RGB :class:`~numpy.ndarray`.

    Args:
        filepath (|Path|): The path to the image file on disk.
        data (:class:`~numpy.ndarray`): The image an HWC array of value.

    """
    # Backend selection (Fastest to slowest).
    if _HAS_LYCON:
        lycon.save(str(filepath), data)
    elif _HAS_CV2:
        cv2.imwrite(str(filepath), cv2.cvtColor(data, cv2.COLOR_RGB2BGR))
    elif _HAS_PILLOW:
        PIL.Image.fromarray(data).save(str(filepath))
    else:
        raise RuntimeError('No backend available to save PNG image.')


class Image(object):
    """A wrapper class around a loaded image data stored as an interfaced exposed RGB HWC :class:`~numpy.ndarray`.

    Args:
        array_data (|ArrayInterfaced|): An |ArrayInterfaced| instance to wrap.

    """

    __slots__ = '_array_data',

    def __init__(self, array_data):
        self._array_data = array_data

    @property
    def __array_interface__(self):  # noqa: D401
        """dict: The stored |ArrayInterfaced| :data:`__array_interface__` property."""
        return self._array_data.__array_interface__

    @classmethod
    def load(cls, filepath):
        """Load an image as an RGB :class:`~numpy.ndarray`.

        Args:
            filepath (PathLike): The path to the image file on disk.

        Returns:
            (|Image|): An |Image| instance wrapping an HWC :class:`~numpy.ndarray`.

        """
        filepath = Path(filepath)
        image_type = imghdr.what(str(filepath))

        if image_type == 'jpeg':
            return cls(_load_jpg(filepath))
        elif image_type == 'png':
            return cls(_load_png(filepath))
        else:
            raise TypeError('Unsupported image type: {}.'.format(image_type))

    def save(self, filepath):
        """Save an |Image| instance wrapping an HWC :class:`~numpy.ndarray`.

        Args:
            filepath (PathLike): The path to the image file on disk.

        """
        filepath = Path(filepath)

        if filepath.ext.lower() in ('jpg', 'jpeg'):
            _dump_jpg(filepath, self._array_data)
        elif filepath.ext.lower() == 'png':
            _dump_png(filepath, self._array_data)
        else:
            raise ValueError('Unsupported image type: {}.'.format(filepath.ext))
