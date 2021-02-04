import os

import numpy as np
import PIL.Image
import pytest

from plums.commons import TileWrapper, RecordCollection, Record, Path
from plums.plot.engine.descriptor import CategoricalDescriptor, Labels
from plums.plot.plot import StandardPlot, PairPlot


__options__ = ('zoom', 'plot_centers', 'plot_confidences', 'title', 'background_color', 'fill',
               'n_cols', 'margins', 'background_color', 'title', 'title_size', 'center',
               'plot_centers', 'plot_confidences', 'zoom', 'fill', 'alpha', 'scale',
               'axis', 'item_margins', 'main_axis_align', 'minor_axis_align', 'secondary_descriptor')


@pytest.fixture(params=__options__)
def option(request):
    return request.param


@pytest.fixture()
def data_point_like():
    # Fake records
    records = [
        Record(
            [[[100, 100], [100, 150], [150, 150], [150, 100], [100, 100]]],
            ('ship', ), confidence=0.9),
        Record(
            [[[710, 100], [710, 150], [760, 150], [760, 100], [710, 100]]],
            ('boat', ), confidence=0.857),
        Record(
            [[[500, 500], [550, 550], [500, 600], [450, 550], [500, 500]]],
            ('boat', ), confidence=0.72),
        Record(
            [[[250, 0], [300, 0], [275, 25], [300, 50], [250, 50], [275, 25], [250, 0]]],
            ('boat', ), confidence=0),
        Record(
            [[[300, 300], [320, 280], [420, 380], [400, 400], [300, 300]]],
            ('boat', ), confidence=0.3),
        Record(
            [[[650, 300], [670, 280], [770, 380], [750, 400], [650, 300]]],
            ('ship', ), confidence=0.1),
        Record(
            [[[-20, 600], [50, 600], [50, 650], [-20, 650], [-20, 600]]],
            ('ship', ), confidence=0.927),
        Record(
            [[[700, 600], [800, 600], [800, 650], [700, 650], [700, 600]]],
            ('vessel', ), confidence=0.927),
        Record(
            [[[500, -50], [550, -50], [550, 50], [500, 50], [500, -50]]],
            ('boat', ), confidence=0.5647),
        Record(
            [[[500, 750], [550, 750], [550, 850], [500, 850], [500, 750]]],
            ('vessel', ), confidence=0.1763),
    ]

    # Create collection
    records_collection = RecordCollection(*records)

    # Instantiate a tile
    tile = TileWrapper(np.zeros((768, 768, 3), dtype=np.uint8), filename=Path('84c1b28caecf.png'))

    # Create a data point like
    return tile, records_collection


class TestStandardPlot(object):
    def test_constructor(self):
        main_descriptor = CategoricalDescriptor('labels', fetch_fn=lambda x: ', '.join(x))
        standard_plot = StandardPlot(main_descriptor=main_descriptor)
        assert len(standard_plot._layout) == 0

    def test_option(self, option):
        main_descriptor = CategoricalDescriptor('labels', fetch_fn=lambda x: ', '.join(x))
        standard_plot = StandardPlot(main_descriptor=main_descriptor, **{option: 'user_value'})

        assert getattr(standard_plot, option) == 'user_value'
        assert standard_plot.properties[option] == 'user_value'
        setattr(standard_plot, option, 'new_value')
        assert getattr(standard_plot, option) == 'new_value'
        assert standard_plot.properties[option] == 'new_value'

        assert option in dir(standard_plot)

        standard_plot.option = 'user'
        assert hasattr(standard_plot, 'option')
        assert not hasattr(standard_plot._orchestrator, 'option')
        assert standard_plot.option == 'user'
        standard_plot.option = 'new_user'
        assert hasattr(standard_plot, 'option')
        assert not hasattr(standard_plot._orchestrator, 'option')
        assert standard_plot.option == 'new_user'

        del standard_plot.option
        assert not hasattr(standard_plot, 'option')

    def test_add(self, data_point_like):
        main_descriptor = CategoricalDescriptor('labels', fetch_fn=lambda x: ', '.join(x))
        standard_plot = StandardPlot(main_descriptor=main_descriptor)

        # Add multiple data point like
        for i in range(100):
            standard_plot.add(*data_point_like)
            assert standard_plot._layout[i] == data_point_like
            assert len(standard_plot._layout) == i + 1

    def test_reset(self, data_point_like):

        main_descriptor = CategoricalDescriptor('labels', fetch_fn=lambda x: ', '.join(x))
        standard_plot = StandardPlot(main_descriptor=main_descriptor)

        # Add multiple data point like
        for i in range(100):
            standard_plot.add(*data_point_like)
        assert len(standard_plot._layout) == 100

        # Reset list
        standard_plot.reset()
        assert len(standard_plot._layout) == 0

        # No data point to plot, raise an error
        with pytest.raises(ValueError):
            standard_plot.plot()

    def test_plot(self, tmp_path, data_point_like):
        main_descriptor = Labels()
        standard_plot = StandardPlot(main_descriptor=main_descriptor)

        # No data point to plot, raise an error
        with pytest.raises(ValueError):
            standard_plot.plot()

        # Add multiple data point like
        for i in range(2):
            standard_plot.add(*data_point_like)

        # Plot
        figure = standard_plot.plot()
        assert isinstance(figure, PIL.Image.Image)

        # Save figure to disk
        tmp_path = os.path.join(str(tmp_path), 'tmp')
        file_path = os.path.join(tmp_path, 'test.png')
        os.mkdir(tmp_path)
        figure = standard_plot.plot(file_path=file_path)

        img = PIL.Image.open(file_path)
        assert img.size == figure.size

        os.remove(file_path)
        os.rmdir(tmp_path)


