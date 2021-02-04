from operator import itemgetter
from abc import abstractmethod, ABC

import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from plums.plot.engine.utils import get_default_font, get_text_color


class Position(object):
    """Simple enum to represent the position of the confidence label."""

    LEFT = 'left'
    RIGHT = 'right'


class Geometry(object):
    """A class that represents a record geometry and computes meaningful properties.

    Args:
        record (tuple, list): The record to extract coordinates from.
        zoom (int): Optional. Defaults to ``1``. Zoom level to use.

    Raises:
        TypeError: When ``coordinates`` is not a collection or a nested.
        ValueError: When the record is invalid.
        ValueError: When a point has not 2 coordinates
        ValueError: When ``coordinates`` collection is empty.
        ValueError: When first and last coordinates differ.
        ValueError: When the record has an invalid geometry type (should be either ``Polygon`` or ``Point``).

    """

    def __init__(self, record, zoom=1):
        # Sanity checks
        if not hasattr(record, 'type') or not hasattr(record, 'coordinates'):
            raise ValueError('A record must expose a ``coordinates`` and a type attributes.')

        if record.type == 'Point':
            if not isinstance(record.coordinates, (tuple, list)):
                raise TypeError('The coordinates arguments should be a collection.')
            if len(record.coordinates) != 2:
                raise ValueError('A point is made of 2 coordinates.')

            # Apply zoom to coordinates
            self._coordinates = [[int(coord * zoom) for coord in record.coordinates]]

        elif record.type == 'Polygon':
            coordinates = record.coordinates[0]
            if not isinstance(coordinates, (tuple, list)):
                raise TypeError('The coordinates arguments should be a collection.')
            if not coordinates:
                raise ValueError('Can\'t compute bounding box of empty list.')
            if coordinates[0] != coordinates[-1]:
                raise ValueError('Record geometry should be a closed polygon.')

            # Re-map coordinates to Pillow format (e.g. [(x, y), (x, y), ...]) and apply zoom
            self._coordinates = [tuple(int(x * zoom) for x in coord) for coord in coordinates]

        else:
            raise ValueError('Invalid geometry type {}'.format(record.type))

    @property
    def min_x(self):
        """int: The minimum value of the coordinates along ``X`` axis."""
        return min(self._coordinates, key=itemgetter(0))[0]

    @property
    def max_x(self):
        """int: The maximum value of the coordinates along ``X`` axis."""
        return max(self._coordinates, key=itemgetter(0))[0]

    @property
    def min_y(self):
        """int: The minimum value of the coordinates along ``Y`` axis."""
        return min(self._coordinates, key=itemgetter(1))[1]

    @property
    def max_y(self):
        """int: The maximum value of the coordinates along ``Y`` axis."""
        return max(self._coordinates, key=itemgetter(1))[1]

    @property
    def centroid(self):
        """tuple: The centroid of the given geometry (mean along ``X`` and ``Y`` axes)."""
        coordinates = self._coordinates[:-1] if len(self._coordinates) > 1 else self._coordinates
        x_list = [coord[0] for coord in coordinates]
        y_list = [coord[1] for coord in coordinates]
        x = sum(x_list) / float(len(coordinates))
        y = sum(y_list) / float(len(coordinates))
        return int(x), int(y)

    @property
    def coordinates(self):
        """list: Full list of coordinates, using PIL format (i.e. ``[(x1, y1), ...]``)."""
        return self._coordinates

    @property
    def leftmost_coordinate(self):
        """tuple: The upper-leftmost coordinates as a ``(x, y)`` tuple."""
        return tuple(sorted(self._coordinates, key=lambda x: (x[0], x[1]))[0])

    @property
    def rightmost_coordinate(self):
        """tuple: The upper-rightmost coordinates as a ``(x, y)`` tuple."""
        return tuple(sorted(self._coordinates, key=lambda x: (-x[0], x[1]))[0])


