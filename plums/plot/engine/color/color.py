import numpy as np
from colorspacious import cspace_convert, cspace_converter, deltaE


class Color(object):
    """A class representing a color in various spaces with distance and arithmetic.

    It is implemented in a immutable fashion, *i.e*:

    * The :attr:`components` property is passive and always returns the |Color| in :attr:`ctype` space.
    * The :meth:`astype(ctype) <astype>` method changes the configured ctype in a new, separate |Color| instance copy.

    To sum-up, this means that the |Color| class acts like an "intelligent" container of some sort which always lives in
    the same color space (the one it was created in) and may spawn copies of itself in new color spaces.

    See Also:
        The current implementation is merely an oriented-object wrapper around the ``colorspacious`` library with a
        convenient "typed" container interface. For more information on the inner workings of color conversion and
        perceptual theory, please see
        `the colorspacious documentation <https://colorspacious.readthedocs.io/en/latest/index.html>`_

    Args:
        *components (int, float): The |Color| components in color space ``ctype``.
        ctype (str): Optional. Default to ``sRGB255``. A color space string specifying in which space :attr:`components`
            lies.

    """

    def __init__(self, *components, **kwargs):
        ctype = kwargs.pop('ctype', 'sRGB255')
        self._components = cspace_convert(components, ctype, 'sRGB255')
        self._ctype = ctype
        self._converter = cspace_converter('sRGB255', self.ctype)
        self._cache = None

    @property
    def ctype(self):
        """str: The color space the |Color| lives in (*e.g.* "sRGB255" or "JCh").

        See Also:
            For more information on valid color spaces, please see `the colorspacious documentation`_

        """
        return self._ctype

    @ctype.setter
    def ctype(self, new_ctype):
        self._cache = None
        self._converter = cspace_converter('sRGB255', new_ctype)
        self._ctype = new_ctype

    @property
    def components(self):
        """:class:`numpy.ndarray`: The |Color| components in the color space specified by :attr:`ctype`."""
        if self._cache is None:
            self._cache = np.array(self._converter(self._components), copy=False, dtype=np.float64)
        return self._cache

    @property
    def __array_interface__(self):  # noqa: D401
        """dict: The |Color| :attr:`components` array :data:`__array_interface__` property."""
        return self.components.__array_interface__

    @property
    def ndim(self):
        """int: The number of dimension of the component :class:`~numpy.ndarray`."""
        return 1

    @property
    def shape(self):
        """int: The shape of the component :class:`~numpy.ndarray`."""
        return self.components.shape

    def __str__(self):
        """Return a string representation of the "sRGB25" components of the |Color|."""
        return str(tuple(np.clip(self.astype('sRGB255').components, 0, 255)))

    def __repr__(self):
        """Return a pythonic representation of the |Color|."""
        return 'Color({}, ctype=\'{}\')'.format(', '.join([str(c) for c in self.components]), self.ctype)

    def __eq__(self, other):
        """Return ``True`` if 2 |Color| have equal components.

        Note that it does not performs any color space conversion before checking for equality. This is to ensure that
        equality implies that both |Color| lives in the same color space.

        Args:
            other (|Color|): Another |Color| to compare with self.

        """
        if hasattr(other, 'components') and hasattr(other, 'ctype'):
            return self.ctype == other.ctype \
                and np.allclose(self.astype('XYZ100').components, other.astype('XYZ100').components)
        else:
            return NotImplemented

    def __ne__(self, other):
        """Return ``True`` if 2 |Color| do not have equal components.

        Note that it does not performs any color space conversion before checking for equality. This is to ensure that
        equality implies that both |Color| lives in the same color space.

        Args:
            other (|Color|): Another |Color| to compare with self.

        """
        return not self == other

    def __add__(self, other):
        """Mix 2 colors together.

        |Color| addition amounts to a canonical vector-space summation in the **XYZ** linear color
        space [1]_, *i.e.*: the returned |Color| is the light-additive mix of the two |Color|.

        Args:
            other (|Color|): A |Color| to mix with.

        Returns:
            |Color|: The resulting |Color|.

        .. [1] https://en.wikipedia.org/wiki/CIE_1931_color_space

        """
        if hasattr(other, 'components') and hasattr(other, 'astype') and hasattr(other, 'ctype'):
            components = np.array(self.astype('XYZ100')) + np.array(other.astype('XYZ100'))
        else:
            return NotImplemented
        return Color(*components, ctype='XYZ100').astype(self.ctype)

    __radd__ = __add__

    def __mul__(self, other):
        r"""Change the colors luminance by a scalar factor.

        Scalar-|Color| multiplication amounts to a canonical vector-space scalar product in the **XYZ** linear color
        space [1]_, *i.e.*: the returned |Color| is the |Color| :math:`\cdot` ``other`` in the **XYZ** space.

        Warnings:
            As of now, left-multiplication with a **Numpy** scalar returns the invalid result
            ``other * self.components`` as an :class:`~numpy.ndarray`.

            A simple but ugly workaround is to ensure that the scalar is either on the left hand side of the
            computation or a builtin :class:`float` instead.

        Args:
            other (int, float): The amount to multiply the |Color| by.

        Returns:
            |Color|: The resulting |Color|.

        """
        try:
            if np.ndim(other) != 0:
                raise TypeError
            components = other * np.array(self.astype('XYZ100'))
        except TypeError:
            return NotImplemented
        return Color(*components, ctype='XYZ100').astype(self.ctype)

    __rmul__ = __mul__

    def __sub__(self, other):
        """Compute the ``DeltaE`` distance between two colors.

        This corresponds to a euclidean distance in the perceptual **CAM02-UCS** space, in which perceptually similar
        colors (*i.e.* "close" colors) have similar coordinates.

        Args:
            other (|Color|): The |Color| to compute the distance index with.

        Returns:
            float: The distance between the two colors.

        """
        if hasattr(other, 'components') and hasattr(other, 'astype') and hasattr(other, 'ctype'):
            return deltaE(self.astype('XYZ100').components,
                          other.astype('XYZ100').components,
                          input_space='XYZ100')
        else:
            return NotImplemented

    def astype(self, ctype):
        """Make a new |Color| instance in a new colors space.

        The returned |Color| instance will share the same perceptual properties (*e.g.* the same "coordinates" of some
        sort) but the returned :attr:`components` will live in a new color space.

        Note that this is a lazy copy operation and that the actual :attr:`ctype` conversion will only be performed
        during the first time the :attr:`components` attribute is accessed.

        Args:
            ctype (str): A color space string specifying in which space ``components`` lies.

        Returns:
            |Color|: The converted |Color| instance.

        Note:
            Nothing is done to take care of "out-of-bounds" values which may occur during conversion to avoid polluting
            eventual future conversion [2]_.

        .. [2] https://colorspacious.readthedocs.io/en/latest/tutorial.html#perceptual-transformations

        """
        if ctype != self.ctype:
            color = Color(*self.components, ctype=self.ctype)
            color.ctype = ctype
            return color

        return self
