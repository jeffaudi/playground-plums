from abc import ABC, abstractmethod

from plums.commons import Path, RecordCollection
from plums.plot.engine.descriptor import CategoricalDescriptor
from plums.plot.engine.orchestrator import Orchestrator


class Plot(ABC):
    """Abstract high-level class that defines the interface each high-level plotting classes must implement.

    It serves as a base class for each end-user orchestrator:

    * Its constructor gives access to all *plumbing classes* parameters to allow extensive configuration of the
      internal plotting machinery. Moreover, every *plumbing classes* used parameters are accessible and
      customizable as attributes of the plot instance.

    Args:
        main_descriptor (|Descriptor|): A |Descriptor| to be used as primary descriptor in the |ColorEngine|.
        secondary_descriptor (|Descriptor|): Optional. Defaults to ``None``. A |Descriptor| to be used as secondary
            descriptor in the |ColorEngine|.
        zoom (float): Optional. Defaults to ``1``. The zooming factor for each |Tile| in the ``layout``.
        title (str): Optional. Defaults to ``None``. The composite figure global title, if provided.
        plot_centers (bool): Optional. Defaults to ``False``. If ``True``, only a dot at the center of each |Record|
            is painted instead of the polygon geometry.
        plot_tag (|Descriptor|): Optional. Defaults to ``None``. Besides the geometry, display a |Record|
            description in a tag attached to the |Record|.
        fill (bool): Optional. Defaults to ``False``. A flag which represents whether to draw filled polygons.
        **kwargs (Any): Additional parameters to set.

    """

    def __init__(self, main_descriptor, secondary_descriptor=None, zoom=1, title=None,
                 plot_centers=False, plot_tag=None, fill=False, **kwargs):
        # Init orchestrator
        self._orchestrator = Orchestrator(main_descriptor=main_descriptor, secondary_descriptor=secondary_descriptor,
                                          zoom=zoom, title=title, plot_centers=plot_centers, plot_tag=plot_tag,
                                          fill=fill, **kwargs)

        # Set attributes
        self._layout = []

    def __getattribute__(self, name):
        """Retrieve an attribute from self or fallback to the underlying |Orchestrator| if ``name`` is unknown."""
        try:
            return super(Plot, self).__getattribute__(name)
        except AttributeError:
            return getattr(self._orchestrator, name)

    def __setattr__(self, name, value):
        """Set an attribute's value in the underlying |Orchestrator| or fallback to self if ``name`` is unknown."""
        if '_orchestrator' in super(Plot, self).__getattribute__('__dict__') and hasattr(self._orchestrator, name):
            setattr(self._orchestrator, name, value)
        else:
            super(Plot, self).__setattr__(name, value)

    def __delattr__(self, name):
        """Delete an attribute in the underlying |Orchestrator| or fallback to self if ``name`` is unknown."""
        if hasattr(self._orchestrator, name):
            delattr(self._orchestrator, name)
        else:
            super(Plot, self).__delattr__(name)

    def __dir__(self):
        """Retrieve self dir with the underlying |Orchestrator| dir appended."""
        return list(super(Plot, self).__dir__()) + list(self._orchestrator.__dir__())

    @abstractmethod
    def add(self, *args, **kwargs):
        """Accumulate a |DataPoint| like entity to the final layout."""
        raise NotImplementedError

    def reset(self):
        """Reset the layout."""
        self._layout = []

    def plot(self, file_path=None):
        """Plot the composite figure with the created layout.

        Args:
            file_path (PathLike): Optional. Defaults to ``None``. Save figure to given the filename.

        Raises:
            ValueError: When the layout is empty, meaning no |DataPoint| to plot.

        Returns:
            :class:`~PIL.Image.Image`: The composite figure with the legend and optionally, a title.

        """
        if not self._layout:
            raise ValueError('You need to accumulate data points first (cf `add` method), in order to plot something.')

        figure = self._orchestrator.draw(self._layout).convert('RGB')

        # Save figure to disk
        if file_path is not None:
            file_path = Path(file_path)
            file_path.mkdir(parents=True, exist_ok=True)
            figure.save(str(file_path))

        return figure


