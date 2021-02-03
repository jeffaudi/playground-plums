Dataset
=======

.. include:: ../include.rst

The Plums dataflow module shares the PyTorch data pipeline API main ideas and is compatible with both PyTorch and
Tensorflow's Keras.

Base datasets
-------------

The main class to stream through data in Plums is the |Dataset| base class, which guarantee a sequence-like
interface to manipulate data in an ordered fashion.

.. autoclass:: playground_plums.dataflow.dataset.Dataset
    :members:
    :special-members: __getitem__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.dataflow.dataset.SizedDataset
    :members:
    :special-members: __getitem__, __add__, __len__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Two utility |Dataset| classes are also provided to ease the creation of dataset partitions and compositions:

.. autoclass:: playground_plums.dataflow.dataset.Subset
    :members:
    :special-members: __getitem__, __len__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.dataflow.dataset.ConcatDataset
    :members:
    :special-members: __getitem__, __len__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Pattern dataset
---------------

.. autoclass:: playground_plums.dataflow.dataset.PatternDataset
    :members:
    :special-members: __getitem__, __len__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

Domain datasets
---------------

The following datasets are domain-specific datasets based on the |PatternDataset|.

Playground
++++++++++

.. autoclass:: playground_plums.dataflow.dataset.PlaygroundDataset
    :members:
    :special-members: __getitem__, __len__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.dataflow.dataset.playground.TileDriver
    :members:
    :special-members: __call__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.dataflow.dataset.playground.AnnotationDriver
    :members:
    :special-members: __call__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.dataflow.dataset.playground.TaxonomyReader
    :members:
    :special-members: __call__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
