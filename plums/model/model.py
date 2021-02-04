import yaml
from schema import SchemaError

from plums.commons.path import Path
from plums.model.exception import PlumsValidationError
from plums.model.components.utils import copy, rmtree, Mock
from plums.model.validation import Metadata
from plums.model.validation import validate
from plums.model.components import Producer, Training, CheckpointCollection, Checkpoint
from plums.model.validation.utils.checksum import md5_checksum


class Model(object):
    """Define a Python representation of a PMF model.

    Args:
        producer_name (str): The name of the package that produced the model
        producer_version_format (str): The version format of the package that produced the model
        producer_version_string (str): The version string representation of the package that produced the model
        model_name (str): The model name
        model_id (str): The model identification string
        configuration (Pathlike): A path to the producer configuration file used to produce the model
        build_parameters (dict): A dictionary containing values necessary to instantiate the model from its weights.

    Attributes:
        name (str): The model name.
        id (str): The model unique identifier.
        build_parameters (dict): A dictionary containing values necessary to instantiate the model from its weights.
        producer (|Producer|): The |Model| producer.
        training (|Training|): The |Model| training metadata.
        checkpoint_collection (|CheckpointCollection|): The |Model| attached collection of |Checkpoint|.

    """

    __version__ = Metadata.__version__

    def __init__(self, producer_name, producer_version_format, producer_version_string,
                 model_name, model_id, configuration, build_parameters):
        self.producer = Producer(producer_name, producer_version_format, producer_version_string, configuration)

        self.name = model_name
        self.id = model_id
        self.build_parameters = build_parameters

        self.training = Training()
        self.checkpoint_collection = CheckpointCollection()
        self._initialisation = None
        self._path = None
        self._checkpoint = None

    @property
    def initialisation(self):
        """|Model|, |Checkpoint|: The model initialisation network if any, ``None`` otherwise."""
        return self._initialisation

    @property
    def path(self):
        """PathLike: If the model was loaded from disk, the |Path| it was loaded from. ``None`` otherwise."""
        return self._path

    @property
    def checkpoint(self):
        """hashable: If the model is a |Model| initialisation, the checkpoint reference used. ``None`` otherwise."""
        return self._checkpoint

    def __repr__(self):
        """Represent a model."""
        return '{}(name={}, id={})'.format(self.__class__.__name__, self.name, self.id)

    def add_checkpoint(self, *checkpoints):
        """Add a |Checkpoint| to the |Model| :attr:`checkpoint_collection`.

        Args:
            *checkpoints (|Checkpoint|): One ore several |Checkpoint| to add to the model |CheckpointCollection|.

        """
        for checkpoint in checkpoints:
            self.checkpoint_collection.add(checkpoint)

    def register_training_start(self, epoch):
        """Register a training start to the :attr:`training` metadata.

        Args:
            epoch (int): The |Training| staring epoch.

        """
        self.training.start(epoch)

    def register_epoch(self, epoch=None):
        """Register a given epoch as being the latest epoch to the :attr:`training` metadata.

        Args:
            epoch (int): Optional. Default to :attr:`latest_epoch` + 1. The epoch to be registered as latest.

        """
        self.training.register_epoch(epoch)

    def register_training_end(self, success):
        """Register a training end or a training failure to the :attr:`training` metadata.

        Args:
            success (bool): Whether the |Training| ended normally.

        """
        if success:
            self.training.end()
        else:
            self.training.interrupt()

    def register_initialisation(self, path, checkpoint_reference=None, name=None):
        """Register a valid PMF model initialisation from a |Path| to :attr:`initialisation`.

        Args:
            path (PathLike): A valid |Path| to the model initialisation.
            checkpoint_reference (hashable): If initialising from a PMF model, one needs to provided a reference to the
                actual model |Checkpoint| used to construct a valid initialisation.
            name (str): If initialising from a file, one needs to provide a name used to identify the initial network to
                construct a valid initialisation.

        Raises:
            OSError: If the path provided does not exists on the filesystem or points to neither a file nor a PMF model.
            ValueError: If the arguments provided are incompatibles: e.g. using a PMF initialisation without a
                checkpoint_reference.
            SchemaError: If the path provided point to an invalid PMF model.

        See Also:
            The |initialisation| function for more information on the :attr:`initialisation` format.

        """
        self._initialisation = initialisation(path, checkpoint_reference, name)

    def save(self, path, force=False, **kwargs):
        """Save a |Model| to |Path|.

        Args:
            path (PathLike): The |Path| where to save.
            force (bool): Optional. Default to ``False``. If path is an existing non-PMF path or a PMF model with the
                same :attr:`id`, do not raise and carry on saving.

        Raises:
            ValueError: If ``path`` points to a file.
            OSError: If ``path`` points to:

                * A non-empty directory which does not contains a PMF model and ``force`` is ``False``.
                * A non-empty directory which contains a PMF model with the same :attr:`id` and ``force`` is ``False``.
                * A non-empty directory which contains a PMF model with a different :attr:`id`.
                * A non-empty directory which contains a PMF model with an invalid metadata file.

        """
        # TODO: Improve docstring.
        path = Path(path)
        model_dst = Mock()

        # sanity checks
        if path.exists():
            if path.is_file():
                raise ValueError('Invalid path: {} is a file.'.format(path))

            if (path / 'metadata.yaml').exists():
                with open(str(path / 'metadata.yaml'), 'r') as f:
                    metadata = yaml.safe_load(f)

                try:
                    metadata = Metadata().validate(metadata)
                except (SchemaError, PlumsValidationError):
                    # If the metadata file happens to be invalid, we might enter uncharted territories we are not
                    # prepared for. Abort !
                    raise OSError('Invalid path: {} is not a valid PMF metadata file.'.format(path / 'metadata.yaml'))

                if metadata['model']['id'] != self.id:
                    # If the destination model id is different from ours, we might enter uncharted territories we are
                    # not prepared for. Abort !
                    raise OSError('Invalid path: {} has a different PMF model id '
                                  '({} != {}).'.format(path / 'metadata.yaml', self.id, metadata['model']['id']))

                try:
                    model_dst = Model.load(path, checkpoints=kwargs.get('checkpoints', True))
                except (SchemaError, PlumsValidationError):
                    if not force:
                        raise OSError('Invalid path: {} is an invalid PMF model '
                                      'with the same model id ({}).'.format(path / 'metadata.yaml', self.id))
                    # Use the insider fail-agnostic back door to load what we can from the model anyway
                    model_dst = Model._init_from_path(path, metadata)
                    # We remove PMF related elements as the previous written model is not valid, not that is the
                    # deletion fails, we ignore it because a valid PMF model will be written anyway and we never
                    # assume the save destination to be empty.
                    rmtree(path, ignore_errors=True, black_list=('metadata', model_dst.producer.configuration))
            else:
                if not force:
                    raise OSError('Invalid path: {} already exists.'.format(path))

        # Initialize destination
        path.mkdir(parents=True, exist_ok=True)

        # Prepare metadata dictionary
        __metadata__ = {
            'format': {
                'version': self.__version__,
                'producer': {
                    'name': self.producer.name,
                    'version': {
                        'format': self.producer.version.format,
                        'value': self.producer.version.version
                    }
                }
            },
            'model': {
                'name': self.name,
                'id': self.id,
                'training': {
                    'status': self.training.status,
                    'start_epoch': self.training.start_epoch,
                    'start_time': self.training.start_timestamp,
                    'latest_epoch': self.training.latest_epoch,
                    'latest_time': self.training.latest_timestamp,
                    'end_epoch': self.training.end_epoch,
                    'end_time': self.training.end_timestamp,
                    'latest': self.checkpoint_collection.latest,
                    'checkpoints': {}
                },
                'initialisation': None,
                'configuration': {}
            }
        }

        # Initialize directory
        (path / 'data' / 'checkpoints').mkdir(parents=True, exist_ok=True)

        # Save build parameters
        # It should be a rather small file, so blindingly overriding it
        # should be faster than write-in-temp and lazy-copy
        with open(str(path / 'data' / 'build_parameters.yaml'), 'w') as f:
            yaml.safe_dump(self.build_parameters, f)

        # Copy configuration
        configuration_dst = path / self.producer.configuration[-1]
        copy(str(self.producer.configuration), str(configuration_dst), lazy=model_dst is not None)
        # Add configuration to metadata
        __metadata__['model']['configuration'].update({
            'path': str(configuration_dst.anchor_to_path(path)),
            'hash': md5_checksum(self.producer.configuration)
        })

        # Copy initialisation
        if self.initialisation is None:
            (path / 'data' / 'initialisation').mkdir(parents=True, exist_ok=True)

        if isinstance(self.initialisation, Checkpoint):
            (path / 'data' / 'initialisation').mkdir(parents=True, exist_ok=True)
            checkpoint_dst = path / 'data' / 'initialisation' / self.initialisation.path[-1]
            copy(str(self.initialisation.path), str(checkpoint_dst), lazy=model_dst is not None,
                 src_hash=self.initialisation.hash, dst_hash=getattr(model_dst.initialisation, 'name', None))
            # Add file initialisation to metadata
            __metadata__['model']['initialisation'] = {
                'file': {
                    'name': str(self.initialisation.name),
                    'path': str(checkpoint_dst.anchor_to_path(path)),
                    'hash': self.initialisation.hash
                }
            }

        if isinstance(self.initialisation, Model):
            self.initialisation.save(path / 'data' / 'initialisation', force=force, checkpoints=False)
            # Add PMF initialisation to metadata
            __metadata__['model']['initialisation'] = {
                'pmf': {
                    'name': self.initialisation.name,
                    'id': self.initialisation.id,
                    'path': str((path / 'data' / 'initialisation').anchor_to_path(path)),
                    'checkpoint': self.initialisation.checkpoint
                }
            }

        # Copy checkpoint_collection
        for reference, checkpoint in self.checkpoint_collection.items():
            checkpoint_dst = path / 'data' / 'checkpoints' / checkpoint.path[-1] \
                if kwargs.get('checkpoints', True) else None
            # Add checkpoint to metadata
            __metadata__['model']['training']['checkpoints'][reference] = {
                'epoch': checkpoint.epoch,
                'path': str(checkpoint_dst.anchor_to_path(path)) if kwargs.get('checkpoints', True) else '.',
                'hash': checkpoint.hash
            }
            # If needed (usually), copy file to destination
            if kwargs.get('checkpoints', True):
                copy(str(checkpoint.path), str(checkpoint_dst), lazy=model_dst is not None,
                     src_hash=checkpoint.hash, dst_hash=model_dst.checkpoint_collection.get(checkpoint.name))

        # Save metadata
        with open(str(path / 'metadata.yaml'), 'w') as f:
            yaml.safe_dump(__metadata__, f)

    @classmethod
    def load(cls, path, strict=True, verbose=False, **kwargs):
        """Load a |Model| from a |Path|.

        Args:
            path (PathLike): The path to a PMF model to load.
            strict (bool): Whether to perform strict validation (see |validate|).
            verbose (bool): Optional. Default to ``False``. Toggle verbose offence reporting.
            **kwargs (Any): Additional arguments are passed to the |validate| function.

        Returns:
            |Model|: A loaded |Model| instance.

        Raises:
            PlumsModelTreeValidationError: If the path provided point to an invalid PMF model.
            PlumsModelMetadataValidationError: If the path provided point to a PMF model with an invalid metadata.

        See Also:
            The |validate| function for more information on the *PMF* validation process.

        """
        path = Path(path)
        metadata = validate(path, strict=strict, verbose=verbose, **kwargs)

        return cls._init_from_path(path, metadata)

    @classmethod
    def _init_from_path(cls, path, metadata):
        """Initialise a |Model| from a |Path| and a |MetadataSchema|.

        Warnings:
            :meth:`_init_from_path` is **HIGHLY** unsafe: it **does not** perform any sorts of validation, it *assumes*
            that everything is correct and **will not** attempt to correct or account for missing or invalid inputs.

        Args:
            path (PathLike): The path of the PMF model to load.
            metadata (dict): The parsed metadata of the PMF model to load.

        Returns:
            |Model|: A loaded |Model| instance.

        """
        if (path / 'data' / 'build_parameters.yaml').is_file():
            with open(str(path / 'data' / 'build_parameters.yaml'), 'r') as f:
                build_parameters = yaml.safe_load(f)
        else:
            build_parameters = {}

        # Attempting to create a model from the provided metadata
        try:
            model = cls(metadata['format']['producer']['name'],
                        metadata['format']['producer']['version']['format'],
                        metadata['format']['producer']['version']['value'],
                        metadata['model']['name'],
                        metadata['model']['id'],
                        str(path / metadata['model']['configuration']['path']),
                        build_parameters)
        except OSError:
            # The only possible cause of OSError here is a missing configuration, in which case we provide a mock one
            # to allow loading anyway.
            with open(str(path / metadata['model']['configuration']['path']), 'w') as f:
                f.write('')

            model = cls(metadata['format']['producer']['name'],
                        metadata['format']['producer']['version']['format'],
                        metadata['format']['producer']['version']['value'],
                        metadata['model']['name'],
                        metadata['model']['id'],
                        str(path / metadata['model']['configuration']['path']),
                        build_parameters)

        model._path = path

        try:
            model.add_checkpoint(*[Checkpoint(reference,
                                              path / checkpoint['path'],
                                              checkpoint['epoch'],
                                              checkpoint['hash'])
                                   for reference, checkpoint in
                                   metadata['model']['training']['checkpoints'].items()])
        except OSError:
            # Most likely that although the checkpoint is referenced, the file is non-existing.
            # This might indicate an initialisation tree in which case we MUST handle this gracefully,
            # or this might be an invalid PMF, in which case we ignore the error because this SHOULD have been caught
            # while validating and did I ever mentioned this method was HIGHLY UNSAFE to use on its own ?!
            model.add_checkpoint(*[Checkpoint(reference,
                                              None,
                                              checkpoint['epoch'],
                                              checkpoint['hash'])
                                   for reference, checkpoint in
                                   metadata['model']['training']['checkpoints'].items()])

        model.training = Training(start_time=metadata['model']['training']['start_time'],
                                  start_epoch=metadata['model']['training']['start_epoch'],
                                  latest_time=metadata['model']['training']['latest_time'],
                                  latest_epoch=metadata['model']['training']['latest_epoch'],
                                  end_time=metadata['model']['training']['end_time'],
                                  end_epoch=metadata['model']['training']['end_epoch'],
                                  status=metadata['model']['training']['status'])

        # Welcome to the ugly initialisation retrieval game.
        # Note that the correct initialisation retrieval is done in the initialisation() function, BUT, here, we
        # wish to retrieve what we can, albeit incorrectly to salvage what may be from invalid models.
        # This is ethically wrong but, and I kind of quote myself here: This method is HIGHLY UNSAFE to use on its own !
        if metadata['model']['initialisation'] is not None:  # We at least trust metadata to tell us to start searching
            # We get the initialisation path, no matter what.
            init_path = metadata['model']['initialisation']['pmf']['path'] \
                if metadata['model']['initialisation'].get('pmf') is not None else \
                metadata['model']['initialisation']['file']['path']

            # We get the initialisation name no matter what.
            init_name = metadata['model']['initialisation']['pmf']['name'] \
                if metadata['model']['initialisation'].get('pmf') is not None else \
                metadata['model']['initialisation']['file']['name']

            # If we point to an hypothetical file, we must assume a file initialisation.
            if (path / init_path).ext:
                try:
                    model._initialisation = Checkpoint(init_name, path / init_path)
                except OSError:
                    # I guess it was a false lead all along. Better leave it there.
                    model._initialisation = None
                    return model

            # If we point to a directory with an existing metadata, we must assume a PMF initialisation.
            elif (path / init_path / 'metadata.yaml').is_file():
                with open(str(path / init_path / 'metadata.yaml'), 'r') as f:
                    init_metadata = yaml.safe_load(f)

                try:
                    init_metadata = Metadata().validate(init_metadata)
                except (SchemaError, PlumsValidationError):
                    # If the metadata file happens to be invalid, we might enter uncharted territories we are not
                    # prepared for. Abort !
                    model._initialisation = None
                    return model

                model._initialisation = cls._init_from_path(path / init_path, init_metadata)
                model._initialisation._checkpoint = metadata['model']['initialisation'].get('pmf', {}).get('checkpoint')

            # When it all goes wrong, it is acceptable to leave it there. It is an unsafe method, not a crazy one.
            else:
                model._initialisation = None

        return model


