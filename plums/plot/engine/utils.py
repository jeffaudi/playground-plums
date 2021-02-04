import PIL.ImageFont
import numpy as np

from plums.commons import Path


def get_text_color(background_color):
    """Select the appropriate text color (black or white) based on the luminance of the background color.

    Arguments:
        background_color (tuple): The record color (RGB or RGBA format).

    Returns:
        tuple: The chosen text color (black or white).

    """
    # Counting the perceptive luminance - human eye favors green color...
    luminance = (0.299 * background_color[0] + 0.587 * background_color[1] + 0.114 * background_color[2]) / 255.
    # Set text color to white on "dark" backgrounds and dark color on "light" background
    if luminance <= 0.5:
        return 255, 255, 255
    return 0, 0, 0


def get_outline_color(background_color):
    """Select the appropriate text color (black or white) based on the luminance of the background color.

    Arguments:
        background_color (tuple): The record color (RGB or RGBA format).

    Returns:
        tuple: The chosen text color (black or white).

    """
    # Counting the perceptive luminance - human eye favors green color...
    luminance = (0.299 * background_color[0] + 0.587 * background_color[1] + 0.114 * background_color[2]) / 255.
    # Set text color to white on "dark" backgrounds and dark color on "light" background
    if luminance <= 0.5:
        return 150, 150, 150
    return 100, 100, 100


def get_default_font(text_size):
    """Get a default font to render targets with text.

    Args:
        text_size (int): text size in pixels

    Returns:
        :class:`~PIL.ImageFont.FreeTypeFont`

    """
    assert isinstance(text_size, int) and text_size > 0, "Text size should be positive integer"
    return PIL.ImageFont.truetype(font=str(Path(__file__)[:-1] / "fonts" / "arial.ttf"), size=text_size)


def dict_equal(dictionary, other_dictionary):
    """Compare two dict with :class:`numpy.ndarray` value handling.

    Comparison is made in two parts:
    * We first check that both dict have the same keys.
    * If they do we then compare each value pair and lazily return ``False`` if any comparison fails.

    Note:
        Value comparison implicitly delegates to the :meth:`__eq__` method of singular elements and avoids explicit
        type-check. Although this is somewhat slower as it involves potentially long element-wise equality checks,
        it allows for duck-typing and rich type handling by particular classes.

    Args:
        dictionary (dict): A :class:`dict` to compare with another.
        other_dictionary (dict): A :class:`dict` to compare with another.

    Returns:
        bool: :any:`True` if the two dict are equal in keys and content.

    """
    if set(dictionary.keys()) == set(other_dictionary.keys()):
        for key, value in dictionary.items():
            if isinstance(value, np.ndarray) or isinstance(other_dictionary[key], np.ndarray):
                # If an ndarray we need explicitly go through np.all() to compare
                if not np.all(value == other_dictionary[key]):
                    # If not the same lazily exit now
                    return False
            else:
                # Otherwise we delegate to cmp()
                if not value == other_dictionary[key]:
                    # If not the same lazily exit now
                    return False
        # All equal, return True
        return True
    # Not even the same keys, return False
    return False
