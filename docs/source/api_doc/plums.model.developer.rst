.. _model_dev:

|Plums| Model developer API
===========================

.. include:: ../include.rst

The **P**\ lums **M**\ odel **F**\ ormat main API is in the |Model| class which allows loading, saving and dynamic
creation through a high-level python API.

The following classes and functions exposes the inner workings of the main |Model| API. It is deemed the *developer* API
because it should not be used directly by end-users or model producers/consumers.

.. seealso::
    The :ref:`model` for the end-user |Model| API.

Producer version handling
-------------------------

.. automodule:: playground_plums.model.components.version
    :members: version, register
    :undoc-members:
    :special-members: __eq__, __lt__, __str__
    :show-inheritance:
    :member-order: bysource

.. automodule:: playground_plums.model.components.version
    :members: Version, PyPA
    :undoc-members:
    :special-members: __eq__, __lt__, __str__
    :show-inheritance:
    :member-order: bysource

Utils
-----

.. automodule:: playground_plums.model.components.utils
    :members: is_duplicate, copy, rmtree
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. automodule:: playground_plums.model.components.utils
    :members: TrainingStatus
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
