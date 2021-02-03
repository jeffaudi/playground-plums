# flake8: noqa R701

import pytest

from playground_plums.model.exception import PlumsValidationError

from playground_plums.commons.path import Path
from playground_plums.model.components.utils import Checkpoint, TrainingStatus
from playground_plums.model.components.version import Version, version, __version_register__, __version_hook_register__, register
from playground_plums.model.components.components import Producer, CheckpointCollection, Training


class TestUtils:
    def test_checkpoint(self, tmp_path):
        with pytest.raises(OSError):
            c = Checkpoint('', '')

        with open(str(Path(tmp_path) / '45.weight'), 'w') as f:
            f.write('')

        with pytest.raises(PlumsValidationError):
            c = Checkpoint('some_name', Path(tmp_path) / '45.weight', epoch=45, hash='')

        c = Checkpoint('some_name', Path(tmp_path) / '45.weight', epoch=45, hash='00236a2ae558018ed13b5222ef1bd977')

        assert c.name == 'some_name'
        assert c.path == Path(tmp_path) / '45.weight'
        assert c.epoch == 45
        assert c.hash == '00236a2ae558018ed13b5222ef1bd977'

        c = Checkpoint('some_name', Path(tmp_path) / '45.weight', epoch=45)

        assert c.name == 'some_name'
        assert c.path == Path(tmp_path) / '45.weight'
        assert c.epoch == 45
        assert c.hash == 'd41d8cd98f00b204e9800998ecf8427e'

        with open(str(Path(tmp_path) / '46.weight'), 'w') as f:
            f.write('0')

        assert c == c
        assert c == Checkpoint('some_other_name', Path(tmp_path) / '46.weight', epoch=45,
                               hash='d41d8cd98f00b204e9800998ecf8427e')
        assert c != Checkpoint('some_name', Path(tmp_path) / '46.weight', epoch=46,
                               hash='d41d8cd98f00b204e9800998ecf8427e')
        assert c != Checkpoint('some_name', Path(tmp_path) / '46.weight', epoch=45)

    def test_training_status(self):
        with pytest.raises(ValueError):
            ts = TrainingStatus('')

        with pytest.raises(ValueError):
            ts = TrainingStatus('pending')
            ts.status = ''

        # To pending
        ts = TrainingStatus('pending')
        ts.status = 'pending'
        with pytest.raises(ValueError):
            ts = TrainingStatus('running')
            ts.status = 'pending'
        with pytest.raises(ValueError):
            ts = TrainingStatus('failed')
            ts.status = 'pending'
        with pytest.raises(ValueError):
            ts = TrainingStatus('finished')
            ts.status = 'pending'

        # To running
        ts = TrainingStatus('pending')
        ts.status = 'running'
        ts = TrainingStatus('running')
        ts.status = 'running'
        with pytest.raises(ValueError):
            ts = TrainingStatus('failed')
            ts.status = 'running'
        with pytest.raises(ValueError):
            ts = TrainingStatus('finished')
            ts.status = 'running'

        # To failed
        ts = TrainingStatus('pending')
        ts.status = 'failed'
        ts = TrainingStatus('running')
        ts.status = 'failed'
        ts = TrainingStatus('failed')
        ts.status = 'failed'
        with pytest.raises(ValueError):
            ts = TrainingStatus('finished')
            ts.status = 'failed'

        # To finished
        with pytest.raises(ValueError):
            ts = TrainingStatus('pending')
            ts.status = 'finished'
        ts = TrainingStatus('running')
        ts.status = 'finished'
        with pytest.raises(ValueError):
            ts = TrainingStatus('failed')
            ts.status = 'finished'
        with pytest.raises(ValueError):
            ts = TrainingStatus('finished')
            ts.status = 'finished'

        ts = TrainingStatus()
        assert ts.status == 'pending'
        assert str(ts) == ts.status


