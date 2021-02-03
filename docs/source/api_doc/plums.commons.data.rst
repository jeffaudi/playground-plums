|Plums| Data-Model
==================

.. include:: ../include.rst

The Plums **data-model** module implements the data-model described in :ref:`commons_data_model`.

User documentation
..................

The actual **data-model** composition is exposed here.

It consists of 2 categories of classes:

* Container classes: They are mainly descriptor classes in that they only serve to aggregates instances of various
  other classes in a semantic fashion with no actual functional purpose.
* Type classes: They encode actual type information and a functional part which controls the way they are constructed
  and manipulated.

Container classes
-----------------

.. autoclass:: plums.commons.data.data.DataPoint
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.data.Annotation
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. Test
.. automodule:: plums.commons
    :members: DataPoint, Annotation
    :undoc-members:
    :show-inheritance:
    :exclude-members: p, r, o, e, t, i, s
    :member-order: bysource

.. autoclass:: plums.commons.data.tile.TileCollection
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.record.RecordCollection(*records, id=None, taxonomy=None)
    :members:
    :special-members: __getitem__, __setitem__, __len__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.mask.MaskCollection
    :members:
    :special-members: __getitem__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Type classes
------------

Tile classes
++++++++++++

.. autoclass:: plums.commons.data.tile.Tile
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.tile.TileWrapper
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. Test
.. automodule:: plums.commons
    :members: Tile, TileWrapper
    :undoc-members:
    :show-inheritance:
    :exclude-members: p, r, o, e, t, i, s
    :member-order: bysource

Record classes
++++++++++++++

.. autoclass:: plums.commons.data.record.Record
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Mask classes
++++++++++++

.. autoclass:: plums.commons.data.mask.VectorMask
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.mask.RasterMask
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. Test
.. automodule:: plums.commons
    :members: VectorMask, RasterMask
    :undoc-members:
    :show-inheritance:
    :exclude-members: p, r, o, e, t, i, s
    :member-order: bysource

Developper documentation
........................

Some internal classes used for interface-checking and semantic typing and base classes for the data model
implementation.

.. autoclass:: plums.commons.data.mixin.PropertyContainer
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.base.ArrayInterfaced
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.base.GeoInterfaced
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. Test
.. automodule:: plums.commons.data
    :members: ArrayInterfaced, GeoInterfaced
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.Mask(name, id=None, **properties)
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Implementation helpers
----------------------

.. Test
.. autoclass:: plums.commons.data.mixin.PropertyContainer
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. Test
.. automodule:: plums.commons.data.mixin
    :members:
    :exclude-members: PropertyContainer, p, r, o, e, t, i, s, d, c
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.commons.data.base._Array
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
