from abc import abstractmethod, ABC
from operator import itemgetter

# Third-party libraries
import PIL.Image
import PIL.ImageDraw

from plums.commons import DataPoint
from plums.plot.engine.painter import Draw, Painter
from plums.plot.engine.legend_painter import LegendPainter
from plums.plot.engine.utils import get_default_font, get_text_color
from plums.plot.engine.position_generator import (
    AdaptiveImagePositionGenerator, LayoutImagePositionGenerator, SimpleImagePositionGenerator
)


class CompositorBase(ABC):
    """An abstract class that represents the minimum interface a Compositor needs.

    Args:
        data_points (array-like): Two formats are allowed: a 2D array-like of |DataPoint|-like collection of |Tile|
            and |RecordCollection| to be drawn. Each line of the 2D array-like is expected to correspond to a line
            layout in the final mosaic cell. Or a 1D array-like of |DataPoint|. In that case, the data points will
            be placed side by side, forming a mosaic of tiles, with rows of same length.
        color_engine_interface (dict): A mapping of categories with colors/colormaps to draw.

    Raises:
        AttributeError: When ``data_points`` is not a list/tuple or a nested list/tuple of data points.

    """

    def __init__(self, data_points, color_engine_interface):

        # Sanity check
        if not isinstance(data_points, (list, tuple)):
            raise AttributeError('`data_points` should either be a list/tuple, but given {}'.format(type(data_points)))

        if not all(isinstance(value, (list, tuple, DataPoint)) for value in data_points):
            raise AttributeError('`data_points` should either be a list/tuple, a list/tuple'
                                 ' of lists/tuples of datapoints.')

        # Init data points list
        self._data_points = data_points
        self._color_engine_interface = color_engine_interface

    @abstractmethod
    def plot(self, n_cols=20, margins=(5, 5), background_color=(127, 127, 120),
             title=None, title_size=25, center=True, **kwargs):
        """Create a mosaic of the different accumulated datapoints, with a legend to identify colors meaning.

        Args:
            n_cols (int): Optional. Defaults to ``20``. Number of data points per line to not exceed
                (if 1D array-like of |DataPoint|).
            margins (tuple): Optional. Defaults to ``(5, 5)``. Margin to use between each image of the mosaic.
            background_color (tuple): Optional. Defaults to ``(127, 127, 120)``. Background color to use for the
                                                       mosaic.
            title (str): Optional. Defaults to ``None``. A title to place on top of the mosaic.
            title_size (int): Optional. Defaults to ``25``. Font size of the title (in pixels).
            center (bool): Optional. Defaults to ``True``. Center the last line of data points.
                (if 1D array-like of |DataPoint|).
            kwargs (dict): These parameters are passed on to the constructors of the |Painter| and the |LegendPainter|.

        Raises:
            NotImplementedError: Since it is an abstract method, you have to implement it.

        """
        raise NotImplementedError


