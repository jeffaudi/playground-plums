import numpy as np
import pytest

from playground_plums.commons import TileWrapper, DataPoint, RecordCollection, Record, Annotation
from playground_plums.plot.engine.color import Color
from playground_plums.plot.engine.compositor import Compositor


class TestCompositor:
    def test_constructor(self):
        # Create data points
        records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ['car'], confidence=0.9),
        ]
        records_collection = RecordCollection(*records)
        annotation = Annotation(records_collection)
        tile = TileWrapper(np.zeros((100, 100, 3)), filename='test.png')
        tile_2 = TileWrapper(np.zeros((200, 200, 3)), filename='test_2.png')
        data_point = DataPoint(tile, annotation)
        data_point_2 = DataPoint(tile_2, annotation)

        # Color engine interface
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

        # Valid datapoints
        data_points_1 = [data_point]
        data_points_2 = [data_point, data_point_2]
        data_points_3 = (data_point_2, )
        data_points_4 = (data_point, data_point_2)
        data_points_5 = [data_points_1]
        data_points_6 = [data_points_3]
        data_points_7 = (data_points_2, )
        data_points_8 = (data_points_4, )

        # Invalid data points
        inv_data_points_1 = None
        inv_data_points_2 = ['test']
        inv_data_points_3 = ('test', data_point)

        # Checks
        Compositor(data_points=data_points_1, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_2, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_3, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_4, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_5, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_6, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_7, color_engine_interface=simple_categorical_interface)
        Compositor(data_points=data_points_8, color_engine_interface=simple_categorical_interface)

        with pytest.raises(AttributeError):
            Compositor(data_points=inv_data_points_1, color_engine_interface=simple_categorical_interface)

        with pytest.raises(AttributeError):
            Compositor(data_points=inv_data_points_2, color_engine_interface=simple_categorical_interface)

        with pytest.raises(AttributeError):
            Compositor(data_points=inv_data_points_3, color_engine_interface=simple_categorical_interface)

    def test_add_title(self):
        import PIL.Image
        import numpy as np

        # Create data points
        records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ['car'], confidence=0.9),
        ]
        records_collection = RecordCollection(*records)
        annotation = Annotation(records_collection)
        tile = TileWrapper(np.zeros((100, 100, 3)), filename='test.png')
        data_point = DataPoint(tile, annotation)
        data_points = [data_point]

        # Color engine interface
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

        # Parameters
        width, height = (300, 300)
        background_color = (0, 0, 0)
        title_size = 25

        # Init compositor
        _compositor = Compositor(data_points=data_points,
                                 color_engine_interface=simple_categorical_interface)

        image = PIL.Image.fromarray(np.zeros((width, height)))

        # Add title
        final_image = _compositor._add_title(mosaic=image, title='', background_color=background_color,
                                             title_size=title_size)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width == width
        assert final_image.height == height + 2 * title_size

    def test_add_legend(self):
        import PIL.Image
        import numpy as np

        # Create data points
        records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ['car'], confidence=0.9),
        ]
        records_collection = RecordCollection(*records)
        annotation = Annotation(records_collection)
        tile = TileWrapper(np.zeros((100, 100, 3)), filename='test.png')
        data_point = DataPoint(tile, annotation)
        data_points = [data_point]

        # Legend
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

        legend_config = {
            'scale': 1,
            'axis': 0,
            'item_margins': (10, 10),
            'main_axis_align': 'start',
            'minor_axis_align': 'start'
        }

        # Parameters
        width, height = (300, 300)
        background_color = (0, 0, 0)

        # Init compositor
        _compositor = Compositor(data_points=data_points,
                                 color_engine_interface=simple_categorical_interface)

        image = PIL.Image.fromarray(np.zeros((width, height)))

        # Add legend
        final_image = _compositor._add_legend(mosaic=image, background_color=background_color,
                                              **legend_config)

        # Checks (vertical mode)
        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.height == height
        assert final_image.width > width

        # Checks horizontal mode
        legend_config['axis'] = 1
        final_image = _compositor._add_legend(mosaic=image, background_color=background_color,
                                              **legend_config)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width == width
        assert final_image.height > height

    def test_plot(self):
        import PIL.Image
        import numpy as np

        # Create data points
        records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ['car'],
                   confidence=0.9, confidence_confidence=0.9, color=Color(26, 188, 156)),
        ]
        records_collection = RecordCollection(*records)
        annotation = Annotation(records_collection)
        tile = TileWrapper(np.zeros((100, 100, 3), dtype=np.uint8), filename='test.png')
        data_point = DataPoint(tile, annotation)
        data_points = []

        # Legend
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

        kwargs = {
            'plot_centers': False,
            'plot_confidences': True,
            'zoom': 1,
            'alpha': 128,
            'scale': 1,
            'axis': 0,
            'background_color': (48, 56, 68, 255),
            'item_margins': (10, 10),
            'main_axis_align': 'start',
            'minor_axis_align': 'start'
        }

        # Accumulates datapoints (flattened)
        nb_datapoints = 15
        for _ in range(nb_datapoints):
            data_points.append(data_point)

        # Parameters
        _compositor = Compositor(data_points=data_points,
                                 color_engine_interface=simple_categorical_interface)
        n_cols = 10
        margins = (5, 5)

        # Test with neither title nor legend (use AdaptiveImagePositionGenerator)
        final_image = _compositor.plot(n_cols=n_cols, margins=margins, title=None, center=True,
                                       **kwargs)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width > n_cols * (100 + 2 * margins[0])
        assert final_image.height > 2 * (100 + 2 * margins[1])  # 2 rows
        assert final_image.height < 3 * (100 + 2 * margins[1])  # but less than 3 rows

        # Test with neither title nor legend (use SimpleImagePositionGenerator)
        final_image = _compositor.plot(n_cols=n_cols, margins=margins, title=None, center=False,
                                       **kwargs)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width > n_cols * (100 + 2 * margins[0])
        assert final_image.height > 2 * (100 + 2 * margins[1])  # 2 rows
        assert final_image.height < 3 * (100 + 2 * margins[1])  # but less than 3 rows

        # Nested datapoints
        nested_data_points = [
            [data_point, data_point, data_point, data_point],
            [data_point, data_point, data_point],
            [data_point, data_point, data_point, data_point],
            [data_point, data_point, data_point, data_point, data_point],
            [data_point, data_point]
        ]

        _compositor = Compositor(data_points=nested_data_points,
                                 color_engine_interface=simple_categorical_interface)

        final_image = _compositor.plot(n_cols=n_cols, margins=margins, title=None, center=True,
                                       **kwargs)

        # Check 5 cols and 5 rows (plus each tile title)
        painter_title_height = 70
        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width > 5 * (100 + 2 * margins[0])
        assert final_image.height > 5 * (100 + 2 * margins[1])
        assert final_image.height < 5 * (100 + painter_title_height + 2 * margins[1])

        # Add title
        final_image_with_title = _compositor.plot(n_cols=n_cols, margins=margins, title='Test', center=True,
                                                  **kwargs)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image_with_title.width == final_image.width
        assert final_image_with_title.height > final_image.height

        # Add legend and title
        final_image_with_legend = _compositor.plot(n_cols=n_cols, margins=margins, title='Test', center=True,
                                                   **kwargs)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image_with_legend.width == final_image_with_title.width
        assert final_image_with_legend.height == final_image_with_title.height
