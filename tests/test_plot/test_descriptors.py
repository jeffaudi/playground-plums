import string
import random
import copy

import pytest
import numpy as np
from schema import SchemaError

from playground_plums.plot.engine.color import Color, CategoricalColorMap
from playground_plums.commons import RecordCollection, Record
from playground_plums.plot.engine.descriptor import (
    CategoricalDescriptor, ContinuousDescriptor, IntervalDescriptor, Descriptor,
    Labels, Confidence, Area, IntervalArea, IntervalConfidence, _area
)
from playground_plums.plot.engine.color_engine import ColorEngine, ByCategoryDescriptor


class Type(object):
    VALID = 0
    INVALID = 1
    OVERLAP = 2


def _value_generator(size=6, chars=string.ascii_uppercase + string.digits, to_number=False):
    if to_number:
        return 100 * random.random() * random.choice([1.0, -1.0])
    else:
        return ''.join(random.choice(chars) for _ in range(size))


def _make_record(*property_pair):
    r = Record([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]], ('dummy', ), 2.0)
    for property_name, value in property_pair:
        if property_name not in ('labels', 'confidence'):
            r.properties[property_name] = value
    return r


def _make_record_collection(record_number, *property_names, **kwargs):
    to_number = kwargs.pop('to_number', False)
    rc = RecordCollection(*[_make_record(*((property_name, _value_generator(to_number=to_number))
                                           for property_name in property_names))
                            for _ in range(record_number)])
    return rc


def _make_descriptor_test_context(descriptor, name, property_name, rc_type=Type.VALID, update=True, to_number=False):
    if rc_type == Type.VALID:
        # Valid RecordCollection
        rc = _make_record_collection(10, name, to_number=to_number)
    elif rc_type == Type.INVALID:
        # Invalid RecordCollection
        rc = _make_record_collection(10, _value_generator(chars=string.ascii_lowercase + '_'), to_number=to_number)
    elif rc_type == Type.OVERLAP:
        # Overlapping RecordCollection
        rc = _make_record_collection(10, name, property_name, to_number=to_number)
    else:
        raise ValueError('Expected a rc_type value from {}'.format(Type))

    if update:
        descriptor.update(rc)

    return rc


class TestSchema:
    _valid_names = ['valid_name', '__valid_name__', 'valid__name', 'Valid_name']
    _invalid_names = ['invalid-name', 'invalid_name0']

    _valid_properties = ['valid_property', 'valid_property', 'valid__property']
    _invalid_properties = ['Invalid_property', 'invalid-property', 'invalid_property0',
                           '_invalid_property', 'invalid_property_']

    _valid_type = ['categorical', 'continuous']
    _invalid_type = ['other']

    _valid_category = [
        {
            'category': 0
        },
        {
            'category': 0.0
        },
        {
            'category': Color(0, 0, 0)
        },
        {
            'category': CategoricalColorMap(10)
        },
        {
            'category': {
                'category': 0
            },
        },
        {
            'category': {
                'category': 0.0
            },
        },
        {
            'category': {
                'category': Color(0, 0, 0)
            },
        },
        {
            'category': {
                'category': CategoricalColorMap(10)
            },
        },
    ]
    _valid_continuous = [CategoricalColorMap(10), (0, 1)]

    _invalid_category = \
        [
            {
                'category': '0'
            },
            {
                'category': (0, )
            },
            {
                'category': Color(0, 0, 0).components
            },
            {
                'category': CategoricalColorMap(10).map_fn
            },
            {
                'category': {
                    'category': '0'
                },
            },
            {
                'category': {
                    'category': (0, )
                },
            },
            {
                'category': {
                    'category': Color(0, 0, 0).components
                },
            },
            {
                'category': {
                    'category': CategoricalColorMap(10).map_fn
                },
            },
        ] + _valid_continuous

    _invalid_continuous = [CategoricalColorMap(10).map_fn, [0, 1], '0, 1', 0, 0.0] + _valid_category

    @staticmethod
    def _make_test(names, types, properties, schemas):
        for name in names:
            for type_ in types:
                for property_ in properties:
                    for schema in schemas:
                        with pytest.raises(SchemaError):
                            dictionary = {
                                'name': name,
                                'type': type_,
                                'property': property_,
                                'schema': schema
                            }
                            print(dictionary)
                            Descriptor.__interface_schema__.validate(dictionary)

                        class DummyDescriptor(Descriptor):
                            def update(self, *record_collections):
                                pass

                            def compute(self, *record_collections):
                                pass

                            def reset(self):
                                pass

                            def _make_interface(self):
                                return dictionary

                            @property
                            def property_name(self):
                                return property_

                        with pytest.raises(ValueError):
                            descriptor = DummyDescriptor(name)
                            print(descriptor.__descriptor__)

    def test_schema(self):
        # Name
        self._make_test(self._invalid_names, ['categorical'], self._valid_properties, self._valid_category)
        self._make_test(self._invalid_names, ['continuous'], self._valid_properties, self._valid_continuous)

        # Type
        self._make_test(self._valid_names, self._invalid_type, self._valid_properties, self._valid_category)
        self._make_test(self._valid_names, self._invalid_type, self._valid_properties, self._valid_continuous)

        # Property
        self._make_test(self._valid_names, ['categorical'], self._invalid_properties, self._valid_category)
        self._make_test(self._valid_names, ['continuous'], self._invalid_properties, self._valid_continuous)

        # Schema
        self._make_test(self._valid_names, ['categorical'], self._valid_properties, self._invalid_category)
        self._make_test(self._valid_names, ['continuous'], self._valid_properties, self._invalid_continuous)

        # Dependency
        self._make_test(self._valid_names, ['continuous'], self._valid_properties, self._valid_category)
        self._make_test(self._valid_names, ['categorical'], self._valid_properties, self._valid_continuous)


