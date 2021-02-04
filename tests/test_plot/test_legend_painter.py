import numpy as np
import PIL.Image

from playground_plums.plot.engine.legend_painter import LegendPainter, LegendItemDrawer
from playground_plums.plot.engine.color import Color, LightnessColorMap


class TestLegendItemDrawer:
    def test_draw_simple_category(self):
        # Parameters
        name = 'Test'
        fill_color = Color(255, 255, 255, ctype='sRGB255')
        margins = (15, 15)

        drawer = LegendItemDrawer((0, 0, 0), scale=1, margins=margins)
        item_1 = drawer.draw_simple_category(name=name, fill_color=fill_color)

        assert isinstance(item_1, PIL.Image.Image)
        assert item_1.width > 0
        assert item_1.height > 0

        # Change scale (> 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=2, margins=margins)
        item_2 = drawer.draw_simple_category(name=name, fill_color=fill_color)

        assert isinstance(item_2, PIL.Image.Image)
        assert item_2.width > item_1.width
        assert item_2.height > item_1.height

        # Change scale (< 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=0.5, margins=margins)
        item_3 = drawer.draw_simple_category(name=name, fill_color=fill_color)

        assert isinstance(item_3, PIL.Image.Image)
        assert item_1.width > item_3.width
        assert item_1.height > item_3.height

    def test_draw_composite_category(self):
        # Parameters
        category_name = 'Test'
        color_engine_interface = {
            'ship': Color(255, 255, 255, ctype='sRGB255'),
            'car': Color(255, 128, 128, ctype='sRGB255')
        }
        max_category_height = 500
        margins = (10, 10)

        drawer = LegendItemDrawer((0, 0, 0), scale=1, margins=margins)
        item_1 = drawer.draw_composite_category(
            descriptor_name='Name',
            category_name=category_name,
            color_engine_interface=color_engine_interface,
            max_category_height=max_category_height
        )

        assert isinstance(item_1, PIL.Image.Image)
        assert item_1.width > 0
        assert item_1.height > 0

        # Change scale (> 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=2, margins=margins)
        item_2 = drawer.draw_composite_category(
            descriptor_name='Name',
            category_name=category_name,
            color_engine_interface=color_engine_interface,
            max_category_height=max_category_height
        )

        assert isinstance(item_2, PIL.Image.Image)
        assert item_2.width > item_1.width
        assert item_2.height > item_1.height

        # Change scale (< 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=0.5, margins=margins)
        item_3 = drawer.draw_composite_category(
            descriptor_name='Name',
            category_name=category_name,
            color_engine_interface=color_engine_interface,
            max_category_height=max_category_height
        )

        assert isinstance(item_3, PIL.Image.Image)
        assert item_1.width > item_3.width
        assert item_1.height > item_3.height

    def test_outline(self):
        # Parameters
        margins = (10, 10)

        item = PIL.Image.fromarray(np.zeros((100, 200, 3)).astype(np.uint8))

        drawer = LegendItemDrawer((0, 0, 0), scale=1, margins=margins)
        item_with_outline = drawer.draw_outline_with_title(descriptor_name='Name', legend_set_item=item)

        assert isinstance(item_with_outline, PIL.Image.Image)
        assert item.width == item_with_outline.width
        assert item.height == item_with_outline.height

        # Change scale (> 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=2, margins=margins)
        item_with_outline = drawer.draw_outline_with_title(descriptor_name='Name', legend_set_item=item)

        assert isinstance(item_with_outline, PIL.Image.Image)
        assert item.width == item_with_outline.width
        assert item.height == item_with_outline.height

        # Change scale (< 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=0.5, margins=margins)
        item_with_outline = drawer.draw_outline_with_title(descriptor_name='Name', legend_set_item=item)

        assert isinstance(item_with_outline, PIL.Image.Image)
        assert item.width == item_with_outline.width
        assert item.height == item_with_outline.height

    def test_draw_colormap(self):
        # Parameters
        descriptor_name = 'Test'
        color_map = LightnessColorMap(Color(50, 78, 50, ctype='JCh'),
                                      lightness_range=(0.8, 0.8),
                                      chroma_range=(-0.3, -0.1), ctype="sRGB1").discretize(256)
        margins = (15, 15)

        drawer = LegendItemDrawer((0, 0, 0), scale=1, margins=margins)
        item_1 = drawer.draw_colormap(descriptor_name='Name', color_map=color_map, category_name=descriptor_name)

        assert isinstance(item_1, PIL.Image.Image)
        assert item_1.width > 0
        assert item_1.height > 0

        # Change scale (> 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=2, margins=margins)
        item_2 = drawer.draw_colormap(descriptor_name='Name', color_map=color_map, category_name=descriptor_name)

        assert isinstance(item_2, PIL.Image.Image)
        assert item_2.width > item_1.width
        assert item_2.height > item_1.height

        # Change scale (< 1)
        drawer = LegendItemDrawer((0, 0, 0), scale=0.5, margins=margins)
        item_3 = drawer.draw_colormap(descriptor_name='Name', color_map=color_map, category_name=descriptor_name)

        assert isinstance(item_3, PIL.Image.Image)
        assert item_1.width > item_3.width
        assert item_1.height > item_3.height


