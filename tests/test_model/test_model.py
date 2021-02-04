import os
import string

import pytest

from plums.commons.path import Path
from plums.model import Producer, CheckpointCollection, Training
from plums.model.components.utils import is_duplicate, copy, rmtree, Checkpoint, md5_checksum
from plums.model.model import Model, initialisation

__char_index = -1


def _char_generator(size=256, chars=string.ascii_uppercase + string.digits, to_bytes=False):
    global __char_index
    __char_index = (__char_index + 1) % len(chars)
    if to_bytes:
        return (chars[__char_index] * size).encode()
    else:
        return chars[__char_index] * size


@pytest.fixture()
def tmp_files(tmp_path):
    tmp_path = Path(tmp_path)

    with open(str(tmp_path / 'small_0.text'), 'w') as f:
        f.write(_char_generator(size=1024))

    with open(str(tmp_path / 'small_0.binary'), 'wb') as f:
        f.write(_char_generator(size=1024, to_bytes=True))

    with open(str(tmp_path / 'large_0.text'), 'w') as f:
        f.write(_char_generator(size=4194304))

    with open(str(tmp_path / 'large_0.binary'), 'wb') as f:
        f.write(_char_generator(size=4194304, to_bytes=True))

    with open(str(tmp_path / 'small_1.text'), 'w') as f:
        f.write(_char_generator(size=1024))

    with open(str(tmp_path / 'small_1.binary'), 'wb') as f:
        f.write(_char_generator(size=1024, to_bytes=True))

    with open(str(tmp_path / 'large_1.text'), 'w') as f:
        f.write(_char_generator(size=4194304))

    with open(str(tmp_path / 'large_1.binary'), 'wb') as f:
        f.write(_char_generator(size=4194304, to_bytes=True))

    with open(str(tmp_path / 'small_2.text'), 'w') as f:
        f.write(_char_generator(size=1025))

    with open(str(tmp_path / 'small_2.binary'), 'wb') as f:
        f.write(_char_generator(size=1025, to_bytes=True))

    with open(str(tmp_path / 'large_2.text'), 'w') as f:
        f.write(_char_generator(size=4194305))

    with open(str(tmp_path / 'large_2.binary'), 'wb') as f:
        f.write(_char_generator(size=4194305, to_bytes=True))

    yield tmp_path

    os.remove(str(tmp_path / 'large_2.binary'))
    os.remove(str(tmp_path / 'large_2.text'))
    os.remove(str(tmp_path / 'small_2.binary'))
    os.remove(str(tmp_path / 'small_2.text'))

    os.remove(str(tmp_path / 'large_1.binary'))
    os.remove(str(tmp_path / 'large_1.text'))
    os.remove(str(tmp_path / 'small_1.binary'))
    os.remove(str(tmp_path / 'small_1.text'))

    os.remove(str(tmp_path / 'large_0.binary'))
    os.remove(str(tmp_path / 'large_0.text'))
    os.remove(str(tmp_path / 'small_0.binary'))
    os.remove(str(tmp_path / 'small_0.text'))


def test_initialisation(valid_tree):
    os.symlink(str(valid_tree / 'nowhere'), str(valid_tree / 'broken-link'))
    os.symlink(str(valid_tree / 'self-link'), str(valid_tree / 'self-link'))

    with pytest.raises(OSError, match='does not exists'):
        initialisation(valid_tree / 'nowhere')

    with pytest.raises(OSError, match='does not exists'):
        initialisation(valid_tree / 'broken-link')

    with pytest.raises(OSError, match='does not exists'):
        initialisation(valid_tree / 'self-link')

    with pytest.raises(OSError, match='must either be a PMF model or a weight file'):
        initialisation(valid_tree / 'data')

    with pytest.raises(ValueError, match='points to a file but name is None'):
        initialisation(valid_tree / 'data' / 'checkpoints' / '6.weight')

    with pytest.raises(ValueError, match='points to a PMF model but no checkpoint reference was given'):
        initialisation(valid_tree)

    with pytest.raises(ValueError, match='points to a PMF model which does not contains'):
        initialisation(valid_tree, checkpoint_reference=10)

    assert isinstance(initialisation(valid_tree / 'data' / 'checkpoints' / '6.weight', name='MyInit'), Checkpoint)
    assert isinstance(initialisation(valid_tree, checkpoint_reference=6), Model)

    assert isinstance(initialisation(valid_tree / 'data' / 'checkpoints' / '6.weight',
                                     name='MyInit',
                                     checkpoint_reference=6), Checkpoint)
    assert isinstance(initialisation(valid_tree, checkpoint_reference=6, name='MyInit'), Model)


