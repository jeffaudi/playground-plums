import pytest
import numpy as np

from playground_plums.plot.engine.color.color import Color


tol = 1e-3

_ctype_list = [
    "sRGB1", "sRGB255",
    "XYZ1", "XYZ100",
    "sRGB1-linear",
    "xyY1", "xyY100",
    "CIELab", "CIELCh",
    "JCh",
    "CAM02-UCS", "CAM02-LCD", "CAM02-SCD"

]


@pytest.fixture(params=_ctype_list)
def ctype(request):
    return request.param


@pytest.fixture(params=_ctype_list)
def add_ctype(request):
    return request.param


_color_dict = {
    "black": Color(0, 0, 0),
    "red": Color(255, 0, 0),
    "green": Color(0, 255, 0),
    "blue": Color(0, 0, 255),
    "yellow": Color(255, 255, 0),
    "cyan": Color(0, 255, 255),
    "magenta": Color(255, 0, 255)
}


def _mix_color(base, add):
    if base == "black":
        return _color_dict[add]
    elif base == "red":
        if add == "black":
            return _color_dict[base]
        elif add == "red":
            return _color_dict["red"]
        elif add == "green":
            return _color_dict["yellow"]
        elif add == "blue":
            return _color_dict["magenta"]
        else:
            raise ValueError
    elif base == "green":
        if add == "black":
            return _color_dict[base]
        elif add == "red":
            return _color_dict["yellow"]
        elif add == "green":
            return _color_dict["green"]
        elif add == "blue":
            return _color_dict["cyan"]
        else:
            raise ValueError
    elif base == "blue":
        if add == "black":
            return _color_dict[base]
        elif add == "red":
            return _color_dict["magenta"]
        elif add == "green":
            return _color_dict["cyan"]
        elif add == "blue":
            return _color_dict["blue"]
        else:
            raise ValueError


def _make_mix_color(base):
    return {add: _mix_color(base, add) for add in ["black", "red", "green", "blue"]}


_mix_color_dict = {base: _make_mix_color(base) for base in ["black", "red", "green", "blue"]}


@pytest.fixture(params=["black", "red", "green", "blue"])
def base(request):
    return request.param


@pytest.fixture(params=["black", "red", "green", "blue"])
def add(request):
    return request.param


@pytest.fixture()
def color_triple(base, add):
    base_color = _color_dict[base]
    add_color = _color_dict[add]
    mix_color = _mix_color_dict[base][add]

    return base_color, add_color, mix_color


class TestColor:
    def test_color(self, ctype, add_ctype, color_triple):
        base_color, add_color, mix_color = color_triple
        # Skip if xyY1 or xyY100 and black color
        if ("xy" in ctype and base_color.components.sum() == 0) or \
                ("xy" in add_ctype and add_color.components.sum() == 0):
            return True

        assert base_color.astype(ctype).astype('sRGB255') == base_color.astype('sRGB255')
        assert not base_color.astype(ctype).astype('sRGB255') != base_color.astype('sRGB255')

        assert np.all(np.isclose(base_color.astype(ctype).astype('sRGB255'),
                                 base_color,
                                 atol=tol))
        assert np.all(np.isclose((1 * base_color.astype(ctype)).astype('sRGB255'),
                                 base_color,
                                 atol=tol))
        assert np.isclose(base_color.astype(ctype) - base_color, 0.0)
        assert np.all(np.isclose(
            np.clip((base_color.astype(ctype) + add_color.astype(add_ctype)).astype('sRGB255'), 0, 255),
            mix_color,
            atol=tol))

        with pytest.raises(TypeError):
            base_color + 'str'

        with pytest.raises(TypeError):
            base_color + (5, )

        with pytest.raises(TypeError):
            base_color + [0, 5, 0]

        with pytest.raises(TypeError):
            base_color * 'str'

        with pytest.raises(TypeError):
            base_color * (5, )

        with pytest.raises(TypeError):
            base_color * [0, 5, 0]

        with pytest.raises(TypeError):
            base_color - 'str'

        with pytest.raises(TypeError):
            base_color - (5, )

        with pytest.raises(TypeError):
            base_color - [0, 5, 0]

    def test_weighted(self, ctype, add_ctype):
        assert np.all(
            np.isclose(
                np.clip(Color(255, 0, 0).astype(ctype) + (0.5 * Color(0, 255, 0).astype(add_ctype)),
                        0, 255),
                Color(255, 187.51603, 0).astype(ctype),
                atol=tol))
