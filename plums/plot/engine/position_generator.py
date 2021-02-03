from operator import itemgetter
from abc import ABC, abstractmethod


class ImagePositionGeneratorBase(ABC):
    """Generate the position of the painted images on the final mosaic.

    Args:
        margins (tuple): Margins to use between each cell in the mosaic.
        max_image_size (tuple): Maximum size of the painted images.

    Attributes:
        _margins (tuple): (x, y) offsets of each painted image in its cell in the mosaic.
        _width (int): Width of each mosaic cell (image width + left/right margins)
        _height (int): Height of each mosaic cell (image height + bottom/top margins)

    """

    def __init__(self, margins, max_image_size):
        # Variables
        self._margins = margins
        self._width, self._height = tuple(map(lambda x, y: x + 2 * y, max_image_size, margins))

    @property
    def mosaic_size(self):
        """(float, float): Dimensions, in pixels, of the output mosaic total cell (width, height)."""
        return self._n_cols * self._width, self._n_rows * self._height

    @abstractmethod
    def __iter__(self):
        """Generate the position of each image cell in the final image mosaic.

        Yields:
            :class:`tuple`: The top-left corner (x, y) position of the current image in the mosaic.

        """
        raise NotImplementedError


class SimpleImagePositionGenerator(ImagePositionGeneratorBase):
    """Generate the position of the painted images on the final mosaic from a list of |DataPoint|-like on a fixed grid.

    Args:
        data_points (list, tuple): List of |DataPoint|-like collection of |Tile| and |RecordCollection| to be drawn.
        max_cols (int): Number of columns not to exceed in the final mosaic.
        margins (tuple): Margins to use between each cell in the mosaic.
        max_image_size (tuple): Maximum size of the painted images.

    Attributes:
        _margin (tuple): (x, y) offsets of each painted image in its cell in the mosaic.
        _width (int): Width of each mosaic cell (image width + left/right margins)
        _height (int): Height of each mosaic cell (image height + bottom/top margins)
        _n_cols (int): Number of columns in the output mosaic.
        _n_rows (int): Number of rows in the output mosaic (excluding remaining images)
        _remainder (int): Number of extra images at the bottom of the mosaic.
                                 (nb_images = _n_cols * _n_rows + _remainder)

    """

    def __init__(self, data_points, max_cols, margins, max_image_size):
        super(SimpleImagePositionGenerator, self).__init__(margins, max_image_size)

        self._max_cols = max_cols

        # Compute dimensions of the final mosaic (columns, rows)
        nb_datapoints = len(data_points)
        self._n_cols = min(nb_datapoints, self._max_cols)
        self._n_rows, self._remainder = divmod(nb_datapoints, self._n_cols)

    def __iter__(self):
        """Generate the position of each image cell in the final image mosaic.

        Yields:
            :class:`tuple`: The top-left corner (x, y) position of the current image in the mosaic.

        """
        # Generate image positions (top-left corner) in the final mosaic
        for r in range(self._n_rows):
            for c in range(self._n_cols):
                yield int(c * self._width + self._margins[0]), int(r * self._height + self._margins[1])

        # Do not forget remaining datapoints
        for c in range(self._remainder):
            yield int(c * self._width + self._margins[0]), int(self._n_rows * self._height + self._margins[1])

    @property
    def mosaic_size(self):
        """(float, float): Dimensions, in pixels, of the output mosaic total cell (width, height)."""
        true_n_rows = self._n_rows + 1 if self._remainder else self._n_rows
        return self._n_cols * self._width, true_n_rows * self._height


class LayoutImagePositionGenerator(ImagePositionGeneratorBase):
    """Generate the position of the painted images on the final mosaic from a 2D-array of |DataPoint|-like.

    As an example:

    .. code-block:: python

        data_point = [[dp1, dp2, dp3],
                      [dp3, dp4],
                      [dp5, dp6, dp7, dp8]]

    would result in the following layout:

    ..image:: /_static/2d_layout.png

    Args:
        data_points (array-like): A 2D array-like of |DataPoint|-like collection of |Tile| and |RecordCollection|
            to be drawn. Each line of the 2D array-like is expected to correspond to a line layout in the final
            mosaic cell.
        margins (tuple): Margins to use between each cell in the mosaic.
        max_image_size (tuple): Maximum size of the painted images.

    Attributes:
        _margins (tuple): (x, y) offsets of each painted image in its cell in the mosaic.
        _width (int): Width of each mosaic cell (image width + left/right margins)
        _height (int): Height of each mosaic cell (image height + bottom/top margins)
        _n_cols (int): Number of columns in the output mosaic.
        _n_rows (int): Number of rows in the output mosaic (excluding remaining images)

    """

    def __init__(self, data_points, margins, max_image_size):
        super(LayoutImagePositionGenerator, self).__init__(margins, max_image_size)

        self._layout = tuple(len(line) for line in data_points)

        self._n_cols = max(self._layout)
        self._n_rows = len(self._layout)

    def __iter__(self):
        """Generate the position of each image cell in the final image mosaic.

        Yields:
            :class:`tuple`: The top-left corner (x, y) position of the current image in the mosaic.

        """
        # Generate image positions (top-left corner) in the final mosaic
        for r, n_cols in enumerate(self._layout):
            layout_margin = 0.5 * ((self.mosaic_size[0] - n_cols * self._width) / float(n_cols))
            for c in range(n_cols):
                yield (c * (self._width + 2 * layout_margin) + self._margins[0] + layout_margin,
                       r * self._height + self._margins[1])