class TestDuplicate:  # noqa: R701
    def test_is_duplicate(self, tmp_files):  # noqa: R701
        assert is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_0.text')
        assert not is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_1.text')
        assert not is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_2.text')
        assert not is_duplicate(tmp_files / 'small_1.text', tmp_files / 'small_2.text')

        assert is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_1.text',
                            hash_2=md5_checksum(tmp_files / 'small_0.text'))
        assert not is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_2.text',
                                hash_2=md5_checksum(tmp_files / 'small_0.text'))
        assert not is_duplicate(tmp_files / 'small_1.text', tmp_files / 'small_2.text',
                                hash_2=md5_checksum(tmp_files / 'small_0.text'))

        assert is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_0.binary')
        assert not is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary')
        assert not is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_2.binary')
        assert not is_duplicate(tmp_files / 'small_1.binary', tmp_files / 'small_2.binary')

        assert is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary',
                            hash_2=md5_checksum(tmp_files / 'small_0.binary'))
        assert not is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_2.binary',
                                hash_2=md5_checksum(tmp_files / 'small_0.binary'))
        assert not is_duplicate(tmp_files / 'small_1.binary', tmp_files / 'small_2.binary',
                                hash_2=md5_checksum(tmp_files / 'small_0.binary'))

        assert is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_0.text')
        assert not is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_1.text')
        assert not is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_2.text')
        assert not is_duplicate(tmp_files / 'large_1.text', tmp_files / 'large_2.text')

        assert is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_1.text',
                            hash_2=md5_checksum(tmp_files / 'large_0.text'))
        assert not is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_2.text',
                                hash_2=md5_checksum(tmp_files / 'large_0.text'))
        assert not is_duplicate(tmp_files / 'large_1.text', tmp_files / 'large_2.text',
                                hash_2=md5_checksum(tmp_files / 'large_0.text'))

        assert is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_0.binary')
        assert not is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary')
        assert not is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_2.binary')
        assert not is_duplicate(tmp_files / 'large_1.binary', tmp_files / 'large_2.binary')

        assert is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary',
                            hash_2=md5_checksum(tmp_files / 'large_0.binary'))
        assert not is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_2.binary',
                                hash_2=md5_checksum(tmp_files / 'large_0.binary'))
        assert not is_duplicate(tmp_files / 'large_1.binary', tmp_files / 'large_2.binary',
                                hash_2=md5_checksum(tmp_files / 'large_0.binary'))

        assert is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_1.text',
                            hash_1=md5_checksum(tmp_files / 'small_1.text'))
        assert not is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_2.text',
                                hash_1=md5_checksum(tmp_files / 'small_2.text'))
        assert not is_duplicate(tmp_files / 'small_1.text', tmp_files / 'small_2.text',
                                hash_1=md5_checksum(tmp_files / 'small_2.text'))

        assert is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary',
                            hash_1=md5_checksum(tmp_files / 'small_1.binary'))
        assert not is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_2.binary',
                                hash_1=md5_checksum(tmp_files / 'small_2.binary'))
        assert not is_duplicate(tmp_files / 'small_1.binary', tmp_files / 'small_2.binary',
                                hash_1=md5_checksum(tmp_files / 'small_2.binary'))

        assert is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_1.text',
                            hash_1=md5_checksum(tmp_files / 'large_1.text'))
        assert not is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_2.text',
                                hash_1=md5_checksum(tmp_files / 'large_2.text'))
        assert not is_duplicate(tmp_files / 'large_1.text', tmp_files / 'large_2.text',
                                hash_1=md5_checksum(tmp_files / 'large_2.text'))

        assert is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary',
                            hash_1=md5_checksum(tmp_files / 'large_1.binary'))
        assert not is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_2.binary',
                                hash_1=md5_checksum(tmp_files / 'large_2.binary'))
        assert not is_duplicate(tmp_files / 'large_1.binary', tmp_files / 'large_2.binary',
                                hash_1=md5_checksum(tmp_files / 'large_2.binary'))

    def test_copy(self, tmp_files):
        with pytest.raises(OSError, match='exists but is not a file'):
            copy(tmp_files / 'small_0.text', tmp_files, lazy=True,
                 dst_hash=md5_checksum(tmp_files / 'small_0.text'))

        with pytest.raises(OSError, match='is not a file'):
            copy(tmp_files, tmp_files / 'small_1.text', lazy=True,
                 dst_hash=md5_checksum(tmp_files / 'small_0.text'))

        with pytest.raises(OSError, match='is not a file'):
            copy(tmp_files / 'nowhere', tmp_files / 'small_1.text', lazy=True,
                 dst_hash=md5_checksum(tmp_files / 'small_0.text'))

        copy(tmp_files / 'small_0.text', tmp_files / 'nowhere', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_0.text'))
        assert is_duplicate(tmp_files / 'small_0.text', tmp_files / 'nowhere')

        copy(tmp_files / 'small_0.text', tmp_files / 'small_0.text', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_1.text'))  # Copy on itself do not do anything
        copy(tmp_files / 'small_0.text', tmp_files / 'small_1.text', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_0.text'))  # Lazy copy do not do anything
        assert not is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_1.text')
        copy(tmp_files / 'small_0.text', tmp_files / 'small_2.text', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_0.text'))  # Lazy copy do it anyway (size difference)
        assert is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_2.text')
        copy(tmp_files / 'small_0.text', tmp_files / 'small_1.text', lazy=False,
             dst_hash=md5_checksum(tmp_files / 'small_0.text'))  # True copy do it anyway
        assert is_duplicate(tmp_files / 'small_0.text', tmp_files / 'small_1.text')

        copy(tmp_files / 'small_0.binary', tmp_files / 'small_0.binary', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_1.binary'))  # Copy on itself do not do anything
        copy(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_0.binary'))  # Lazy copy do not do anything
        assert not is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary')
        copy(tmp_files / 'small_0.binary', tmp_files / 'small_2.binary', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'small_0.binary'))  # Lazy copy do it anyway (size difference)
        assert is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_2.binary')
        copy(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary', lazy=False,
             dst_hash=md5_checksum(tmp_files / 'small_0.binary'))  # True copy do it anyway
        assert is_duplicate(tmp_files / 'small_0.binary', tmp_files / 'small_1.binary')

        copy(tmp_files / 'large_0.text', tmp_files / 'large_0.text', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'large_1.text'))  # Copy on itself do not do anything
        copy(tmp_files / 'large_0.text', tmp_files / 'large_1.text', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'large_0.text'))  # Lazy copy do not do anything
        assert not is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_1.text')
        copy(tmp_files / 'large_0.text', tmp_files / 'large_2.text', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'large_0.text'))  # Lazy copy do it anyway (size difference)
        assert is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_2.text')
        copy(tmp_files / 'large_0.text', tmp_files / 'large_1.text', lazy=False,
             dst_hash=md5_checksum(tmp_files / 'large_0.text'))  # True copy do it anyway
        assert is_duplicate(tmp_files / 'large_0.text', tmp_files / 'large_1.text')

        copy(tmp_files / 'large_0.binary', tmp_files / 'large_0.binary', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'large_1.text'))  # Copy on itself do not do anything
        copy(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'large_0.binary'))  # Lazy copy do not do anything
        assert not is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary')
        copy(tmp_files / 'large_0.binary', tmp_files / 'large_2.binary', lazy=True,
             dst_hash=md5_checksum(tmp_files / 'large_0.binary'))  # Lazy copy do it anyway (size difference)
        assert is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_2.binary')
        copy(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary', lazy=False,
             dst_hash=md5_checksum(tmp_files / 'large_0.binary'))  # True copy do it anyway
        assert is_duplicate(tmp_files / 'large_0.binary', tmp_files / 'large_1.binary')


