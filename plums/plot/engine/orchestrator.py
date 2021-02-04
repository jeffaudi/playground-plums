from plums.commons import PropertyContainer, DataPoint, Annotation, Tile, RecordCollection
from plums.plot.engine.color_engine import ColorEngine
from plums.plot.engine.compositor import Compositor


class OrchestratorBase(PropertyContainer):
    """Medium-level orchestrator which configure a |Compositor| and a |ColorEngine| from |Descriptor| and a layout.

    It serves as an intermediary between high-level *porcelain classes* and low-level *plumbing classes*:

    * Its constructor gives access to all *plumbing classes* parameters to allow extensive configuration of the
      internal potting machinery (Moreover, every *plumbing classes* used parameters are accessible and
      parameterizable as attributes of the orchestrator instance.)
    * Its :meth:`draw(layout) <draw>` method takes a generic ``layout`` iterable as input with no assumption on the
      semantic role of a particular figure cell.

    However, the *plumbing call sequence* does assume a standard workflow which reflect the *porcelain classes* API.

    Args:
        main_descriptor (|Descriptor|): A |Descriptor| to be used as primary descriptor in the |ColorEngine|.
        secondary_descriptor (|Descriptor|): Optional. Default to ``None``. A |Descriptor| to be used as secondary
            descriptor in the |ColorEngine|.
        zoom (float): Optional. Default to ``1``. The zooming factor for each |Tile| in the ``layout``.
        title (str): Optional. Default to ``None``. The composite figure global title, if provided.
        plot_centers (bool): Optional. Default to ``False``. If ``True``, only a dot at the center of each |Record|
            is painted instead of the polygon geometry.
        plot_tag (|Descriptor|): Optional. Defaults to ``None``. Besides the geometry, display a |Record|
            description in a tag attached to the |Record|.
        fill (bool): Optional. Default to ``False``. A flag which represents whether to draw filled polygons.
        **kwargs (Any): Additional parameters to set.

    Attributes:
        main_descriptor (|Descriptor|): |ColorEngine| **parameter**: A |Descriptor| to be used as primary descriptor.
        secondary_descriptor (|Descriptor|): |ColorEngine| **parameter**: A |Descriptor| to be used as secondary
            descriptor.
        n_cols (int): |Compositor| **parameter**: Number of data points per line to not exceed (if 1D array-like of
            |DataPoint|).
        margins (tuple): |Compositor| **parameter**: Margin to use between each image of the mosaic.
        title (str): |Compositor| **parameter**: The composite figure global title, if provided.
        title_size (int): |Compositor| **parameter**: Font size of the title (in pixels).
        center (bool): |Compositor| **parameter**: Center the last line of data points (if 1D array-like of
            |DataPoint|).
        background_color (tuple): (|Compositor|, |LegendPainter|) Background color to use for the mosaic and the legend.
        scale (float): |LegendPainter| **parameter**: Scale to use, regarding the default dimensions used.
        axis (int): |LegendPainter| **parameter**: Main direction of the legend (**0** = vertically, **1** =
            horizontally)
        item_margins (tuple): |LegendPainter| **parameter**: Margins around the item (left/right and top/bottom).
        main_axis_align (str): |LegendPainter| **parameter**: Alignment of the item in its cell along the main axis.
        minor_axis_align (str): |LegendPainter| **parameter**: Alignment of the item in its cell along the minor axis.
        zoom (float): |Painter| **parameter**: The zooming factor for each |Tile| in the ``layout``.
        plot_centers (bool): |Painter| **parameter**: If ``True``, only a dot at the center of each |Record| is
            painted instead of the polygon geometry.
        plot_confidences (bool): |Painter| **parameter**: If ``True``, a label with the confidence is painted next to
            each |Record|.
        fill (bool): |Painter| **parameter**: A flag which represents whether to draw filled polygons.
        alpha (int): |Painter| **parameter**: A positive integer (between 0 and 255) that represents the fill
            transparency.

    """

    __options__ = ('zoom', 'plot_centers', 'plot_confidences', 'plot_tag', 'title', 'background_color', 'fill',
                   'n_cols', 'margins', 'background_color', 'title', 'title_size', 'center',
                   'plot_centers', 'plot_confidences', 'zoom', 'fill', 'alpha', 'scale',
                   'axis', 'item_margins', 'main_axis_align', 'minor_axis_align',
                   'main_descriptor', 'secondary_descriptor')

    def __init__(self):
        super(OrchestratorBase, self).__init__(**{option: None for option in self.__options__})


