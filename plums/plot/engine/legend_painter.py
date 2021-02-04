import re
from abc import abstractmethod, ABC

import numpy as np
import PIL.Image
import PIL.ImageDraw

from plums.commons import Record, RecordCollection
from plums.plot.engine.painter import TagPainter, Draw
from plums.plot.engine.color import Color, color_map
from plums.plot.engine.position_generator import LegendItemPositionGenerator
from plums.plot.engine.utils import get_default_font, get_outline_color, get_text_color
from plums.plot.engine.descriptor import Confidence, CategoricalDescriptor


class LegendItemDrawer(object):
    """Class that draw legend items, depending on their types.

    Items either be:

    * **categorical**: item would look like a colored box with the name of the category next to it.
    * **nested categorical**: a category name with several categorical items under it.
    * **continuous**: a color map with its range and, optionally, a descriptor name.

    Args:
        background_color (tuple): Legend background color (``RGB`` or ``RGBA`` format).
        scale (float): Optional. Defaults to ``1.0`` Scale to use, regarding the default dimensions used.
        margins (tuple): Optional. Defaults to ``(15, 15)``. Margins around the item (left/right and top/bottom).

    """

    # Default parameters

    # General
    MODE = 'RGBA'
    ITEM_BACKGROUND_COLOR = (255, 255, 255, 0)  # RGBA

    # Main categories
    BOX_DIMENSIONS = (80, 40)  # in pixels
    BOX_OUTLINE_WIDTH = 1  # in pixels
    SEPARATION_DISTANCE = 20  # in pixels
    TEXT_SIZE = 20  # in pixels

    # Outline
    OUTLINE_HEADER_MARGIN = 5  # in pixel

    # Sub categories
    SUB_ITEMS_AXIS = 0  # either 0 (vertical) or 1 (horizontal)
    SUB_ITEM_SCALE = 0.7
    SUB_ITEM_OFFSET = 20  # in pixels

    # Color maps
    COLOR_MAP_DIMENSIONS = (200, 50)  # in pixels
    COLOR_MAP_MARGIN = 8  # in pixels
    COLOR_MAP_TITLE_HEIGHT = 18  # in pixels
    COLOR_MAP_TEXT_HEIGHT = 13  # in pixels

    def __init__(self, background_color, scale=1., margins=(15, 15)):
        self._background_color = background_color
        self._scale = scale
        self._margins = margins

    def draw_simple_category(self, name, fill_color, scale=None, margins=None):
        """Draw a simple category item: a colored box with a category name next to it.

        Args:
            name (str): Category name to draw.
            fill_color (|Color|): Color of the category.
            scale (float): Optional. Defaults to ``None`` Scale to use, regarding the default dimensions used.
            margins (tuple): Optional. Defaults to ``None``. Margins around the item (left/right and top/bottom).

        Returns:
            :class:`~PIL.Image.Image`: A simple categorical item.

        """
        # Override default scale and margins (for composite category)
        scale = float(scale) if scale is not None else self._scale
        margins = tuple(margins) if margins is not None else self._margins
        # Scale dimensions
        text_size = int(self.TEXT_SIZE * scale)
        separation_distance = int(self.SEPARATION_DISTANCE * scale)
        box_width, box_height = tuple(map(lambda x: int(x * scale), self.BOX_DIMENSIONS))

        # Category parameters (coordinates, color)
        box_coordinates = [margins, (box_width + margins[0], box_height + margins[1])]
        box_fill_color = tuple(fill_color.astype('sRGB255').components.astype(int))
        box_outline_color = get_text_color(self._background_color)

        # Text parameters (font, dimensions, color, coordinates)
        text_font = get_default_font(text_size=text_size)
        text_width, text_height = text_font.getsize(name)
        text_color = get_text_color(self._background_color)
        text_coordinates = (box_width + separation_distance + margins[0],
                            int((box_height - text_height) / 2) + margins[1])

        # Legend item parameters
        item_size = (box_width + separation_distance + text_width + 2 * self.BOX_OUTLINE_WIDTH + 2 * margins[0],
                     box_height + 2 * self.BOX_OUTLINE_WIDTH + 2 * margins[1])

        # Create legend item (colored rectangle + category name next to it)
        item = PIL.Image.new(mode=self.MODE, size=item_size, color=self.ITEM_BACKGROUND_COLOR)
        draw = PIL.ImageDraw.Draw(item)

        # Draw item (box + text on left side)
        draw.rectangle(xy=box_coordinates, fill=box_fill_color, outline=box_outline_color, width=self.BOX_OUTLINE_WIDTH)
        draw.text(xy=text_coordinates, text=name, fill=text_color, font=text_font)

        return item

    def draw_composite_category(self, descriptor_name, category_name, color_engine_interface, max_category_height):
        """Draw a nested category item: a category name with several categorical items under it.

        Args:
            descriptor_name (str): Name of the |CategoricalDescriptor| used.
            category_name (str): Name of the primary category.
            color_engine_interface (dict): Interface of the |ColorEngine| object. (key = category name,
                value = color/colormaps).
            max_category_height (int): Height of the item to not exceed, in pixels.

        Returns:
            :class:`~PIL.Image.Image`: A nested categorical item.

        """
        # Scale dimensions
        text_size = int(self.TEXT_SIZE * self._scale)
        sub_item_margins = tuple(map(lambda x: int(x * self.SUB_ITEM_SCALE * self._scale), self._margins))

        # Create sub categories
        items = [
            self.draw_simple_category(name=name, fill_color=fill_color,
                                      scale=self.SUB_ITEM_SCALE, margins=sub_item_margins)
            for name, fill_color in sorted(color_engine_interface.items(), key=lambda x: x[0])
        ]

        # Main category parameters
        text_font = get_default_font(text_size=text_size)
        text_width, text_height = text_font.getsize(category_name)
        text_color = get_text_color(self._background_color)
        text_coordinates = (self._margins[0], self._margins[1])
        offset_y = int((self.BOX_DIMENSIONS[1] - 2 * text_height) / 2) + self._margins[1]

        # Compute final PIL Image dimensions
        item_sizes = [item.size for item in items]
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=self.SUB_ITEMS_AXIS,
            max_size_along_axis=max_category_height,
            main_axis_align='start',
            minor_axis_align='start'
        )

        # Compute position for each item
        items_with_position = [(items[i], position) for i, position in enumerate(list(position_generator))]

        # Compute legend size
        item_size = (
            position_generator.legend_size[0] + self.SUB_ITEM_OFFSET + 2 * self._margins[0],
            items_with_position[-1][1][1] + item_sizes[-1][1] + text_height + 2 * self._margins[1] + offset_y
        )

        # Create legend
        item = PIL.Image.new(mode=self.MODE, size=item_size, color=self.ITEM_BACKGROUND_COLOR)
        draw = PIL.ImageDraw.Draw(item)
        draw.text(xy=text_coordinates, text=category_name, fill=text_color, font=text_font)

        # Add items to the legend image
        for item_, position_ in items_with_position:
            top_left_corner = (position_[0] + self.SUB_ITEM_OFFSET + self._margins[0],
                               position_[1] + text_height + self._margins[1] + offset_y)
            item.alpha_composite(im=item_, dest=top_left_corner)

        self.draw_outline_with_title(descriptor_name,
                                     item,
                                     scale=self.SUB_ITEM_SCALE,
                                     margins=(self.SUB_ITEM_OFFSET, text_size + offset_y, 0, 0, 0))

        return item

    def draw_outline_with_title(self, descriptor_name, legend_set_item, scale=None, margins=(0, 0, 0, 0)):
        """Draw a set of category item: a descriptor name with a border and several categorical items under it.

        Args:
            descriptor_name (str): Name of the |CategoricalDescriptor| used.
            legend_set_item (:class:`~PIL.Image.Image`): A nested legend categorical set item.
            scale (float): Optional. Defaults to ``None`` Scale to use, regarding the default dimensions used.
            margins (tuple): Optional. Default to (0, 0, 0, 0). Optional margin in between legend item exterior and
                outline start coordinates

        Returns:
            :class:`~PIL.Image.Image`: A nested categorical item.

        """
        scale = float(scale) if scale is not None else self._scale
        # Scale dimensions
        text_size = int(self.TEXT_SIZE * scale)
        text_margin = int(self.OUTLINE_HEADER_MARGIN * scale)

        # Compute legend size
        item_size = legend_set_item.size

        # Main category parameters
        text_font = get_default_font(text_size=text_size)
        text_width, text_height = text_font.getsize(descriptor_name)
        outline_color = get_outline_color(self._background_color)
        text_coordinates = (item_size[0] - text_width - margins[2], margins[1])

        # Create legend
        item = legend_set_item
        draw = PIL.ImageDraw.Draw(item)
        draw.rectangle(xy=(0.15 * text_width + margins[0],
                           0.5 * text_height + margins[1],
                           item_size[0] - margins[2] - 0.15 * text_width - 1,
                           item_size[1] - 0.5 * text_height - margins[3] - 1),
                       outline=outline_color)  # RGBA
        draw.rectangle(xy=((text_coordinates[0] - text_margin,
                            text_coordinates[1] - text_margin),
                           (text_coordinates[0] + text_width + text_margin,
                            text_coordinates[1] + text_height + text_margin)),
                       fill=self._background_color)  # RGBA
        draw.text(xy=text_coordinates, text=descriptor_name, fill=outline_color, font=text_font)

        return item

    def draw_colormap(self, descriptor_name, color_map, category_name=None):
        """Draw a color map: a color map with its range and descriptor name (optional).

        Args:
            descriptor_name (str): The name of the descriptor.
            color_map (|ContinuousColorMap|): A |ContinuousColorMap| which vary the the color around a
                reference |Color|.
            category_name (str): Optional. Defaults to ``None``. The name of the category.

        Returns:
            :class:`~PIL.Image.Image`: The computed colormap item.

        """
        # Rescale dimensions
        box_width = int(self.COLOR_MAP_DIMENSIONS[0] * self._scale)
        box_height = int(self.COLOR_MAP_DIMENSIONS[1] * self._scale)
        text_margin = int(self.COLOR_MAP_MARGIN * self._scale)
        text_height = int(self.COLOR_MAP_TEXT_HEIGHT * self._scale)
        title_height = int(self.COLOR_MAP_TITLE_HEIGHT * self._scale) if category_name is not None else 0

        # Text parameters
        start, end = color_map.range
        avg = (start + end) / 2.
        start_str = str(round(start, 2))
        avg_str = str(round(avg, 2))
        end_str = str(round(end, 2))

        text_color = get_text_color(self._background_color)
        text_font = get_default_font(text_size=text_height)

        avg_text_width, _ = text_font.getsize(avg_str)
        end_text_width, _ = text_font.getsize(end_str)
        name_text_width, _ = text_font.getsize(str(descriptor_name))

        start_coordinates = (self._margins[0], title_height + box_height + 2 * text_margin + self._margins[1])
        avg_coordinates = (self._margins[0] + int((box_width - avg_text_width) / 2.),
                           title_height + box_height + 2 * text_margin + self._margins[1])
        end_coordinates = (box_width - end_text_width + self._margins[0],
                           title_height + box_height + 2 * text_margin + self._margins[1])

        name_coordinates = (self._margins[0] + int((box_width - name_text_width) / 2.),
                            title_height + box_height + 4 * text_margin + self._margins[1])

        # Item parameters
        item_size = (box_width + 2 * self._margins[0],
                     title_height + 2 * text_height + box_height + text_margin + 2 * (self._margins[1] + text_margin))
        box_coordinates = (self._margins[0], title_height + text_margin + self._margins[1])

        # Create colored array
        array = np.tile(np.linspace(start, end, box_width), (box_height, 1))
        color_array = np.clip(color_map.astype('sRGB1')(array), 0., 1.)
        color_array = (color_array * 255).astype(np.uint8)

        # Create PIL image
        item = PIL.Image.new(mode=self.MODE, size=item_size, color=self.ITEM_BACKGROUND_COLOR)
        item.paste(im=PIL.Image.fromarray(color_array, mode='RGB'), box=box_coordinates)

        # Draw range values (min, avg & max) under color map
        draw = PIL.ImageDraw.Draw(item)
        if category_name is not None:
            title_font = get_default_font(text_size=title_height)
            draw.text(xy=self._margins, text=str(category_name), fill=text_color, font=title_font)
        draw.text(xy=start_coordinates, text=start_str, fill=text_color, font=text_font)
        draw.text(xy=avg_coordinates, text=avg_str, fill=text_color, font=text_font)
        draw.text(xy=end_coordinates, text=end_str, fill=text_color, font=text_font)
        draw.text(xy=name_coordinates, text=str(descriptor_name), fill=text_color, font=text_font)

        return item


