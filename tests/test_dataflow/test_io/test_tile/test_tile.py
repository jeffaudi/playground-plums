import pytest
import numpy as np

from plums.commons.path import Path
from plums.dataflow.io.tile import Tile, rgb, rgba, bgr, bgra, y


@pytest.fixture(params=('ext', 'no_ext'))
def jpeg_image(request):
    if request.param == 'no_ext':
        return Path(__file__)[:-1] / '_data' / 'test_jpg'
    return Path(__file__)[:-1] / '_data' / 'test_jpg.jpg'


@pytest.fixture(params=('ext', 'no_ext'))
def png_image(request):
    if request.param == 'no_ext':
        return Path(__file__)[:-1] / '_data' / 'test_png'
    return Path(__file__)[:-1] / '_data' / 'test_png.png'


@pytest.fixture(params=('jpg', 'png'))
def image(request, png_image, jpeg_image):
    if request.param == 'jpg':
        return jpeg_image
    return png_image


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


def test_tile(image, tmp_path):  # noqa: R701
    tile = Tile(image)
    assert tile.filename == image
    assert tile.ptype == rgb
    assert tile.dtype == np.uint8
    assert tile.width == tile.height == 512
    assert tile.size == (512, 512)
    assert tile.shape == (512, 512, 3)
    assert tile.shape[2] == 3
    # Additional tests
    properties_container_suite(tile)
    with pytest.raises(TypeError, match='Invalid ptype provided: Only RGB is supported for save operation for now.'):
        tile.save(tmp_path / image[-1], ptype=bgr)
    with pytest.raises(TypeError, match='Invalid ptype provided: Only RGB is supported for save operation for now.'):
        tile.save(tmp_path / image[-1], ptype=rgba)
    with pytest.raises(ValueError):
        tile.save(tmp_path / 'test.xfile')

    # Test conversions
    tile = Tile(image, ptype=bgra)
    assert tile.filename == image
    assert tile.ptype == bgra
    assert tile.dtype == np.uint8
    assert tile.shape[2] == 4

    tile = Tile(image, dtype=np.float64)
    assert tile.filename == image
    assert tile.ptype == rgb
    assert tile.dtype == np.float64
    assert tile.shape[2] == 3

    tile = Tile(image, ptype=bgra, dtype=np.float64)
    assert tile.filename == image
    assert tile.ptype == bgra
    assert tile.dtype == np.float64
    assert tile.shape[2] == 4

    clone = tile.clone()
    assert clone.filename == image
    assert clone.ptype == bgra
    assert clone.dtype == np.float64
    assert clone.shape[2] == 4

    conversion = tile.astype(ptype=y)
    assert conversion.filename == image
    assert conversion.ptype == y
    assert conversion.dtype == np.float64
    assert conversion.shape[2] == 1

    conversion = tile.astype(dtype=np.uint8)
    assert conversion.filename == image
    assert conversion.ptype == bgra
    assert conversion.dtype == np.uint8
    assert conversion.shape[2] == 4

    conversion = tile.astype(ptype=y, dtype=np.uint8)
    assert conversion.filename == image
    assert conversion.ptype == y
    assert conversion.dtype == np.uint8
    assert conversion.shape[2] == 1

    conversion.ptype = bgr
    assert conversion.filename == image
    assert conversion.ptype == bgr
    assert conversion.dtype == np.uint8
    assert conversion.shape[2] == 3

    conversion.dtype = np.float64
    assert conversion.filename == image
    assert conversion.ptype == bgr
    assert conversion.dtype == np.float64
    assert conversion.shape[2] == 3
