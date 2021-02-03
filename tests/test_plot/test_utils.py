import pytest

from playground_plums.plot.engine.utils import get_default_font, get_text_color


def test_get_text_color():
    assert get_text_color((255, 0, 0)) == (255, 255, 255)
    assert get_text_color((0, 255, 0)) == (0, 0, 0)
    assert get_text_color((0, 0, 255)) == (255, 255, 255)
    assert get_text_color((255, 255, 0)) == (0, 0, 0)
    assert get_text_color((0, 255, 255)) == (0, 0, 0)
    assert get_text_color((255, 0, 255)) == (255, 255, 255)
    assert get_text_color((128, 128, 128)) == (0, 0, 0)


def test_get_default_font():
    import PIL.ImageFont

    with pytest.raises(AssertionError):
        get_default_font(-5)

    assert isinstance(get_default_font(10), PIL.ImageFont.FreeTypeFont)
