import time
from collections import OrderedDict
from functools import total_ordering

from plums.commons.path import Path
from plums.model.exception import PlumsModelMetadataValidationError
from plums.model.validation.metadata import Training as TrainingMetadata
from plums.model.components.version import version
from plums.model.components.utils import TrainingStatus, Checkpoint, is_duplicate


class Training(object):
    """Define a Python representation of a model training state.

    Args:
        start_time (float): The training stating time, or ``None`` if non existent
        start_epoch (int): The training stating epoch, or ``None`` if non existent
        latest_epoch (int): The training latest epoch, or ``None`` if non existent
        latest_time (float): The training latest epoch time, or ``None`` if non existent
        end_time (float): The training ending time, or ``None`` if non existent
        end_epoch (int): The training ending epoch, or ``None`` if non existent
        status (str): The training status, or ``'pending'`` if non existent

    """

    def __init__(self, start_time=None, start_epoch=None, latest_time=None, latest_epoch=None,
                 end_time=None, end_epoch=None, status='pending'):

        if latest_epoch is None:
            if end_epoch is not None:
                latest_epoch = end_epoch
            else:
                latest_epoch = start_epoch

        if latest_time is None:
            if end_time is not None:
                latest_time = end_time
            else:
                latest_time = start_time

        try:
            TrainingMetadata(verbose=True).validate({
                'status': status,
                'start_time': start_time,
                'start_epoch': start_epoch,
                'latest_time': latest_time,
                'latest_epoch': latest_epoch,
                'end_time': end_time,
                'end_epoch': end_epoch,
                'latest': None,
                'checkpoints': {}
            })
        except PlumsModelMetadataValidationError as e:
            raise ValueError('Invalid training parameters: \n{}'.format(e.code))

        self._start_epoch = start_epoch
        self._start_timestamp = start_time
        self._latest_epoch = latest_epoch
        self._latest_timestamp = latest_time
        self._end_epoch = end_epoch
        self._end_timestamp = end_time
        self._status = TrainingStatus(status)

    @property
    def status(self):
        """str: The training status, *i.e.* pending, running, failed or finished."""
        return str(self._status)

    @status.setter
    def status(self, value):
        self._status.status = value

    @property
    def start_epoch(self):
        """int: The training starting epoch if any, or ``None`` otherwise."""
        return self._start_epoch

    @property
    def start_timestamp(self):
        """int: The training starting timestamp if any, or ``None`` otherwise."""
        return self._start_timestamp

    @property
    def latest_epoch(self):
        """int: The training latest epoch if any, or ``None`` otherwise."""
        return self._latest_epoch

    @property
    def latest_timestamp(self):
        """int: The training latest timestamp if any, or ``None`` otherwise."""
        return self._latest_timestamp

    @property
    def end_epoch(self):
        """int: The training ending epoch if any, or ``None`` otherwise."""
        return self._end_epoch

    @property
    def end_timestamp(self):
        """int: The training ending timestamp if any, or ``None`` otherwise."""
        return self._end_timestamp

    @property
    def is_running(self):
        """bool: Whether the training is running."""
        return self.status == 'running'

    @property
    def is_pending(self):
        """bool: Whether the training is pending."""
        return self.status == 'pending'

    @property
    def is_finished(self):
        """bool: Whether the training is finished."""
        return self.status == 'finished'

    @property
    def is_failed(self):
        """bool: Whether the training is failed."""
        return self.status == 'failed'

    def __repr__(self):
        """Represent a training."""
        return '{}({})'.format(self.__class__.__name__, self.status)

    def start(self, epoch):
        """Start the training and register the starting epoch and timestamp.

        Args:
            epoch (int): The starting epoch.

        """
        self._status.status = 'running'
        self._start_epoch = epoch
        self._start_timestamp = time.time()
        self._latest_epoch = epoch
        self._latest_timestamp = self._start_timestamp

    def interrupt(self):
        """Interrupt the training in a non-standard way and register the failing epoch and timestamp as the latest."""
        self._status.status = 'failed'
        self._end_epoch = self._latest_epoch
        self._end_timestamp = self._latest_timestamp

    def end(self):
        """Interrupt the training in a standard way and register the ending epoch and timestamp as the latest."""
        self._status.status = 'finished'
        self._end_epoch = self._latest_epoch
        self._end_timestamp = self._latest_timestamp

    def register_epoch(self, epoch=None):
        """Register a given epoch as being the latest epoch in the training along with its timestamp.

        Args:
            epoch (int): Optional. Default to :attr:`latest_epoch` + 1. The epoch to be registered as latest.

        """
        if epoch is not None:
            self._latest_epoch = max(self._latest_epoch, epoch)
        else:
            self._latest_epoch += 1
        self._latest_timestamp = time.time()