class Compositor(CompositorBase):
    """A class that draws a complete mosaic of the given data points, with optionally a title and a meaningful legend.

    The |Compositor| aims to produce a fashionable way of visualising several |DataPoint| side-to-side.
    If a **flattened** list of data points is provided, the data points will be placed in a successive way, filling
    a grid (cf |SimpleImagePositionGenerator| or |AdaptiveImagePositionGenerator|).
    If a **2D array-like** of data points is given, we produce as many lines in the final mosaic as the length of the
    provided list. The lines may be of different sizes, the items are centered (cf |LayoutImagePositionGenerator|).
    The size of the mosaic will just adapt, depending on the chosen layout.

    Args:
        data_points (array-like): Two formats are allowed: a 2D array-like of |DataPoint|-like collection of |Tile|
            and |RecordCollection| to be drawn. Each line of the 2D array-like is expected to correspond to a line
            layout in the final mosaic cell. Or a 1D array-like of |DataPoint|. In that case, the data points will
            be placed side by side, forming a mosaic of tiles, with rows of same length.
        color_engine_interface (dict): A mapping of categories with |Color|/|ColorMap| to draw.

    Raises:
        AttributeError: When ``data_points`` is not a list/tuple or a nested list/tuple of data points.

    """

    # CONSTANTS
    MODE = 'RGBA'

    def __init__(self, data_points, color_engine_interface):
        super(Compositor, self).__init__(data_points=data_points, color_engine_interface=color_engine_interface)

    def _add_title(self, mosaic, title, background_color, title_size):
        """Add a title on top of the given image.

        Args:
            mosaic (:class:`~PIL.Image.Image`): The mosaic to use.
            title (str): The title to draw.
            background_color (tuple): Title background color to use.
            title_size (int): Font size of the title (in pixels).

        Returns:
            :class:`~PIL.Image.Image`: The given mosaic with a title.

        """
        # Compute the height needed above the image to correctly draw the title
        title_height = 2 * title_size
        # Compute new image size
        new_image_size = (mosaic.width, mosaic.height + title_height)
        # Draw text on new image
        draw = Draw(size=new_image_size,
                    zoom=1,
                    mode=self.MODE,
                    background_color=background_color)

        # Select font
        text_font = get_default_font(text_size=title_size)
        text_width, text_height = text_font.getsize(title)
        text_color = get_text_color(background_color=background_color)
        text_coordinates = ((mosaic.width - text_width) / 2., (title_height - text_height) / 2.)

        # Draw text
        draw.text(text_coordinates=text_coordinates, text=title, font=text_font, fill_color=text_color)

        # Fill empty space with original image
        final_image = draw.overlay
        final_image.paste(im=mosaic, box=(0, title_height))

        return final_image

    def _add_legend(self, mosaic, background_color, **kwargs):
        """Add a legend to the given mosaic, and place it according the axis defined in the legend parameters.

        Args:
            mosaic (:class:`~PIL.Image.Image`): The mosaic to use.
            background_color (tuple): Title background color to use.
            kwargs (dict): These parameters are passed on to the constructor of the |LegendPainter|.

        Returns:
            :class:`~PIL.Image.Image`: The given mosaic with a legend.

        """
        # Init and draw the legend
        legend_painter_ = LegendPainter(color_engine_interface=self._color_engine_interface,
                                        mosaic_size=mosaic.size,
                                        background_color=background_color, **kwargs)
        legend = legend_painter_.draw()

        # Compute new image size
        if legend.width == mosaic.width:
            new_mosaic_size = (mosaic.width, mosaic.height + legend.height)
        else:
            new_mosaic_size = (mosaic.width + legend.width, mosaic.height)

        # Create final mosaic
        new_mosaic = PIL.Image.new(mode=self.MODE, size=new_mosaic_size, color=background_color)
        new_mosaic.paste(im=mosaic, box=(0, 0))

        if legend.width == mosaic.width:
            new_mosaic.paste(im=legend, box=(0, mosaic.height))
        else:
            new_mosaic.paste(im=legend, box=(mosaic.width, 0))

        return new_mosaic

    def plot(self, n_cols=20, margins=(5, 5), background_color=(127, 127, 120),
             title=None, title_size=25, center=True, **kwargs):
        """Create a mosaic of the different accumulated data points, with a legend to identify colors meaning.

        Args:
            n_cols (int): Optional. Defaults to ``20``. Number of data points per line to not exceed
                (if 1D array-like of |DataPoint|).
            margins (tuple): Optional. Defaults to ``(5, 5)``. Margin to use between each image of the mosaic.
            background_color (tuple): Optional. Defaults to ``(127, 127, 120)``. Background color to use for the
                                                       mosaic.
            title (str): Optional. Defaults to ``None``. A title to place on top of the mosaic.
            title_size (int): Optional. Defaults to ``25``. Font size of the title (in pixels).
            center (bool): Optional. Defaults to ``True``. Center the last line of data points.
                (if 1D array-like of |DataPoint|).
            kwargs (dict): These parameters are passed on to the constructors of the |Painter| and the |LegendPainter|.

        Returns:
            :class:`~PIL.Image`: The final mosaic containing the painted images, a legend, and optionally a title.

        """
        # Flatten data points list if necessary, but keep original structure
        data_points = self._data_points
        nested_lists = isinstance(data_points[0], (list, tuple))
        if nested_lists is True:
            data_points = [point for points in data_points for point in points]

        # Draw image for each datapoint in the list
        painter_ = Painter(**kwargs)
        images = [painter_.draw(datapoint) for datapoint in data_points]

        # Compute max image size we have
        sizes = [image.size for image in images]
        max_image_width = max(sizes, key=itemgetter(0))[0]
        max_image_height = max(sizes, key=itemgetter(1))[1]

        # Init the appropriate position generator
        if nested_lists is True:
            positions_generator = LayoutImagePositionGenerator(data_points=self._data_points,
                                                               margins=margins,
                                                               max_image_size=(max_image_width, max_image_height))
        else:
            if center is True:
                positions_generator = AdaptiveImagePositionGenerator(data_points=data_points,
                                                                     max_cols=n_cols,
                                                                     margins=margins,
                                                                     max_image_size=(max_image_width, max_image_height))
            else:
                positions_generator = SimpleImagePositionGenerator(data_points=data_points,
                                                                   max_cols=n_cols,
                                                                   margins=margins,
                                                                   max_image_size=(max_image_width, max_image_height))

        # Init mosaic image
        mosaic = PIL.Image.new(mode=self.MODE, size=positions_generator.mosaic_size, color=background_color)

        # Paste images on their positions onto the mosaic
        for index, top_left_corner in enumerate(list(positions_generator)):
            top_left_corner = tuple(map(lambda x: int(x), top_left_corner))
            mosaic.paste(im=images[index], box=top_left_corner)

        # Add title if necessary
        if title is not None:
            mosaic = self._add_title(mosaic=mosaic, title=str(title),
                                     background_color=background_color, title_size=title_size)

        # Add a legend which maps color to descriptor names
        mosaic = self._add_legend(mosaic=mosaic, background_color=background_color, **kwargs)

        return mosaic
