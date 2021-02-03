import pytest
import numpy as np
import PIL.Image

from playground_plums.commons.data import TileWrapper, RecordCollection, Record
from playground_plums.plot.engine.descriptor import (
    CategoricalDescriptor, ContinuousDescriptor, IntervalDescriptor, Labels
)
from playground_plums.plot.engine.orchestrator import Orchestrator


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
    tile = TileWrapper(np.zeros((768, 768, 3), dtype=np.uint8), filename='84c1b28caecf.png')

    # Create a data point like
    return tile, records_collection


class TestOrchestrator:
    def test_option(self, option):
        orchestrator = Orchestrator(CategoricalDescriptor('labels'), **{option: 'user_value'})
        assert getattr(orchestrator, option) == 'user_value'
        assert orchestrator.properties[option] == 'user_value'
        setattr(orchestrator, option, 'new_value')
        assert getattr(orchestrator, option) == 'new_value'
        assert orchestrator.properties[option] == 'new_value'

    def test_layout(self):
        # Invalid 1
        layout = (TileWrapper(np.zeros((100, 100, 3)), filename='file.file'),
                  RecordCollection(Record([0, 0], ('car', ), 0.9)))

        with pytest.raises(ValueError):
            orchestrator = Orchestrator(Labels())
            orchestrator.draw(layout)

        data_point = (TileWrapper(np.zeros((100, 100, 3)), filename='file.file'),
                      RecordCollection(Record([0, 0], ('car', ), 0.9)))

        # Invalid 2
        layout = (data_point, TileWrapper(np.zeros((100, 100, 3)), filename='file.file'))

        with pytest.raises(ValueError):
            orchestrator = Orchestrator(Labels())
            orchestrator.draw(layout)

        # Invalid 3
        layout = ((data_point, TileWrapper(np.zeros((100, 100, 3)), filename='file.file')), )

        with pytest.raises(ValueError):
            orchestrator = Orchestrator(Labels())
            orchestrator.draw(layout)

        # Invalid 4
        layout = ((data_point, data_point), data_point)

        with pytest.raises(ValueError):
            orchestrator = Orchestrator(Labels())
            orchestrator.draw(layout)

    def test_draw_1d(self, data_point_like):
        o = Orchestrator(Labels(),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [data_point_like]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(Labels(),
                         secondary_descriptor=ContinuousDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [data_point_like]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(Labels(),
                         secondary_descriptor=IntervalDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [data_point_like]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(IntervalDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [data_point_like]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(ContinuousDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [data_point_like]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

    def test_draw_2d(self, data_point_like):
        o = Orchestrator(Labels(),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [[data_point_like], [data_point_like]]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(Labels(),
                         secondary_descriptor=ContinuousDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [[data_point_like], [data_point_like]]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(Labels(),
                         secondary_descriptor=IntervalDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [[data_point_like], [data_point_like]]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(IntervalDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [[data_point_like], [data_point_like]]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)

        o = Orchestrator(ContinuousDescriptor('confidence'),
                         title='Test orchestrator', fill=True, zoom=1, background_color=(240, 250, 255))

        layout = [[data_point_like], [data_point_like]]
        fig = o.draw(layout)
        assert isinstance(fig, PIL.Image.Image)
