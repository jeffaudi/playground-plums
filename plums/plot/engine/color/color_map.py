from abc import abstractmethod, ABC
from copy import deepcopy

import numpy as np

from plums.plot.engine.utils import dict_equal
from plums.plot.engine.color.color import Color


def identity(x):
    """Return exactly what was provided."""
    return x


class ColorMap(ABC):
    """An abstract base class for all ``ColorMap`` classes.

    Subclass must implement the private :meth:`_get_color` method which maps a given ``value`` to a |Color| instance.

    Args:
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    Attributes:
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which (ideally bijectivelly)
            maps input values to a working range.

    """

    def __init__(self, ctype='sRGB255', map_fn=None):
        self.ctype = ctype
        self.map_fn = map_fn or identity

    def __eq__(self, other):
        """Return ``True`` if two |ColorMap| have the same attributes and class."""
        if self.__class__ == other.__class__:
            return dict_equal(self.__dict__, other.__dict__)
        return False

    def __ne__(self, other):
        """Return ``True`` if two |ColorMap| do not have the same attributes and class."""
        return not self == other

    @property
    def range(self):
        """tuple: The input range supported by the |ColorMap|.

        Warnings:
            The range returned corresponds to the input range mapped through :attr:`map_fn`

        """
        return self._start, self._end

    @abstractmethod
    def _get_color(self, value):
        """Map a given ``value`` to a |Color| instance.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        raise NotImplementedError

    def get_color(self, value):
        """Get the |Color| corresponding to the value provided.

        Note:
            The actual ``value`` used to get the corresponding |Color| is the ``value`` provided mapped through
            :attr:`map_fn`.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        return self._get_color(self.map_fn(value)).astype(self.ctype)

    def __call__(self, array, keep_colors=False):
        """Generalizes :meth:`get_color` on :class:`~np.ndarray` inputs.

        Note that because on the non-vectorized nature of color maps, this is not guaranteed to be a fast operation.

        It is however included to allow for readable color mapping on arrays.

        Args:
            array (:class:`~numpy.ndarray`): An array on which to apply the color map.
            keep_colors (bool): Optional. Default to ``False``. If ``True``, returns an array of |Color|, otherwise, an
                :class:`~np.ndarray` of :attr:`~plums.plot.color.color.Color.components` is returned.

        Returns:
            :class:`~numpy.ndarray`: An array of |Color| or :attr:`~plums.plot.color.color.Color.components`
            corresponding to values in ``array``.

        """
        array = np.array(array, copy=False)
        if keep_colors:
            return np.vectorize(self.get_color, otypes=[Color])(array)

        return np.vectorize(self.get_color, signature='()->(n)')(array)

    def astype(self, ctype):
        """Make a new |ColorMap| instance in a new colors space.

        The returned |ColorMap| instance will share the same perceptual properties (*e.g.* the same "coordinates" of
        some sort) but the returned :attr:`components` will live in a new color space.

        Note that this is a lazy copy operation and that the actual :attr:`ctype` conversion will only be performed
        during the first time the :meth:`get_color` attribute is called.

        Args:
            ctype (str): A color space string specifying in which space returned |Color| lie.

        Returns:
            |ColorMap|: The converted |ColorMap| instance.

        Note:
            Nothing is done to take care of "out-of-bounds" values which may occur during conversion to avoid polluting
            eventual future conversion [2]_.

        .. [2] https://colorspacious.readthedocs.io/en/latest/tutorial.html#perceptual-transformations

        """
        if ctype != self.ctype:
            color_map = deepcopy(self)
            color_map.ctype = ctype
            return color_map

        return self


