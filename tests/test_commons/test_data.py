import re
from collections import OrderedDict

import pytest
import numpy as np
from tests.test_commons.base import mixin_suite

import plums.commons.data as data
import plums.commons.data.mixin
from plums.commons.data.taxonomy import Label, Taxonomy


@pytest.fixture(params=('ordered-dict', 'tile-collection'))
def tiles(request):
    if request.param == 'ordered-dict':
        return OrderedDict((('tile', data.TileWrapper(np.zeros((5, 5, 3)),
                                                      filename='somefile.png',
                                                      some_property='some_value')), ))

    return data.TileCollection(('tile', data.TileWrapper(np.zeros((5, 5, 3)),
                                                         filename='somefile.png',
                                                         some_property='some_value')))


class TestBase:
    def test_array_interfaced(self):
        import numpy as np

        a = np.arange(10)
        assert isinstance(a, data.ArrayInterfaced)

        class Dummy(object):
            @property
            def __array_interface__(self):
                return None

        d = Dummy()
        assert isinstance(d, data.ArrayInterfaced)

    def test_array(self):
        import numpy as np

        a = np.arange(10)
        assert isinstance(a, data.base._Array)

        class Dummy(object):
            @property
            def __array_interface__(self):
                return None

        d = Dummy()
        assert not isinstance(d, data.base._Array)

    def test_geo_interfaced(self):
        import geojson

        a = geojson.loads('{"type":"Point", "coordinates":[0, 5, 6]}')
        assert isinstance(a, data.GeoInterfaced)
        assert a.is_valid

        class Dummy(object):
            @property
            def __geo_interface__(self):
                return None

        d = Dummy()
        assert isinstance(d, data.GeoInterfaced)

    def test_property_container(self):
        # Check construction
        p = plums.commons.data.mixin.PropertyContainer()
        mixin_suite(p)  # Base validity tests

    def test_id_mixin(self):
        id_ = plums.commons.data.mixin.IdentifiedMixIn()
        mixin_suite(id_)  # Base validity tests