class Draw(object):
    """A wrapper class arround :class:`~PIL.ImageDraw.ImageDraw` to customize drawing methods.

    Args:
        size (tuple): The tile dimensions as ``(width, height)`` tuple.
        zoom (int): Zoom level to use.
        mode (str): Image mode to use (matching :class:`~PIL.ImageMode.ImageMode`) (e.g. ``RGBA``)
        background_color (tuple): Color to use for the image background as a tuple (``RGB`` or ``RGBA``)

    Attributes:
        _draw (:class:`~PIL.ImageDraw.ImageDraw`): An object that can be used to draw in the given
                                                   image :attr:`_overlay`.

    """

    def __init__(self, size, zoom, mode, background_color):
        # Make a blank image for the annotation, initialized to transparent text color
        self._overlay = PIL.Image.new(mode=mode, size=size, color=background_color)
        self._draw = PIL.ImageDraw.Draw(self.overlay)
        self._zoom = zoom

    @property
    def overlay(self):
        """:class:`~PIL.Image.Image`: The overlay on top of the tile, including annotation drawings."""
        return self._overlay

    def circle(self, centroid, fill_color):
        """Draw a particular ellipse with a radius depending on the zoom level.

        Args:
            centroid (tuple): The centroid coordinates as a ``(x, y)`` tuple.
            fill_color (tuple): The color to use for the circle. ``RGB`` or ``RGBA`` format.

        """
        radius = 2 + int(2 * (self._zoom - 1))
        ellipse_coordinates = [
            (int(centroid[0] - radius), int(centroid[1] - radius)),
            (int(centroid[0] + radius), int(centroid[1] + radius))
        ]
        # Draw a circle onto the image
        self._draw.ellipse(ellipse_coordinates, fill=fill_color)

    def line(self, points, fill_color):
        """Draw record geometry with successive lines since PIL does not support polygon thickness.

        Args:
            points (list): A list of points as ``(x, y)`` tuples.
            fill_color (tuple): The color to use for the lines. ``RGB`` or ``RGBA`` format.

        """
        line_width = 2 + int(2 * (self._zoom - 1))
        self._draw.line(points, fill=fill_color, width=line_width, joint='curve')

    def polygon(self, points, fill_color):
        """Draw a polygon, used for the confidence label.

        Args:
            points (list`): A list of point as ``(x, y)`` tuples.
            fill_color (tuple): The color to use for the polygon. ``RGB`` or ``RGBA`` format.

        """
        self._draw.polygon(points, fill=fill_color)

    def text(self, text_coordinates, text, font, fill_color):
        """Draw a text string at the given position.

        Args:
            text_coordinates (tuple): Top-left corner text coordinates as a ``(x, y)`` tuple.
            text (str): Text to be drawn.
            font (:class:`~PIL.ImageFont.ImageFont`): Font familly to be used.
            fill_color (tuple): The color to use for the text. ``RGB`` or ``RGBA`` format.

        """
        self._draw.text(text_coordinates, text, font=font, fill=fill_color)


