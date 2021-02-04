import os
import os.path
import shutil

import yaml

from plums.commons.path import Path
from plums.model.validation.schema_core import MD5Checksum
from plums.model.validation.utils.checksum import md5_checksum


def is_duplicate(file_1, file_2, hash_1=None, hash_2=None, checksum=md5_checksum):
    """Compare two files and return wether their are duplicates.

    For efficiency, a first decision is taken based on the two files size.

    If it is not enough, their content checksum are used.

    Args:
        file_1 (PathLike): The first file to compare.
        file_2 (PathLike): The second file to compare.
        hash_1 (str): Optional. Default to ``None``. If provided, it is used in place of the
            first file checksum to compare content.
        hash_2 (str): Optional. Default to ``None``. If provided, it is used in place of the
            second file checksum to compare content.
        checksum (Callable): A function which computes a checksum from a |Path|.

    Returns:
        bool: ``True`` if both files have the same content.

    """
    file_1 = Path(file_1)
    file_2 = Path(file_2)

    if os.path.getsize(str(file_1)) != os.path.getsize(str(file_2)):
        return False

    hash_1 = hash_1 if hash_1 is not None else checksum(file_1)
    hash_2 = hash_2 if hash_2 is not None else checksum(file_2)

    if hash_1 != hash_2:
        return False

    return True


def copy(source, destination, lazy=True, src_hash=None, dst_hash=None, checksum=md5_checksum):
    """Copy file from *source* to *destination*.

    If ``lazy`` is set to ``True`` and ``destination`` exists, the file **will be** copied **if and only if**
    *destination* is a different file (content-wise) than *source*.

    Args:
        source (PathLike): The first file to compare.
        destination (PathLike): The second file to compare.
        lazy (bool): Optional. Default to ``True``. If set to ``True``, actual copy performed if *destination* exists
            and has a different content than *source*.
        src_hash (str): Optional. Default to ``None``. If provided, it is used in place of the
            first file checksum to compare content.
        dst_hash (str): Optional. Default to ``None``. If provided, it is used in place of the
            second file checksum to compare content.
        checksum (Callable): A function which computes a checksum from a |Path|.

    Raises:
        OSError: If something went wrong during copy.

    """
    source = Path(source)
    destination = Path(destination)

    if source == destination:
        return

    if not source.is_file():
        raise OSError('Invalid source: {} is not a file.'.format(source))

    if destination.exists() and not destination.is_file():
        raise OSError('Invalid destination: {} exists but is not a file.'.format(destination))

    if not destination.exists():
        lazy = False

    if (destination.is_file() and lazy) and is_duplicate(source, destination, src_hash, dst_hash, checksum=checksum):
        return

    shutil.copy(str(source), str(destination))


def rmtree(path, ignore_errors=False, rm_all=False, black_list=()):
    """Partial removal of a filesystem tree from a black list entry point and PMF-trees specific directory entry rules.

    For example, to remove a PMF model located at ``path`` with a configuration file name ``configuration``, one would
    use:

    .. code:: python

        rmtree(path, black_list=('metadata', configuration))

    Args:
        path (PathLike): A |Path| to a PMF |Model| to erase.
        ignore_errors (bool): Optional. Default to ``False``. If ``True``, any error arising when trying to delete
            or list elements will be silently swallowed.
        rm_all (bool): Optional. Default to ``False``. If ``True``, the entire filesystem tree descending from
            *path* will be deleted, independent on whether it looks PMF related.
        black_list (tuple): A tuple of filename (with or without extensions) to be deleted from *path*.


    Warnings:
        ``rm_all`` is to be used with caution, especially coupled with ``ignore_errors`` as it may lead to irreversible
        and indifferenciated data loss.

    """
    path = Path(path)

    black_list_extension = tuple(str(element) for element in black_list if Path(element).ext)
    black_list_no_extension = tuple(str(element) for element in black_list if not Path(element).ext)

    try:
        for element in path.listdir():
            # Delete files from rm rule or optional black lists
            if (path / element).is_file():
                if rm_all:
                    os.remove(str(path / element))
                    continue
                if element.filename in black_list_no_extension:
                    os.remove(str(path / element))
                    continue
                if str(element[-1]) in black_list_extension:
                    os.remove(str(path / element))
                    continue
            # Enter directories with tree dependent black lists or rm rules
            elif (path / element).is_dir():
                # If it is data, foreign elements might be there so we specifically look for build_parameters
                if element[-1] == 'data':
                    rmtree(path / element, ignore_errors=ignore_errors, rm_all=rm_all,
                           black_list=('build_parameters', ))
                # If it is checkpoints, only checkpoints should be there, we delete everything.
                elif element[-1] == 'checkpoints':
                    rmtree(path / element, ignore_errors=ignore_errors, rm_all=True)
                # If it is initialisation, we need to check the initialisation type.
                elif element[-1] == 'initialisation':
                    # If it is PMF initialisation, we use the typical PMF entry point with metadata and configuration
                    if (path / element / 'metadata.yaml').is_file() or \
                            (path / element / 'metadata.yml').is_file():  # Catch obvious naming mistake
                        metadata = None
                        if (path / element / 'metadata.yaml').is_file():
                            with open(str(path / element / 'metadata.yaml'), 'r') as f:
                                metadata = yaml.safe_load(f)
                        elif (path / element / 'metadata.yml').is_file():
                            with open(str(path / element / 'metadata.yml'), 'r') as f:
                                metadata = yaml.safe_load(f)

                        configuration_path = metadata['model']['configuration']['path']
                        rmtree(path / element, ignore_errors=ignore_errors, rm_all=rm_all,
                               black_list=('metadata', configuration_path))
                    # If it is not PMF initialisation, it is either:
                    # * A file initialisation
                    # * No initialisation
                    # * A PMF with no metadata to be found, which is as worrying as it is impossible to work with
                    # In all case above, the remedy is simple: we burn it all !
                    else:
                        rmtree(path / element, ignore_errors=ignore_errors, rm_all=True)

        # Delete path if it is empty
        if not list(path.listdir()):
            os.rmdir(str(path))

    except OSError as e:
        if ignore_errors:
            pass
        else:
            raise e


