|Plums| Plot
============

.. include:: ../include.rst

The role of the **plot** classes is to provide a user-friendly, still highly customizable, API for drawing composite figure.
As a result, the final plot will represent the different tiles with their respective annotations, with colors and a legend.

Several plots are available:

* **standard**: the |StandardPlot| accumulates the individual |DataPoint|-like object and paints each tile, following
  each others.
* **comparison**: the |PairPlot| provides two layouts. It accumulates a ground truth |RecordCollection| and one or
  several predictions |RecordCollection|. Those predictions can either be painted above the ground truths (if only
  one |RecordCollection|) or filling a line in the final layout (the first tile being the ground truth, the following
  being the predictions).

The |Plot| class serves as a base class for all *porcelain interface* classes intended to be
used by end-users. It indicates which interfaces and attributes one should expect from such classes. However, because
one *porcelain interface* behaviour may significantly differ from another, one should read each class documentation
individually rather than relying on the |Plot| to assume subclasses behaviour.

.. automodule:: plums.plot
    :members: Plot
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: plums.plot
    :members: StandardPlot, PairPlot
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
