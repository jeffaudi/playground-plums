.. _plot_quickstart:

Quickstart
==========

.. include:: ../../include.rst


The Plums plot allows to visualize objects detection and segmentation results.

In this QuickStart, we will use the following image:

.. image:: /_static/plot/ships.png
   :scale: 40 %
   :align: center

*Plums* plot uses two components to create figures, the |StandardPlot| or the |PairPlot| interfaces
(which all behave in a similar fashion: one accumulates |DataPoint|-like elements with
:meth:`~playground_plums.plot.plot.Plot.add` and aggregates them into a single figure with
:meth:`~playground_plums.plot.plot.Plot.plot`), and the :ref:`descriptor`.

Each *Plot* class has slight differences:

* |StandardPlot| takes a |Tile| and a single |RecordCollection| for each
  :meth:`~playground_plums.plot.plot.StandardPlot.add` call.
* |PairPlot| takes a |Tile| and a pair of |RecordCollection| (implicitly interpreted as *predictions*
  and *ground-truths* respectively) for each :meth:`~playground_plums.plot.plot.StandardPlot.add` call.


.. code-block:: python

    import numpy as np
    import PIL.Image
    import playground_plums.commons.data as data
    from playground_plums.plot.plot import StandardPlot, PairPlot
    from playground_plums.plot.descriptor import Labels, Confidence

    # Make the prediction record collection
    records = [
        data.Record(
            [[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]],
            ['Ship'], confidence=0.9),
        data.Record(
            [[[500, 500], [550, 550], [500, 600], [450, 550], [500, 500]]],
            ['Bus'], confidence=0.62),
        data.Record(
            [[[250, 0], [300, 0], [275, 25], [300, 50], [250, 50], [275, 25], [250, 0]]],
            ['Car'], confidence=0.5),
        data.Record(
            [[[300, 300], [320, 280], [420, 380], [400, 400], [300, 300]]],
            ['Ship'], confidence=0.3),
        data.Record(
            [[[650, 300], [670, 280], [770, 380], [750, 400], [650, 300]]],
            ['Ship'], confidence=0.86),
        data.Record(
            [[[-20, 600], [50, 600], [50, 650], [-20, 650], [-20, 600]]],
            ['Car'], confidence=0.927),
        data.Record(
            [[[650, 450], [650, 550], [600, 550], [600, 450], [650, 450]]],
            ['Ship'], confidence=0.927),
        data.Record(
            [[[500, -50], [550, -50], [550, 50], [500, 50], [500, -50]]],
            ['Bus'], confidence=0.885),
    ]

    # Make the ground truths record collection
    records_ground_truths = [
        data.Record(
            [[[30, 0.], [125, 130], [165, 120], [80, 0], [30, 0]]],
            ['Ship']),
        data.Record(
            [[[580, 440], [610, 430], [690, 560], [660, 570], [580, 440]]],
            ['Ship']),
    ]

    # Create collection
    record_collection = data.RecordCollection(*records)
    record_collection_ground_truths = data.RecordCollection(*records_ground_truths)

     # Open a tile
    tile = PIL.Image.open('image.png')

    # Plot the results with StandardPlot
    plot = StandardPlot(Labels(),
                        secondary_descriptor=Confidence(),
                        title='StandardPlot',
                        fill=True,
                        plot_tag=Confidence())
    plot.add(tile, record_collection)
    plot.plot('StandardPlot.png')

    # Plot the results with PairPlot
    plot_pair = PairPlot(secondary_descriptor=Labels(),
                         title='PairPlot',
                         plot_tag=Labels(),
                         fill=True)
    plot_pair.add(tile, record_collection_ground_truths, record_collection)
    plot_pair.plot('PairPlot.png')


Code breakdown
..............

.. _make_record_collection_plot:

Make record collections and the tile
------------------------------------

The first step would be to construct a few |Record| with different coordinates in the image and one label for each and
to store them in a |RecordCollection| as predictions or ground truths.


.. code-block:: python

    import playground_plums.commons.data as data

    records = [
        data.Record(
            [[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]],
            ['Ship'], confidence=0.9),
        data.Record(
            [[[500, 500], [550, 550], [500, 600], [450, 550], [500, 500]]],
            ['Bus'], confidence=0.62),
        data.Record(
            [[[250, 0], [300, 0], [275, 25], [300, 50], [250, 50], [275, 25], [250, 0]]],
            ['Car'], confidence=0.5),
        data.Record(
            [[[300, 300], [320, 280], [420, 380], [400, 400], [300, 300]]],
            ['Ship'], confidence=0.3),
        data.Record(
            [[[650, 300], [670, 280], [770, 380], [750, 400], [650, 300]]],
            ['Ship'], confidence=0.86),
        data.Record(
            [[[-20, 600], [50, 600], [50, 650], [-20, 650], [-20, 600]]],
            ['Car'], confidence=0.927),
        data.Record(
            [[[650, 450], [650, 550], [600, 550], [600, 450], [650, 450]]],
            ['Ship'], confidence=0.927),
        data.Record(
            [[[500, -50], [550, -50], [550, 50], [500, 50], [500, -50]]],
            ['Bus'], confidence=0.885),
    ]

    records_ground_truths = [
        data.Record(
            [[[30, 0], [80, 0], [165, 120], [125, 130], [30, 0]]],
            ['Ship']),
        data.Record(
            [[[580, 440], [610, 430], [690, 560], [660, 570], [580, 440]]],
            ['Ship']),
    ]

    records_collection = data.RecordCollection(*records)
    records_collection_ground_truths = data.RecordCollection(*records_ground_truths)

Then, we need to open and instantiate the |Tile| with the image:

.. code-block:: python

    import numpy as np
    import PIL.Image
    import playground_plums.commons.data as data

    tile = PIL.Image.open('image.png')


.. _StandardPlot:

StandardPlot
------------

The |StandardPlot| will compose a figure by painting each record contained in the |RecordCollection| on the |Tile|.

It can use one or two descriptors to classify the objects contained in a |RecordCollection|.
In this example, we use |Labels| as first descriptor which is used to extract the
:attr:`~playground_plums.commons.data.record.Record.labels` from
each |Record| and the |Confidence| as secondary descriptor which is used to extract their
:attr:`~playground_plums.commons.data.record.Record.confidence` property.

.. code-block:: python

   from playground_plums.plot.plot import StandardPlot

   plot = StandardPlot(Labels(),
                       secondary_descriptor=Confidence(),
                       title='StandardPlot',
                       fill=True,
                       plot_tag=Confidence())
    plot.add(tile, record_collection)
    plot.plot('StandardPlot.png')

.. image:: /_static/plot/standard_confidence.png
   :scale: 60 %
   :align: center



.. _PairPlot:

PairPlot
--------

An other way to paint your records is to use the |PairPlot| which provides two layouts.

The |PairPlot| will compose a figure by painting the ground truths and the predictions.
It accumulates the ground truths |RecordCollection| and one or several predictions |RecordCollection|.

You have two options :
 * Painting the ground truths and the predictions on the same tile.
 * Painting the ground truths and the predictions on different tiles.

In this example, we use |Labels| as secondary descriptor and we paint the ground truths and the predictions on
different tiles.

.. code-block:: python

    from playground_plums.plot.plot import  PairPlot

    plot_pair = PairPlot(secondary_descriptor=Labels(),
                         title='PairPlot',
                         plot_tag=Labels(),
                         fill=True)
    plot_pair.add(tile, record_collection_ground_truths, record_collection)
    plot_pair.plot('PairPlot.png')

.. image:: /_static/plot/pair.png