class TrainingStatus(object):
    """Helper component class to handle |Training| status logic.

    Args:
        status (str): Optional. Default to 'pending'. An optional initial status.

    """

    def __init__(self, status='pending'):
        if status not in ['pending', 'running', 'failed', 'finished']:
            raise ValueError('Invalid training status: {} not pending or running or failed or finished')
        self._status = status

    def __str__(self):
        """Return a string representation of the current status."""
        return self.status

    __repr__ = __str__

    @property
    def status(self):
        """str: The current |Training| status.

        The setter checks that the given value is authorized given the current value.

        Raises:
            ValueError: If the value given to the setter is deemed unauthorized.

        """
        return self._status

    @status.setter
    def status(self, value):
        if value not in ['pending', 'running', 'failed', 'finished']:
            raise ValueError('Invalid training status: {} not pending or running or failed or finished')

        if value == 'pending' and self._status in ['running', 'failed', 'finished']:
            raise ValueError('Invalid training status: A started training may not be set to pending.')

        if value == 'running' and self._status in ['failed', 'finished']:
            raise ValueError('Invalid training status: A finished or failed training may not be started.')

        if value == 'failed' and self._status in ['finished']:
            raise ValueError('Invalid training status: A finished training may not fail.')

        if value == 'finished' and self._status in ['pending', 'failed', 'finished']:
            raise ValueError('Invalid training status: A finished, failed or pending training may not finish.')

        self._status = value


class Checkpoint(object):
    """Define a checkpoint Python representation.

    A |Checkpoint| might be defined by the following parameters:

    * A :attr:`name`, a :attr:`path` and a :attr:`hash`.
    * A :attr:`name` and a :attr:`hash`.
    * A :attr:`name` and a :attr:`path`.

    Note that although the :attr:`epoch` is never needed to strictly define a |Checkpoint|, it is compulsory to inject
    it into a |CheckpointCollection|.

    Args:
        name (hashable): The |Checkpoint| unique identifier.
        path (Pathlike): Optional. default to ``None``. The path to the |Checkpoint| data file.
        epoch (int): Optional. default to ``None``. The |Checkpoint| epoch, if known.
        hash (str): Optional. default to ``None``. The |Checkpoint| data file checksum.

    Attributes:
        name (hashable): The |Checkpoint| unique identifier.
        path (Pathlike): The path to the |Checkpoint| data file.
        epoch (int): The |Checkpoint| epoch, if known.
        hash (str): The |Checkpoint| data file checksum.

    """

    def __init__(self, name, path=None, epoch=None, hash=None):
        self.path = Path(path) if path is not None else path

        if self.path is not None and not self.path.is_file():
            raise OSError('Invalid checkpoint: {} is not a file.'.format(path))

        self.name = name
        self.epoch = epoch
        self.hash = MD5Checksum().validate(hash) if hash is not None else md5_checksum(self.path)

    def __repr__(self):
        """Return a representation of a |Checkpoint|."""
        return '{}(name={}, path={}, epoch={}, hash={})'.format(self.__class__.__name__,
                                                                self.name,
                                                                self.path,
                                                                self.epoch,
                                                                self.hash)

    __str__ = __repr__

    def __eq__(self, other):
        """Return whether two |Checkpoint| have the same :attr:`epoch` and the same :attr:`hash`.

        Args:
            other (|Checkpoint|): A |Checkpoint| to compare to.

        Returns:
            bool: ``True`` if both have the same :attr:`epoch` and the same :attr:`hash`.

        """
        try:
            return self.epoch == other.epoch and self.hash == other.hash
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        """Return whether two |Checkpoint| do not have the same :attr:`epoch` and the same :attr:`hash`.

        Args:
            other (|Checkpoint|): A |Checkpoint| to compare to.

        Returns:
            bool: ``True`` if none have the same :attr:`epoch` and the same :attr:`hash`.

        """
        return not self == other

    def __hash__(self):
        """Return a valid hash for hte |Checkpoint|.

        Returns:
            str: A hash consisting in the hash of the (:attr:`epoch`, :attr:`hash`) tuple.

        """
        return hash((self.epoch, self.hash))


class Mock(object):
    """Mock class which return itself for all attribute access."""

    def __repr__(self):
        """Represent a mock."""
        return '{}()'.format(self.__class__.__name__)

    def __getattr__(self, item):
        """Return an instance of self for all item."""
        try:
            return super(Mock, self).__getattribute__(item)
        except AttributeError:
            return self

    def __call__(self, *args, **kwargs):
        """Return an instance of self for all args and kwargs."""
        return self