class TestVersion:
    def test_version(self):
        assert 'py_pa' in __version_register__
        assert 'py_pa' not in __version_hook_register__

        with pytest.raises(ValueError):
            version('dummy_version', '')

        class DummyVersion:
            format = 'dummy_version'

            def __init__(self, version):
                self.attribute = 'OK'

        def hook(cls):
            cls.attribute = 'NOK'
            return cls

        register(DummyVersion)

        version_instance = version('dummy_version', '')
        assert isinstance(version_instance, DummyVersion)
        assert version_instance.attribute == 'OK'

        register(DummyVersion, hook=hook)

        version_instance = version('dummy_version', '')
        assert isinstance(version_instance, DummyVersion)
        assert version_instance.attribute == 'NOK'

    def test_version_class(self):
        class DummyVersion(Version):
            def __init__(self, version):
                self.attribute = 'OK'

            def __eq__(self, other):
                return True

            def __lt__(self, other):
                return True

            def __str__(self):
                return self.attribute

        def hook(cls):
            cls.attribute = 'NOK'
            return cls

        register(DummyVersion)

        version_instance = version('dummy_version', '')
        assert isinstance(version_instance, DummyVersion)
        assert version_instance.attribute == 'OK'
        assert repr(version_instance) == 'DummyVersion(OK)'
        assert str(version_instance) == 'OK'

        assert version_instance == 0
        assert version_instance < 0
        assert version_instance <= 0
        assert not version_instance > 0
        assert not version_instance >= 0
        assert not version_instance != 0

        register(DummyVersion, hook=hook)

        version_instance = version('dummy_version', '')
        assert isinstance(version_instance, DummyVersion)
        assert version_instance.attribute == 'NOK'
        assert repr(version_instance) == 'DummyVersion(NOK)'
        assert str(version_instance) == 'NOK'

        assert version_instance == 0
        assert version_instance < 0
        assert version_instance <= 0
        assert not version_instance > 0
        assert not version_instance >= 0
        assert not version_instance != 0

        class DummyVersion(Version):
            def __init__(self, version):
                self.attribute = 'OK'

            @property
            def format(self):
                return 'dummy_format'  # Does nothing due to meta-class magic

            def __eq__(self, other):
                return True

            def __lt__(self, other):
                return True

            def __str__(self):
                return self.attribute

        register(DummyVersion)

        version_instance = version('dummy_version', '')
        assert isinstance(version_instance, DummyVersion)
        assert version_instance.format == 'dummy_version'
        assert version_instance.attribute == 'OK'
        assert repr(version_instance) == 'DummyVersion(OK)'
        assert str(version_instance) == 'OK'

        assert version_instance == 0
        assert version_instance < 0
        assert version_instance <= 0
        assert not version_instance > 0
        assert not version_instance >= 0
        assert not version_instance != 0

    def test_py_pa(self):
        from playground_plums.model.components.version import version

        version_instance = version('py_pa', '2.0.0')
        assert str(version_instance) == '2.0.0'
        assert repr(version_instance) == 'PyPA(2.0.0)'
        assert version_instance == version('py_pa', '2.0.0')
        assert version_instance < version('py_pa', '3.0.0')
        assert version_instance <= version('py_pa', '3.0.0')
        assert not version_instance > version('py_pa', '3.0.0')
        assert not version_instance >= version('py_pa', '3.0.0')
        assert version_instance != version('py_pa', '3.0.0')