class TestDescriptor:
    @staticmethod  # noqa: R701
    def _make_descriptor_test(descriptor, property_type, name=None, to_number=False, skip_invalid=False, **callbacks):
        assert isinstance(descriptor, Descriptor)

        name = name or descriptor.name

        _internals = copy.deepcopy(descriptor.__dict__)
        _descriptor = copy.deepcopy(descriptor)

        # Test VALID:
        # > Test <update internals>
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.VALID, update=True, to_number=to_number)
        assert not descriptor.__dict__ == _internals
        # >> Test <non equality>
        assert not descriptor == _descriptor
        assert descriptor != _descriptor
        # > Test <__descriptor_interface_>
        print(descriptor.__descriptor__)
        # > Test <update does not add property>
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        # >> Test <equality>
        assert descriptor == _descriptor
        assert not descriptor != _descriptor
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.VALID, update=True, to_number=to_number)
        assert all(not hasattr(record, descriptor.property_name) for record in rc)
        if callbacks.get('valid', {}).get('update', None) is not None:
            callbacks['valid']['update'](descriptor, rc, name)
        # > Test <compute add correct property>
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.VALID, update=True, to_number=to_number)
        rc_c = descriptor.compute(rc)
        assert all(hasattr(record, descriptor.property_name)
                   for record_collection in rc_c
                   for record in record_collection)
        assert all(isinstance(getattr(record, descriptor.property_name), property_type)
                   for record_collection in rc_c
                   for record in record_collection)
        if callbacks.get('valid', {}).get('compute', None) is not None:
            callbacks['valid']['compute'](descriptor, rc, rc_c, name)
        # > Test <no update fails>
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.VALID, update=False, to_number=to_number)
        with pytest.raises(ValueError):
            descriptor.compute(rc)
        assert all(not hasattr(record, descriptor.property_name) for record in rc)

        if not skip_invalid:
            # Test INVALID
            # > Test <update fails>
            descriptor.reset()
            assert descriptor.__dict__ == _internals  # Test reset() validity
            rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                               rc_type=Type.INVALID, update=False, to_number=to_number)
            with pytest.raises(ValueError):
                descriptor.update(rc)
            assert all(not hasattr(record, descriptor.property_name) for record in rc)
            # > Test <compute fails>
            descriptor.reset()
            assert descriptor.__dict__ == _internals  # Test reset() validity
            rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                               rc_type=Type.INVALID, update=False, to_number=to_number)
            with pytest.raises(ValueError):
                descriptor.compute(rc)
            assert all(not hasattr(record, descriptor.property_name) for record in rc)

        # Test OVERLAP:
        # > Test <update internals>
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.OVERLAP, update=True, to_number=to_number)
        assert not descriptor.__dict__ == _internals
        # > Test <update does not add property>
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.OVERLAP, update=False, to_number=to_number)
        properties = [getattr(record, descriptor.property_name) for record in rc]
        descriptor.update(rc)
        assert all(hasattr(record, descriptor.property_name) for record in rc)
        assert all(getattr(record, descriptor.property_name) == properties[i] for i, record in enumerate(rc))
        if callbacks.get('overlap', {}).get('update', None) is not None:
            callbacks['overlap']['update'](descriptor, rc, name)
        # > Test <compute add correct property>
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.OVERLAP, update=False, to_number=to_number)
        properties = [getattr(record, descriptor.property_name) for record in rc]
        descriptor.update(rc)
        rc_c = descriptor.compute(rc)
        assert all(hasattr(record, descriptor.property_name)
                   for record_collection in rc_c
                   for record in record_collection)
        assert all(getattr(record, descriptor.property_name) != properties[i]
                   for record_collection in rc_c
                   for i, record in enumerate(record_collection))
        assert all(isinstance(getattr(record, descriptor.property_name), property_type)
                   for record_collection in rc_c
                   for record in record_collection)
        if callbacks.get('overlap', {}).get('compute', None) is not None:
            callbacks['overlap']['compute'](descriptor, rc, rc_c, name)
        # > Test <no update fails>
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                           rc_type=Type.OVERLAP, update=False, to_number=to_number)
        properties = [getattr(record, descriptor.property_name) for record in rc]
        with pytest.raises(ValueError):
            descriptor.compute(rc)
        assert all(hasattr(record, descriptor.property_name) for record in rc)
        assert all(getattr(record, descriptor.property_name) == properties[i] for i, record in enumerate(rc))

        # Test EMPTY RECORD COLLECTIONS:
        descriptor.reset()
        assert descriptor.__dict__ == _internals  # Test reset() validity
        rc = RecordCollection()
        rc_c = descriptor.compute(rc)
        assert len(rc_c) == 1
        assert len(rc_c[0].records) == 0

    def test_categorical(self):
        def _valid_update(descriptor, rc, name):
            assert len(descriptor._categories) == len(rc)

        def _valid_compute(descriptor, rc, rc_c, name):
            descriptor.reset()
            rc = RecordCollection(*[_make_record(('some_property', str(i % 3))) for i in range(12)])
            descriptor.update(rc)
            assert descriptor._categories == {'0', '1', '2'}
            rc_c = descriptor.compute(rc)[0]
            for i, record in enumerate(rc_c):
                assert record.categorical_descriptor_some_property == (i % 3) + 0.5

        def _overlap_update(descriptor, rc, name):
            assert len(descriptor._categories) == len(rc)

        def _overlap_compute(descriptor, rc, rc_c, name):
            descriptor.reset()
            rc = RecordCollection(*[_make_record(*(('some_property', str(i % 3)),
                                                   ('categorical_descriptor_some_property', 255)))
                                    for i in range(12)])
            descriptor.update(rc)
            assert descriptor._categories == {'0', '1', '2'}
            rc_c = descriptor.compute(rc)[0]
            for i, record in enumerate(rc_c):
                assert record.categorical_descriptor_some_property == (i % 3) + 0.5

        _callbacks = {
            'valid': {
                'update': _valid_update,
                'compute': _valid_compute,
            },
            'overlap': {
                'update': _overlap_update,
                'compute': _overlap_compute,
            }
        }

        descriptor = CategoricalDescriptor('some_property')
        self._make_descriptor_test(descriptor, float, **_callbacks)

    def test_continuous(self):
        def _update(descriptor, rc, name):
            assert descriptor._start != 0
            assert descriptor._end != 0

        def _compute(descriptor, rc, rc_c, name):
            rc_c = rc_c[0]
            assert all(rc[i].some_property == rc_c[i].continuous_descriptor_some_property for i in range(len(rc)))

        _callbacks = {
            'valid': {
                'update': _update,
                'compute': _compute,
            },
            'overlap': {
                'update': _update,
                'compute': _compute,
            }
        }

        descriptor = ContinuousDescriptor('some_property')
        self._make_descriptor_test(descriptor, float, to_number=True, **_callbacks)

    def test_continuous_scale(self):
        def _update(descriptor, rc, name):
            assert descriptor._start != 0
            assert descriptor._end != 0

            descriptor.reset()
            rc = RecordCollection(*[_make_record(('some_property', i + 10)) for i in range(31)])
            descriptor.update(rc)
            assert descriptor._start == 10
            assert descriptor._end == 40

        def _compute(descriptor, rc, rc_c, name):
            rc_c = rc_c[0]
            assert all(0 <= rc_c[i].continuous_descriptor_some_property <= 1 for i in range(len(rc)))

        _callbacks = {
            'valid': {
                'update': _update,
                'compute': _compute,
            },
            'overlap': {
                'update': _update,
                'compute': _compute,
            }
        }

        descriptor = ContinuousDescriptor('some_property', scale=(0, 1))
        self._make_descriptor_test(descriptor, float, to_number=True, **_callbacks)

    def test_interval(self):
        def _update(descriptor, rc, name):
            assert len(descriptor._categories) == 3

        def _compute(descriptor, rc, rc_c, name):
            descriptor.reset()
            rc = RecordCollection(*[_make_record(('some_property', i + 10)) for i in range(31)])
            descriptor.update(rc)
            assert descriptor._categories == ('[10.00, 20.00[', '[20.00, 30.00[', '[30.00, 40.00[')
            rc_c = descriptor.compute(rc[:30])[0]
            for i, record in enumerate(rc_c):
                def make_class(i):
                    if i < 10:
                        return 0.5
                    elif 10 <= i < 20:
                        return 1.5
                    else:
                        return 2.5

                assert record.interval_descriptor_some_property == make_class(i)

            descriptor.reset()

            descr = IntervalDescriptor('some_property', n=2)
            rc = RecordCollection(*[_make_record(('some_property', float(250 * i + np.finfo(np.float32).eps)))
                                    for i in range(21)])
            descr.update(rc)
            assert descr._categories == ('[0.00, 2500.00[', '[2500.00, 5000.00[')
            rc_c = descr.compute(rc)[0]
            for i, record in enumerate(rc_c):
                def make_class(i):
                    if i < 10:
                        return 0.5
                    elif 10 <= i < 21:
                        return 1.5
                    else:
                        return 2.5

                assert record.interval_descriptor_some_property == make_class(i)

        _callbacks = {
            'valid': {
                'update': _update,
                'compute': _compute,
            },
        }

        descriptor = IntervalDescriptor('some_property', n=3)
        self._make_descriptor_test(descriptor, float, to_number=True, **_callbacks)

    def test_color_engine(self):
        def _compute(descriptor, rc, rc_c, name):
            if descriptor._secondary_descriptor is not None:
                assert sorted(descriptor._secondary_descriptor._per_category_descriptors.keys()) == \
                    sorted(descriptor._main_interface['schema'].values())

            assert all(getattr(record, descriptor.property_name).ctype == descriptor.ctype
                       for record_collection in rc_c
                       for record in record_collection)
            descriptor.ctype = 'CAM02-UCS'
            descriptor.reset()
            rc = _make_descriptor_test_context(descriptor, name, descriptor.property_name,
                                               rc_type=Type.VALID, update=True, to_number=True)
            rc_c = descriptor.compute(rc)
            assert all(hasattr(record, descriptor.property_name)
                       for record_collection in rc_c
                       for record in record_collection)
            assert all(isinstance(getattr(record, descriptor.property_name), Color)
                       for record_collection in rc_c
                       for record in record_collection)
            assert all(getattr(record, descriptor.property_name).ctype == descriptor.ctype
                       for record_collection in rc_c
                       for record in record_collection)
            descriptor.ctype = 'sRGB255'

        _callbacks = {
            'valid': {
                'compute': _compute,
            },
            'overlap': {
                'compute': _compute,
            }
        }

        descriptor = ColorEngine(ContinuousDescriptor('color_engine'))
        self._make_descriptor_test(descriptor, Color, name='color_engine', to_number=True, **_callbacks)

        descriptor = ColorEngine(CategoricalDescriptor('color_engine'))
        self._make_descriptor_test(descriptor, Color, name='color_engine', to_number=True, **_callbacks)

        descriptor = ColorEngine(CategoricalDescriptor('color_engine'), ContinuousDescriptor('color_engine'))
        self._make_descriptor_test(descriptor, Color, name='color_engine', to_number=True, **_callbacks)

        descriptor = ColorEngine(CategoricalDescriptor('color_engine'), IntervalDescriptor('color_engine'))
        self._make_descriptor_test(descriptor, Color, name='color_engine', to_number=True, **_callbacks)

    def test_by_category_descriptor(self):
        def _compute(descriptor, rc, rc_c, name):
            pass

        _callbacks = {
            'valid': {
                'compute': _compute,
            },
            'overlap': {
                'compute': _compute,
            }
        }

        descriptor = ByCategoryDescriptor('some_property', ContinuousDescriptor('confidence'))
        descriptor.name = 'some_property'
        self._make_descriptor_test(descriptor, float, to_number=True, **_callbacks)

        descriptor = ByCategoryDescriptor('some_property', CategoricalDescriptor('labels', fetch_fn=lambda x: x[0]))
        descriptor.name = 'some_property'
        self._make_descriptor_test(descriptor, float, to_number=True, **_callbacks)

        descriptor = ByCategoryDescriptor('some_property', IntervalDescriptor('confidence'))
        descriptor.name = 'some_property'
        self._make_descriptor_test(descriptor, float, to_number=True, **_callbacks)

    def test_labels(self):
        descriptor = Labels()
        self._make_descriptor_test(descriptor, float, skip_invalid=True)

    def test_confidence(self):
        descriptor = Confidence()
        self._make_descriptor_test(descriptor, float, skip_invalid=True)

    def test_interval_confidence(self):
        descriptor = IntervalConfidence()
        self._make_descriptor_test(descriptor, float, skip_invalid=True)

    def test_area(self):
        descriptor = Area()
        self._make_descriptor_test(descriptor, float, skip_invalid=True)

    def test_interval_area(self):
        descriptor = IntervalArea()
        self._make_descriptor_test(descriptor, float, skip_invalid=True)


def test_area_computer():
    assert _area([[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                  [[4, 4], [4, 6], [6, 6], [6, 4], [4, 4]]]) == 96.0
    assert _area([[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]) == 100.0
