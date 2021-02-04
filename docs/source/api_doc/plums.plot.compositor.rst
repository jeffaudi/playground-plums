|Plums| Compositor
==================

.. include:: ../include.rst

The role of the |Compositor| is, from a given list of |DataPoint|, to draw a kind of mosaic, representing the different
tiles with their respective annotations.
In some ways, the |Compositor| is customizable. Different layouts of the mosaic can be built, depending on the use cases:

* **simple layout**: the tiles will be placed following each others, mapping a rectangular grid. The number of columns
  of the final mosaic can be fixed.
* **adaptive layout**: very similar with the **simple** layout, except that the last row of the mosaic is centered.
* **2D layout**: in the case where a 2D array-like of |DataPoint| is given to the |Compositor|, each line of the mosaic
  will correspond to a row of that array (the row being generally of different lengths).

Moreover, you can decorate your final composition by adding a title on top of it, and a legend (cf. |LegendPainter|).

The actual **compositor** API is exposed here.

.. automodule:: playground_plums.plot.engine.compositor
    :members: CompositorBase
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: playground_plums.plot.engine
    :members: Compositor
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