class CheckpointCollection(object):
    """Define a checkpoint collection Python representation.

    CheckpointCollection may be added through ``__setitem__`` or through :meth:`add`.

    Args:
        checkpoints (|Checkpoint|): A |Checkpoint| to be added to the collection.

    """

    def __init__(self, *checkpoints):
        self._checkpoints = OrderedDict()
        self._references = set()
        self._latest = None
        if checkpoints:
            for checkpoint in checkpoints:
                self.add(checkpoint)
            self._latest = checkpoints[-1].name

    @property
    def latest(self):
        """hashable: A reference to the latest |Checkpoint| added to the collection."""
        return self._latest

    @property
    def eloc(self):
        """|CheckpointCollection|: Retrieve a |CheckpointCollection| from an epoch number."""
        class _EpochIndexer(object):
            def __init__(self, checkpoint_collection):
                self._checkpoint_collection = checkpoint_collection

            def __repr__(self):
                """Represent a checkpoint collection."""
                return self._checkpoint_collection.__repr__()

            def get_references_for_epoch(self, epoch):
                reference_list = []
                for ref, value in self._checkpoint_collection.items():
                    if value.epoch == epoch:
                        reference_list.append(ref)
                return reference_list

            def __getitem__(self, key):
                references = self.get_references_for_epoch(key)
                if not references:
                    raise IndexError('Invalid epoch number provided: {}'.format(key))
                return CheckpointCollection(*(self._checkpoint_collection[reference] for reference in references))

        return _EpochIndexer(self)

    @property
    def iloc(self):
        """|Checkpoint|, (|Checkpoint|, ): Retrieve a |Checkpoint| from its insertion index."""
        class _IndexIndexer(object):
            def __init__(self, checkpoint_collection):
                self._checkpoint_collection = checkpoint_collection
                self._index = tuple(self._checkpoint_collection.keys())

            def __repr__(self):
                """Represent a checkpoint collection."""
                return self._checkpoint_collection.__repr__()

            def __getitem__(self, key):
                if isinstance(key, slice):
                    return tuple(self._checkpoint_collection[reference] for reference in self._index[key])

                return self._checkpoint_collection[self._index[key]]

        return _IndexIndexer(self)

    def __repr__(self):
        """Represent a checkpoint collection."""
        return '{}({})'.format(self.__class__.__name__, tuple(checkpoint for ref, checkpoint in self.items()))

    def __eq__(self, other):
        """Return whether two |CheckpointCollection| have the same set of |Checkpoint|.

        Args:
            other (|CheckpointCollection|): A |CheckpointCollection| to compare to.

        Returns:
            bool: ``True`` if both have the set of |Checkpoint|.

        """
        try:
            return set(self.items()) == set(other.items())
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        """Return whether two |CheckpointCollection| do not have the same set of |Checkpoint|.

        Args:
            other (|CheckpointCollection|): A |CheckpointCollection| to compare to.

        Returns:
            bool: ``True`` if none have the same set of |Checkpoint|.

        """
        return not self == other

    def add(self, checkpoint):
        """Add a |Checkpoint| to the collection.

        Args:
            checkpoint (|Checkpoint|): A |Checkpoint| to add to the collection.

        Raises:
            KeyError: If the |Checkpoint| name was already registered as a reference.
            ValueError: If the |Checkpoint| epoch is ``None``.

        """
        if checkpoint.name in self._references:
            raise KeyError('Checkpoint name {} already registered: {}'.format(checkpoint.name,
                                                                              self._checkpoints[checkpoint.name]))

        if checkpoint.epoch is None:
            raise ValueError('Checkpoint epoch is None in a CheckpointCollection.')

        self._references.add(checkpoint.name)
        self._checkpoints[checkpoint.name] = checkpoint
        self._latest = checkpoint.name

    def __getitem__(self, reference):
        """Retrieve a |Checkpoint| by its unique reference (its name).

        Args:
            reference (hashable): A |Checkpoint| unique reference.

        Returns:
            |Checkpoint|: The corresponding |Checkpoint|

        Raises:
            KeyError: If the given reference is not found in set of known references.

        """
        return self._checkpoints[reference]

    def __setitem__(self, reference, checkpoint):
        """Set a |Checkpoint| name to a new unique reference and either add it to the collection or replace the old one.

        Args:
            reference (hashable): A new |Checkpoint| unique reference.
            checkpoint (|Checkpoint|): A |Checkpoint| to add to the collection.

        Raises:
            ValueError: If the |Checkpoint| epoch is ``None``.

        """
        checkpoint = Checkpoint(name=reference, path=checkpoint.path, epoch=checkpoint.epoch, hash=checkpoint.hash)
        try:
            self.add(checkpoint)
        except KeyError:
            self._checkpoints[reference] = checkpoint

    def __delitem__(self, reference):
        """Delete a |Checkpoint| by its unique reference (its name).

        Args:
            reference (hashable): A |Checkpoint| unique reference.

        Raises:
            KeyError: If the given reference is not found in set of known references.

        """
        del self._checkpoints[reference]
        self._references.discard(reference)
        try:
            self._latest = tuple(self._checkpoints.keys())[-1]
        except IndexError:
            self._latest = None

    def __contains__(self, reference):
        """Return whether a given reference exists in the |CheckpointCollection|.

        Args:
            reference (hashable): A reference to assert existence on.

        Returns:
            bool: ``True`` if reference is registered in the collection.

        """
        return reference in self._references

    def __len__(self):
        """Return the number of registered references in the |CheckpointCollection|.

        Returns:
            int: The number of registered references in the collection.

        """
        return len(self._references)

    def get(self, reference, default=None):
        """Retrieve a |Checkpoint| by its unique reference (its name) or a ``default`` if reference is not found.

        Args:
            reference (hashable): A |Checkpoint| unique reference.
            default (Any): The default to return if reference is not a valid |Checkpoint| reference.

        Returns:
            |Checkpoint|, Any: The corresponding |Checkpoint| or ``default``.

        """
        element = self._checkpoints.get(reference)
        return element if element is not None else default

    def keys(self):
        """Iterate through the collection's references as in a dict, in insertion order.

        Yields:
            hashable: A reference of a |Checkpoint|.

        """
        return self._checkpoints.keys()

    def values(self):
        """Iterate through the collection's |Checkpoint| as in a dict, in insertion order.

        Yields:
            :class:`~plums.model.components.utils.Checkpoint`: A |Checkpoint|.

        """
        return self._checkpoints.values()

    def items(self):
        """Iterate through the collection as in a dict, in insertion order.

        Yields:
            (hashable, :class:`~plums.model.components.utils.Checkpoint`): Reference and |Checkpoint|.

        """
        return self._checkpoints.items()


