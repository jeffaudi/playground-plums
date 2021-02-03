|Plums| Orchestrator
====================

.. include:: ../include.rst

The role of the |Orchestrator| is, from a given list of |DataPoint|-like, to draw a composite figure, representing the
different tiles with their respective annotations, with colors and a legend.


The |Orchestrator| is highly customizable, and different layouts of the mosaic can be built, depending on the use cases:

* **simple layout**: the tiles will be placed following each others, mapping a rectangular grid. The number of columns
  of the final mosaic can be fixed.
* **adaptive layout**: very similar with the **simple** layout, except that the last row of the mosaic is centered.
* **2D layout**: in the case where a 2D array-like of |DataPoint| is given to the |Orchestrator|, each line of the
  mosaic will correspond to a row of that array (the row being generally of different lengths).


.. automodule:: playground_plums.plot.engine
    :members: Orchestrator
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: playground_plums.plot.engine.orchestrator
    :members: OrchestratorBase
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