class TagPainter(object):
    """A tag artist class which draw a tag next to a given |Record| geometry.

    Args:
        descriptor (|Descriptor|): The |Descriptor| description to plot next to each |Record|.

            .. note::

                The |TagPainter| class assumes that each |Record| have already been described by the
                provided |Descriptor|.

        text_margin (int): Optional. Default to 2. The margin in pixel to leave between the tag text and its border.
        text_size (int): Optional. Default to 11. The tag text font size in pixel.
        zoom (int): Optional. Defaults to ``1``. Zoom level to use.

    .. versionadded:: 0.2.0

    """

    def __init__(self, descriptor, text_margin=2, text_size=11, zoom=1):
        self._descriptor = descriptor
        self._text_margin = text_margin
        self._text_size = text_size
        self._zoom = zoom

    @staticmethod
    def _compute_label_size(text, font, margin):
        """Determine the size of the label on which the text appears.

        Args:
            text (str): Text to be drawn.
            font (:class:`~PIL.ImageFont.ImageFont`): Font familly to be used.
            margin (int): Margin to be used around the text.

        Returns:
            tuple: A tuple representing the dimensions of the label as ``(width, height)`` tuple.

        """
        text_width, text_height = font.getsize(text)
        return text_width + 2 * margin, text_height + 2 * margin

    @staticmethod
    def _compute_label_position(max_x, label_width, max_width):
        """Determine the position of label according to remaining space on right side.

        Args:
            max_x (int): Rightmost value of the record geometry (in pixels).
            label_width (int): Space needed by the label to be fully drawn (in pixels).
            max_width (int): Image width that we can't exceed (in pixels).

        Returns:
            |Position|: The chosen position.

        """
        if (max_x + label_width) > max_width:
            return Position.LEFT
        return Position.RIGHT

    @staticmethod
    def _compute_label_starting_point(geometry, position):
        """Compute the coordinates from which the confidence label should take as a reference.

        Args:
            geometry (|Geometry|): The record reformatted geometry.
            position (|Position|): The agreed position of the confidence label.

        Returns:
            tuple: The coordinates (x, y) to use as a reference.

        """
        if position == Position.RIGHT:
            return geometry.rightmost_coordinate
        return geometry.leftmost_coordinate

    @staticmethod
    def _compute_vertical_margin(min_y, label_height):
        """Compute vertical margin needed to properly draw the confidence label on the image.

        Args:
            min_y (int): Uppermost Y value of the record geometry (in pixels).
            label_height (int): The heights the label needs to be fully drawn.

        Returns:
            int: The needed margin (in pixels).

        """
        return int(max(0., -min_y + label_height / 2.))

    def _compute_label_coordinates(self, geometry, text, font, tile_width):
        """Compute confidence label and text coordinates on the final image.

        Args:
            geometry (|Geometry|): The record reformatted geometry.
            text (str): Text to be drawn.
            font (:class:`~PIL.ImageFont.ImageFont`): Font familly to be used.
            tile_width (int): Final image width (in pixels).

        Returns:
            tuple: Label and text coordinates (in pixels).

        """
        # Compute label size
        width, height = self._compute_label_size(text=text, font=font, margin=self._text_margin)

        # Compute label position
        position = self._compute_label_position(max_x=geometry.max_x,
                                                label_width=1.5 * width,
                                                max_width=tile_width)

        # Now the position is set, get starting point of the label
        x, y = self._compute_label_starting_point(geometry=geometry, position=position)

        # Shift label downward if upper limit is reached (coordinates min_y)
        y_margin = self._compute_vertical_margin(min_y=geometry.min_y, label_height=height)

        # Compute label and text coordinates
        sign = 1 if position == Position.RIGHT else -1

        label_coordinates = [
            (x, y + y_margin),
            (x + sign * height / 2., y - height / 2. + y_margin),
            (x + sign * (height / 2. + width), y - height / 2. + y_margin),
            (x + sign * (height / 2. + width), y + height / 2. + y_margin),
            (x + sign * height / 2., y + height / 2. + y_margin),
        ]

        # We do not want the arrow extremity, so skip first coordinate
        label_min_x, label_min_y = sorted(label_coordinates[1:], key=lambda val: (val[0], val[1]))[0]

        text_coordinates = (label_min_x + self._text_margin, label_min_y + self._text_margin)

        return label_coordinates, text_coordinates

    def draw(self, record, draw):
        """Draw a tag next to the provided |Record| using the provided |Draw|.

        Args:
            record (|Record|): A |Record| on which to attach a tag containing its description.
            draw (|Draw|): A |Draw| instance on which to draw the tag, preferably the |Record| draw instance.

        """
        # Retrieve color to use
        record_color = tuple(record.color.astype('sRGB255').components.astype(int)) + (255,)
        # Re-map coordinates to Pillow format (e.g. [(x, y), (x, y), ...])
        geometry = Geometry(record=record, zoom=self._zoom)

        # Define font and text to use
        text_font = get_default_font(text_size=int(self._text_size * self._zoom))
        if self._descriptor.__descriptor__['type'] == 'categorical':
            translate_dict = {value: key
                              for key, value in self._descriptor.__descriptor__['schema'].items()}
            text_str = \
                '{description}'.format(description=translate_dict[getattr(record, self._descriptor.property_name)])
        else:
            text_str = '{description}'.format(description=getattr(record, self._descriptor.property_name))

        # Compute confidence label coordinates
        label_coordinates, text_coordinates = \
            self._compute_label_coordinates(geometry=geometry, text=text_str, font=text_font,
                                            tile_width=draw.overlay.width)

        # Draw text and tag on overlay
        confidence_color = get_text_color(record_color)
        draw.polygon(points=label_coordinates, fill_color=record_color)
        draw.text(text_coordinates=text_coordinates, text=text_str, font=text_font, fill_color=confidence_color)