class TestPairPlot(object):

    def test_constructor(self):

        overlap = True
        pair_plot = PairPlot(overlap=overlap)
        assert len(pair_plot._layout) == 0
        assert pair_plot._overlap == overlap

    def test_option(self, option):
        pair_plot = PairPlot(**{option: 'user_value'})

        assert getattr(pair_plot, option) == 'user_value'
        assert pair_plot.properties[option] == 'user_value'
        setattr(pair_plot, option, 'new_value')
        assert getattr(pair_plot, option) == 'new_value'
        assert pair_plot.properties[option] == 'new_value'

        assert option in dir(pair_plot)

        pair_plot.option = 'user'
        assert hasattr(pair_plot, 'option')
        assert not hasattr(pair_plot._orchestrator, 'option')
        assert pair_plot.option == 'user'
        pair_plot.option = 'new_user'
        assert hasattr(pair_plot, 'option')
        assert not hasattr(pair_plot._orchestrator, 'option')
        assert pair_plot.option == 'new_user'

        del pair_plot.option
        assert not hasattr(pair_plot, 'option')

    def test__get_label(self):
        assert isinstance(PairPlot._get_label(True), str)
        assert isinstance(PairPlot._get_label(False), str)

    def test__set_ground_truth_property(self, data_point_like):

        tile, record_collection = data_point_like

        for record in record_collection:
            assert hasattr(record, 'set') is False

        # Set records of the collection to ground truth
        collection = PairPlot._set_ground_truth_property(record_collection, True)

        for record in collection:
            assert hasattr(record, 'set') is True
            assert record.set is True

        # Set records of the collection to predictions
        collection = PairPlot._set_ground_truth_property(record_collection, False)

        for record in collection:
            assert hasattr(record, 'set') is True
            assert record.set is False

    def test_add(self, data_point_like):

        tile, record_collection = data_point_like

        # Mode with overlap
        pair_plot = PairPlot(overlap=True)

        with pytest.raises(ValueError):
            pair_plot.add(tile, record_collection, record_collection, record_collection)

        pair_plot.reset()
        assert pair_plot._line_length is None

        pair_plot.add(tile, record_collection, record_collection)
        assert len(pair_plot._layout) == 1
        assert len(pair_plot._layout[0]) == 2

        # Mode without overlap
        pair_plot = PairPlot(overlap=False)

        with pytest.raises(ValueError):
            pair_plot.add(tile, record_collection, record_collection, record_collection)
            pair_plot.add(tile, record_collection, record_collection)

        with pytest.raises(ValueError):
            pair_plot.add(tile, record_collection, record_collection)
            pair_plot.add(tile, record_collection, record_collection, record_collection)

        pair_plot.reset()
        assert pair_plot._line_length is None

        pair_plot.add(tile, record_collection, record_collection, record_collection)
        assert pair_plot._line_length == 3
        assert len(pair_plot._layout) == 1
        assert len(pair_plot._layout[0]) == 3

    def test_reset(self, data_point_like):

        tile, record_collection = data_point_like

        # Mode with overlap
        pair_plot = PairPlot(overlap=True)
        assert pair_plot._line_length is None
        assert len(pair_plot._layout) == 0

        pair_plot.add(tile, record_collection, record_collection)
        assert pair_plot._line_length is None
        assert len(pair_plot._layout) == 1

        pair_plot.reset()
        assert pair_plot._line_length is None
        assert len(pair_plot._layout) == 0

        # Mode without overlap
        pair_plot = PairPlot(overlap=False)
        assert pair_plot._line_length is None
        assert len(pair_plot._layout) == 0

        pair_plot.add(tile, record_collection, record_collection)
        assert pair_plot._line_length == 2
        assert len(pair_plot._layout) == 1

        pair_plot.reset()
        assert pair_plot._line_length is None
        assert len(pair_plot._layout) == 0

        # No data point to plot, raise an error
        with pytest.raises(ValueError):
            pair_plot.plot()

    def test_plot(self, data_point_like):
        pair_plot = PairPlot()

        # No data point to plot, raise an error
        with pytest.raises(ValueError):
            pair_plot.plot()

        # Add multiple data point like
        for i in range(2):
            pair_plot.add(*data_point_like)

        # Plot
        figure = pair_plot.plot()
        assert isinstance(figure, PIL.Image.Image)
