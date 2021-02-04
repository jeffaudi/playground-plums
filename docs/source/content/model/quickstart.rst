.. _quickstart:

Quickstart
==========

.. include:: ../../include.rst

Before it lives in a filesystem, a *PMF* |Model| lives in the *Python* realm through the ``plums.model`` *python* API.

Creating a *python* |Model| is a simple process:

.. code-block:: python

    from plums.model import Model

    model = Model('some_producer', 'py_pa', '1.0.1',
                  'some_model_name',
                  'some_model_id',
                  'some_conf_file.conf',
                  {})

Note that to create a |Model|, we need to know 5 things:

* The :term:`producer` used to create it: it usually is a factor of the current runtime environnement and it is stored
  internally as a |Producer|, along with the configuration path.
* The configuration path: It is a |Path| to the configuration file used to configure the |Producer| to train the
  |Model|. It is stored internally inside the |Producer| class as the
  :attr:`~plums.model.components.components.Producer.configuration` attribute.
* The model name and unique identifier: as :class:`str`.
* Its ``build_parameters`` (here an empty dictionary): a :class:`dict` storing any relevant parameter that a particular
  :term:`producer` might want to pass on to eventual :term:`consumer` opening the |Model|.

The created ``model`` is both empty and pending *by default*, and any more information must be filled out *after*
instantiation.

Interacting with the ``model`` may be done through two overlapping interfaces:

* Through the |Model| class methods.
* Through its component attributes' own interfaces.

For example, registering a training start can be done with:

.. code-block:: python

    # With a Model class method
    model.register_training_start(1)

    # With the Training component's own method
    model.training.start(1)

    # With a new Training component (not the preferred way because it allows accidental rewrites)
    import time
    model.training = Training(status='running', start_epoch=1, start_time=time.time())

Similarly, registering a model |Checkpoint| has several possible interfaces:

.. code-block:: python

    from plums.model import Checkpoint

    checkpoint = Checkpoint(name='some_reference',
                            path='a/path/to/a/checkpoint_file.model',
                            epoch=2)

    # With a Model class method
    model.add_checkpoint(checkpoint)

    # With the CheckpointCollection component's own method
    model.checkpoint_collection.add(checkpoint)

    # With the CheckpointCollection component's dictionary-like interface
    # (not the preferred way because it allows accidental rewrites)
    model.checkpoint_collection[checkpoint.name] = checkpoint

.. warning::
    Registering a |Checkpoint| with an :attr:`~plums.model.components.utils.Checkpoint.epoch` stricly superior to the
    |Training| :attr:`~plums.model.components.components.Training.latest_epoch` without registering a new latest epoch
    will result in a invalid *PMF* model when saved on disk.

    Generally speaking, the :meth:`~plums.model.model.Model.save` operation is performed lazily with no prior validation
    step and it is up to the user to ensure that the implemented |Model| life-cycle does result in a valid model.

Accessing the ``model`` initialisation is done through the :attr:`~plums.model.model.Model.initialisation` attribute
which might either be ``None``, a |Model| instance or a |Checkpoint| depending on the initialisation type.

Registering an initialisation is simple:

.. code-block:: python

    # For a PMF initialisation
    model.register_initialisation('an/initialisation/path', checkpoint_reference='some_reference')

    # For a checkpoint initialisation
    model.register_initialisation('an/initialisation/path', name='some_name')

Saving a |Model| to disk is done through the :meth:`~plums.model.model.Model.save` method:

.. code-block:: python

    model.save('a/destination/path')

Similarly, loading a saved |Model| from disk can be done with the :meth:`~plums.model.model.Model.load` class method:

.. code-block:: python

    from plums.model import Model

    model = Model.load('a/source/path')
