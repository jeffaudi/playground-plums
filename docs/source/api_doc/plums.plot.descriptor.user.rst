|Plums| Descriptor API
======================

.. include:: ../include.rst

A |Descriptor| is a special kind of object which takes in one or many |RecordCollection|, and output one or many
|RecordCollection| where each enclosed |Record| have an additional
:attr:`property <~playground_plums.commons.data_model.PropertyContainer.properties>`.

Each |Descriptor| defines a specific :attr:`property <~playground_plums.commons.data_model.PropertyContainer.properties>`
(*i.e.* how to construct it from a |Record| and how to interpret the result) and can be used as a high level API to
summarise a |Record| information or set of information in an enclosed highly semantic pattern.

Because each :attr:`descriptor property <~playground_plums.commons.data_model.PropertyContainer.properties>` is added to a
|Record|, |Descriptor| may be chained to generate arbitrary sequences of description processing.

A collection of generic |Descriptor| are already included in Plums *plot*, but extending the base API is easy by
creating new |Descriptor| classes.

.. seealso::
    :ref:`descriptor_dev`

Specific descriptors
--------------------

.. automodule:: playground_plums.plot
    :members: Labels, Confidence, IntervalConfidence, Area, IntervalArea
    :undoc-members:
    :show-inheritance:
    :member-order: bysource


Generic descriptors
-------------------

.. automodule:: playground_plums.plot
    :members: CategoricalDescriptor, ContinuousDescriptor, IntervalDescriptor
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
