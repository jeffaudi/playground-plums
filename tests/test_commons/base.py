import re

import pytest

from playground_plums.commons.data.mixin import PropertyContainer, IdentifiedMixIn


def identified_suite(obj):
    assert hasattr(obj, 'id')
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z', obj.id)


def properties_container_suite(obj):
    # Check that properties exists and it's a dictionary
    assert hasattr(obj, 'properties')
    assert isinstance(obj.properties, dict)

    # Add properties
    obj.properties['foo'] = 'bar'
    obj.properties['bar'] = 5

    # Check that properties are accessible as attributes and as keys
    assert hasattr(obj, 'foo')
    assert hasattr(obj, 'bar')
    assert 'foo' in obj.properties
    assert 'bar' in obj.properties

    # Check that properties populate __dir__
    assert 'foo' in dir(obj)
    assert 'bar' in dir(obj)

    # Check that __getattr__ does not allow non-existing attributes or keys
    assert not hasattr(obj, 'foobar')

    # Check that properties value change works and does not create a new attribute
    obj.foo = 'foobar'
    with pytest.raises(KeyError):
        print(obj.__dict__['foo'])
    assert obj.properties['foo'] == 'foobar'

    # Check that attribute creation works and that new attributes are genuine and not properties in disguise
    obj.foobar = 'foo'
    assert hasattr(obj, 'foobar')
    with pytest.raises(KeyError):
        print(obj.properties['foobar'])

    # Check that properties deletion works
    del obj.foo
    with pytest.raises(KeyError):
        print(obj.__dict__['foo'])
    assert 'foo' not in obj.properties
    assert not hasattr(obj, 'foo')

    # Check that attribute deletion works
    del obj.foobar
    assert not hasattr(obj, 'foobar')
    with pytest.raises(KeyError):
        print(obj.properties['foobar'])

    # Test deep copy
    from copy import deepcopy
    obj_copy = deepcopy(obj)
    assert obj is not obj_copy
    assert obj.properties == obj_copy.properties

    # Test pickling
    import pickle
    from pickle import dumps, loads
    obj_pickle = loads(dumps(obj, protocol=max(2, getattr(pickle, 'DEFAULT_PROTOCOL', 0))))
    assert obj is not obj_pickle
    assert obj.properties == obj_pickle.properties

    # Cleanup
    del obj.bar


def mixin_suite(obj):
    if isinstance(obj, IdentifiedMixIn):
        identified_suite(obj)
    if isinstance(obj, PropertyContainer):
        properties_container_suite(obj)