class LegendPainterBase(ABC):
    """An abstract base class that defines the interface a legend painter should implement.

    Args:
        color_engine_interface (dict): A mapping of categories with colors/colormaps to draw.
        mosaic_size (tuple): The size, in pixels, of the mosaic computed by the |Compositor|.
        scale (float): Optional. Defaults to ``1.0``. Scale to use, regarding the default dimensions used.
        axis (int): Optional. Defaults to ``0``. Main direction of the legend (**0** = vertically, **1** = horizontally)
        background_color (tuple): Optional. Defaults to ``(255, 255, 255)``. Legend background color
            (``RGB`` or ``RGBA`` format).
        item_margins (tuple): Optional. Defaults to ``(10, 10)``. Margins around the item (left/right and top/bottom).
        main_axis_align (str): Optional. Defaults to ``start``. Alignment of the item in its cell along the main axis.
        minor_axis_align (str): Optional. Defaults to ``start``. Alignment of the item in its cell along the minor axis.

    """

    def __init__(self, color_engine_interface, mosaic_size, scale=1.0, axis=0, background_color=(255, 255, 255),
                 item_margins=(10, 10), main_axis_align='start', minor_axis_align='start', **kwargs):

        # Set compiled descriptor name regex
        self._descriptor_name_regex = re.compile(r'[\w]+\(([a-zA-Z_ ]+)(?:, ([a-zA-Z_ ]+))?\)')

        # Set legend painter attributes
        self._color_engine_interface = color_engine_interface
        self._scale = scale
        self._background_color = background_color
        self._axis = axis
        self._item_margins = item_margins
        self._main_axis_align = main_axis_align
        self._minor_axis_align = minor_axis_align

        # Set tag legend attributes
        self._plot_tag = kwargs.get('plot_confidences') if kwargs.get('plot_confidences') is not None \
            else kwargs.get('plot_tag') is not None
        self._tag_descriptor = kwargs.get('plot_tag') if kwargs.get('plot_confidences') is None else Confidence()

        # Computed property
        self._max_size_along_axis = mosaic_size[1] if axis == 0 else mosaic_size[0]

    @property
    def _primary_descriptor_name(self):
        return self._descriptor_name_regex.search(self._color_engine_interface['name']).group(1)

    @property
    def _secondary_descriptor_name(self):
        return self._descriptor_name_regex.search(self._color_engine_interface['name']).group(2)

    @abstractmethod
    def draw(self):
        """Draw the legend, along the given axis.

        The generated legend is a grid with each cell having the dimensions of the biggest item to draw.
        The grid is then filled along the main axis first. The size of the legend along the
        main axis is fixed while the size along the minor one is variable.

        Returns:
            :class:`~PIL.Image.Image`: The output legend.

        """
        raise NotImplementedError