class TestRmtree:
    def test_valid(self, valid_tree):
        rmtree(valid_tree, black_list=('metadata', 'my_config_file.yaml'))
        assert not valid_tree.exists()

    def test_valid_empty(self, valid_tree_empty):
        rmtree(valid_tree_empty, black_list=('metadata', 'my_config_file.yaml'))
        assert not valid_tree_empty.exists()

    def test_valid_extra(self, valid_tree_extra):
        rmtree(valid_tree_extra, black_list=('metadata', 'my_config_file.yaml'))
        assert len(tuple(valid_tree_extra.rglob('*'))) == 18  # 15 files and 3 directories

    def test_invalid_strict(self, invalid_tree_strict):
        rmtree(invalid_tree_strict, black_list=('metadata', 'my_config_file.yaml'))
        assert not invalid_tree_strict.exists()

    def test_invalid(self, invalid_tree_with_name):
        name, invalid_tree = invalid_tree_with_name
        rmtree(invalid_tree, black_list=('metadata', 'my_config_file.yaml'))

        if 'missing' in name:
            if 'extra' in name:
                assert 0 < len(tuple(invalid_tree.rglob('*'))) <= 18  # 15 files and 3 directories
            else:
                assert not invalid_tree.exists()
        elif 'discrepancy' in name:
            assert not invalid_tree.exists()
        elif name == 'invalid-tree-content-5' or name == 'invalid-tree-content-8' or \
                name == 'invalid-tree-content-9' or name == 'invalid-tree-content-10' or \
                name == 'invalid-tree-content-11' or name == 'invalid-tree-content-12':
            assert not invalid_tree.exists()
        elif name == 'invalid-tree-content-6':
            assert len(tuple(invalid_tree.rglob('*'))) == 1 and \
                tuple(invalid_tree.listdir()) == ('my_config_file_0.yaml',)
        elif name == 'invalid-tree-content-7':
            assert len(tuple(invalid_tree.rglob('*'))) == 3 and \
                tuple((invalid_tree / 'data' / 'initialisation').listdir()) == ('my_config_file_0.yaml',)
        else:
            raise AssertionError('Invalid test name')