class TestRecord:
    def test_record(self):
        import geojson

        taxonomy = Taxonomy(Label('road vehicle', children=(Label('car'), )))
        incomplete_taxonomy = Taxonomy(Label('road vehicle'))

        with pytest.raises(ValueError, match='Expected at least 1 label'):
            r = data.Record([0, 2, 3], [])

        r = data.Record([0, 1, 2], ['car', 'road vehicle'], some_property='some property', another_property=45)
        mixin_suite(r)  # Base validity tests

        assert hasattr(r, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', r.id)

        # Check label fetch w/o taxonomy
        assert all(isinstance(n, Label) for n in r.labels)
        with pytest.raises(ValueError, match='No taxonomy exists for this record but a max_depth was provided'):
            r.get_labels(max_depth=1)
        assert all(isinstance(n, Label) for n in r.get_labels())

        # Check label fetch w/ incomplete taxonomy
        r.taxonomy = incomplete_taxonomy
        with pytest.raises(KeyError):
            assert all(isinstance(n, Label) for n in r.labels)

        # Check label fetch w/ taxonomy
        r.taxonomy = taxonomy
        assert all(isinstance(n, Label) for n in r.labels)
        assert r.labels[0].parent.id == taxonomy.road_vehicle.root.id
        assert r.labels[1].id == taxonomy.road_vehicle.root.id

        assert hasattr(r, 'some_property')
        assert hasattr(r, 'another_property')

        assert r.is_valid
        assert r.type == 'Point'

        assert geojson.dumps(r, sort_keys=True) == '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                   '"properties": {"another_property": 45, ' \
                                                   '"category": ["car", "road vehicle"], ' \
                                                   '"confidence": null, "some_property": "some property"}, ' \
                                                   '"type": "Feature"}'

        assert geojson.dumps(r.to_geojson(style='export-service'), sort_keys=True) \
            == '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
               '"properties": {"another_property": 45, ' \
               '"score": null, ' \
               '"some_property": "some property", ' \
               '"tags": "car,road vehicle"}, ' \
               '"type": "Feature"}'

        r = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'road vehicle'],
                        some_property='some property', another_property=45)

        assert hasattr(r, 'some_property')
        assert hasattr(r, 'another_property')

        assert r.is_valid
        assert r.type == 'Polygon'

        assert geojson.dumps(r, sort_keys=True) == '{"geometry": {"coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]], ' \
                                                   '"type": "Polygon"}, ' \
                                                   '"properties": {"another_property": 45, ' \
                                                   '"category": ["car", "road vehicle"], ' \
                                                   '"confidence": null, "some_property": "some property"}, ' \
                                                   '"type": "Feature"}'

        assert geojson.dumps(r.to_geojson(style='export-service'), sort_keys=True) \
            == '{"geometry": {"coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]], ' \
               '"type": "Polygon"}, ' \
               '"properties": {"another_property": 45, ' \
               '"score": null, ' \
               '"some_property": "some property", ' \
               '"tags": "car,road vehicle"}, ' \
               '"type": "Feature"}'

    def test_record_collection_with_taxonomy_init(self):  # noqa: R701
        import geojson

        taxonomy = Taxonomy(Label('road vehicle'), Label('car'))
        invalid_taxonomy = Taxonomy(Label('road vehicle', children=(Label('car'), )), Label('other'))
        different_taxonomy = Taxonomy(Label('road vehicle'), Label('other'))
        incomplete_taxonomy = Taxonomy(Label('road vehicle'))

        r = data.Record([0, 1, 2], ['car', 'road vehicle'], some_property='some property', another_property=45)

        with pytest.raises(ValueError, match='Expected at most'):
            rc = data.RecordCollection(r, taxonomy=incomplete_taxonomy)

        with pytest.raises(ValueError, match='are not part of the taxonomy'):
            rc = data.RecordCollection(r, taxonomy=different_taxonomy)

        with pytest.raises(ValueError, match='Some labels are part of the same true-root subtree'):
            rc = data.RecordCollection(r, taxonomy=invalid_taxonomy)

        rc = data.RecordCollection(r, taxonomy=taxonomy)
        mixin_suite(rc)  # Base validity tests

        assert hasattr(rc, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', rc.id)

        assert len(rc) == 1
        assert rc[0] == r
        r2 = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'truck'],
                         some_property='some property', another_property=45)

        with pytest.raises(ValueError, match='are not part of the taxonomy'):
            rc.append(r2)

        rc.taxonomy = Taxonomy(Label('road vehicle', children=(Label('truck'), )), Label('car'))
        rc.append(r2)

        assert rc.get()[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get()[1].labels == (Label('car'), Label('truck'))
        assert tuple(label.labels for label in rc.get()[0:]) == (rc.get()[0].labels,
                                                                 rc.get()[1].labels)

        assert rc.get(max_depth=1)[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get(max_depth=1)[1].labels == (Label('car'), Label('road vehicle'))
        assert tuple(label.labels for label in rc.get(max_depth=1)[0:]) == (rc.get(max_depth=1)[0].labels,
                                                                            rc.get(max_depth=1)[1].labels)

        assert rc.get(max_depth={'road vehicle': 0})[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get(max_depth={'road vehicle': 0})[1].labels == (Label('car'), Label('road vehicle'))
        assert tuple(label.labels for label in rc.get(max_depth={'road vehicle': 0})[0:]) \
            == (rc.get(max_depth={'road vehicle': 0})[0].labels,
                rc.get(max_depth={'road vehicle': 0})[1].labels)

        assert rc.get(max_depth={'car': 0})[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get(max_depth={'car': 0})[1].labels == (Label('car'), Label('truck'))
        assert tuple(label.labels for label in rc.get(max_depth={'car': 0})[0:]) \
            == (rc.get(max_depth={'car': 0})[0].labels,
                rc.get(max_depth={'car': 0})[1].labels)

        assert len(rc) == 2
        assert rc[1] == r2

        assert geojson.dumps(rc, sort_keys=True) == '{"features": [' \
                                                    '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                    '"properties": {"another_property": 45, ' \
                                                    '"category": ["car", "road vehicle"], ' \
                                                    '"confidence": null, "some_property": "some property"}, ' \
                                                    '"type": "Feature"}, ' \
                                                    '{"geometry": {"coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]], '\
                                                    '"type": "Polygon"}, ' \
                                                    '"properties": {"another_property": 45, ' \
                                                    '"category": ["car", "truck"], ' \
                                                    '"confidence": null, ' \
                                                    '"some_property": "some property"}, "type": "Feature"}], ' \
                                                    '"type": "FeatureCollection"}'

        with pytest.raises(ValueError, match='are not part of'):
            rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'trucks'],
                                some_property='some property', another_property=45)

        with pytest.raises(ValueError, match='Some labels are part of the same true-root subtree'):
            rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['road vehicle', 'truck'],
                                some_property='some property', another_property=45)

        rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car'],
                            some_property='some property', another_property=45)
        assert rc[1].labels == (Label('car'), )

    def test_record_collection_with_taxonomy_add(self):  # noqa: R701
        import geojson

        taxonomy = Taxonomy(Label('road vehicle'), Label('car'))
        invalid_taxonomy = Taxonomy(Label('road vehicle', children=(Label('car'), )), Label('other'))
        different_taxonomy = Taxonomy(Label('road vehicle'), Label('other'))
        incomplete_taxonomy = Taxonomy(Label('road vehicle'))

        r = data.Record([0, 1, 2], ['car', 'road vehicle'], some_property='some property', another_property=45)
        rc = data.RecordCollection(r)
        mixin_suite(rc)  # Base validity tests

        assert hasattr(rc, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', rc.id)

        with pytest.raises(ValueError, match='Expected at most'):
            rc.taxonomy = incomplete_taxonomy

        with pytest.raises(ValueError, match='are not part of the taxonomy'):
            rc.taxonomy = different_taxonomy

        with pytest.raises(ValueError, match='Some labels are part of the same true-root subtree'):
            rc.taxonomy = invalid_taxonomy

        rc.taxonomy = taxonomy

        assert len(rc) == 1
        assert rc[0] == r
        r2 = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'truck'],
                         some_property='some property', another_property=45)

        with pytest.raises(ValueError, match='are not part of the taxonomy'):
            rc.append(r2)

        rc.taxonomy = Taxonomy(Label('road vehicle', children=(Label('truck'), )), Label('car'))
        rc.append(r2)

        assert rc.get()[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get()[1].labels == (Label('car'), Label('truck'))
        assert tuple(label.labels for label in rc.get()[0:]) == (rc.get()[0].labels,
                                                                 rc.get()[1].labels)

        assert rc.get(max_depth=1)[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get(max_depth=1)[1].labels == (Label('car'), Label('road vehicle'))
        assert tuple(label.labels for label in rc.get(max_depth=1)[0:]) == (rc.get(max_depth=1)[0].labels,
                                                                            rc.get(max_depth=1)[1].labels)

        assert rc.get(max_depth={'road vehicle': 0})[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get(max_depth={'road vehicle': 0})[1].labels == (Label('car'), Label('road vehicle'))
        assert tuple(label.labels for label in rc.get(max_depth={'road vehicle': 0})[0:]) \
            == (rc.get(max_depth={'road vehicle': 0})[0].labels,
                rc.get(max_depth={'road vehicle': 0})[1].labels)

        assert rc.get(max_depth={'car': 0})[0].labels == (Label('car'), Label('road vehicle'))
        assert rc.get(max_depth={'car': 0})[1].labels == (Label('car'), Label('truck'))
        assert tuple(label.labels for label in rc.get(max_depth={'car': 0})[0:]) \
            == (rc.get(max_depth={'car': 0})[0].labels,
                rc.get(max_depth={'car': 0})[1].labels)

        assert len(rc) == 2
        assert rc[1] == r2

        assert geojson.dumps(rc, sort_keys=True) == '{"features": [' \
                                                    '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                    '"properties": {"another_property": 45, ' \
                                                    '"category": ["car", "road vehicle"], ' \
                                                    '"confidence": null, "some_property": "some property"}, ' \
                                                    '"type": "Feature"}, ' \
                                                    '{"geometry": {"coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]], '\
                                                    '"type": "Polygon"}, ' \
                                                    '"properties": {"another_property": 45, ' \
                                                    '"category": ["car", "truck"], ' \
                                                    '"confidence": null, ' \
                                                    '"some_property": "some property"}, "type": "Feature"}], ' \
                                                    '"type": "FeatureCollection"}'

        with pytest.raises(ValueError, match='are not part of'):
            rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'trucks'],
                                some_property='some property', another_property=45)

        with pytest.raises(ValueError, match='Some labels are part of the same true-root subtree'):
            rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['road vehicle', 'truck'],
                                some_property='some property', another_property=45)

        rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car'],
                            some_property='some property', another_property=45)
        assert rc[1].labels == (Label('car'), )

    def test_record_collection_without_taxonomy(self):
        import geojson

        r = data.Record([0, 1, 2], ['car', 'road vehicle'], some_property='some property', another_property=45)
        rc = data.RecordCollection(r)
        mixin_suite(rc)  # Base validity tests

        assert hasattr(rc, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', rc.id)

        assert len(rc) == 1
        assert rc[0] == r
        r2 = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'truck'],
                         some_property='some property', another_property=45)
        rc.append(r2)

        assert len(rc) == 2
        assert rc[1] == r2

        assert geojson.dumps(rc, sort_keys=True) == '{"features": [' \
                                                    '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                    '"properties": {"another_property": 45, ' \
                                                    '"category": ["car", "road vehicle"], ' \
                                                    '"confidence": null, "some_property": "some property"}, ' \
                                                    '"type": "Feature"}, ' \
                                                    '{"geometry": {"coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]], '\
                                                    '"type": "Polygon"}, ' \
                                                    '"properties": {"another_property": 45, ' \
                                                    '"category": ["car", "truck"], ' \
                                                    '"confidence": null, ' \
                                                    '"some_property": "some property"}, "type": "Feature"}], ' \
                                                    '"type": "FeatureCollection"}'

        assert 'car' in rc.taxonomy
        assert rc.taxonomy['car'].parent == rc.taxonomy.root
        assert 'truck' in rc.taxonomy
        assert rc.taxonomy['truck'].parent == rc.taxonomy.root
        assert 'road vehicle' in rc.taxonomy
        assert rc.taxonomy['road vehicle'].parent == rc.taxonomy.root

        rc[1] = data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['trucks'],
                            some_property='some property', another_property=45)
        assert rc[1].labels == (Label('trucks'), )
        assert 'trucks' in rc.taxonomy
        assert rc.taxonomy['trucks'].parent == rc.taxonomy.root

        rc = data.RecordCollection(r)


class TestTile:
    def test_tile(self):
        import PIL.Image
        import numpy as np

        im = PIL.Image.fromarray(np.arange(600).astype(np.uint8).reshape(10, 20, 3))

        assert isinstance(im, data.Tile)

        with pytest.raises(TypeError, match='Tile expect an object which exposes the __array_interface__'):
            t = data.Tile(0)  # noqa: F841

    def test_tile_wrapper(self):
        tw = data.TileWrapper(np.zeros((5, 5, 3)), filename='somefile.png', some_property='some_value')
        mixin_suite(tw)  # Base validity tests

        class Dummy(object):
            @property
            def __array_interface__(self):
                return None

        with pytest.raises(TypeError, match='TileWrapper expect a ndarray-like object, got:'):
            tw = data.TileWrapper(Dummy(), filename='somefile.png', some_property='some_value')

        class Dummy(object):
            def __init__(self, *shape):
                self._shape = shape

            @property
            def shape(self):
                return self._shape

            @property
            def __array_interface__(self):
                return None

        with pytest.raises(ValueError, match='TileWrapper expect a 3-dim ndarray, got:'):
            tw = data.TileWrapper(Dummy(1, 5, 6, 3), filename='somefile.png', some_property='some_value')

        with pytest.raises(ValueError, match='TileWrapper expect a HWC formatted image'):
            tw = data.TileWrapper(Dummy(3, 6, 5), filename='somefile.png', some_property='some_value')

        with pytest.raises(ValueError, match='TileWrapper expect a HWC formatted image'):
            tw = data.TileWrapper(Dummy(3, 6, 3), filename='somefile.png', some_property='some_value')

        with pytest.raises(ValueError, match='TileWrapper expect a HWC formatted image'):
            tw = data.TileWrapper(Dummy(3, 3, 3), filename='somefile.png', some_property='some_value')

        tw = data.TileWrapper(Dummy(5, 10, 3), filename='somefile.png', some_property='some_value')

        assert hasattr(tw, 'filename')
        assert tw.size == (10, 5)
        assert tw.width == 10
        assert tw.height == 5

        assert tw.some_property == 'some_value'
        assert tw.__array_interface__ is None

        tw.info['some_other_property'] = 56
        assert tw.properties['some_other_property'] == 56

    def test_tile_collection(self):  # noqa: R701
        import PIL.Image
        import numpy as np

        im = PIL.Image.fromarray(np.arange(600).astype(np.uint8).reshape(10, 20, 3))
        tw = data.TileWrapper(np.zeros((5, 5, 3)), filename='somefile.png', some_property='some_value')

        tc = data.TileCollection(im, tw)
        assert tc.iloc[0] is im
        assert tc['tile_0'] is im
        assert tc.iloc[1] is tw
        assert tc['tile_1'] is tw

        tc = data.TileCollection(('first', im), ('second', tw))
        assert tc.iloc[0] is im
        assert tc['first'] is im
        assert tc.iloc[1] is tw
        assert tc['second'] is tw

        tc = data.TileCollection(im, ('second', tw))
        assert tc.iloc[0] is im
        assert tc['tile_0'] is im
        assert tc.iloc[1] is tw
        assert tc['second'] is tw

        import sys
        if sys.version_info[1] >= 6:
            tc = data.TileCollection(first=im, second=tw)
            assert tc.iloc[0] is im
            assert tc['first'] is im
            assert tc.iloc[1] is tw
            assert tc['second'] is tw

            tc = data.TileCollection(('first', im), second=tw)
            assert tc.iloc[0] is im
            assert tc['first'] is im
            assert tc.iloc[1] is tw
            assert tc['second'] is tw

            tc = data.TileCollection(im, second=tw)
            assert tc.iloc[0] is im
            assert tc['tile_0'] is im
            assert tc.iloc[1] is tw
            assert tc['second'] is tw

            with pytest.raises(TypeError, match='Expected each tiles to expose the __array_interface__ attribute'):
                _ = data.TileCollection(im, ('second', tw), false=0)

        else:
            with pytest.raises(ValueError, match='Ordered keyword argument were introduced in Python'):
                _ = data.TileCollection(first=im, second=tw)

        with pytest.raises(TypeError, match='Expected each tiles to expose the __array_interface__ attribute'):
            _ = data.TileCollection(('first', im), 0, ('second', tw))

        with pytest.raises(TypeError, match='Expected each tiles to expose the __array_interface__ attribute'):
            _ = data.TileCollection(('first', im), ('false', 0), ('second', tw))


class TestMask:
    def test_mask(self):
        m = data.mask.Mask(name='some_name', some_property='some_value')
        mixin_suite(m)  # Base validity tests

        assert hasattr(m, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', m.id)

        assert 'name' in m.__dict__
        assert 'name' not in m.properties

        assert m.name == 'some_name'
        assert m.some_property == 'some_value'
        assert m.mask

    def test_vector_mask(self):
        vm = data.VectorMask([[[0, 0], [0, 1], [1, 1], [0, 0]]], 'data',
                             some_property='some_value', another_property=45)
        mixin_suite(vm)  # Base validity tests

        assert hasattr(vm, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', vm.id)

        assert vm.name == 'data'
        assert vm.some_property == 'some_value'
        assert vm.another_property == 45
        assert vm.mask

    def test_raster_mask(self):
        rm = data.RasterMask(np.zeros((5, 5, 3)), 'data', some_property='some_value')
        mixin_suite(rm)  # Base validity tests

        class Dummy(object):
            @property
            def __array_interface__(self):
                return None

        with pytest.raises(TypeError, match='RasterMask expect a ndarray-like object, got:'):
            rm = data.RasterMask(Dummy(), 'data', some_property='some_value')

        class Dummy(object):
            def __init__(self, *shape):
                self._shape = shape

            @property
            def shape(self):
                return self._shape

            @property
            def __array_interface__(self):
                return None

        rm = data.RasterMask(Dummy(5, 10), 'data', some_property='some_value')

        assert hasattr(rm, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', rm.id)

        assert rm.name == 'data'
        assert rm.size == (10, 5)
        assert rm.width == 10
        assert rm.height == 5

        assert rm.some_property == 'some_value'
        assert rm.__array_interface__ is None

        rm.properties['some_other_property'] = 56
        assert rm.properties['some_other_property'] == 56

    def test_mask_collection(self):
        class Dummy(object):
            def __init__(self, *shape):
                self._shape = shape

            @property
            def shape(self):
                return self._shape

            @property
            def __array_interface__(self):
                return None

        rm = data.RasterMask(Dummy(5, 10), 'raster-data', some_property='some_value')
        vm = data.VectorMask([[[0, 0], [0, 1], [1, 1], [0, 0]]], 'vector-data',
                             some_property='some_value', another_property=45)

        mc = data.MaskCollection(rm, vm)
        mixin_suite(mc)  # Base validity tests

        assert mc[0] == rm
        assert mc[1] == vm

        assert mc['vector-data'] == vm
        assert mc['raster-data'] == rm


class TestData:
    def test_annotation(self):
        import geojson

        class Dummy(object):
            @property
            def __geo_interface__(self):
                return None

        r = data.Record([0, 1, 2], ['car', 'road vehicle'], some_property='some property', another_property=45)
        rc = data.RecordCollection(r, data.Record([[[0, 0], [0, 1], [1, 1], [0, 0]]], ['car', 'road vehicle'],
                                                  some_property='some property', another_property=45))

        vm = data.VectorMask([[[0, 0], [0, 1], [1, 1], [0, 0]]], 'vector-data',
                             some_property='some_value', another_property=45)

        mc = data.MaskCollection(vm)

        with pytest.raises(TypeError, match='Expected "record_collection" to expose the __geo_interface__ attribute'):
            a = data.Annotation(0, mc, some_property='some_value')

        a = data.Annotation(Dummy(), mc, some_property='some_value')
        assert a.__geo_interface__ is None

        a = data.Annotation(rc, mc, some_property='some_value')
        mixin_suite(a)  # Base validity tests

        assert hasattr(a, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', a.id)

        assert a.some_property == 'some_value'
        assert a[0] == r

        assert geojson.dumps(a, sort_keys=True) == '{"features": [' \
                                                   '{"geometry": {"coordinates": [0, 1, 2], "type": "Point"}, ' \
                                                   '"properties": {"another_property": 45, ' \
                                                   '"category": ["car", "road vehicle"], ' \
                                                   '"confidence": null, "some_property": "some property"}, ' \
                                                   '"type": "Feature"}, ' \
                                                   '{"geometry": {"coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]], ' \
                                                   '"type": "Polygon"}, ' \
                                                   '"properties": {"another_property": 45, ' \
                                                   '"category": ["car", "road vehicle"], ' \
                                                   '"confidence": null, ' \
                                                   '"some_property": "some property"}, "type": "Feature"}], ' \
                                                   '"type": "FeatureCollection"}'

    def test_deprecated_data_point(self):
        # Old deprecated interface
        with pytest.deprecated_call():
            dp = data.DataPoint(data.TileWrapper(np.zeros((5, 5, 3)),
                                                 filename='somefile.png',
                                                 some_property='some_value'),
                                data.Annotation(data.RecordCollection()))
        mixin_suite(dp)  # Base validity tests

        with pytest.deprecated_call():
            assert isinstance(dp.tile, data.Tile)

        class DummyGeo(object):
            @property
            def __geo_interface__(self):
                return 0

        class DummyArray(object):
            @property
            def __array_interface__(self):
                return 1

        class DummyTile(data.Tile):
            @property
            def __array_interface__(self):
                return 1

        dp = data.DataPoint(DummyTile(DummyArray()), DummyGeo(), some_property='some_value')

        assert hasattr(dp, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', dp.id)

        assert dp.some_property == 'some_value'

        with pytest.raises(TypeError, match='Expected an ordered dictionary like object as tiles'):
            dp = data.DataPoint(0, DummyGeo(), some_property='some_value')

        with pytest.raises(TypeError, match='Expected "annotation" to expose the __geo_interface__ attribute'):
            dp = data.DataPoint(DummyTile(DummyArray()), 0, some_property='some_value')

    def test_data_point(self, tiles):
        dp = data.DataPoint(tiles,
                            data.Annotation(data.RecordCollection()))
        mixin_suite(dp)  # Base validity tests

        class DummyGeo(object):
            @property
            def __geo_interface__(self):
                return 0

        dp = data.DataPoint(tiles, DummyGeo(), some_property='some_value')

        assert hasattr(dp, 'id')
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', dp.id)

        assert dp.some_property == 'some_value'

        with pytest.raises(TypeError, match='Expected "annotation" to expose the __geo_interface__ attribute'):
            dp = data.DataPoint(tiles, 0, some_property='some_value')

        with pytest.raises(TypeError, match='Expected an ordered dictionary like object as tiles'):
            dp = data.DataPoint({}, DummyGeo(), some_property='some_value')