class AdaptiveImagePositionGenerator(LayoutImagePositionGenerator):
    """Generate the position of images on the final mosaic from a list of |DataPoint|-like with a centered last row.

    Args:
        data_points (list, tuple): List of |DataPoint|-like collection of |Tile| and |RecordCollection| to be drawn.
        max_cols (int): Number of columns not to exceed in the final mosaic.
        margins (tuple): Margins to use between each cell in the mosaic.
        max_image_size (tuple): Maximum size of the painted images.

    Attributes:
        _margin (tuple): (x, y) offsets of each painted image in its cell in the mosaic.
        _width (int): Width of each mosaic cell (image width + left/right margins)
        _height (int): Height of each mosaic cell (image height + bottom/top margins)
        _n_cols (int): Number of columns in the output mosaic.
        _n_rows (int): Number of rows in the output mosaic (excluding remaining images)
        _remainder (int): Number of extra images at the bottom of the mosaic.
                                 (nb_images = _n_cols * _n_rows + _remainder)

    """

    def __init__(self, data_points, max_cols, margins, max_image_size):
        self._max_cols = max_cols

        # Compute dimensions of the final mosaic (columns, rows)
        nb_datapoints = len(data_points)
        n_cols = min(nb_datapoints, self._max_cols)
        n_rows, remainder = divmod(nb_datapoints, n_cols)
        layout = [[data_points[i + n_cols * j] for i in range(n_cols)] for j in range(n_rows)]
        if remainder:
            layout += [[data_points[n_rows * n_cols + i] for i in range(remainder)]]
        super(AdaptiveImagePositionGenerator, self).__init__(layout, margins, max_image_size)