class StandardPlot(Plot):
    """Standard plot class that accumulates |Tile| and |RecordCollection| and compose a figure.

    It serves as a *porcelain class*:

    * Its constructor gives access to all *plumbing classes* parameters to allow extensive configuration of the
      internal potting machinery (Moreover, every *plumbing classes* used parameters are accessible and
      parameterizable as attributes of the plot instance.)

    Args:
        main_descriptor (|Descriptor|): A |Descriptor| to be used as primary descriptor in the |ColorEngine|.
        secondary_descriptor (|Descriptor|): Optional. Defaults to ``None``. A |Descriptor| to be used as secondary
            descriptor in the |ColorEngine|.
        zoom (float): Optional. Defaults to ``1``. The zooming factor for each |Tile| in the ``layout``.
        title (str): Optional. Defaults to ``None``. The composite figure global title, if provided.
        plot_centers (bool): Optional. Defaults to ``False``. If ``True``, only a dot at the center of each |Record|
            is painted instead of the polygon geometry.
        plot_tag (|Descriptor|): Optional. Defaults to ``None``. Besides the geometry, display a |Record|
            description in a tag attached to the |Record|.
        fill (bool): Optional. Defaults to ``False``. A flag which represents whether to draw filled polygons.
        **kwargs (Any): Additional parameters to set.

    """

    def __init__(self, main_descriptor, secondary_descriptor=None, zoom=1, title=None, plot_centers=False,
                 plot_tag=None, fill=False, **kwargs):

        super(StandardPlot, self).__init__(main_descriptor=main_descriptor, secondary_descriptor=secondary_descriptor,
                                           zoom=zoom, title=title, plot_centers=plot_centers, plot_tag=plot_tag,
                                           fill=fill, **kwargs)

    def add(self, tile, record_collection):
        """Accumulate a |Tile| and a |RecordCollection| to the final layout.

        The painted tiles are accumulated along the horizontal axis, next to each others. When the maximum number of
        tiles is reached, a new row is created, filling a grid.

        Args:
            tile (|Tile|): The |Tile| to paint records on.
            record_collection (|RecordCollection|): A |RecordCollection| that should be painted on the tile.

        """
        self._layout.append((tile, record_collection))


