.. _pmf_spec:

|Plums| Model Format specification
==================================

.. include:: ../../include.rst

The Plums **M**\ odel **F**\ ormat (**PMF**) is a *content-agnostic* format to save :term:`model` in a
*semantically-rich* and *standardized* manner.

It consists in two parts:

* A :ref:`metadata` file which describes the way a model was produced, and a summary of its *apparent* content.
* A :ref:`structure` which stores *semi-arbitrary* data in a *semantically-rich* manner to allow for easy and consistent
  analysis of a given model content across :term:`producer`.

.. note::
    The **PMF** specification describes a *minimum* specification. That is to say that it may be freely extended
    although :term:`consumer` should not expect any *PMF*-foreign elements to be present in any valid *PMF* model.

.. _structure:

Tree structure
--------------

.. note::
    In the rest of this page, files named as ``<name>`` are content agnostic and may contain anything the
    :term:`producer`/:term:`consumer` pair may need.

A **PMF** model is characterized by its minimal filesystem tree structure :

.. image:: /_static/model/PMF_no_init.png
    :alt: PMF minimal structure
    :scale: 15%

Where:

* **metadata.yaml** (*yaml*): The main *PMF* metadata contains most of the information used to construct a valid *PMF*
  model. For more information on how to construct a valid *PMF* metadata file, see :ref:`metadata`.
* **<configuration file>** (*Any*): The :term:`producer` configuration file used to train the model. It may be of any
  form, format or content.
* **build_parameters.yaml** (*yaml*): Optional ``key:value`` parameters that a :term:`producer` might store alongside
  a *PMF* model for the :term:`consumer` to use.
* **<checkpoint file>** (*Any*): Any file used to store any checkpoints. It may be of any form, format or content, and
  it is up to a particular :term:`producer`/:term:`consumer` pair to know how to open it.

The **initialisation/** folder contains information on any prior data the model was initially based on. If it is empty,
the underlying assumption is that the model was trained *from scratch*.

If it contains a *PMF*-like tree (*i.e.* a *PMF* tree with no **checkpoints/** folder), the underlying assumption is
that the model was trained based on a previous *PMF* model, *e.g.*:

.. image:: /_static/model/PMF_PMF_init.png
    :alt: PMF minimal structure
    :scale: 15%

If it contains a single file (of any form, format or content), the underlying assumption is that the model was trained
based on a previous model checkpoint, *e.g.*:

.. image:: /_static/model/PMF_file_init.png
    :alt: PMF minimal structure
    :scale: 15%

The **<model root>/** and **data/** folders may contain additional files.

.. _metadata:

Metadata.yaml
-------------

The **metadata.yaml** file encode various standard information in a dictionary-like ``key:value`` form.

Specification
.............

It is made of two sections:

* A |FormatSchema| section which documents the stored *PMF* |Model| format production, *i.e.*:

  * The *PMF* format ``version``.
  * The *PMF* model |Producer| information *i.e.*:

    * Its :attr:`~playground_plums.model.components.components.Producer.name`
    * Its :attr:`~playground_plums.model.components.components.Producer.version`

* A |ModelSchema| section which documents the stored *PMF* |Model| contents.

The |ModelSchema| section is itself made of various metadata and two sections:

* The model :attr:`~playground_plums.model.model.Model.name`.
* The model :attr:`~playground_plums.model.model.Model.id`.
* A |TrainingSchema| section which documents metadata on the model |Training| *i.e.*:

  * The training *status* (*i.e.* pending, running, failed or finished).
  * The training *start* (Epoch number and timestamp).
  * The training *latest* known epoch (Epoch number and timestamp).
  * The training *end* (Epoch number and timestamp).
  * A |CheckpointSchema| section which documents registered model |CheckpointCollection|.

* A |InitialisationSchema| section which document the model |initialisation|.

The |CheckpointSchema| section is a mapping between a |Checkpoint| reference
(its :attr:`~playground_plums.model.components.utils.Checkpoint.name`) and its
:attr:`~playground_plums.model.components.utils.Checkpoint.epoch` and :attr:`~playground_plums.model.components.utils.Checkpoint.path`. That
is to say that each |Checkpoint| will be registered in the **metadata** as:

.. code-block:: yaml

    reference:
        epoch: int
        path: <path-to-checkpoint-file>
        hash: <checksum-of-checkpoint-file>

The |InitialisationSchema| may take any of those three forms:

* A ``null`` value if the *PMF* model has no initialisation.
* An |InitialisationPMFSchema| section documenting a *PMF* model used as initialisation *i.e.*:

  .. code-block:: yaml

    pmf:
        name: <name-of-pmf-model>
        id: <id-of-pmf-model>
        path: <path-to-pmf-like-model-tree>
        checkpoint: <reference-to-pmf-model-checkpoint-used-as-initialisation>
* An |InitialisationPathSchema| section documenting a model *checkpoint* used as initialisation *i.e.*:

  .. code-block:: yaml

    file:
        name: <name-of-checkpoint>
        path: <path-to-checkpoint-file>
        hash: <checksum-of-checkpoint-file>

Example
.......

.. code-block:: yaml

    format:
        producer:
            name: faster_rcnn
            version:
                format: py_pa
                value: 0.4.0
        version: 1.0.0
    model:
        name: model_name
        id: 3d6acb1fce4469ee1559ba16e02f922f
        configuration:
            hash: 43ccb8cd86048450e11a26b472d5efd0
            path: model_configuration.py
        initialisation:
            file:
                hash: a268eb855778b3df3c7506639542a6af
                name: imagenet
                path: data/initialisation/resnet_weights_tf_dim_ordering_tf_kernels_notop.h5
        training:
            checkpoints:
            1:
                epoch: 1
                hash: b4975f62e007d54a55f53b44a367d998
                path: data/checkpoints/1.h5
            10:
                epoch: 10
                hash: 9d03a4a7455829da47c1c346eb17ddb1
                path: data/checkpoints/10.h5
            12:
                epoch: 12
                hash: 01afa021fdf47b609decd434755c06f6
                path: data/checkpoints/12.h5
            end_epoch: null
            end_time: null
            latest: 12
            latest_epoch: 12
            latest_time: 1552481973.357268
            start_epoch: 0
            start_time: 1552464823.166782
            status: running

Glossary
--------

.. glossary::

    model
        A model reference the concept of model in general, independent on how they are stored. As such, it might
        reference a |Model| instance which is an accepted representation of a model.

    producer
        A producer is a piece of software which is responsible for creating and modifying a given :term:`model`.

    consumer
        A consumer is a piece of software which is responsible for interpreting and manipulating a :term:`model`
        **without** modifying its content.
