from pprint import pformat
from contextlib import contextmanager

import pytest

from playground_plums.model.exception import PlumsModelMetadataValidationError


@contextmanager
def does_not_raise():
    yield

#  'SchemaComponent',
#  'Default',
#  'Path',
#  'MD5Checksum',

#  'ProducerVersion',
#  'Producer',
#  'Format',

#  'Checkpoint',
#  'Training',
#  'Configuration',
#  'InitialisationPath',
#  'InitialisationPMF',
#  'Initialisation',
#  'Model',
#  'Metadata',


def _make_params(name):
    p_valid = tuple('{}-valid-{}'.format(name, i) for i in range(len(globals()['{}_{}'.format('valid', name)])))
    p_invalid = tuple('{}-invalid-{}'.format(name, i) for i in range(len(globals()['{}_{}'.format('invalid', name)])))

    return p_valid + p_invalid


def _parse_param(param):
    name, type_, i = param.split('-')
    return type_ == 'valid', globals()['{}_{}'.format(type_, name)][int(i)]


invalid_path = [
    '/invalid/path/with\x00/zero/byte',
    'invalid/long/component/{}/path'.format('a' * 256)
]

valid_path = [
    '/valid/root/path'
]


@pytest.fixture(params=_make_params('path'))
def path(request):
    return _parse_param(request.param)


invalid_md5 = [
    'A0236a2ae558018ed13b5222ef1bd977',
    '00236a2ae558018ed13b5222ef1bd977a',
    '00236a2ae558018ed13b5222ef1bd97',
    '00236a2ae55801-ed13b5222ef1bd977',
]

valid_md5 = [
    '00236a2ae558018ed13b5222ef1bd977'
]


@pytest.fixture(params=_make_params('md5'))
def md5(request):
    return _parse_param(request.param)


invalid_producer_version = [
    {
        'format': int(),
        'value': str()
    },
    {
        'format': str(),
        'value': int()
    },
]


valid_producer_version = [
    {
        'format': str(),
        'value': str()
    }
]


@pytest.fixture(params=_make_params('producer_version'))
def producer_version(request):
    return _parse_param(request.param)


invalid_producer = [
    {
        'name': '_bc9_Ab56b_5',
        'version': None
    },
    {
        'name': '0bc9_Ab56b_5',
        'version': None
    },
    {
        'name': 'abc9-Ab56b_5',
        'version': None
    },
    {
        'name': 'Abc9_Ab56b_5\x00',
        'version': None
    },
]


valid_producer = [
    {
        'name': 'abc9_Ae56b_5',
        'version': None
    },
]


@pytest.fixture(params=_make_params('producer'))
def producer(request, producer_version):
    fixt = _parse_param(request.param)
    fixt[1]['version'] = producer_version[1]
    return fixt[0] and producer_version[0], fixt[1]


@pytest.fixture()
def producer_no_param():
    producer_version = _parse_param('producer_version-valid-0')
    fixt = _parse_param('producer-valid-0')
    fixt[1]['version'] = producer_version[1]
    return fixt[0] and producer_version[0], fixt[1]


invalid_format = [
    {
        'version': 1.0,
        'producer': None
    },
    {
        'version': str(),
        'producer': None
    },
]

valid_format = [
    {
        'version': '1.0.0',
        'producer': None
    }
]


@pytest.fixture(params=_make_params('format'))
def format(request, producer):
    fixt = _parse_param(request.param)
    fixt[1]['producer'] = producer[1]
    return fixt[0] and producer[0], fixt[1]


@pytest.fixture(params=_make_params('format'))
def format_low_param(request, producer_no_param):
    producer = producer_no_param
    fixt = _parse_param(request.param)
    fixt[1]['producer'] = producer[1]
    return fixt[0] and producer[0], fixt[1]


invalid_checkpoint = [
    {
        (0, ): {
            'epoch': 1,
            'path': None,
            'hash': None,
        }
    },
    {
        '0': {
            'epoch': str(),
            'path': None,
            'hash': None,
        }
    },
    {
        0: {
            'epoch': str(),
            'path': None,
            'hash': None,
        }
    },
]


valid_checkpoint = [
    {
        1: {
            'epoch': 1,
            'path': None,
            'hash': None,
        }
    },
    {
        '1': {
            'epoch': 1,
            'path': None,
            'hash': None,
        }
    },
    {}
]


