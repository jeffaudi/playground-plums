.. _model:

|Plums| Model API
============================

.. include:: ../include.rst

The **P**\ lums **M**\ odel **F**\ ormat main API is in the |Model| class which allows loading, saving and dynamic
creation through a high-level python API. Moreover, it implement python representations of common |Model| components
objects like |Training|, |Producer|, |CheckpointCollection| and |Checkpoint|.

.. seealso::
    The :ref:`model_dev` for more information on the |Model| API inner workings.

.. automodule:: plums.model.model
    :members: Model
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Components
----------

.. automodule:: plums.model.model
    :members: initialisation
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: plums.model.components.components
    :members:
    :special-members: __eq__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: plums.model.components.utils.Checkpoint
    :members:
    :special-members: __eq__, __hash__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Exceptions
----------

.. automodule:: plums.model.exception
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
