|Plums| Model validation API
============================

.. include:: ../include.rst

Most **P**\ lums **M**\ odel **F**\ ormat validation is performed with the |validate| function, which take in a |Path|
and returns the validated model *metadata* or raises a :exc:`PlumsValidationError`.

.. automodule:: plums.model.validation
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

However, if one needs to validate part of a **PMF** model or needs fine grained access to validation internals for
further work, Plums *model* also exposes a *developer* validation API.

.. _validation_developer:

Developer API
-------------

The developer API exposes the low-level internal API used by the |validate| function. Most of the validation
heavy-lifting is made by the excellent `Schema library <https://github.com/keleshev/schema>`_.

Each documented class is a |SchemaComponent| and defines part of the total validation schema.

PMF data tree validation API
............................

You may find here the list of |TreeComponent| compositing the :ref:`structure` schema.

.. automodule:: plums.model.validation.structure
    :members:
    :undoc-members:
    :exclude-members: TreeComponent, DefaultTree
    :show-inheritance:
    :member-order: bysource

Metadata validation API
.......................

You may find here the list of |MetadataComponent| compositing the :ref:`metadata` schema.

.. automodule:: plums.model.validation.metadata
    :members:
    :undoc-members:
    :exclude-members: MetadataComponent, DefaultMetadata
    :show-inheritance:
    :member-order: bysource

Core validation API
.......................

.. automodule:: plums.model.validation.schema_core
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: plums.model.validation.metadata
    :members: MetadataComponent, DefaultMetadata
    :undoc-members:
    :exclude-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: plums.model.validation.structure
    :members: TreeComponent, DefaultTree
    :undoc-members:
    :exclude-members:
    :show-inheritance:
    :member-order: bysource

Helper functions
................

.. automodule:: plums.model.validation.utils.dict_from_tree
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: plums.model.validation.utils.checksum
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: plums.model.validation.utils.validate_path
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