@total_ordering
class Producer(object):
    """Define a Python representation of a **PMF** model producer with its configuration.

    Args:
        name (str): The name of the package that produced the model.
        version_format (str): The version *format* of the package that produced the model.
        version_string (str): The version *representation string* of the package that produced the model.
        configuration (Pathlike): A path to the producer configuration file used to produce the model.

    See Also:
        The |ProducerVersion| class for more information on the |Producer| version handling.

    Attributes:
        name (str): The name of the package that produced the model.
        version (|ProducerVersion|): The version of the package that produced the model.
        configuration (Pathlike): A path to the producer configuration file used to produce the model.

    """

    def __init__(self, name, version_format, version_string, configuration):
        if not Path(configuration).is_file():
            raise OSError('Invalid configuration: {} is not a file.'.format(configuration))

        self.name = name
        self.version = version(version_format, version_string)
        self.configuration = Path(configuration)

    def __repr__(self):
        """Represent a producer."""
        return '{}(name={}, version={})'.format(self.__class__.__name__, self.name, self.version.__repr__())

    def __eq__(self, other):
        """Return if two |Producer| have the same :attr:`name` and :attr:`version`.

        Args:
            other (|Producer|): Another |Producer| to compare with.

        Returns:
            bool: ``True`` if the two |Producer| are identical in name and |ProducerVersion|.

        """
        try:
            return self.name == other.name and self.version == other.version
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        """Return if two |Producer| do not have the same :attr:`name` and :attr:`version`.

        Args:
            other (|Producer|): Another |Producer| to compare with.

        Returns:
            bool: ``True`` if the two |Producer| are not identical in name and |ProducerVersion|.

        """
        return not self == other

    def __lt__(self, other):
        """If two |Producer| have the same :attr:`name`, return their :attr:`version` order.

        Args:
            other (|Producer|): Another |Producer| to compare with.

        Returns:
            bool: ``True`` if the two |Producer| are identical in name, and if ``other`` |ProducerVersion| is less than
            self :attr:`version`.

        """
        try:
            return self.name == other.name and self.version < other.version
        except AttributeError:
            return NotImplemented

    def strict_equals(self, other):
        """Return if two |Producer| have the same :attr:`name` and :attr:`version` and :attr:`configuration` file.

        Args:
            other (|Producer|): Another |Producer| to compare with.

        Returns:
            bool: ``True`` if the two |Producer| are identical in name, |ProducerVersion| and configuration.

        """
        try:
            return self == other and is_duplicate(str(self.configuration), str(other.configuration))
        except AttributeError:
            return NotImplemented