class PainterBase(ABC):
    """An abstract base class that defines the basic elements a Painter needs to draw a data point.

    Args:
        plot_centers (bool): Optional. Defaults to ``False``. Plot records centers (instead of full geometry).
        plot_tag (|Descriptor|): Optional. Defaults to ``None``. Besides the geometry, display a |Record|
            description in a tag attached to the |Record|.

            .. note::

                The |PainterBase| class assumes that each |Record| have already been described by the provided
                |Descriptor|.

        zoom (int): Optional. Defaults to ``1``. Zoom level to use.
        fill (bool): Optional. Default to ``False``. A flag which represents whether to draw filled polygons.
        alpha (int): Optional. Defaults to ``64``. A positive integer (between 0 and 255) that represents the fill
            transparency.

    """

    def __init__(self, plot_centers=False, plot_tag=None, zoom=1, fill=False, alpha=64, **kwargs):
        # Set painter attributes
        self._plot_centers = plot_centers
        self._plot_tag = plot_tag is not None
        self._tag_descriptor = plot_tag
        self._zoom = zoom
        self._fill = fill
        self._alpha = alpha

    @abstractmethod
    def draw(self, data_point):
        """Draw a data point (annotations on a given tile) and return the composed :class:`~PIL.Image.Image`.

        Arguments:
            data_point (|DataPoint|): Data point to be drawn (tile + annotations).

        Raises:
            ValueError: When a record has an invalid geometry type.

        Returns:
            :class:`~PIL.Image.Image`: The composed image (tile with annotations)

        """
        raise NotImplementedError