class Orchestrator(OrchestratorBase):
    """Medium-level orchestrator which configure a |Compositor| and a |ColorEngine| from |Descriptor| and a layout.

    It serves as an intermediary between high-level *porcelain classes* and low-level *plumbing classes*:

    * Its constructor gives access to all *plumbing classes* parameters to allow extensive configuration of the
      internal potting machinery (Moreover, every *plumbing classes* used parameters are accessible and
      parameterizable as attributes of the orchestrator instance.)
    * Its :meth:`draw(layout) <draw>` method takes a generic ``layout`` iterable as input with no assumption on the
      semantic role of a particular figure cell.

    However, the *plumbing call sequence* does assume a standard workflow which reflect the *porcelain classes* API.

    Args:
        main_descriptor (|Descriptor|): A |Descriptor| to be used as primary descriptor in the |ColorEngine|.
        secondary_descriptor (|Descriptor|): Optional. Default to ``None``. A |Descriptor| to be used as secondary
            descriptor in the |ColorEngine|.
        zoom (float): Optional. Default to ``1``. The zooming factor for each |Tile| in the ``layout``.
        title (str): Optional. Default to ``None``. The composite figure global title, if provided.
        plot_centers (bool): Optional. Default to ``False``. If ``True``, only a dot at the center of each |Record|
            is painted instead of the polygon geometry.
        plot_confidences (bool): Optional. Deprecated (Superseded by ``plot_tag``). Defaults to ``False``. If ``True``,
            a label with the confidence is painted next to each |Record|.
        plot_tag (|Descriptor|): Optional. Defaults to ``None``. Besides the geometry, display a |Record|
            description in a tag attached to the |Record|. Note that while ``plot_confidences`` is being deprecated,
            specifying it will override ``plot_tag``.
        fill (bool): Optional. Default to ``False``. A flag which represents whether to draw filled polygons.
        **kwargs (Any): Additional parameters to set.

    Attributes:
        main_descriptor (|Descriptor|): |ColorEngine| **parameter**: A |Descriptor| to be used as primary descriptor.
        secondary_descriptor (|Descriptor|): |ColorEngine| **parameter**: A |Descriptor| to be used as secondary
            descriptor.
        n_cols (int): |Compositor| **parameter**: Number of data points per line to not exceed (if 1D array-like of
            |DataPoint|).
        margins (tuple): |Compositor| **parameter**: Margin to use between each image of the mosaic.
        title (str): |Compositor| **parameter**: The composite figure global title, if provided.
        title_size (int): |Compositor| **parameter**: Font size of the title (in pixels).
        center (bool): |Compositor| **parameter**: Center the last line of data points (if 1D array-like of
            |DataPoint|).
        background_color (tuple): (|Compositor|, |LegendPainter|) Background color to use for the mosaic and the legend.
        scale (float): |LegendPainter| **parameter**: Scale to use, regarding the default dimensions used.
        axis (int): |LegendPainter| **parameter**: Main direction of the legend (**0** = vertically, **1** =
            horizontally)
        item_margins (tuple): |LegendPainter| **parameter**: Margins around the item (left/right and top/bottom).
        main_axis_align (str): |LegendPainter| **parameter**: Alignment of the item in its cell along the main axis.
        minor_axis_align (str): |LegendPainter| **parameter**: Alignment of the item in its cell along the minor axis.
        zoom (float): |Painter| **parameter**: The zooming factor for each |Tile| in the ``layout``.
        plot_centers (bool): |Painter| **parameter**: If ``True``, only a dot at the center of each |Record| is
            painted instead of the polygon geometry.
        plot_tag (|Descriptor|):|Painter| **parameter**: Besides the geometry, display a |Record|
            description in a tag attached to the |Record|. Note that while :attr:`plot_confidences` is being deprecated,
            specifying it will override :attr:`plot_tag`.
        fill (bool): |Painter| **parameter**: A flag which represents whether to draw filled polygons.
        alpha (int): |Painter| **parameter**: A positive integer (between 0 and 255) that represents the fill
            transparency.

    """

    def __init__(self, main_descriptor, secondary_descriptor=None, zoom=1, title=None, plot_centers=False,
                 plot_tag=None, fill=False, **kwargs):
        # Initialize properties dictionary
        super(Orchestrator, self).__init__()

        # Set defaults option values as properties
        self.n_cols = 20
        self.margins = (5, 5)
        self.title_size = 25
        self.background_color = (255, 255, 255)
        self.center = True
        self.alpha = 64
        self.scale = 1.0
        self.axis = 0
        self.item_margins = (10, 10)
        self.main_axis_align = 'start'
        self.minor_axis_align = 'start'

        # Update properties with optional user-provided values
        self.properties.update(kwargs)

        # Set explicit kwargs values
        self.fill = fill
        self.plot_tag = plot_tag
        self.plot_centers = plot_centers
        self.title = title
        self.zoom = zoom
        self.secondary_descriptor = secondary_descriptor
        self.main_descriptor = main_descriptor

    def draw(self, layout):  # noqa: R701
        """Draw a composite figure according to the stored *plumbing class* parameters and a layout array.

        Args:
            layout (array-like): Two formats are allowed: a 2D array-like of |DataPoint|-like collection of |Tile|
                and |RecordCollection| to be drawn. Each line of the 2D array-like is expected to correspond to a line
                layout in the final mosaic cell. Or a 1D array-like of |DataPoint|. In that case, the data points will
                be placed side by side, forming a mosaic of tiles, with rows of same length.

        Returns:
            :class:`~PIL.Image.Image`: A composite figure.

        """
        # Sanity check
        if not isinstance(layout, (list, tuple)):
            raise ValueError('`layout` should either be a list/tuple, but given {}'.format(type(layout)))

        if not all(isinstance(value, (list, tuple)) for value in layout):
            raise ValueError('`layout` should either be a list/tuple of DataPoint-like array '
                             'or a list/tuple of lists/tuples of DataPoint-like array.')

        if all(isinstance(sub_value, (list, tuple))
               for value in layout
               for sub_value in value):
            layout_2d = True

        elif all(isinstance(sub_value, (Tile, RecordCollection))
                 for value in layout
                 for sub_value in value):
            layout_2d = False

        else:
            raise ValueError('`layout` should either be a list/tuple of DataPoint-like array '
                             'or a list/tuple of lists/tuples of DataPoint-like array.')

        tag_descriptor = self.plot_tag
        color_engine = ColorEngine(self.main_descriptor, self.secondary_descriptor)

        # Update descriptors with total data range
        if layout_2d:
            for line in layout:
                for data_point_like in line:
                    # If plot tag next to record: Handle tag descriptor first
                    if tag_descriptor is not None:
                        tag_descriptor.update(*data_point_like[1:])
                    # Handle colors
                    color_engine.update(*data_point_like[1:])
        else:
            for data_point_like in layout:
                # If plot tag next to record: Handle tag descriptor first
                if tag_descriptor is not None:
                    tag_descriptor.update(*data_point_like[1:])
                # Handle colors
                color_engine.update(*data_point_like[1:])

        # Compute Colors and retrieve RecordCollections to paint
        data_point_layout = []
        if layout_2d:
            for line in layout:
                data_point_line = []

                for data_point_like in line:
                    # If plot tag next to record: Handle tag descriptor first
                    if tag_descriptor is not None:
                        record_collection_tuple = tag_descriptor.compute(*data_point_like[1:])
                        data_point_like = (data_point_like[0], ) + record_collection_tuple
                    # Handle colors
                    record_collection = color_engine.compute(*data_point_like[1:])[0]
                    data_point_line.append(DataPoint(data_point_like[0], Annotation(record_collection)))

                data_point_layout.append(data_point_line)
        else:
            for data_point_like in layout:
                # If plot tag next to record: Handle tag descriptor first
                if tag_descriptor is not None:
                    record_collection_tuple = tag_descriptor.compute(*data_point_like[1:])
                    data_point_like = (data_point_like[0], ) + record_collection_tuple
                # Handle colors
                record_collection = color_engine.compute(*data_point_like[1:])[0]
                data_point_layout.append(DataPoint(data_point_like[0], Annotation(record_collection)))

        # Compose the total figure from computed, described DataPoint layout
        compositor = Compositor(data_point_layout, color_engine.__descriptor__)
        pillow_figure = compositor.plot(**self.properties)

        return pillow_figure