def initialisation(path, checkpoint_reference=None, name=None):
    """Construct a valid PMF model initialisation from a |Path|.

    The return type depends on the initialisation type:

    * If the model was initialised from a PMF model, the function will return a |Model| instance.
    * If the model was initialised from a single file, the function will return a |Checkpoint|.

    Args:
        path (PathLike): A valid |Path| to the model initialisation.
        checkpoint_reference (hashable): If initialising from a PMF model, one needs to provided a reference to the
            actual model |Checkpoint| used to construct a valid initialisation.
        name (str): If initialising from a file, one needs to provide a name used to identify the initial network to
            construct a valid initialisation.

    Returns:
        |Model|, |Checkpoint|: The retrieved model initialisation.

    Raises:
        OSError: If the path provided does not exists on the filesystem or points to neither a file nor a PMF model.
        ValueError: If the arguments provided are incompatibles: e.g. using a PMF initialisation without a
            checkpoint_reference.
        PlumsModelTreeValidationError: If the path provided point to an invalid PMF model.
        PlumsModelMetadataValidationError: If the path provided point to a PMF model with an invalid metadata.

    """
    path = Path(path)
    if not path.exists():
        raise OSError('Invalid path provided: {} does not exists'.format(path))

    if not path.is_dir():

        if path.is_file():
            if name is None:
                raise ValueError('Invalid arguments provided: {} points to a file but name is None.'.format(path))

            return Checkpoint(name, path)

    elif (path / 'metadata.yaml').is_file():
        if checkpoint_reference is None:
            raise ValueError('Invalid arguments provided: '
                             '{} points to a PMF model but no checkpoint reference was given.'.format(path))

        model = Model.load(path, checkpoints=False)
        if checkpoint_reference not in model.checkpoint_collection:
            raise ValueError('Invalid arguments provided: '
                             '{} points to a PMF model which does not '
                             'contains {} as a checkpoint.'.format(path, checkpoint_reference))
        model._checkpoint = checkpoint_reference

        return model

    else:
        raise OSError('Invalid path provided: {} must either be a PMF model or a weight file.'.format(path))
