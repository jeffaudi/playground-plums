import pytest
import numpy as np

from plums.plot.engine.color import ContinuousColorMap, DiscreteColorMap, KeyPointsColorMap, \
    CircularColorMap, LightnessColorMap, Color, SemiCircularColorMap


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


class TestColorMap:
    def _base_color_map_test(self, cm, **kwargs):
        assert cm == cm.__class__(**kwargs)
        assert not cm != cm.__class__(**kwargs)

        # Check get_color return type and ctype
        assert isinstance(cm.get_color(0.5), Color)
        assert cm.get_color(0.5).ctype == cm.ctype

        # Check map_fn handling
        color = cm.get_color(0.5)
        leg_map = cm.map_fn
        cm.map_fn = lambda x: 0.5 * leg_map(x)
        assert cm.get_color(1) == color
        assert not cm == cm.__class__(**kwargs)
        assert cm != cm.__class__(**kwargs)
        cm.map_fn = leg_map

        # Check __call__ return type, ctype and numpy integration
        value_array = [[[0.1, 0.2, 0.3],
                        [0.4, 0.5, 0.6]],
                       [[0.7, 0.8, 0.9],
                        [0.1, 0.2, 0.3]]]

        color_array = cm(value_array, keep_colors=True)
        components_array = cm(value_array)

        for i in range(color_array.shape[0]):
            for j in range(color_array.shape[1]):
                for k in range(color_array.shape[2]):
                    color = color_array[i, j, k]
                    assert color.ctype == cm.ctype
                    assert np.all(color.components == components_array[i, j, k, :])

        # Check get_color, __call__ return type, ctype and numpy integration when discretized and range handling
        if isinstance(cm, ContinuousColorMap):
            # Check range handling
            # Save value
            start_color = cm.get_color(cm._start)
            middle_color = cm.get_color(0.5 * (cm._start + cm._end))
            end_color = cm.get_color(cm._end)
            # Change range and check equivalence
            start = cm._start
            end = cm._end
            cm._start = start + 1
            cm._end = end * 3
            assert cm.get_color(start + 1) == start_color
            assert cm.get_color(0.5 * (start + 1 + 3 * end)) == middle_color
            assert cm.get_color(3 * end) == end_color
            cm._start = start
            cm._end = end

            assert isinstance(cm.get_color(0.5), Color)
            assert cm.get_color(0.5).ctype == cm.ctype

            color_array = cm.discretize(256)(value_array, keep_colors=True)
            components_array = cm.discretize(256)(value_array)

            for i in range(color_array.shape[0]):
                for j in range(color_array.shape[1]):
                    for k in range(color_array.shape[2]):
                        color = color_array[i, j, k]
                        assert color.ctype == cm.ctype
                        assert np.all(color.components == components_array[i, j, k, :])

    def test_key_point_cm(self, ctype):
        cm = KeyPointsColorMap({1: 2 * Color(0, 255, 0), 0: 2 * Color(0, 0, 255), 2: 2 * Color(255, 0, 0)}, ctype=ctype)
        self._base_color_map_test(cm,
                                  mapping={1: 2 * Color(0, 255, 0), 0: 2 * Color(0, 0, 255), 2: 2 * Color(255, 0, 0)},
                                  ctype=ctype)

        assert cm.get_color(0.5) == Color(0, 255, 255).astype(ctype)
        assert cm.get_color(1.5) == Color(255, 255, 0).astype(ctype)

    def test_circular(self, ctype):
        cm = CircularColorMap(0, ctype=ctype)
        array = np.linspace(0, 1, 10)
        assert all(np.allclose(color._components, Color(50, 0, 0, ctype='JCh')._components)
                   for color in cm(array, keep_colors=True))

        cm = CircularColorMap(0.3, ctype=ctype)
        self._base_color_map_test(cm, ray=0.3, ctype=ctype)

        # Check periodicity
        for value in array:
            assert cm.get_color(value) == cm.get_color(value + 1.0)

        array = np.linspace(0, 1, 10)
        local_deriv = np.diff(np.linspace(0, 1, 10 - 1))[0] * np.diff(cm(array, keep_colors=True))
        local_deriv = np.diff(np.linspace(0, 1, 10 - 2))[0] * np.diff(local_deriv)
        assert np.allclose(local_deriv.astype(np.float64), 0)

    def test_semi_circular(self, ctype):
        cm = SemiCircularColorMap(0, 3, 0.1, ctype=ctype)
        array = np.linspace(0, 1, 10)
        assert all(np.allclose(color._components, Color(40, 0, 0, ctype='JCh')._components)
                   for color in cm(array, keep_colors=True))

        cm = SemiCircularColorMap(0.3, 3, 0.1, ctype=ctype)
        self._base_color_map_test(cm, ray=0.3, period=3, intensity=0.1, ctype=ctype)

        # # Check periodicity
        for value in array:
            assert cm.get_color(value) == cm.get_color(value + 3.0)

    def test_linear(self, ctype):
        color = Color(50, 100, 50, ctype='JCh')
        cm = LightnessColorMap(color, lightness_range=(0, 0), ctype=ctype)
        array = np.linspace(0, 1, 10)
        assert all(color == Color(50, 100, 50, ctype='JCh').astype(ctype)
                   for color in cm(array, keep_colors=True))

        cm = LightnessColorMap(color, ctype=ctype)
        self._base_color_map_test(cm, color=color, ctype=ctype)
        array = np.linspace(0, 1, 10)
        local_deriv = np.diff(np.linspace(0, 1, 10 - 1))[0] * np.diff(cm(array, keep_colors=True))
        local_deriv = np.diff(np.linspace(0, 1, 10 - 2))[0] * np.diff(local_deriv)
        assert np.allclose(local_deriv.astype(np.float64), 0)

        cm = LightnessColorMap(color, chroma_range=(0.1, 0.1), ctype=ctype)
        self._base_color_map_test(cm, color=color, chroma_range=(0.1, 0.1), ctype=ctype)
        array = np.linspace(0, 1, 10)
        local_deriv = np.diff(np.linspace(0, 1, 10 - 1))[0] * np.diff(cm(array, keep_colors=True))
        local_deriv = np.diff(np.linspace(0, 1, 10 - 2))[0] * np.diff(local_deriv)
        assert np.allclose(local_deriv.astype(np.float64), 0)

    def test_discrete(self, ctype):
        cm = CircularColorMap(0.3, ctype='sRGB1')
        n = 10

        with pytest.raises(ValueError):
            cm_ = DiscreteColorMap(list(range(1, n)) + [0],
                                   [cm.get_color(np.sqrt(3) * np.sqrt(2) * i) for i in range(n)],
                                   ctype='sRGB1')

        cm_ = DiscreteColorMap(list(range(n)),
                               [cm.get_color(np.sqrt(3) * np.sqrt(2) * i) for i in range(n)],
                               ctype='sRGB1')

        self._base_color_map_test(cm_,
                                  values=list(range(n)),
                                  colors=[cm.get_color(np.sqrt(3) * np.sqrt(2) * i) for i in range(n)],
                                  ctype='sRGB1')