class LegendPainter(LegendPainterBase):
    """Class that draws a legend from a given color mapping.

    The legend could be drawn either **horizontally** or **vertically**. Moreover, the item could occupy different
    positions in its cell.

    Args:
        color_engine_interface (dict): A mapping of categories with colors/colormaps to draw.
        mosaic_size (tuple): The size, in pixels, of the mosaic computed by the |Compositor|.
        scale (float): Optional. Defaults to ``1.0``. Scale to use, regarding the default dimensions used.
        axis (int): Optional. Defaults to ``0``. Main direction of the legend (**0** = vertically, **1** = horizontally)
        background_color (tuple): Optional. Defaults to ``(255, 255, 255)``. Legend background color
            (``RGB`` or ``RGBA`` format).
        item_margins (tuple): Optional. Defaults to ``(10, 10)``. Margins around the item (left/right and top/bottom).
        main_axis_align (str): Optional. Defaults to ``start``. Alignment of the item in its cell along the main axis.
        minor_axis_align (str): Optional. Defaults to ``start``. Alignment of the item in its cell along the minor axis.

    """

    def __init__(self, color_engine_interface, mosaic_size, scale=1.0, axis=0, background_color=(255, 255, 255),
                 item_margins=(10, 10), main_axis_align='start', minor_axis_align='start', **kwargs):
        super(LegendPainter, self).__init__(color_engine_interface=color_engine_interface, scale=scale, axis=axis,
                                            mosaic_size=mosaic_size, background_color=background_color,
                                            item_margins=item_margins, main_axis_align=main_axis_align,
                                            minor_axis_align=minor_axis_align, **kwargs)

    def _draw_items(self, drawer):
        """Draw items depending on their type (categorical, continuous, etc.).

        Returns:
            list: List of the drawn items.

        """
        # Depending on the type
        items = []
        if self._color_engine_interface['type'] == 'categorical':
            for name, value in sorted(self._color_engine_interface['schema'].items(), key=lambda x: x[0]):
                # Depending on the type, draw corresponding item
                if isinstance(value, Color):
                    item = drawer.draw_simple_category(name=name, fill_color=value)
                    items.append(item)

                elif isinstance(value, dict):
                    item = drawer.draw_composite_category(
                        descriptor_name=self._secondary_descriptor_name,
                        category_name=name,
                        color_engine_interface=value,
                        max_category_height=self._max_size_along_axis - self._item_margins[1],
                    )
                    items.append(item)

                elif isinstance(value, color_map.ColorMap):
                    item = drawer.draw_colormap(color_map=value, category_name=name,
                                                descriptor_name=self._secondary_descriptor_name)
                    items.append(item)

        elif self._color_engine_interface['type'] == 'continuous':
            if isinstance(self._color_engine_interface['schema'], color_map.ColorMap):
                # Draw given colormap with PIL
                item = drawer.draw_colormap(color_map=self._color_engine_interface['schema'],
                                            descriptor_name=self._primary_descriptor_name)
                items.append(item)

        return items

    def draw(self):
        """Draw the legend, along the given axis.

        The generated legend is a grid with each cell having the dimensions of the biggest item to draw.
        The grid is then filled along the main axis first. The size of the legend along the
        main axis is fixed while the size along the minor one is variable.

        Returns:
            :class:`~PIL.Image.Image`: The output legend.

        """
        # Init legend item drawer
        drawer = LegendItemDrawer(background_color=self._background_color,
                                  scale=self._scale,
                                  margins=self._item_margins)

        margin = int(drawer.TEXT_SIZE * self._scale)
        # Draw all items
        items = self._draw_items(drawer)

        # No items to draw means empty legend
        if not items:
            return PIL.Image.new(mode='RGBA', size=(0, 0))

        # Compute position for each item
        position_generator = LegendItemPositionGenerator(
            items_sizes=[item.size for item in items],
            axis=self._axis,
            max_size_along_axis=self._max_size_along_axis - 2 * margin,
            main_axis_align=self._main_axis_align,
            minor_axis_align=self._minor_axis_align
        )
        items_with_position = [(items[i], position) for i, position in enumerate(list(position_generator))]

        # Prepare tag if needed
        upper_margin = 0
        draw = None
        if self._plot_tag:
            upper_margin = int((2 * 2 + 0.75 * drawer.TEXT_SIZE + 2 * 4) * self._scale)
            # Prepare record and descriptor
            tag_descriptor = CategoricalDescriptor(name='name')
            tag_record = Record(coordinates=[[[0.5 * margin, int(upper_margin / 2)],
                                              [0.5 * margin, int(upper_margin / 2) + 1],
                                              [0.5 * margin + 1, int(upper_margin / 2) + 1],
                                              [0.5 * margin + 1, int(upper_margin / 2)],
                                              [0.5 * margin, int(upper_margin / 2)]]],
                                labels=['Dummy'],
                                name=self._tag_descriptor.__descriptor__['name'],
                                categorical_descriptor_name=0.5,
                                color=Color(*get_outline_color(self._background_color), ctype='sRGB255'))
            tag_descriptor.update(RecordCollection(tag_record))
            # Prepare TagPainter and Draw
            tag_painter = TagPainter(tag_descriptor,
                                     text_margin=2 * self._scale,
                                     text_size=0.75 * drawer.TEXT_SIZE * self._scale)
            draw = Draw(size=(int(position_generator.legend_size[0] + 2 * margin), upper_margin),
                        zoom=1,
                        mode='RGBA',
                        background_color=self._background_color)
            # Draw legend tag
            tag_painter.draw(tag_record, draw=draw)

        # Create legend
        legend = PIL.Image.new(mode='RGBA',
                               size=(position_generator.legend_size[0] + 2 * margin,
                                     position_generator.legend_size[1] + 2 * margin + upper_margin),
                               color=self._background_color)

        for item, position in items_with_position:
            legend.alpha_composite(im=item, dest=(position[0] + margin,
                                                  position[1] + margin + upper_margin))

        if draw is not None:
            legend.alpha_composite(im=draw.overlay, dest=(0, 4))

        if self._color_engine_interface['type'] == 'categorical':
            bottom_margin = position_generator.legend_size[1] - position_generator.true_legend_size[1]
            drawer.draw_outline_with_title(self._primary_descriptor_name, legend, margins=(0, upper_margin,
                                                                                           0, bottom_margin))

        return legend