class TestTraining:
    def test_properties(self):
        training = Training()
        assert training.status == 'pending'
        assert training.is_pending
        assert not training.is_running
        assert not training.is_failed
        assert not training.is_finished
        assert training.start_epoch is None
        assert training.start_timestamp is None
        assert training.latest_epoch is None
        assert training.latest_timestamp is None
        assert training.end_epoch is None
        assert training.end_timestamp is None

        training = Training(start_epoch=0, start_time=0, status='running')
        assert training.status == 'running'
        assert not training.is_pending
        assert training.is_running
        assert not training.is_failed
        assert not training.is_finished
        assert training.start_epoch == 0
        assert training.start_timestamp == 0
        assert training.latest_epoch == 0
        assert training.latest_timestamp == 0
        assert training.end_epoch is None
        assert training.end_timestamp is None

        training = Training(start_epoch=0, start_time=0, end_epoch=10, end_time=10, status='failed')
        assert training.status == 'failed'
        assert not training.is_pending
        assert not training.is_running
        assert training.is_failed
        assert not training.is_finished
        assert training.start_epoch == 0
        assert training.start_timestamp == 0
        assert training.latest_epoch == 10
        assert training.latest_timestamp == 10
        assert training.end_epoch == 10
        assert training.end_timestamp == 10

        training = Training(start_epoch=0, start_time=0, latest_epoch=5, latest_time=5,
                            end_epoch=10, end_time=10, status='finished')
        assert training.status == 'finished'
        assert not training.is_pending
        assert not training.is_running
        assert not training.is_failed
        assert training.is_finished
        assert training.start_epoch == 0
        assert training.start_timestamp == 0
        assert training.latest_epoch == 5
        assert training.latest_timestamp == 5
        assert training.end_epoch == 10
        assert training.end_timestamp == 10

        with pytest.raises(ValueError):
            training = Training(start_epoch=0, start_time=0, latest_epoch=5, latest_time=5,
                                end_epoch=10, end_time=10, status='running')

        with pytest.raises(ValueError):
            training = Training(start_epoch=0, start_time=0, latest_epoch=50, latest_time=50,
                                end_epoch=10, end_time=10, status='finished')

    def test_interfaces(self):
        training = Training()
        training.start(0)
        assert training.is_running
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 0
        assert training.latest_timestamp is not None
        assert training.end_epoch is None
        assert training.end_timestamp is None

        training = Training(start_epoch=0, start_time=0, status='running')
        training.start(0)
        assert training.is_running
        assert training.start_epoch == 0
        assert training.start_timestamp != 0
        assert training.latest_epoch == 0
        assert training.latest_timestamp != 0
        assert training.end_epoch is None
        assert training.end_timestamp is None

        training = Training(start_epoch=0, start_time=0, status='running')
        training.interrupt()
        assert training.is_failed
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 0
        assert training.latest_timestamp is not None
        assert training.end_epoch == 0
        assert training.end_timestamp is not None

        training = Training(start_epoch=0, start_time=0, status='running')
        training.end()
        assert training.is_finished
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 0
        assert training.latest_timestamp is not None
        assert training.end_epoch == 0
        assert training.end_timestamp is not None

        training = Training(start_epoch=0, start_time=0, status='running')
        training.register_epoch(3)
        assert training.is_running
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 3
        assert training.latest_timestamp is not None and training.latest_timestamp != training.start_timestamp
        assert training.end_epoch is None
        assert training.end_timestamp is None
        training.interrupt()
        assert training.is_failed
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 3
        assert training.latest_timestamp is not None and training.latest_timestamp != training.start_timestamp
        assert training.end_epoch == 3
        assert training.end_timestamp

        training = Training(start_epoch=0, start_time=0, status='running')
        training.register_epoch()
        assert training.is_running
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 1
        assert training.latest_timestamp is not None and training.latest_timestamp != training.start_timestamp
        assert training.end_epoch is None
        assert training.end_timestamp is None
        training.end()
        assert training.is_finished
        assert training.start_epoch == 0
        assert training.start_timestamp is not None
        assert training.latest_epoch == 1
        assert training.latest_timestamp is not None and training.latest_timestamp != training.start_timestamp
        assert training.end_epoch == 1
        assert training.end_timestamp is not None