@pytest.fixture(params=_make_params('checkpoint'))
def checkpoint(request, path, md5):
    fixt = _parse_param(request.param)
    if fixt[1]:
        for key in fixt[1]:
            fixt[1][key]['path'] = path[1]
            fixt[1][key]['hash'] = md5[1]
        return fixt[0] and path[0] and md5[0], fixt[1]
    return fixt


@pytest.fixture()
def checkpoint_no_param():
    path = _parse_param('path-valid-0')
    md5 = _parse_param('md5-valid-0')
    fixt = _parse_param('checkpoint-valid-0')
    if fixt[1]:
        for key in fixt[1]:
            fixt[1][key]['path'] = path[1]
            fixt[1][key]['hash'] = md5[1]
        return fixt[0] and path[0] and md5[0], fixt[1]
    return fixt


invalid_training = [
    {
        'status': 'pending',
        'start_time': None,
        'latest_time': None,
        'end_time': 1,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': 1,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'running',
        'start_time': None,
        'latest_time': 1,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': 1,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'running',
        'start_time': None,
        'latest_time': 1,
        'end_time': 10,
        'start_epoch': None,
        'latest_epoch': 1,
        'end_epoch': 10,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'pending',
        'start_time': None,
        'latest_time': None,
        'end_time': 1,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'running',
        'start_time': None,
        'latest_time': 1,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'finished',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': 1,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': 1,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'pending',
        'start_time': 0,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'running',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': 0,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 9,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 9,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 0,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 0,
        'end_time': 0,
        'start_epoch': 0,
        'latest_epoch': 0,
        'end_epoch': 0,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': '',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': '0',
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': '10',
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': '10',
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': '0',
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': '10',
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': '10',
        'latest': 1,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': '10',
        'checkpoints': None
    },
]


valid_training = [
    {
        'status': 'pending',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'running',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'finished',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': None,
        'latest_time': None,
        'end_time': None,
        'start_epoch': None,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': None,
        'end_time': None,
        'start_epoch': 0,
        'latest_epoch': None,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': None,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': None,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': None,
        'checkpoints': None
    },
    {
        'status': 'failed',
        'start_time': 0,
        'latest_time': 10,
        'end_time': 10,
        'start_epoch': 0,
        'latest_epoch': 10,
        'end_epoch': 10,
        'latest': 1,
        'checkpoints': None
    },
]


@pytest.fixture(params=_make_params('training'))
def training(request, checkpoint):
    fixt = _parse_param(request.param)
    if checkpoint[0] and checkpoint[1].get('1') is not None:
        checkpoint[1][1] = checkpoint[1]['1']
    fixt[1]['checkpoints'] = checkpoint[1]
    if not fixt[1]['checkpoints'] and request.param.split('-')[2] in ['10', '11', '19']:
        fixt = (True, fixt[1])
    return fixt[0] and checkpoint[0], fixt[1]


@pytest.fixture()
def training_low_param(request, checkpoint_no_param):
    checkpoint = checkpoint_no_param
    fixt = _parse_param('training-valid-0')
    if checkpoint[0] and checkpoint[1].get('1') is not None:
        checkpoint[1][1] = checkpoint[1]['1']
    fixt[1]['checkpoints'] = checkpoint[1]
    if not fixt[1]['checkpoints'] and request.param.split('-')[2] in ['10', '11', '19']:
        fixt = (True, fixt[1])
    return fixt[0] and checkpoint[0], fixt[1]


@pytest.fixture()
def configuration(path, md5):
    return path[0] and md5[0], {'path': path[1], 'hash': md5[1]}


invalid_initialisation = [
    {
        '': {}
    },
    {
        'pmf': {}
    },
    {
        'file': {}
    },
    {
        'pmf': {
            'name': 0,
            'id': '',
            'checkpoint': '',
            'path': None
        }
    },
    {
        'pmf': {
            'name': None,
            'id': 0,
            'checkpoint': '',
            'path': None
        }
    },
    {
        'pmf': {
            'name': None,
            'id': '',
            'checkpoint': (0, ),
            'path': None
        }
    },
    {
        'file': {
            'name': 0,
            'path': None,
            'hash': None
        }
    },
]

