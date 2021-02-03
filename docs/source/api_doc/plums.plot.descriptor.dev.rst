.. _descriptor_dev:

|Plums| Descriptor developer API
================================

.. include:: ../include.rst

A |Descriptor| is a special kind of object which takes in one or many |RecordCollection|, and output one or many
|RecordCollection| where each enclosed |Record| have an additional
:attr:`property <~playground_plums.commons.data_model.PropertyContainer.properties>`.

The developer API exposes the abstract base class for all descriptors which indicates necessary interfaces to
implement to construct a valid |Descriptor|.

It also exposes two special kinds of |Descriptor|:

* The |ColorEngine|, which is used internally to generate a ``color``
  property which contains the |Color| used to plot a |Record| from one or two |Descriptor|.
* The |ByCategoryDescriptor| which wraps a |Descriptor| to make it dependent on a monitored property in |Record|.

.. autoclass:: playground_plums.plot.engine.Descriptor
    :members: property_name, __descriptor__, __eq__, update, compute, reset, _make_interface
    :special-members: __eq__, __descriptor__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.plot.engine.color_engine.ByCategoryDescriptor
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.plot.engine.color_engine.ColorEngine
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
