import pytest
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
import numpy as np


from plums.commons import TileWrapper, DataPoint, RecordCollection, Record, Annotation, Label
from plums.plot.engine.painter import Geometry, Draw, TagPainter, Position, Painter
from plums.plot.engine.descriptor import Confidence
from plums.plot.engine.color import Color


class TestGeometry:
    def test_constructor(self):
        dummy_record_list = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('car',), confidence=0.9)
        dummy_record_tuple = Record((((0, 0), (0, 1), (1, 1), (1, 0), (0, 0),),), ('car',), confidence=0.9)

        geometry_list = Geometry(record=dummy_record_list)
        geometry_tuple = Geometry(record=dummy_record_tuple)

        # Check coordinates format
        assert isinstance(geometry_list.coordinates, list)
        for i, coordinate in enumerate(geometry_list.coordinates):
            assert isinstance(coordinate, tuple)
            assert coordinate == tuple(dummy_record_list.coordinates[0][i])

        assert isinstance(geometry_tuple.coordinates, list)
        for i, coordinate in enumerate(geometry_tuple.coordinates):
            assert isinstance(coordinate, tuple)
            assert coordinate == tuple(dummy_record_tuple.coordinates[0][i])

        # Check exceptions
        class InvalidRecord(object):
            def __init__(self, type, coordinates):
                self.type = type
                self.coordinates = coordinates

        with pytest.raises(ValueError):
            Geometry(record=object())
        with pytest.raises(ValueError):
            Geometry(record=InvalidRecord(type='Point', coordinates=[1]))
        with pytest.raises(ValueError):
            Geometry(record=InvalidRecord(type='Point', coordinates=[1, 2, 3]))
        with pytest.raises(ValueError):
            Geometry(record=InvalidRecord(type='Polygon', coordinates=[[]]))
        with pytest.raises(ValueError):
            Geometry(record=InvalidRecord(type='Polygon', coordinates=[[[0, 0], [1, 0], [1, 1]]]))
        with pytest.raises(ValueError):
            Geometry(record=InvalidRecord(type='Test', coordinates=[[[0, 0], [1, 0], [1, 1]]]))
        with pytest.raises(TypeError):
            Geometry(record=InvalidRecord(type='Point', coordinates='Test'))
        with pytest.raises(TypeError):
            Geometry(record=InvalidRecord(type='Polygon', coordinates=['Hello']))

        # Test zoom = 2
        dummy_record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('car',), confidence=0.9)
        expected_coordinates = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        geometry_list = Geometry(record=dummy_record, zoom=2)

        assert isinstance(geometry_list.coordinates, list)
        for i, coordinate in enumerate(geometry_list.coordinates):
            assert isinstance(coordinate, tuple)
            assert coordinate == expected_coordinates[i]

        # Test zoom = 0.6
        dummy_record = Record([[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]], ('car',), confidence=0.9)
        expected_coordinates = [(0, 0), (0, 6), (6, 6), (6, 0), (0, 0)]
        geometry_list = Geometry(record=dummy_record, zoom=0.6)

        assert isinstance(geometry_list.coordinates, list)
        for i, coordinate in enumerate(geometry_list.coordinates):
            assert isinstance(coordinate, tuple)
            assert coordinate == expected_coordinates[i]

    def test_min_x(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 1], [2, 2], [3, 3], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.min_x, int)
        assert geometry.min_x == 0
        # Point
        dummy_record = Record([0, 0], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.min_x, int)
        assert geometry.min_x == 0

    def test_max_x(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 1], [2, 2], [3, 3], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.max_x, int)
        assert geometry.max_x == 3
        # Point
        dummy_record = Record([1, 1], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.min_x, int)
        assert geometry.max_x == 1

    def test_min_y(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 1], [2, 2], [3, 3], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.min_y, int)
        assert geometry.min_y == 0
        # Point
        dummy_record = Record([1, 1], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.min_x, int)
        assert geometry.min_y == 1

    def test_max_y(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 1], [2, 2], [3, 3], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.max_y, int)
        assert geometry.max_y == 3
        # Point
        dummy_record = Record([2, 2], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert isinstance(geometry.min_x, int)
        assert geometry.max_y == 2

    def test_centroid(self):
        # Polygon
        dummy_record = Record([[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        centroid = geometry.centroid
        assert isinstance(centroid, tuple)
        assert centroid == (1, 1)
        # Point
        dummy_record = Record([1, 2], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        centroid = geometry.centroid
        assert isinstance(centroid, tuple)
        assert centroid == (1, 2)

    def test_coordinates(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert geometry.coordinates == geometry._coordinates
        # Point
        dummy_record = Record([0, 1], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert geometry.coordinates == geometry._coordinates

    def test_leftmost_coordinate(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert geometry.leftmost_coordinate == (0, 0)
        # Point
        dummy_record = Record([0, 1], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert geometry.leftmost_coordinate == (0, 1)

    def test_rightmost_coordinate(self):
        # Polygon
        dummy_record = Record([[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert geometry.rightmost_coordinate == (1, 0)
        # Point
        dummy_record = Record([0, 1], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        assert geometry.rightmost_coordinate == (0, 1)


class TestDraw:
    def test_constructor(self):
        dummy_size = (500, 500)
        dummy_zoom = 2
        dummy_mode = 'RGBA'
        dummy_background_color = (255, 255, 255, 255)

        draw = Draw(size=dummy_size, zoom=dummy_zoom, mode=dummy_mode, background_color=dummy_background_color)

        # Check overlay
        assert isinstance(draw._overlay, PIL.Image.Image)
        assert draw._overlay == draw.overlay
        assert draw._overlay.size == dummy_size
        assert draw._overlay.mode == dummy_mode
        array = np.array(draw._overlay)
        assert array.shape == dummy_size + (len(dummy_background_color), )
        assert (array == dummy_background_color).all()

        # Check draw object
        assert isinstance(draw._draw, PIL.ImageDraw.ImageDraw)

        # Check zoom
        assert isinstance(draw._zoom, int)
        assert draw._zoom == dummy_zoom

    def test_circle(self):
        dummy_size = (4, 4)
        dummy_zoom = 1
        dummy_mode = 'RGBA'
        dummy_background_color = (255, 255, 255, 255)

        dummy_circle_centroid = (2, 2)
        dummy_circle_color = (0, 0, 0, 255)

        # Draw circle
        draw = Draw(size=dummy_size, zoom=dummy_zoom, mode=dummy_mode, background_color=dummy_background_color)
        draw.circle(centroid=dummy_circle_centroid, fill_color=dummy_circle_color)

        # Checks
        assert isinstance(draw._overlay, PIL.Image.Image)
        assert draw._overlay == draw.overlay
        assert draw._overlay.size == dummy_size
        assert draw._overlay.mode == dummy_mode
        array = np.array(draw._overlay)
        assert array.shape == dummy_size + (len(dummy_background_color), )
        assert not (array == dummy_background_color).all()

        # Check pixels
        assert (array[0][0] == dummy_background_color).all()
        assert (array[1][:] == dummy_circle_color).all()
        assert (array[2][:] == dummy_circle_color).all()
        assert (array[:][1] == dummy_circle_color).all()
        assert (array[:][2] == dummy_circle_color).all()

    def test_line(self):
        dummy_size = (4, 4)
        dummy_zoom = 1
        dummy_mode = 'RGBA'
        dummy_background_color = (255, 255, 255, 255)

        dummy_line_points = [(1, 1), (1, 2)]
        dummy_line_color = (0, 0, 0, 255)

        # Draw circle
        draw = Draw(size=dummy_size, zoom=dummy_zoom, mode=dummy_mode, background_color=dummy_background_color)
        draw.line(points=dummy_line_points, fill_color=dummy_line_color)

        # Checks
        assert isinstance(draw._overlay, PIL.Image.Image)
        assert draw._overlay == draw.overlay
        assert draw._overlay.size == dummy_size
        assert draw._overlay.mode == dummy_mode
        array = np.array(draw._overlay)
        assert array.shape == dummy_size + (len(dummy_background_color), )
        assert not (array == dummy_background_color).all()

        # Check pixels
        assert (array[0][:] == dummy_background_color).all()
        assert (array[3][:] == dummy_background_color).all()
        assert (array[:][0] == dummy_background_color).all()
        assert (array[:][3] == dummy_background_color).all()
        assert (array[1][1] == dummy_line_color).all()
        assert (array[2][1] == dummy_line_color).all()

    def test_polygon(self):
        dummy_size = (4, 4)
        dummy_zoom = 1
        dummy_mode = 'RGBA'
        dummy_background_color = (255, 255, 255, 255)

        dummy_polygon_points = [(1, 1), (1, 2)]
        dummy_polygon_color = (0, 0, 0, 255)

        # Draw circle
        draw = Draw(size=dummy_size, zoom=dummy_zoom, mode=dummy_mode, background_color=dummy_background_color)
        draw.polygon(points=dummy_polygon_points, fill_color=dummy_polygon_color)

        # Checks
        assert isinstance(draw._overlay, PIL.Image.Image)
        assert draw._overlay == draw.overlay
        assert draw._overlay.size == dummy_size
        assert draw._overlay.mode == dummy_mode
        array = np.array(draw._overlay)
        assert array.shape == dummy_size + (len(dummy_background_color), )
        assert not (array == dummy_background_color).all()

        # Check pixels
        assert (array[0][:] == dummy_background_color).all()
        assert (array[3][:] == dummy_background_color).all()
        assert (array[:][0] == dummy_background_color).all()
        assert (array[:][3] == dummy_background_color).all()
        assert (array[1][1] == dummy_polygon_color).all()
        assert (array[2][1] == dummy_polygon_color).all()

    def test_text(self):
        dummy_size = (20, 20)
        dummy_zoom = 1
        dummy_mode = 'RGBA'
        dummy_background_color = (255, 255, 255, 255)

        dummy_text_coordinates = [(0, 0)]
        dummy_text_color = (0, 0, 0, 255)
        dummy_text = 'a'
        dummy_font = PIL.ImageFont.load_default()

        # Draw circle
        draw = Draw(size=dummy_size, zoom=dummy_zoom, mode=dummy_mode, background_color=dummy_background_color)
        draw.text(text_coordinates=dummy_text_coordinates, text=dummy_text,
                  font=dummy_font, fill_color=dummy_text_color)

        # Checks
        assert isinstance(draw._overlay, PIL.Image.Image)
        assert draw._overlay == draw.overlay
        assert draw._overlay.size == dummy_size
        assert draw._overlay.mode == dummy_mode
        array = np.array(draw._overlay)
        assert array.shape == dummy_size + (len(dummy_background_color), )
        assert not (array == dummy_background_color).all()


class TestTagPainter:
    def test_constructor(self):
        # Parameters
        descriptor = Confidence()
        text_margin = 2
        text_size = 11
        zoom = 1

        _painter = TagPainter(descriptor=descriptor, text_margin=text_margin, text_size=text_size, zoom=zoom)

        # Check
        assert _painter._descriptor == descriptor
        assert _painter._text_margin == text_margin
        assert _painter._text_size == text_size
        assert _painter._zoom == zoom

    def test_compute_label_size(self):
        # Parameters
        font = PIL.ImageFont.load_default()  # size = 11

        # Check
        size = TagPainter._compute_label_size(text='', font=font, margin=3)

        assert isinstance(size, tuple)
        assert size == (6, 11 + 6)

    def test_compute_label_position(self):
        # Check
        position = TagPainter._compute_label_position(max_x=10, label_width=10, max_width=15)

        assert isinstance(position, str)
        assert position == Position.LEFT

        position = TagPainter._compute_label_position(max_x=10, label_width=10, max_width=30)

        assert isinstance(position, str)
        assert position == Position.RIGHT

    def test_compute_label_starting_point(self):
        # Check
        dummy_record = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        starting_point = TagPainter._compute_label_starting_point(
            geometry=geometry, position=Position.RIGHT)

        assert isinstance(starting_point, tuple)
        assert starting_point == (1, 0)

        starting_point = TagPainter._compute_label_starting_point(
            geometry=geometry, position=Position.LEFT)

        assert isinstance(starting_point, tuple)
        assert starting_point == (0, 0)

    def test_compute_vertical_margin(self):
        # Check
        vertical_margin = TagPainter._compute_vertical_margin(min_y=20, label_height=10)

        assert isinstance(vertical_margin, int)
        assert vertical_margin == 0

        vertical_margin = TagPainter._compute_vertical_margin(min_y=5, label_height=20)

        assert isinstance(vertical_margin, int)
        assert vertical_margin == 5

    def test_compute_label_coordinates(self):
        # Parameters
        _painter = TagPainter(Confidence())

        # Check
        dummy_record = Record([[[0, 5], [20, 5], [20, 25], [0, 25], [0, 5]]], ('car',), confidence=0.9)
        geometry = Geometry(record=dummy_record)
        text = ''
        font = PIL.ImageFont.load_default()  # size = 11
        text_width, text_height = font.getsize(text)
        tile_width = 50

        label_coordinates, text_coordinates = _painter._compute_label_coordinates(
            geometry=geometry, text=text,
            font=font, tile_width=tile_width)

        assert isinstance(label_coordinates, list)
        assert len(label_coordinates) == 5
        for coordinate in label_coordinates:
            assert isinstance(coordinate, tuple)
            assert len(coordinate) == 2
        assert isinstance(text_coordinates, tuple)


class TestPainter:
    def test_constructor(self):
        # Parameters
        plot_centers = False
        plot_tag = Confidence()
        zoom = 1
        alpha = 64

        _painter = Painter(plot_centers=plot_centers, plot_tag=plot_tag, zoom=zoom, alpha=alpha)

        # Check
        assert _painter._plot_centers == plot_centers
        assert _painter._plot_tag
        assert _painter._tag_descriptor == plot_tag
        assert _painter._zoom == zoom
        assert _painter._alpha == alpha

        # Parameters
        plot_centers = False
        zoom = 1
        alpha = 64

        # Check
        assert _painter._plot_centers == plot_centers
        assert _painter._plot_tag
        assert _painter._tag_descriptor == plot_tag
        assert _painter._zoom == zoom
        assert _painter._alpha == alpha

    def test_add_title(self):
        # Parameters
        width, height = (300, 300)
        _painter = Painter()

        image = PIL.Image.fromarray(np.zeros((width, height)))

        # Add title
        final_image = _painter._add_title(image=image, title='')

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width == width
        assert final_image.height == height + _painter.TITLE_HEIGHT

    def test_draw(self):
        # Fake records
        invalid_records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ('car',),
                   confidence=0.9),
            Record([[[100, 100], [110, 110], [100, 100]]], ('car',), confidence=0.9),
        ]
        records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ('car',),
                   confidence=0.9,
                   color=Color(255, 128, 128)),
            Record([[[100, 100], [100, 150], [100, 100]]], ('car',), confidence=0.9,
                   color=Color(128, 255, 255)),
            Record([100, 100], ('ship',), confidence=0.3, color=Color(128, 255, 255)),
        ]

        # Create collection
        invalid_records_collection = RecordCollection(*invalid_records)
        records_collection = RecordCollection(*records)

        # Finally, the annotation
        invalid_annotation = Annotation(invalid_records_collection)
        annotation = Annotation(records_collection)

        # Instantiate a tile
        tile = TileWrapper(np.zeros((300, 300, 4), dtype=np.uint8), filename='test.png')

        # Create a datapoint
        invalid_datapoint = DataPoint(tile, invalid_annotation)
        datapoint = DataPoint(tile, annotation)

        # Parameters
        _painter = Painter(fill=True)

        # Sanity check
        with pytest.raises(AttributeError):
            _painter.draw(invalid_datapoint)

        # Draw datapoint
        final_image = _painter.draw(datapoint)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width == 300
        assert final_image.height == 300 + _painter.TITLE_HEIGHT

        # With centers
        _painter = Painter(plot_centers=True)

        # Sanity check
        with pytest.raises(AttributeError):
            _painter.draw(invalid_datapoint)

        # Draw datapoint
        final_image = _painter.draw(datapoint)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width == 300
        assert final_image.height == 300 + _painter.TITLE_HEIGHT

        # Test zoom
        zoom = 2.5
        _painter = Painter(zoom=zoom)

        final_image = _painter.draw(datapoint)

        assert isinstance(final_image, PIL.Image.Image)
        assert final_image.width == 300 * zoom
        assert final_image.height == (300 + _painter.TITLE_HEIGHT) * zoom

        # Check invalid geometry
        class InvalidRecord(object):
            def __init__(self, type, coordinates):
                self.id = '1'
                self.type = type
                self.coordinates = coordinates
                self.labels = Label('test'),
                self.color = Color(255, 128, 128, ctype='sRGB255')

        records = [
            Record([[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]], ('car',),
                   confidence=0.9,
                   color=Color(255, 128, 128)),
            Record([[[100, 100], [100, 150], [100, 100]]], ('car',), confidence=0.9,
                   color=Color(128, 255, 255)),
            InvalidRecord(type='Test', coordinates=[])
        ]

        # Create data point
        records_collection = RecordCollection(*records)
        annotation = Annotation(records_collection)
        tile = TileWrapper(np.zeros((300, 300, 4), dtype=np.uint8), filename='test.png')
        data_point = DataPoint(tile, annotation)

        _painter = Painter(fill=True)

        with pytest.raises(ValueError):
            _painter.draw(data_point)
