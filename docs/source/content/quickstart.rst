.. _commons_quickstart:

Quickstart
==========

.. include:: ../include.rst

.. role:: python(code)
   :language: python
   :class: highlight

The Plums :ref:`commons_data_model` describes a common descriptor format with python representations for object
commonly used.

Lets look at a basic example where we will try to construct a simple |DataPoint| with an empty |Tile|, a few |Record|
which reference a |Taxonomy|:

.. code-block:: python

    import numpy as np
    from plums.commons.data import DataPoint, Annotation, TileWrapper, RecordCollection, Record
    from plums.commons.data.taxonomy import Taxonomy, Label

    # Make a taxonomy
    breakfast = Label('breakfast item')
    eggs = Label('eggs', parent=breakfast)
    fried = Label('fried', parent=eggs)
    scrambled = Label('scrambled', parent=eggs)
    meat = Label('meat', parent=breakfast)
    bacon = Label('bacon', parent=meat)
    spam = Label('spam', parent=meat)

    taxonomy = Taxonomy(breakfast)

    # Make a record collection
    first = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('eggs', ))
    second = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('bacon', ))
    third = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('scrambled', ))
    fourth = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('meat', ))
    fifth = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('eggs', ))
    last = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('spam', ),
                  spam=('spam', 'spam'),
                  beautiful='spam')

    record_collection = RecordCollection(first, second, third, fourth, fifth, last)
    record_collection.taxonomy = taxonomy

    # Make a tile
    tile = TileWrapper(np.zeros((100, 100, 3)))

    # Make an annotation
    annotation = Annotation(record_collection)

    # Make a data point
    data_point = DataPoint(tile, annotation)

Code breakdown
..............

.. _make_taxonomy:

Make a taxonomy
---------------

The first step would be to construct a |Taxonomy| using the :ref:`Taxonomy API <commons_taxonomy>`:

.. code-block:: python

    from plums.commons.data.taxonomy import Taxonomy, Label

    breakfast = Label('breakfast item')
    eggs = Label('eggs', parent=breakfast)
    fried = Label('fried', parent=eggs)
    scrambled = Label('scrambled', parent=eggs)
    meat = Label('meat', parent=breakfast)
    bacon = Label('bacon', parent=meat)
    spam = Label('spam', parent=meat)

    taxonomy = Taxonomy(breakfast)

Lets break that down quickly.

At the base of a |Taxonomy| is a set of |Label| on which we declare hierarchical relationships, here using the
``parent`` keyword argument of the |Label| constructor as in:

.. code-block:: python

    eggs = Label('eggs', parent=breakfast)

These |Label| once linked implicitly defines a label |Tree|, thus we may define a |taxonomy| which is a special kind
of tree with the last line:

.. code-block:: python

    taxonomy = Taxonomy(breakfast)

We can print it to check that it was correctly created:

.. code-block:: pycon

    >>> print(taxonomy)
    ╰── breakfast item
        ├── eggs
        │   ├── fried
        │   ╰── scrambled
        ╰── meat
            ├── bacon
            ╰── spam

.. _make_record_collection:

Make a record collection
------------------------

The next step is to create a bunch of |Record| and to store them in a |RecordCollection|:

.. code-block:: python

    from plums.commons.data import RecordCollection, Record

    first = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('eggs', ))
    second = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('bacon', ))
    third = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('scrambled', ))
    fourth = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('meat', ))
    fifth = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('eggs', ))
    last = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('spam', ),
                  spam=('spam', 'spam'),
                  beautiful='spam')

    record_collection = RecordCollection(first, second, third, fourth, fifth, last)

Let's break that down.

We begin by creating a few |Record| with basic and identical coordinates and one label for each, for example:

.. code-block:: python

    first = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('eggs', ))

Note that |Record| may gather arbitrary properties with them which are accessible as attributes, for example, we
added properties in the ``last`` record:

.. code-block:: python

    last = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('spam', ),
                  spam=('spam', 'spam'),
                  beautiful='spam')

The |RecordCollection| is what we call a **container class** because it gives us a compact manner to hold a set of
|Record| with convenient access and extension mechanisms.

Moreover, |RecordCollection| are context-aware, in the sense that that we can attach a |Taxonomy| to them and make use
of the relationships defined.

As of now, the |RecordCollection| constructed a flat, non-informative |Taxonomy| from its records:

.. code-block:: pycon

    >>> print(record_collection.taxonomy)
    ├── eggs
    ├── bacon
    ├── scrambled
    ├── meat
    ╰── spam

If we want to go further than that, let's attach the taxonomy from earlier:

.. code-block:: python

    record_collection.taxonomy = taxonomy

This allows getting |Record| with labels *"up to a certain depth"* for example:

.. code-block:: pycon

    >>> print(record_collection[1])
    bacon
    >>> print(record_collection.get(max_depth=2)[1])
    meat

Or enforcing a set of known |Label| with automatic validation for all modification:

.. code-block:: pycon

    >>> invalid_record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('sausages', ))
    >>> record_collection.append(invalid_record)
    Traceback (most recent call last):
      File "plums/commons/data/taxonomy/__init__.py", line 183, in validate
        if len(set(labels) & viewkeys(self._label.descendants)) != len(labels):
    ValueError: Invalid label tuple: {Label(name=sausages)} are not part of the taxonomy.
    >>> record_collection[1] = invalid_record
    Traceback (most recent call last):
      File "plums/commons/data/taxonomy/__init__.py", line 183, in validate
        if len(set(labels) & viewkeys(self._label.descendants)) != len(labels):
    ValueError: Invalid label tuple: {[Label(name=sausages)} are not part of the taxonomy.

Make a tile, an annotation and a data point
-------------------------------------------

From here on making a |DataPoint| is rather straight forward as it mainly involves *container classes*.

We have to build an |Annotation| from our |RecordCollection|:

.. code-block:: python

    from plums.commons.data import Annotation

    annotation = Annotation(record_collection)

Then we will build a dummy empty |Tile| with numpy and the |TileWrapper| util class:

.. code-block:: python

    import numpy as np
    from plums.commons.data import TileWrapper

    tile = TileWrapper(np.zeros((100, 100, 3)))

A |DataPoint| is a *container class* for a |Tile|, |Annotation| couple, which is straightforward to construct:

.. code-block:: python

    from plums.commons.data import DataPoint

    data_point = DataPoint(tile, annotation)