def _model_equal(model_1, model_2):
    if not model_1.producer.strict_equals(model_2.producer):
        print('Producer fail: {} != {}'.format(model_1.producer, model_2.producer))
        return False
    if model_1.checkpoint_collection != model_2.checkpoint_collection:
        print('Checkpoint Collection fail: {} != {}'.format(model_1.checkpoint_collection,
                                                            model_2.checkpoint_collection))
        return False
    if model_1.training.status != model_2.training.status or \
            model_1.training.start_epoch != model_2.training.start_epoch or \
            model_1.training.start_timestamp != model_2.training.start_timestamp or \
            model_1.training.latest_epoch != model_2.training.latest_epoch or \
            model_1.training.latest_timestamp != model_2.training.latest_timestamp or \
            model_1.training.end_epoch != model_2.training.end_epoch or \
            model_1.training.end_timestamp != model_2.training.end_timestamp:
        print('Training fail: {} != {}'.format(model_1.training, model_2.training))
        return False
    if isinstance(model_1.initialisation, Model) and isinstance(model_2.initialisation, Model):
        return _model_equal(model_1.initialisation, model_2.initialisation)
    elif isinstance(model_1.initialisation, Checkpoint) and isinstance(model_2.initialisation, Checkpoint) and \
            model_1.initialisation != model_2.initialisation:
        print('Initialisation fail: {} != {}'.format(model_1.initialisation, model_2.initialisation))
        return False
    elif not isinstance(model_1.initialisation, model_2.initialisation.__class__):
        print('Initialisation fail: {} != {}'.format(model_1.initialisation, model_2.initialisation))
        return False

    return True