class LegendItemPositionGenerator(object):
    """A class that generates the position of each legend item in an arbitrary grid.

    This class generates a grid with each cell having the dimensions of the biggest item to draw.
    Then it fills the grid along the main axis first, then the minor one. The size of the legend along the
    main axis is fixed while the size along the minor one is variable.

    Moreover, items could be aligned in their own cells, both vertically and horizontally. Three kinds of alignment
    are allowed (``start``, ``center`` and ``end``), relatively to the cell it concerns.

    Args:
        items_sizes (list): List of tuples representing item dimensions, using *(width, height)* format.
        axis (int): Main direction of the legend (**0** = vertically, **1** = horizontally)
        max_size_along_axis (int): The size, in pixels, to not exceed along the main axis.
        main_axis_align (str): Optional. Defaults to ``start``. Alignment of the item in its cell along the main axis.
        minor_axis_align (str): Optional. Defaults to ``start``. Alignment of the item in its cell along the minor axis.

    Raises:
        ValueError: When ``items_sizes`` is not a non-empty list.
        ValueError: When an item size exceeds the maximum allowed size along the main axis.

    """

    def __init__(self, items_sizes, axis, max_size_along_axis, main_axis_align='start', minor_axis_align='start'):

        # Sanity checks
        if not isinstance(items_sizes, list) or not items_sizes:
            raise ValueError('Items_sizes should be a non-empty list.')

        # Set attributes
        self._items_sizes = items_sizes
        self._axis = axis
        self._max_size_along_axis = max_size_along_axis
        self._main_axis_align = main_axis_align
        self._minor_axis_align = minor_axis_align

        # Compute cell size (max_cell_width, max_cell_height)
        self._cell_size = (max(items_sizes, key=itemgetter(0))[0],
                           max(items_sizes, key=itemgetter(1))[1])

        # Retrieve index of the main and minor axes (either 0 or 1)
        self._new_positions = (1, 0) if self._axis == 0 else (0, 1)
        self._main_axis_index, self._minor_axis_index = self._new_positions

        # Sanity checks : only items that fit into the legend
        if self._cell_size[self._main_axis_index] >= max_size_along_axis:
            raise ValueError('Items could not fit into a legend of max size {}px.'.format(self._max_size_along_axis))

        # Compute legend grid dimensions, meaning number of items/cells in each direction
        self._n_items_along_main_axis = max_size_along_axis // self._cell_size[self._main_axis_index]
        self._n_items_along_minor_axis, self._remainder = divmod(len(items_sizes), self._n_items_along_main_axis)

    def __iter__(self):
        """tuple: Generate the true position of each item in the legend."""
        # Fill the grid, first along primary axis, then the secondary one
        for s in range(self._n_items_along_minor_axis):
            for p in range(self._n_items_along_main_axis):
                # Compute item coordinates
                main_axis_coordinate = p * self._cell_size[self._main_axis_index]
                minor_axis_coordinate = s * self._cell_size[self._minor_axis_index]
                # Yield item final position
                yield self.align_cell_in_box(main_axis_coordinate=main_axis_coordinate,
                                             minor_axis_coordinate=minor_axis_coordinate,
                                             item_size=self._items_sizes[p + s * self._n_items_along_main_axis])

        # Do not forget remaining items
        for r in range(self._remainder):
            main_axis_coordinate = r * self._cell_size[self._main_axis_index]
            minor_axis_coordinate = self._n_items_along_minor_axis * self._cell_size[self._minor_axis_index]
            # Yield item final position
            yield self.align_cell_in_box(main_axis_coordinate=main_axis_coordinate,
                                         minor_axis_coordinate=minor_axis_coordinate,
                                         item_size=self._items_sizes[-self._remainder:][r])

    def align_cell_in_box(self, main_axis_coordinate, minor_axis_coordinate, item_size):
        """Place each item relatively to its cell.

        Different alignments are allowed, along the two directions:

        * **vertically**: ``start``, ``center`` or ``end`` - vertical position of the item in its cell.
        * **horizontally**: ``start``, ``center`` or ``end`` - horizontal position of the item in its cell.

        Args:
            main_axis_coordinate (int): Coordinate of the item along the main axis, in pixels.
            minor_axis_coordinate (int): Coordinate of the item along the minor axis, in pixels.
            item_size (tuple): Item dimensions, using *(width, height)* format.

        Returns:
            tuple: Final position of the item in the output legend.

        """
        # Set coefficient for all available alignment (start, center or end)
        coefficients = {'start': 0, 'center': 0.5, 'end': 1}

        # Compute new coordinates
        main_axis_coordinate = int(main_axis_coordinate
                                   + coefficients[self._main_axis_align] * self._cell_size[self._main_axis_index]
                                   - coefficients[self._main_axis_align] * item_size[self._main_axis_index])
        minor_axis_coordinate = int(minor_axis_coordinate
                                    + coefficients[self._minor_axis_align] * self._cell_size[self._minor_axis_index]
                                    - coefficients[self._minor_axis_align] * item_size[self._minor_axis_index])

        # Return new coordinates in the rightful order (depending on the index of the main axis)
        return itemgetter(*self._new_positions)((main_axis_coordinate, minor_axis_coordinate))

    @property
    def cell_size(self):
        """tuple: Dimensions of the legend grid cells, using *(width, height)* format."""
        return self._cell_size

    @property
    def legend_size(self):
        """tuple: Dimensions, in pixels, of the legend, using *(width, height)* format."""
        main_axis_size = self._max_size_along_axis
        if self._remainder:
            minor_axis_size = (self._n_items_along_minor_axis + 1) * self._cell_size[self._minor_axis_index]
        else:
            minor_axis_size = self._n_items_along_minor_axis * self._cell_size[self._minor_axis_index]

        # Return legend size in the rightful order (depending on the index of the main axis)
        return itemgetter(*self._new_positions)((main_axis_size, minor_axis_size))

    @property
    def true_legend_size(self):
        """tuple: True dimensions, in pixels, of the legend, using *(width, height)* format."""
        main_axis_size = min(self._n_items_along_main_axis,
                             len(self._items_sizes)) * self._cell_size[self._main_axis_index]

        if self._remainder:
            minor_axis_size = (self._n_items_along_minor_axis + 1) * self._cell_size[self._minor_axis_index]
        else:
            minor_axis_size = self._n_items_along_minor_axis * self._cell_size[self._minor_axis_index]

        # Return legend size in the rightful order (depending on the index of the main axis)
        return itemgetter(*self._new_positions)((main_axis_size, minor_axis_size))
