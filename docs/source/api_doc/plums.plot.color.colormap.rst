|Plums| Color and ColorMap
==========================

.. include:: ../include.rst

All handling of colors in Plums **plot** rely on the special |Color| container class to manipulate colors
and a set of |ColorMap| classes to generate them.

The Color class
-----------------

The way colors are handled in Plums **plot** depends on the high-level
`Colorspacious <https://colorspacious.readthedocs.io/en/latest/index.html>`_ color handling library and the |Color|
class is a simple container class which delegates all the heavy lifting to *colorspacious*.

It offers a typed handling of colors and introduces the concept of :attr:`~plums.plot.engine.Color.ctype` which
represents a color space in which a |Color| instances live, and thus indicates how its
:attr:`~plums.plot.engine.Color.components` should be interpreted.

Internally, the actual |Color| components are stored in the limited but highly common ``sRGB255`` space.

.. autoclass:: plums.plot.engine.Color(*components, ctype='sRGB255')
    :members:
    :special-members: __eq__, __add__, __mul__, __sub__, __array_interface__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Color Maps
----------

A |ColorMap| performs a link between a set :math:`\mathcal{V} \subset \mathbb{R}` of value and a set
:math:`\mathcal{C}^S \subset S` of colors (where :math:`S` is a given color space).

Note that both sets might be infinite, in which case we construct a |ContinuousColorMap|, or finite, in which case we
construct a |DiscreteColorMap|.

.. autoclass:: plums.plot.engine.ColorMap
    :members: _get_color, get_color, __call__
    :special-members: __call__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Constructor classes
...................


.. automodule:: plums.plot.engine
    :members: ContinuousColorMap, DiscreteColorMap
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Concrete color maps classes
...........................

.. automodule:: plums.plot.engine
    :members: CircularColorMap, SemiCircularColorMap, LightnessColorMap, KeyPointsColorMap, CategoricalColorMap
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
