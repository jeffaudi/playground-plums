import sys
import json
import contextlib

try:
    import unittest.mock as mock
except ImportError:
    import mock

import pytest

from playground_plums.commons.path import Path


@pytest.fixture(scope="module", params=('large', 'small'))
def size(request):
    return request.param


@pytest.fixture(scope="module", params=('json', 'geojson'))
def json_file(request, size):
    if request.param == 'json':
        return Path(__file__)[:-1] / '_data' / '{}.json'.format(size)
    return Path(__file__)[:-1] / '_data' / '{}.geojson'.format(size)


@pytest.fixture(scope='module')
def data(json_file):
    with open(str(json_file), 'r') as f:
        return json.load(f)


@contextlib.contextmanager
def disable_import(*modules):
    with mock.patch.dict(sys.modules, {mod: None for mod in modules}) as context:
        yield [context]


class TestImport:
    @pytest.fixture(autouse=True)
    def clean_up(self):
        # Ugly cleanup
        for module in [module for module in sys.modules if 'playground_plums.dataflow.io.json' in module]:
            try:
                del sys.modules[module]
            except KeyError:
                pass
        try:
            del sys.modules['orjson']
        except KeyError:
            pass
        try:
            del sys.modules['rapidjson']
        except KeyError:
            pass
        try:
            del sys.modules['simplejson']
        except KeyError:
            pass

        yield

    def test_orjson_fail(self):
        with disable_import('orjson'):
            import playground_plums.dataflow.io.json
            assert not playground_plums.dataflow.io.json._HAS_ORJSON
            assert playground_plums.dataflow.io.json._HAS_RAPIDJSON
            assert playground_plums.dataflow.io.json._HAS_SIMPLEJSON

    def test_rapidjson_fail(self):
        with disable_import('rapidjson'):
            import playground_plums.dataflow.io.json
            assert playground_plums.dataflow.io.json._HAS_ORJSON
            assert not playground_plums.dataflow.io.json._HAS_RAPIDJSON
            assert playground_plums.dataflow.io.json._HAS_SIMPLEJSON

    def test_simplejson_fail(self):
        with disable_import('simplejson'):
            import playground_plums.dataflow.io.json
            assert playground_plums.dataflow.io.json._HAS_ORJSON
            assert playground_plums.dataflow.io.json._HAS_RAPIDJSON
            assert not playground_plums.dataflow.io.json._HAS_SIMPLEJSON


class TestIO:
    @pytest.fixture(autouse=True)
    def clean_up(self):
        # Ugly cleanup
        for module in [module for module in sys.modules if 'playground_plums.dataflow.io.json' in module]:
            try:
                del sys.modules[module]
            except KeyError:
                pass
        try:
            del sys.modules['orjson']
        except KeyError:
            pass
        try:
            del sys.modules['rapidjson']
        except KeyError:
            pass
        try:
            del sys.modules['simplejson']
        except KeyError:
            pass

        yield

    @pytest.mark.parametrize('disabled_backend', (('none', ), ('orjson', ),
                                                  ('orjson', 'rapidjson'),
                                                  ('orjson', 'rapidjson', 'simplejson'),
                                                  ('rapidjson', 'simplejson'),
                                                  ('orjson', 'simplejson')), ids=lambda backends: ', '.join(backends))
    def test_load(self, disabled_backend, json_file, data):
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.json import load
            test_data = load(json_file)

        assert data == test_data

    @pytest.mark.parametrize('disabled_backend', (('none', ), ('orjson', ),
                                                  ('orjson', 'rapidjson'),
                                                  ('orjson', 'rapidjson', 'simplejson'),
                                                  ('rapidjson', 'simplejson'),
                                                  ('orjson', 'simplejson')), ids=lambda backends: ', '.join(backends))
    def test_save(self, disabled_backend, json_file, data, tmp_path):
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.json import load, dump
            dump(data, str(tmp_path / 'test.json'))
            test_data = load(str(tmp_path / 'test.json'))

        assert data == test_data