class TestLegendPainter:
    def test_constructor(self):
        # Parameters
        color_engine_interface = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {
                'ship': Color(255, 255, 255, ctype='sRGB255'),
                'car': Color(255, 128, 128, ctype='sRGB255')
            }
        }
        scale = 1
        axis = 0
        mosaic_size = (500, 500)
        background_color = (0, 0, 0)
        item_margins = (10, 10)
        main_axis_align = 'start'
        minor_axis_align = 'start'

        LegendPainter(
            color_engine_interface=color_engine_interface,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

    def test_draw_items(self):
        # Parameters
        scale = 1
        axis = 0
        mosaic_size = (500, 500)
        background_color = (0, 0, 0)
        item_margins = (10, 10)
        main_axis_align = 'start'
        minor_axis_align = 'start'

        # Test invalid mapping schema
        invalid_color_engine_interface = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {
                'ship': 'Hello'
            }
        }

        painter = LegendPainter(
            color_engine_interface=invalid_color_engine_interface,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        drawer = LegendItemDrawer(background_color=background_color,
                                  scale=scale,
                                  margins=item_margins)

        # Draw items
        items = painter._draw_items(drawer)

        # Checks
        assert isinstance(items, list)
        assert len(items) == 0

        # Single descriptor - categorical
        simple_categorical_interface = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {
                'Ship': Color(26, 188, 156, ctype='sRGB255'),
                'Car': Color(241, 196, 15, ctype='sRGB255'),
                'Truck': Color(41, 128, 185, ctype='sRGB255'),
                'Wind-turbines': Color(236, 240, 241, ctype='sRGB255')
            }
        }
        painter = LegendPainter(
            color_engine_interface=simple_categorical_interface,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        drawer = LegendItemDrawer(background_color=background_color,
                                  scale=scale,
                                  margins=item_margins)

        # Draw items
        items = painter._draw_items(drawer)

        # Checks
        assert isinstance(items, list)
        assert len(items) == 4
        for item in items:
            assert isinstance(item, PIL.Image.Image)

        # Single descriptor - continuous - color map
        simple_continuous_interface_cm = {
            'name': 'Name(Main, Secondary)',
            'type': 'continuous',
            'schema': LightnessColorMap(Color(50, 78, 50, ctype='JCh'),
                                        lightness_range=(0.8, 0.8),
                                        chroma_range=(-0.3, -0.1), ctype="sRGB1").discretize(256)
        }
        painter = LegendPainter(
            color_engine_interface=simple_continuous_interface_cm,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        drawer = LegendItemDrawer(background_color=background_color,
                                  scale=scale,
                                  margins=item_margins)

        # Draw items
        items = painter._draw_items(drawer)

        # Checks
        assert isinstance(items, list)
        assert len(items) == 1
        for item in items:
            assert isinstance(item, PIL.Image.Image)

        # Two descriptors - both categorical
        double_categorical_interface = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {
                'Ship size': {
                    'Small (< 26m)': Color(26, 188, 156, ctype='sRGB255'),
                    'Medium': Color(241, 196, 15, ctype='sRGB255'),
                    'Large (< 100m)': Color(41, 128, 185, ctype='sRGB255')
                },
                'Confidence': {
                    'Little (< 0.5)': Color(26, 188, 156, ctype='sRGB255'),
                    'Strong (>= 0.5)': Color(241, 196, 15, ctype='sRGB255')
                }
            }
        }
        painter = LegendPainter(
            color_engine_interface=double_categorical_interface,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        drawer = LegendItemDrawer(background_color=background_color,
                                  scale=scale,
                                  margins=item_margins)

        # Draw items
        items = painter._draw_items(drawer)

        # Checks
        assert isinstance(items, list)
        assert len(items) == 2
        for item in items:
            assert isinstance(item, PIL.Image.Image)

        # One descriptor - categorical / color map
        double_categorical_interface_cm = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {
                'Confidence': LightnessColorMap(Color(50, 78, 50, ctype='JCh'),
                                                lightness_range=(0.8, 0.8),
                                                chroma_range=(-0.3, -0.1), ctype="sRGB1").discretize(256),
                'Size': LightnessColorMap(Color(50, 78, 270, ctype='JCh'),
                                          lightness_range=(0.8, 0.8),
                                          chroma_range=(-0.3, -0.1), ctype="sRGB1").discretize(256)
            }
        }

        painter = LegendPainter(
            color_engine_interface=double_categorical_interface_cm,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        drawer = LegendItemDrawer(background_color=background_color,
                                  scale=scale,
                                  margins=item_margins)

        # Draw items
        items = painter._draw_items(drawer)

        # Checks
        assert isinstance(items, list)
        assert len(items) == 2
        for item in items:
            assert isinstance(item, PIL.Image.Image)

    def test_draw(self):
        # Parameters
        color_engine_interface = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {
                'size': {
                    'small': Color(255, 0, 0, ctype='sRGB255'),
                    'medium': Color(255, 0, 0, ctype='sRGB255'),
                    'large': Color(255, 0, 0, ctype='sRGB255')
                }
            }
        }
        scale = 1
        axis = 0
        mosaic_size = (500, 500)
        background_color = (0, 0, 0)
        item_margins = (10, 10)
        main_axis_align = 'start'
        minor_axis_align = 'start'

        painter = LegendPainter(
            color_engine_interface=color_engine_interface,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        # Draw legend
        legend = painter.draw()

        # Checks
        assert isinstance(legend, PIL.Image.Image)
        assert legend.height == 500
        assert legend.width > 0

        # Empty Color Engine schema -> means empty RecordCollection

        # Parameters
        color_engine_interface = {
            'name': 'Name(Main, Secondary)',
            'type': 'categorical',
            'schema': {}
        }

        painter = LegendPainter(
            color_engine_interface=color_engine_interface,
            scale=scale,
            axis=axis,
            mosaic_size=mosaic_size,
            background_color=background_color,
            item_margins=item_margins,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        # Draw legend
        legend = painter.draw()

        # Checks
        assert isinstance(legend, PIL.Image.Image)
        assert legend.height == 0
        assert legend.width == 0