class TestModel:
    def test_creation(self, valid_tree):
        model = Model('my-producer',
                      'py_pa',
                      '1.0.0',
                      'my-model',
                      'my-model-id',
                      valid_tree / 'my_config_file.yaml',
                      {'my_param': 'my_value'})

        assert model.name == 'my-model'
        assert model.id == 'my-model-id'
        assert Producer('my-producer',
                        'py_pa',
                        '1.0.0',
                        valid_tree / 'my_config_file.yaml').strict_equals(model.producer)
        assert isinstance(model.checkpoint_collection, CheckpointCollection)
        assert len(model.checkpoint_collection) == 0
        assert isinstance(model.training, Training)
        assert model.training.is_pending
        assert model.initialisation is None
        assert model.path is None
        assert model.checkpoint is None

    def test_initialisation(self, valid_tree):
        model = Model('my-producer',
                      'py_pa',
                      '1.0.0',
                      'my-model',
                      'my-model-id',
                      valid_tree / 'my_config_file.yaml',
                      {'my_param': 'my_value'})

        assert model.initialisation is None
        model.register_initialisation(valid_tree, checkpoint_reference=6)
        assert isinstance(model.initialisation, Model)
        assert model.initialisation.checkpoint == 6

    def test_checkpoint(self, valid_tree):
        model = Model('my-producer',
                      'py_pa',
                      '1.0.0',
                      'my-model',
                      'my-model-id',
                      valid_tree / 'my_config_file.yaml',
                      {'my_param': 'my_value'})

        assert len(model.checkpoint_collection) == 0
        checkpoint_1 = Checkpoint('first', valid_tree / 'data' / 'checkpoints' / '1.weight', 1)
        checkpoint_6 = Checkpoint('sixth', valid_tree / 'data' / 'checkpoints' / '6.weight', 6)
        model.add_checkpoint(checkpoint_1)
        assert len(model.checkpoint_collection) == 1
        assert model.checkpoint_collection['first'] == checkpoint_1
        model.add_checkpoint(checkpoint_6)
        assert len(model.checkpoint_collection) == 2
        assert model.checkpoint_collection['sixth'] == checkpoint_6

        model = Model('my-producer',
                      'py_pa',
                      '1.0.0',
                      'my-model',
                      'my-model-id',
                      valid_tree / 'my_config_file.yaml',
                      {'my_param': 'my_value'})

        assert len(model.checkpoint_collection) == 0
        checkpoint_1 = Checkpoint('first', valid_tree / 'data' / 'checkpoints' / '1.weight', 1)
        checkpoint_6 = Checkpoint('sixth', valid_tree / 'data' / 'checkpoints' / '6.weight', 6)
        model.add_checkpoint(checkpoint_1, checkpoint_6)
        assert len(model.checkpoint_collection) == 2
        assert model.checkpoint_collection['first'] == checkpoint_1
        assert model.checkpoint_collection['sixth'] == checkpoint_6

    def test_training(self, valid_tree):
        model = Model('my-producer',
                      'py_pa',
                      '1.0.0',
                      'my-model',
                      'my-model-id',
                      valid_tree / 'my_config_file.yaml',
                      {'my_param': 'my_value'})

        assert model.training.is_pending
        model.register_training_start(5)
        assert model.training.is_running
        assert model.training.start_epoch == 5
        assert model.training.latest_epoch == 5
        model.register_epoch()
        assert model.training.latest_epoch == 6
        model.register_epoch(15)
        assert model.training.latest_epoch == 15
        model.register_epoch()
        assert model.training.latest_epoch == 16
        model.register_training_end(success=True)
        assert model.training.is_finished
        assert model.training.end_epoch == 16

        model = Model('my-producer',
                      'py_pa',
                      '1.0.0',
                      'my-model',
                      'my-model-id',
                      valid_tree / 'my_config_file.yaml',
                      {'my_param': 'my_value'})

        assert model.training.is_pending
        model.register_training_start(5)
        assert model.training.is_running
        assert model.training.start_epoch == 5
        assert model.training.latest_epoch == 5
        model.register_epoch()
        assert model.training.latest_epoch == 6
        model.register_epoch(15)
        assert model.training.latest_epoch == 15
        model.register_epoch()
        assert model.training.latest_epoch == 16
        model.register_training_end(success=False)
        assert model.training.is_failed
        assert model.training.end_epoch == 16

    def test_load(self, valid_tree):
        reference_model = Model('a_producer_name',
                                'py_pa',
                                '1.0.0',
                                'my_model',
                                'some_id',
                                valid_tree / 'my_config_file.yaml',
                                {})

        reference_model._initialisation = Model('a_producer_name',
                                                'py_pa',
                                                '1.0.0',
                                                'my_init_model',
                                                'some_init_id',
                                                valid_tree / 'data' / 'initialisation' / 'my_config_file.yaml',
                                                {})

        reference_model.initialisation._initialisation = \
            Checkpoint('my_init_file',
                       valid_tree / 'data' / 'initialisation' / 'data' / 'initialisation' / 'init.weight',
                       hash='d41d8cd98f00b204e9800998ecf8427e')

        checkpoint_1 = Checkpoint(1, valid_tree / 'data' / 'checkpoints' / '1.weight', 3,
                                  hash='d41d8cd98f00b204e9800998ecf8427e')
        checkpoint_6 = Checkpoint(6, valid_tree / 'data' / 'checkpoints' / '6.weight', 10,
                                  hash='cfcd208495d565ef66e7dff9f98764da')

        init_checkpoint_6 = Checkpoint(6,
                                       epoch=10,
                                       hash='cfcd208495d565ef66e7dff9f98764da')

        init_checkpoint_7 = Checkpoint(7,
                                       epoch=9,
                                       hash='cfcd208495d565ef66e7dff9f98764da')

        reference_model.add_checkpoint(checkpoint_1, checkpoint_6)
        reference_model.initialisation.add_checkpoint(init_checkpoint_6, init_checkpoint_7)

        reference_model.training = Training(**{'status': 'finished',
                                               'start_epoch': 0,
                                               'start_time': 0,
                                               'latest_epoch': 10,
                                               'latest_time': 10,
                                               'end_epoch': 10,
                                               'end_time': 10})

        reference_model.initialisation.training = Training(**{'status': 'finished',
                                                              'start_epoch': 0,
                                                              'start_time': 0,
                                                              'latest_epoch': 10,
                                                              'latest_time': 10,
                                                              'end_epoch': 10,
                                                              'end_time': 10})

        assert _model_equal(Model.load(valid_tree), reference_model)

    def test_load_extra(self, valid_tree_extra):
        reference_model = Model('a_producer_name',
                                'py_pa',
                                '1.0.0',
                                'my_model',
                                'some_id',
                                valid_tree_extra / 'my_config_file.yaml',
                                {})

        reference_model._initialisation = Model('a_producer_name',
                                                'py_pa',
                                                '1.0.0',
                                                'my_init_model',
                                                'some_init_id',
                                                valid_tree_extra / 'data' / 'initialisation' / 'my_config_file.yaml',
                                                {})

        reference_model.initialisation._initialisation = \
            Checkpoint('my_init_file',
                       valid_tree_extra / 'data' / 'initialisation' / 'data' / 'initialisation' / 'init.weight',
                       hash='d41d8cd98f00b204e9800998ecf8427e')

        checkpoint_1 = Checkpoint(1, valid_tree_extra / 'data' / 'checkpoints' / '1.weight', 3,
                                  hash='d41d8cd98f00b204e9800998ecf8427e')
        checkpoint_6 = Checkpoint(6, valid_tree_extra / 'data' / 'checkpoints' / '6.weight', 10,
                                  hash='cfcd208495d565ef66e7dff9f98764da')

        init_checkpoint_6 = Checkpoint(6,
                                       epoch=10,
                                       hash='cfcd208495d565ef66e7dff9f98764da')

        init_checkpoint_7 = Checkpoint(7,
                                       epoch=9,
                                       hash='cfcd208495d565ef66e7dff9f98764da')

        reference_model.add_checkpoint(checkpoint_1, checkpoint_6)
        reference_model.initialisation.add_checkpoint(init_checkpoint_6, init_checkpoint_7)

        reference_model.training = Training(**{'status': 'finished',
                                               'start_epoch': 0,
                                               'start_time': 0,
                                               'latest_epoch': 10,
                                               'latest_time': 10,
                                               'end_epoch': 10,
                                               'end_time': 10})

        reference_model.initialisation.training = Training(**{'status': 'finished',
                                                              'start_epoch': 0,
                                                              'start_time': 0,
                                                              'latest_epoch': 10,
                                                              'latest_time': 10,
                                                              'end_epoch': 10,
                                                              'end_time': 10})

        assert _model_equal(Model.load(valid_tree_extra), reference_model)

    def test_save(self, valid_tree):

        model = Model.load(valid_tree)
        model.save(valid_tree / 'nowhere')

        assert _model_equal(model, Model.load(valid_tree / 'nowhere'))

        model.id = 'new_id'
        with pytest.raises(OSError):
            model.save(valid_tree / 'nowhere')
        with pytest.raises(OSError):
            model.save(valid_tree / 'nowhere', force=True)

        model.training._end_epoch = 0
        model.save(valid_tree / 'nowhere_now')

        model.training._end_epoch = 10

        with pytest.raises(OSError):
            model.save(valid_tree / 'nowhere_now')
        with pytest.raises(OSError):
            model.save(valid_tree / 'nowhere_now', force=True)

        model.initialisation.training._end_epoch = 0
        model.save(valid_tree / 'nowhere_again')

        model.initialisation.training._end_epoch = 10

        with pytest.raises(OSError):
            model.save(valid_tree / 'nowhere_again')

        model.save(valid_tree / 'nowhere_again', force=True)
        assert _model_equal(model, Model.load(valid_tree / 'nowhere_again'))

    def test_save_valid_on_extra(self, valid_tree, valid_tree_extra):

        model = Model.load(valid_tree)
        model.save(valid_tree_extra)

        assert _model_equal(model, Model.load(valid_tree_extra))

    def test_save_valid_on_empty(self, valid_tree, valid_tree_empty):

        model = Model.load(valid_tree)
        model.save(valid_tree_empty)

        assert _model_equal(model, Model.load(valid_tree_empty))

    def test_save_empty_on_valid(self, valid_tree, valid_tree_empty):

        model = Model.load(valid_tree_empty)
        model.save(valid_tree)

        assert _model_equal(model, Model.load(valid_tree))

    def test_save_extra_on_valid(self, valid_tree, valid_tree_extra):

        model = Model.load(valid_tree_extra)
        model.save(valid_tree)

        assert _model_equal(model, Model.load(valid_tree))

    def test_save_valid_on_invalid(self, valid_tree, invalid_tree):

        model = Model.load(valid_tree)
        with pytest.raises(OSError):
            model.save(invalid_tree)

        model.save(invalid_tree, force=True)

        assert _model_equal(model, Model.load(invalid_tree))

    def test_save_extra_on_invalid(self, valid_tree_extra, invalid_tree):

        model = Model.load(valid_tree_extra)
        with pytest.raises(OSError):
            model.save(invalid_tree)

        model.save(invalid_tree, force=True)

        assert _model_equal(model, Model.load(invalid_tree))

    def test_save_valid_on_invalid_strict(self, valid_tree, invalid_tree_strict):

        model = Model.load(valid_tree)
        with pytest.raises(OSError):
            model.save(invalid_tree_strict)

        model.save(invalid_tree_strict, force=True)

        assert _model_equal(model, Model.load(invalid_tree_strict))

    def test_save_extra_on_invalid_strict(self, valid_tree_extra, invalid_tree_strict):

        model = Model.load(valid_tree_extra)
        with pytest.raises(OSError):
            model.save(invalid_tree_strict)

        model.save(invalid_tree_strict, force=True)

        assert _model_equal(model, Model.load(invalid_tree_strict))