valid_initialisation = [
    None,
    {
        'pmf': {
            'name': '',
            'id': '',
            'checkpoint': '',
            'path': None
        }
    },
    {
        'file': {
            'name': '',
            'path': None,
            'hash': None
        }
    },
]


@pytest.fixture(params=_make_params('initialisation'))
def initialisation(request, path, md5):
    fixt = _parse_param(request.param)
    if fixt[1] is None:
        return True, None
    if fixt[1].get('pmf') is not None:
        fixt[1]['pmf']['path'] = path[1]
        return fixt[0] and path[0], fixt[1]
    if fixt[1].get('file') is not None:
        fixt[1]['file']['path'] = path[1]
        fixt[1]['file']['hash'] = md5[1]
        return fixt[0] and path[0] and md5[0], fixt[1]
    return fixt


@pytest.fixture(params=_make_params('initialisation'))
def initialisation_low_param(request):
    path = _parse_param('path-valid-0')
    md5 = _parse_param('md5-valid-0')
    fixt = _parse_param(request.param)
    if fixt[1] is None:
        return True, None
    if fixt[1].get('pmf') is not None:
        fixt[1]['pmf']['path'] = path[1]
        return fixt[0] and path[0], fixt[1]
    if fixt[1].get('file') is not None:
        fixt[1]['file']['path'] = path[1]
        fixt[1]['file']['hash'] = md5[1]
        return fixt[0] and path[0] and md5[0], fixt[1]
    return fixt


invalid_model = [
    {
        'name': 0,
        'id': '',
        'initialisation': None,
        'training': None,
        'configuration': None
    },
    {
        'name': '',
        'id': 0,
        'initialisation': None,
        'training': None,
        'configuration': None
    },
]


valid_model = [
    {
        'name': None,
        'id': '',
        'initialisation': None,
        'training': None,
        'configuration': None
    },
    {
        'name': '',
        'id': '',
        'initialisation': None,
        'training': None,
        'configuration': None
    },
]


@pytest.fixture(params=_make_params('model'))
def model(request, initialisation_low_param, training_low_param, configuration):
    initialisation = initialisation_low_param
    training = training_low_param
    fixt = _parse_param(request.param)
    fixt[1]['initialisation'] = initialisation[1]
    fixt[1]['training'] = training[1]
    fixt[1]['configuration'] = configuration[1]
    return fixt[0] and initialisation[0] and training[0] and configuration[0], fixt[1]


@pytest.fixture()
def metadata(format_low_param, model):
    format = format_low_param
    return format[0] and model[0], {'format': format[1], 'model': model[1]}


def test_metadata(metadata):
    from playground_plums.model.validation.metadata import Metadata as Schema

    schema = Schema(verbose=False)

    passes, data = metadata

    print('Expected to pass: {}'.format(passes))
    print('On: {}'.format(pformat(data)))

    ctx = does_not_raise() if passes else pytest.raises(PlumsModelMetadataValidationError)

    with ctx:
        schema.validate(data)

    assert schema.is_valid(data) == passes


def test_initialisation(initialisation):
    from playground_plums.model.validation.metadata import Initialisation as Schema

    schema = Schema(verbose=False)

    passes, data = initialisation

    print('Expected to pass: {}'.format(passes))
    print('On: {}'.format(pformat(data)))

    ctx = does_not_raise() if passes else pytest.raises(PlumsModelMetadataValidationError)

    with ctx:
        schema.validate(data)

    assert schema.is_valid(data) == passes


def test_training(training):
    from playground_plums.model.validation.metadata import Training as Schema

    schema = Schema(verbose=False)

    passes, data = training

    print('Expected to pass: {}'.format(passes))
    print('On: {}'.format(pformat(data)))

    ctx = does_not_raise() if passes else pytest.raises(PlumsModelMetadataValidationError)

    with ctx:
        schema.validate(data)

    assert schema.is_valid(data) == passes


def test_format(format):
    from playground_plums.model.validation.metadata import Format as Schema

    schema = Schema(verbose=False)

    passes, data = format

    print('Expected to pass: {}'.format(passes))
    print('On: {}'.format(pformat(data)))

    ctx = does_not_raise() if passes else pytest.raises(PlumsModelMetadataValidationError)

    with ctx:
        schema.validate(data)

    assert schema.is_valid(data) == passes