class ContinuousColorMap(ColorMap, ABC):
    r"""A |ContinuousColorMap| based on a set of increasing key points.

    It implements:

    .. math::

        \begin{align*}
          f \colon [a, b] &\to \mathcal{C}^S\\
          x &\mapsto f(x)
        \end{align*}

    Where :math:`f \in C^0`, :math:`[a, b] \subset \mathbb{R}` and :math:`\mathcal{C}^S` is a color space handled by
    the |Color| class.

    To speed up computation and ease storage, it may be "discretized" into a convenient LUT
    (*i.e.* a |DiscreteColorMap|) with the :meth:`discretize` method.

    Args:
        start (float): The start value :math:`a` of the input range.
        end (float): The start value :math:`b` of the input range.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, start, end, ctype, map_fn):
        super(ContinuousColorMap, self).__init__(ctype, map_fn)
        if end < start:
            raise ValueError('End is expected to be greater than start but: {} < {}'.format(end, start))
        self._start = self.map_fn(start)
        self._end = self.map_fn(end)

    def discretize(self, n=256):
        """Transform a |ContinuousColorMap| into a |DiscreteColorMap| with n points.

        Args:
            n (int): Optional. Default to 256. The number of point used to construct the |DiscreteColorMap|.

        Returns:
            |DiscreteColorMap|: A |DiscreteColorMap| with the same "shape" as self.

        """
        values = np.linspace(self._start, self._end, n)
        return DiscreteColorMap(values, self(values, keep_colors=True), ctype=self.ctype, map_fn=self.map_fn)


class KeyPointsColorMap(ContinuousColorMap):
    """A |ContinuousColorMap| based on a set of increasing key points.

    Args:
        mapping (dict): A ``{key_point: color}`` mapping where ``key_point`` is either an :class:`int` or a
            :class:`float` and ``color`` is a valid |Color| instance..
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, mapping, ctype='sRGB255', map_fn=None):
        super(KeyPointsColorMap, self).__init__(tuple(mapping.keys())[0], tuple(mapping.keys())[-1], ctype, map_fn)
        _key_points = np.array([self.map_fn(k) for k in sorted(mapping.keys())])

        self._start = _key_points[0]
        self._end = _key_points[-1]

        self._key_points = np.float_(_key_points) / (self._end - self._start)

        self._key_colors = tuple(mapping[key] for key in sorted(mapping.keys()))

    def _get_color(self, value):
        """Map a given ``value`` to a |Color| instance.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        if value <= self._start:
            return self._key_colors[0]
        if value >= self._end:
            return self._key_colors[-1]

        value = (float(value) - self._start) / (self._end - self._start)
        i = np.where((self._key_points - value) >= 0)[0][0] - 1
        lambda_ = float((value - self._key_points[i]) / (self._key_points[i + 1] - self._key_points[i]))
        return ((1 - lambda_) * self._key_colors[i]) + (lambda_ * self._key_colors[i + 1])


class CircularColorMap(ContinuousColorMap):
    """A |ContinuousColorMap| which runs on a (eventually tilted) circle in the JCh color space.

    Args:
        ray (float): A normalized ray, where 1 corresponds to the the maximum possible circle in the JCh space.
        tilt (tuple): Optional. Default to ``(0, 0)``. An optional tilt parameter where the first value is the tilt
            hue reference (in degree) and the second value a (signed) elevation parameter controlling the lightness at
            the tilt hue.
        data_range (tuple): Optional. Default to ``(0, 1)``. A range over which input values will be normalized.
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, ray, tilt=(0, 0), data_range=(0, 1), ctype='sRGB255', map_fn=None):
        super(CircularColorMap, self).__init__(data_range[0], data_range[1], ctype, map_fn)
        self._ray = 260 * ray
        self._tilt = tilt

    def _get_color(self, value):
        """Map a given ``value`` to a |Color| instance.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        x = float(360.0 * (value - self._start) / (self._end - self._start)) % 360.0
        tilt = \
            float((self._tilt[1] / 2)
                  * (1 - self._ray
                     * (np.cos((2 * np.pi / 360.0) * x) * np.cos((2 * np.pi / 360.0) * self._tilt[0])
                        + np.sin((2 * np.pi / 360.0) * x) * np.sin((2 * np.pi / 360.0) * self._tilt[0]))))
        col = Color(50 + tilt,
                    self._ray,
                    x,
                    ctype='JCh')
        return col


class SemiCircularColorMap(ContinuousColorMap):
    """A |ContinuousColorMap| which runs on a circle in the JCh color space with a chroma cycle.

    Args:
        ray (float): A normalized ray, where 1 corresponds to the the maximum possible circle in the JCh space.
        period (int): The chroma cycle normalized period where 1 corresponds to a complete hue circle.
        intensity (float): The chroma cycle normalized intensity where 1 corresponds to the the maximum possible
            circle in the JCh space. Note that the actual cycle intensity used is the minimum between the provided
            intensity and the maximum possible chroma range starting from ``ray``.
        delay (float): Optional. Default to 0. The chroma cycle start (in degrees) in the first circle relative to the
            color-map reference point.
        data_range (tuple): Optional. Default to ``(0, 1)``. A range over which input values will be normalized.
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, ray, period, intensity, delay=0, data_range=(0, 1), ctype='sRGB255', map_fn=None):
        super(SemiCircularColorMap, self).__init__(data_range[0], data_range[1], ctype, map_fn)
        self._ray = 260 * ray
        self._period = period
        self._intensity = 260 * min(min(260 - ray, ray - 0), intensity)
        self._delay = delay

    def _get_color(self, value):
        """Map a given ``value`` to a |Color| instance.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        normalized_value = (value - self._start) / (self._end - self._start)
        x = (360.0 * normalized_value) % 360.0
        inner_x = (360.0 * (normalized_value * self._period)) % 360.0
        col = Color(40,
                    self._ray + self._intensity * np.cos((2 * np.pi / 360.0) * (x - self._delay)),
                    inner_x,
                    ctype='JCh')
        return col


class LightnessColorMap(ContinuousColorMap):
    """A |ContinuousColorMap| which vary the lightness parameter in the J'a'b' color space around a reference |Color|.

    Args:
        color (|Color|): A reference |Color| around which the lightness value in the JCh space will be changed.
        lightness_range (tuple): Optional. Default to ``(0.3, 0.3)``. A normalized range, where 1 corresponds to the the
            maximum possible J range in the JCh space.
        chroma_range (tuple): Optional. Default to ``(0.0, 0.0)``. A normalized range, where 1 corresponds to the
            the maximum possible C range in the JCh space.
        data_range (tuple): Optional. Default to ``(0, 1)``. A range over which input values will be normalized.
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, color, lightness_range=(0.3, 0.3), chroma_range=(0.0, 0.0),
                 data_range=(0, 1), ctype='sRGB255', map_fn=None):
        super(LightnessColorMap, self).__init__(data_range[0], data_range[1], ctype, map_fn)
        self._center = color.astype('CAM02-UCS')
        self._lightness_range = \
            np.clip(self._center.components[0] + 50 * (np.array(lightness_range) * np.array([-1, 1])), 0, 100)
        self._chroma_range = \
            np.clip(self._center.components[1] + 150 * (np.array(chroma_range) * np.array([-1, 1])), 0, 100)

    def _get_color(self, value):
        """Map a given ``value`` to a |Color| instance.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        if value <= self._start:
            return Color(self._lightness_range[0],
                         self._chroma_range[0],
                         self._center.components[2],
                         ctype='CAM02-UCS')
        if value >= self._end:
            return Color(self._lightness_range[1],
                         self._chroma_range[1],
                         self._center.components[2],
                         ctype='CAM02-UCS')

        lambda_ = float((value - self._start) / (self._end - self._start))
        return Color(float((1 - lambda_) * self._lightness_range[0]) + float(lambda_ * self._lightness_range[1]),
                     float((1 - lambda_) * self._chroma_range[0]) + float(lambda_ * self._chroma_range[1]),
                     self._center.components[2],
                     ctype='CAM02-UCS')


class DiscreteColorMap(ColorMap):
    """A |DiscreteColorMap| based on a set of increasing values to be mapped on an array of |Color|.

    Args:
        values (array-like): An array of increasing values to map with ``colors``.
        colors (array-like): An array of |Color| corresponding to ``value``.
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, values, colors, ctype='sRGB255', map_fn=None):
        values = np.array(values, copy=False)

        super(DiscreteColorMap, self).__init__(ctype, map_fn)

        if np.any(np.diff(values) < 0):
            raise ValueError('Invalid key point mapping: '
                             'Values array is expected to be monotonically increasing.')

        self._values = np.vectorize(self.map_fn)(values)
        self._colors = colors

    @property
    def _start(self):
        return self._values[0]

    @property
    def _end(self):
        return self._values[-1]

    def _get_color(self, value):
        """Map a given ``value`` to a |Color| instance.

        Args:
            value (float): The ``value`` to get a |Color| for.

        Returns:
            |Color|: The corresponding |Color|.

        """
        if value <= self._values[0]:
            return self._colors[0]
        if value >= self._values[-1]:
            return self._colors[-1]
        i = np.where((self._values - value) >= 0)[0][0] - 1
        return self._colors[i]


class CategoricalColorMap(DiscreteColorMap):
    """A |DiscreteColorMap| based on a |CircularColorMap| which represents a categorical variable with ``n`` categories.

    Args:
        n (int): The number of categories to handle. Note that each categories corresponds to a tuple (value, |Color|).
        slope (float): Optional. Default to ``1.65``. The rate at which we cycle through the |CircularColorMap| to
            to construct the color map (``1.0`` represents a full circle).
        offset (float): Optional. Default to ``0.1``. The initial |Color| position in the |CircularColorMap|.
        ctype (str): A valid |Color| return type in which colors returned by the *color map* will be.
        map_fn (Callable): A function (ideally continuous and monotonically increasing) which take in a number and
            returns a number.

    """

    def __init__(self, n, slope=1.65, offset=0.05, ctype='sRGB255', map_fn=None):
        cm = SemiCircularColorMap(0.3, 20, 0.1, delay=160, data_range=(0, 20))
        super(CategoricalColorMap, self).__init__(list(range(n)),
                                                  [cm.get_color(offset + slope * i) for i in range(n)],
                                                  ctype=ctype, map_fn=map_fn)