class TestCheckpointCollection:
    def test_checkpoint_collection(self, tmp_path):  # noqa: R701
        with open(str(Path(tmp_path) / '1.weight'), 'w') as f:
            f.write('')

        with open(str(Path(tmp_path) / '0.weight'), 'w') as f:
            f.write('0')

        checkpoint_empty = Checkpoint('', Path(tmp_path) / '1.weight', epoch=0)
        checkpoint_zero = Checkpoint('0', Path(tmp_path) / '0.weight', epoch=0)

        # +-> Insertion
        checkpoint_collection = CheckpointCollection(checkpoint_empty)
        assert checkpoint_collection.latest == ''
        assert len(checkpoint_collection) == 1
        assert checkpoint_collection[''] == checkpoint_empty
        assert checkpoint_collection == checkpoint_collection

        checkpoint_collection.add(checkpoint_zero)
        assert checkpoint_collection.latest == '0'
        assert len(checkpoint_collection) == 2
        assert checkpoint_collection['0'] == checkpoint_zero

        with pytest.raises(KeyError):
            checkpoint_collection.add(checkpoint_zero)

        checkpoint_collection['0'] = checkpoint_empty
        assert checkpoint_collection.latest == '0'
        assert len(checkpoint_collection) == 2
        assert checkpoint_collection['0'] == checkpoint_empty

        checkpoint_collection['0'] = checkpoint_zero
        assert checkpoint_collection.latest == '0'
        assert len(checkpoint_collection) == 2
        assert checkpoint_collection['0'] == checkpoint_zero

        # +-> Dict-like iterators
        assert tuple(checkpoint_collection.keys()) == ('', '0')
        assert tuple(checkpoint_collection.values()) == (checkpoint_empty, checkpoint_zero)
        assert tuple(checkpoint_collection.items()) == (('', checkpoint_empty), ('0', checkpoint_zero))

        # +-> Epoch based set retrieval
        assert checkpoint_collection.eloc[0] == checkpoint_collection
        with pytest.raises(IndexError):
            assert checkpoint_collection.eloc[1] != checkpoint_collection

        # +-> Index based checkpoint retrieval
        assert checkpoint_collection.iloc[0] == checkpoint_empty
        assert checkpoint_collection.iloc[-2] == checkpoint_empty
        assert checkpoint_collection.iloc[1] == checkpoint_zero
        assert checkpoint_collection.iloc[-1] == checkpoint_zero

        with pytest.raises(IndexError):
            _ = checkpoint_collection.iloc[2]

        with pytest.raises(IndexError):
            _ = checkpoint_collection.iloc[-3]

        assert checkpoint_collection.iloc[:] == (checkpoint_empty, checkpoint_zero)
        assert checkpoint_collection.iloc[:-1] == (checkpoint_empty, )
        assert checkpoint_collection.iloc[1:] == (checkpoint_zero, )

        # +-> Deletion
        del checkpoint_collection['0']
        assert '0' not in checkpoint_collection
        assert checkpoint_collection.latest == ''
        assert len(checkpoint_collection) == 1

        del checkpoint_collection['']
        assert '' not in checkpoint_collection
        assert checkpoint_collection.latest is None
        assert len(checkpoint_collection) == 0


class TestProducer:
    def test_producer(self, tmp_path):
        with open(str(Path(tmp_path) / '0.conf'), 'w') as f:
            f.write('0')

        with open(str(Path(tmp_path) / '1.conf'), 'w') as f:
            f.write('')

        with open(str(Path(tmp_path) / '0.1.conf'), 'w') as f:
            f.write('0')

        with pytest.raises(OSError):
            p = Producer('', 'py_pa', '1.0.0', Path(tmp_path) / '2.conf')

        with pytest.raises(ValueError):
            p = Producer('', 'version_format', '1.0.0', Path(tmp_path) / '0.conf')

        p = Producer('', 'py_pa', '1.0.0', Path(tmp_path) / '0.conf')
        p_eq = Producer('', 'py_pa', '1.0.0', Path(tmp_path) / '1.conf')
        p_seq = Producer('', 'py_pa', '1.0.0', Path(tmp_path) / '0.conf')
        p_dup = Producer('', 'py_pa', '1.0.0', Path(tmp_path) / '0.1.conf')
        p_gt = Producer('', 'py_pa', '2.0.0', Path(tmp_path) / '0.conf')

        assert p == p_eq
        assert p <= p_eq
        assert p >= p_eq
        assert not p < p_eq
        assert not p > p_eq
        assert not p.strict_equals(p_eq)
        assert not p_eq.strict_equals(p)

        assert p == p_seq
        assert p <= p_seq
        assert p >= p_seq
        assert not p < p_seq
        assert not p > p_seq
        assert p.strict_equals(p_seq)
        assert p_seq.strict_equals(p)

        assert p == p_dup
        assert p <= p_dup
        assert p >= p_dup
        assert not p < p_dup
        assert not p > p_dup
        assert p.strict_equals(p_dup)
        assert p_dup.strict_equals(p)

        assert p != p_gt
        assert p <= p_gt
        assert not p >= p_gt
        assert p < p_gt
        assert not p > p_gt
        assert not p.strict_equals(p_gt)
        assert not p_gt.strict_equals(p)