class PairPlot(Plot):
    """Pair plot which accumulates couples of ground truths and predictions and plot them.

    It serves as a *porcelain class*:

    * Its constructor gives access to all *plumbing classes* parameters to allow extensive configuration of the
      internal potting machinery (Moreover, every *plumbing classes* used parameters are accessible and
      parameterizable as attributes of the orchestrator instance.)

    Two layout modes are available:

    * **Overlapping**: The ground truths and the predictions are painted on the same tile.
    * **Non-overlapping**: Each :meth:`add` method add a new line to the final layout, where the first painted tile
      corresponds to the ground truths and the ones that follows, the different predictions.

    Args:
        secondary_descriptor (|Descriptor|): Optional. Defaults to ``None``. A |Descriptor| to be used as secondary
            descriptor in the |ColorEngine|.
        overlap (boo): Optional. Defaults to ``False``. If ``True``, overlap the predictions with the ground truths
            on a single tile. Otherwise, display them next to each other.
        zoom (float): Optional. Defaults to ``1``. The zooming factor for each |Tile| in the ``layout``.
        title (str): Optional. Defaults to ``None``. The composite figure global title, if provided.
        plot_centers (bool): Optional. Defaults to ``False``. If ``True``, only a dot at the center of each |Record|
            is painted instead of the polygon geometry.
        plot_tag (|Descriptor|): Optional. Defaults to ``None``. Besides the geometry, display a |Record|
            description in a tag attached to the |Record|.
        fill (bool): Optional. Defaults to ``False``. A flag which represents whether to draw filled polygons.
        **kwargs (Any): Additional parameters to set.

    """

    def __init__(self, secondary_descriptor=None, overlap=False, zoom=1, title=None, plot_centers=False, plot_tag=None,
                 fill=False, **kwargs):

        # Set attributes
        self._line_length = None
        self._overlap = overlap

        # Init orchestrator with predefined main descriptor (ground truth vs prediction)
        super(PairPlot, self).__init__(main_descriptor=CategoricalDescriptor('set', fetch_fn=self._get_label),
                                       secondary_descriptor=secondary_descriptor, zoom=zoom, title=title,
                                       plot_centers=plot_centers, plot_tag=plot_tag, fill=fill, **kwargs)

    @staticmethod
    def _get_label(ground_truth):
        """Compute the name of the categories to display on the legend, depending on the ``ground_truth`` flag.

        Args:
            ground_truth (bool): Flag that indicates if the record has the property ``ground_truth`` sets to ``True``.

        Returns:
            str: A human-readable label.

        """
        return 'Ground Truth' if ground_truth is True else 'Prediction'

    @staticmethod
    def _set_ground_truth_property(record_collection, value):
        """Set the ``ground_truth`` property on a whole |RecordCollection|.

        Args:
            record_collection (|RecordCollection|): The collection on which the property should be set.
            value (bool): Flag that indicates if the records of the collection are ground truths or predictions.

        Returns:
            |RecordCollection|: The updated collection.

        """
        for index, _ in enumerate(record_collection):
            record_collection[index].set = value
        return record_collection

    def add(self, tile, ground_truths_collection, *predictions_collections):
        """Accumulate a |RecordCollection| of ground truths and at least one |RecordCollection| of predictions.

        Two different layouts are available:

        * **Overlapping**: The ground truth and the predictions are painted on the same tile. As a result, you can
          not exceed a single |RecordCollection| for the predictions on a given tile. Readibility matters.
        * **Non-overlapping**: Each :meth:`add` method add a new line to the final layout, where the first painted tile
          corresponds to the ground truths and the ones that follows, the different predictions. Currently, the length
          of each line is fixed by the first call of this very method.

        Args:
            tile (|Tile|): The |Tile| to paint records on.
            ground_truths_collection (|RecordCollection|): A collection of |Record| that aims to be the ground truth.
            *predictions_collections (|RecordCollection|): A collection of |Record| that constitutes the predictions.

        Raises:
            ValueError: When too many predictions |RecordCollection| are given in ``Overlapping`` mode.
            ValueError: When lines are of different lengths in ``non-Overlapping`` mode.

        """
        # Sanity checks
        if self._overlap is True and len(predictions_collections) > 1:
            raise ValueError('You can only overlap a single predictions record collection to the ground truths.')
        if self._line_length is not None and self._line_length != len(predictions_collections) + 1:
            raise ValueError('Lines of the final layout should be of same length.')

        # Add a property to distinguish ground truths from predictions
        new_ground_truths_collection = self._set_ground_truth_property(ground_truths_collection, True)

        new_predictions_collections = [self._set_ground_truth_property(collection, False)
                                       for collection in predictions_collections]

        # Fill the layout
        if self._overlap is True:
            preds = [item for sublist in new_predictions_collections for item in sublist]
            record_collection = RecordCollection(*(new_ground_truths_collection.records + preds))
            self._layout.append((tile, record_collection))
        else:
            line = [(tile, new_ground_truths_collection)]
            line += [(tile, preds) for preds in new_predictions_collections]
            self._layout.append(line)
            # Update the size of the layout to respect for future accumulations
            if self._line_length is None:
                self._line_length = len(line)

    def reset(self):
        """Reset the layout."""
        self._line_length = None
        super(PairPlot, self).reset()
