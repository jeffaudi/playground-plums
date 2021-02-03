|Plums| Legend painter
======================

.. include:: ../include.rst

A legend is a visual explanation of the colors used on the visualisations.
By visualisations, we mean one or several tiles with their respective painted annotations (records geometry with
optionally confidence).

* **Content** is contained in the legend to aid in the interpretation of the visualisations. For **Plums** purposes,
  the legend will map colors or color maps to some meaningful descriptors (exposed by the |ColorEngine|).
* **Design** involves the overall appearance of the legend. As a rule of thumb, we have chosen to handle two modes of
  visualisation. First, descriptors that are categorical. They will be represented with a colored rectangle, whereas,
  continuous descriptors will appear as plain colormaps.
* **Placement** is where the legend itself is located on the final composition. Some places are better than others.
  Keep in mind that the legend is not the main attraction, it is used to describe the main attraction. The size should
  only be large enough to be legible for the reader. The legend can either be placed **horizontally** or **vertically**.

The actual legend API is exposed here.

.. automodule:: plums.plot.engine.legend_painter
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
