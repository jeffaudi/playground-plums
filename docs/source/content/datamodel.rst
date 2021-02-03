.. _commons_data_model:

|Plums| Data-Model
==================

.. include:: ../include.rst

The Plums data-model describes a common descriptor format for data used in ML pipelines.

Introduction
------------

It consists in a set of **container classes** and **type classes** which are used to describe respectively structures
and components.

The latter exposes common interface to ease sharing with external libraries in extension of sharing within the Plums
environment.

.. note::
    The data-model implementation is **non-defensive** in that it does little to no type-check but rather enforces a
    set of standard interfaces on which microlibs may rely.

Description
-----------

.. image:: /_static/plums_data_model.png
    :alt: The Plums Data-Model

At the top-level sits the |DataPoint| container class which encapsulate a |TileCollection| and an |Annotation|.

A |TileCollection| is an :class:`~collections.OrderedDict`-like container which store |Tile| mapped to eventual names.

A valid |Tile| is expected to be either a :class:`~PIL.Image.Image` or a subclass of |Tile| (such as the convenient
|TileWrapper| for non-pillow images), whereas |Annotation| is expected to be a |GeoInterfaced| class.

The |Annotation| class provided acts as a container class aggregating a |MaskCollection| container class and a
|RecordCollection| container class.

A |Mask| is an entity which encodes some non target-related data along with a name and optional properties. The stored
data defines either a |RasterMask| which encodes *raster* data or a |VectorMask| which encodes *vector* data (as a
GeoJSON Polygon typically).

A |Record| is a |GeoInterfaced| entity which stores a geometry (either a *Point* or a *Polygon*) along with
some properties, *i.e.*:

* A list of |Label|
* An optional confidence score
* Any additional property

.. hint::
    
    .. _taxonomies: https://en.wikipedia.org/wiki/Taxonomy_(general)

    A |RecordCollection| is a context-aware container to which one may attach a |Taxonomy|. A |Taxonomy| is a mean of
    describing known |Label| and the way they interact with one another (describing kinship relationships). For more
    information on taxonomies_ and the way they are used in **Plums**, see the
    :ref:`Taxonomy API documentation <commons_taxonomy>`.

Note that all classes with a *properties* badge are |PropertyContainer| able to store arbitrary properties with easy
retrieval capacities.

Expected interfaces and attributes
----------------------------------

The following table lists which *interfaces* and *attributes* one should expect from a **type** or a **container** class
in the *data-model*. This serves both as a summary of the *data-model* and an extension guide, indicating what element
*MUST* be implemented by a user custom duck-typing class to interface seamlessly with the rest of the library.

.. note::
    This is a **minimum** specification of the expected available API. Specific implementation may extend on this but
    external component should not expect those extensions.

+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| Class              | Interfaces                                                        | Attributes                                                       |
+====================+===================================================================+==================================================================+
| |DataPoint|        | :math:`\varnothing`                                               | * :attr:`~plums.commons.DataPoint.tile`                          |
|                    |                                                                   | * :attr:`~plums.commons.DataPoint.annotation`                    |
|                    |                                                                   | * :attr:`~plums.commons.DataPoint.properties`                    |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |TileCollection|   | * :meth:`~object.__getitem__`                                     |                                                                  |
|                    | * :meth:`~object.__setitem__`                                     |                                                                  |
|                    | * :meth:`~object.__delitem__`                                     |                                                                  |
|                    | * :meth:`~object.__iter__`                                        |                                                                  |
|                    | * :meth:`~object.__len__`                                         |                                                                  |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |Tile|             | * :data:`__array_interface__`                                     | * :attr:`~plums.commons.TileWrapper.filename`                    |
|                    |                                                                   | * :attr:`~plums.commons.TileWrapper.size`                        |
|                    |                                                                   | * :attr:`~plums.commons.TileWrapper.width`                       |
|                    |                                                                   | * :attr:`~plums.commons.TileWrapper.height`                      |
|                    |                                                                   | * :attr:`~plums.commons.TileWrapper.info`                        |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |Annotation|       | * :data:`__geo_interface__`                                       | * :attr:`~plums.commons.Annotation.record_collection`            |
|                    |                                                                   | * :attr:`~plums.commons.Annotation.mask_collection`              |
|                    |                                                                   | * :attr:`~plums.commons.Annotation.properties`                   |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |RecordCollection| | * :data:`__geo_interface__`                                       | * :attr:`~plums.commons.RecordCollection.id`                     |
|                    | * :meth:`~plums.commons.RecordCollection.__getitem__`             | * :attr:`~plums.commons.RecordCollection.records`                |
|                    | * :meth:`~plums.commons.RecordCollection.__setitem__`             |                                                                  |
|                    | * :meth:`~plums.commons.RecordCollection.__len__`                 |                                                                  |
|                    | * :meth:`~plums.commons.RecordCollection.append`                  |                                                                  |
|                    | * :meth:`~plums.commons.RecordCollection.to_geojson`              |                                                                  |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |Record|           | * :data:`__geo_interface__`                                       | * :attr:`~plums.commons.Record.id`                               |
|                    | * :meth:`~plums.commons.RecordCollection.to_geojson`              | * :attr:`~plums.commons.Record.labels`                           |
|                    |                                                                   | * :attr:`~plums.commons.Record.confidence`                       |
|                    |                                                                   | * :attr:`~plums.commons.Record.coordinates`                      |
|                    |                                                                   | * :attr:`~plums.commons.Record.type`                             |
|                    |                                                                   | * :attr:`~plums.commons.Record.properties`                       |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |MaskCollection|   | * :meth:`~plums.commons.MaskCollection.__getitem__`               | * :attr:`~plums.commons.MaskCollection.masks`                    |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |VectorMask|       | * :data:`__geo_interface__`                                       | * :attr:`~plums.commons.VectorMask.name`                         |
|                    | * :meth:`~plums.commons.VectorMask.to_geojson`                    | * :attr:`~plums.commons.VectorMask.coordinates`                  |
|                    |                                                                   | * :attr:`~plums.commons.VectorMask.properties`                   |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
| |RasterMask|       | * :data:`__array_interface__`                                     | * :attr:`~plums.commons.RasterMask.name`                         |
|                    |                                                                   | * :attr:`~plums.commons.RasterMask.size`                         |
|                    |                                                                   | * :attr:`~plums.commons.RasterMask.width`                        |
|                    |                                                                   | * :attr:`~plums.commons.RasterMask.height`                       |
|                    |                                                                   | * :attr:`~plums.commons.RasterMask.properties`                   |
+--------------------+-------------------------------------------------------------------+------------------------------------------------------------------+