class Painter(PainterBase):
    """A basic Painter that implements the |PainterBase| class.

    The role of the painter is to aggregate annotations on a given tile, giving to the user
    a meaningful representation of the records.

    Args:
        plot_centers (bool): Optional. Defaults to ``False``. Plot records centers (instead of full geometry).
        plot_tag (|Descriptor|):  Defaults to ``None``. Besides the geometry, display a |Record| description
            in a tag attached to the |Record|.

            .. note::

                The |Painter| class assumes that each |Record| have already been described by the provided |Descriptor|.

        zoom (int): Optional. Defaults to ``1``. Zoom level to use.
        fill (bool): Optional. Default to ``False``. A flag which represents whether to draw filled polygons.
        alpha (int): Optional. Defaults to ``64``. A positive integer (between 0 and 255) that represents the fill
            transparency.

    """

    # CONSTANTS
    MODE = 'RGBA'
    TEXT_MARGIN = 2  # in pixels
    TITLE_HEIGHT = 30  # in pixels
    TITLE_SIZE = 15  # in pixels
    TITLE_BACKGROUND_COLOR = (46, 49, 49)
    TAG_TEXT_SIZE = 11  # in pixels

    def __init__(self, plot_centers=False, plot_tag=None, zoom=1, fill=False, alpha=64, **kwargs):
        super(Painter, self).__init__(plot_centers=plot_centers, plot_tag=plot_tag, zoom=zoom, fill=fill, alpha=alpha)
        self._tag = TagPainter(self._tag_descriptor, text_margin=self.TEXT_MARGIN,
                               text_size=self.TAG_TEXT_SIZE, zoom=self._zoom)

    def _add_title(self, image, title):
        """Add title on top of the given image.

        Args:
            image (:class:`~PIL.Image.Image`): The image to use.
            title (str): The title to draw.

        Returns:
            :class:`~PIL.Image.Image`: The given image with a title.

        """
        # Rescale title height
        title_height = int(self.TITLE_HEIGHT * self._zoom)
        # Compute final image size
        width, height = image.size
        final_image_size = (width, height + title_height)

        # Create image
        draw = Draw(size=final_image_size,
                    zoom=self._zoom,
                    mode=self.MODE,
                    background_color=self.TITLE_BACKGROUND_COLOR)

        # Select font
        text_font = get_default_font(text_size=int(self.TITLE_SIZE * self._zoom))
        text_width, text_height = text_font.getsize(title)
        text_color = get_text_color(self.TITLE_BACKGROUND_COLOR)
        text_coordinates = ((width - text_width) / 2., (title_height - text_height) / 2.)

        # Draw text
        draw.text(text_coordinates=text_coordinates, text=title, font=text_font, fill_color=text_color)

        # Fill empty space with original image
        final_image = draw.overlay
        final_image.paste(im=image, box=(0, title_height))

        return final_image

    def draw(self, data_point):
        """Draw a data point (annotations on a given tile) and return the composed :class:`~PIL.Image.Image`.

        Arguments:
            data_point (|DataPoint|): Data point to be drawn (tile + annotations).

        Raises:
            ValueError: When a record has an invalid geometry type.

        Returns:
            :class:`~PIL.Image.Image`: The composed image (tile with annotations)

        """
        # Get image to show and rescale it, regarding the zoom
        image = PIL.Image.fromarray(np.asarray(data_point.tile)).convert(self.MODE)
        image = image.resize(tuple(int(self._zoom * x) for x in image.size), resample=PIL.Image.NEAREST)

        # Iterate over the records, and draw the appropriate geometry
        for record in data_point.annotation.record_collection.records:

            # Make a blank image for the annotation, initialized to transparent text color
            draw = Draw(size=image.size, zoom=self._zoom, mode=self.MODE, background_color=(255, 255, 255, 0))

            # Retrieve color to use
            record_color = tuple(record.color.astype('sRGB255').components.astype(int)) + (255, )
            record_fill_color = tuple(record.color.astype('sRGB255').components.astype(int)) + (self._alpha,)
            # Re-map coordinates to Pillow format (e.g. [(x, y), (x, y), ...])
            geometry = Geometry(record=record, zoom=self._zoom)
            # Draw proper geometry, according to the record geometry type (Points / Centers / Polygons)
            if record.type == 'Point' or self._plot_centers is True:
                draw.circle(centroid=geometry.centroid, fill_color=record_color)
            elif record.type == 'Polygon':
                if self._fill:
                    draw.polygon(points=geometry.coordinates, fill_color=record_fill_color)
                draw.line(points=geometry.coordinates, fill_color=record_color)
            else:
                raise ValueError('Invalid record geometry: {}. Expect `Polygon` or `Point`.'.format(record.type))

            # Add confidence scores
            if self._plot_tag is True:
                self._tag.draw(record, draw)

            # Merge tile with annotations
            image = PIL.Image.alpha_composite(im1=image, im2=draw.overlay)

        # Add filename as a title
        final_image = self._add_title(image=image, title=str(data_point.tile.filename))

        return final_image
