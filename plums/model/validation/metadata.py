import schema

from plums.model.exception import PlumsValidationError, PlumsModelMetadataValidationError
from plums.model.validation.schema_core import SchemaComponent, Path, MD5Checksum, Default


class MetadataComponent(SchemaComponent):
    """A 'validatable' component in a PMF model metadata schema validation.

    To alleviate complex nested schema creation and validation, one possible solution is to cut it up into semantically
    consistent chunks, each defining its innermost schema.

    With this, each component validation might be customized (if one needs to check more than the innermost schema
    data conformity, *e.g.* for data cross-dependencies or to simplify optional or default value definition) and
    it is easier to accumulate and report all offending data elements in one shot.

    The class |MetadataComponent| defines a simple building block which allows both static and dynamic schema
    composition by defining its enclosed schema respectively as a :obj:`class` attribute or a :obj:`instance` attribute.

    See Also:
        The `Schema library <https://github.com/keleshev/schema>`_ for more information on the schema validation
        backend.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, verbose=False):
        super(MetadataComponent, self).__init__(verbose=verbose)

    def validate(self, data):
        """Validate a given data against the enclosed schema.

        Args:
            data (Any): The data to validate.

        Returns:
            Any: The validated data.

        Raises:
            PlumsModelMetadataValidationError: If any offence is detected in the metadata.

        """
        try:
            return self.__schema__.validate(data)
        except (schema.SchemaError, PlumsValidationError) as e:
            raise PlumsModelMetadataValidationError(self._parse_errors(e.errors, e.autos, e.code))


class DefaultMetadata(Default, MetadataComponent):
    """A 'validatable' component in a PMF metadata schema validation which accepts a default ``null`` value.

    Args:
        schema_ (Validatable): A schema to enclose.
        default (Any): A default ``null`` value to accept as a valid data.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, schema_, default=None, verbose=False):
        super(DefaultMetadata, self).__init__(schema_, default=default, verbose=verbose)


########################################################################################################################
# --------------------------------------------   Metadata section   -------------------------------------------------- #
########################################################################################################################
class Metadata(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* metadata.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        format (:class:`~plums.model.validation.metadata.Format`): The format metadata section.
        model (:class:`~plums.model.validation.metadata.Model`): The model metadata section.

    """

    __version__ = '1.0.0'

    def __init__(self, verbose=False):
        super(Metadata, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'format': Format(verbose=verbose),
                'model': Model(verbose=verbose)
            }
        )


########################################################################################################################
# ----------------------------------------------   Model section   --------------------------------------------------- #
########################################################################################################################
class Configuration(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* model configuration section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        path (:class:`~plums.model.validation.schema_core.Path`): The configuration file path.
        hash (:class:`~plums.model.validation.schema_core.MD5Checksum`): The configuration file checksum.

    """

    def __init__(self, verbose=False):
        super(Configuration, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'path': Path(verbose=verbose),
                'hash': MD5Checksum(verbose=verbose)
            }
        )


class InitialisationPMF(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* model 'initialisation from a *PMF model*' section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        name (:class:`str`, ``None``): The initialisation |Model| name.
        id (:class:`str`): The initialisation |Model| id.
        checkpoint (:class:`str`, :class:`int`): The initialisation |Model| checkpoint reference used to initialise.
        path (:class:`~plums.model.validation.schema_core.Path`): The initialisation |Model| location.

    """

    def __init__(self, verbose=False):
        super(InitialisationPMF, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'name': DefaultMetadata(schema.Schema(str),
                                        default=None,
                                        verbose=verbose),
                'id': str,
                'checkpoint': schema.Or(str, int),
                'path': Path(verbose=verbose)
            }
        )


class InitialisationPath(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* model 'initialisation from a *file*' section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        name (:class:`str`, ``None``): The initialisation name.
        path (:class:`~plums.model.validation.schema_core.Path`): The initialisation file path.
        hash (:class:`~plums.model.validation.schema_core.MD5Checksum`): The initialisation file checksum.

    """

    def __init__(self, verbose=False):
        super(InitialisationPath, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'name': DefaultMetadata(schema.Schema(str),
                                        default=None,
                                        verbose=verbose),
                'path': Path(verbose=verbose),
                'hash': MD5Checksum(verbose=verbose)
            }
        )


class Initialisation(DefaultMetadata):
    """A 'validatable' component which only accepts valid *PMF* model initialisation section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, verbose=False):
        super(Initialisation, self).__init__(schema.Or({'pmf': dict}, {'file': dict}),
                                             default=None,
                                             verbose=verbose)

        self._pmf_schema = InitialisationPMF(verbose=verbose)
        self._file_schema = InitialisationPath(verbose=verbose)

    def validate(self, data):
        """Validate a given data against the default value or one of  the *pmf* or *file* enclosed schema.

        Args:
            data (Any): The data to validate.

        Raises:
            PlumsModelMetadataValidationError: If any offence is detected in the data.

        """
        super(Initialisation, self).validate(data)

        if data is self._default:
            return data

        if 'pmf' in data:
            data = self._pmf_schema.validate(data['pmf'])
            return {'pmf': data}

        if 'file' in data:
            data = self._file_schema.validate(data['file'])
            return {'file': data}


class Model(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* model section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        name (:class:`str`, ``None``): The |Model| name.
        id (:class:`str`): The |Model| name.
        initialisation (:class:`~plums.model.validation.metadata.Initialisation`):
            The |Model| initialisation section.
        training (:class:`~plums.model.validation.metadata.Training`):
            The |Model| training section.
        configuration (:class:`~plums.model.validation.metadata.Configuration`):
            The |Model| configuration section.

    """

    def __init__(self, verbose=False):
        super(Model, self).__init__(verbose=verbose)

        self.__schema__ = schema.Schema(
            {
                'name': DefaultMetadata(schema.Schema(str),
                                        default=None,
                                        verbose=verbose),
                'id': str,
                'initialisation': Initialisation(verbose=verbose),
                'training': Training(verbose=verbose),
                'configuration': Configuration(verbose=verbose)
            }
        )


########################################################################################################################
# --------------------------------------------   Training section   -------------------------------------------------- #
########################################################################################################################
class Checkpoint(DefaultMetadata):
    """A 'validatable' component which only accepts valid *PMF* model training checkpoints section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Validates a mapping between a :class:`str` or :class:`int` |Checkpoint| reference key and the following
    *checkpoint* schema:

    Schema:
        epoch (:class:`int`): The |Checkpoint| epoch.
        path (:class:`~plums.model.validation.schema_core.Path`): The |Checkpoint| file path.
        hash (:class:`~plums.model.validation.schema_core.MD5Checksum`): The |Checkpoint| file checksum.

    """

    def __init__(self, verbose=False):
        super(Checkpoint, self).__init__(None, verbose=verbose)

        self._default = {}
        self.__schema__ = schema.Schema(
            {
                schema.Or(str, int): {
                    'epoch': int,
                    'path': Path(verbose=verbose),
                    'hash': MD5Checksum(verbose=verbose)
                }
            }
        )


class Training(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* model training section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        status (:class:`str`): The |Training| status (either 'pending', 'running', 'finished' or 'failed').
        start_time (:class:`int`, :class:`float`, ``None``): The |Training| starting epoch timestamp.
        start_epoch (:class:`int`, :class:`float`, ``None``): The |Training| starting epoch number.
        latest_time (:class:`int`, :class:`float`, ``None``): The |Training| latest epoch timestamp.
        latest_epoch (:class:`int`, :class:`float`, ``None``): The |Training| latest epoch number.
        end_time (:class:`int`, :class:`float`, ``None``): The |Training| ending epoch timestamp.
        end_epoch (:class:`int`, :class:`float`, ``None``): The |Training| ending epoch number.
        latest (:class:`str`, :class:`int`): A reference to the latest registered |Checkpoint| in the |CheckpointSchema|
            section.
        checkpoint (:class:`~plums.model.validation.metadata.Configuration`):
            The |Training| checkpoints section.

    """

    def __init__(self, verbose=False):
        super(Training, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'status': schema.Or('pending', 'running', 'finished', 'failed'),
                'start_time': DefaultMetadata(schema.Or(int, float),
                                              default=None,
                                              verbose=verbose),

                'latest_time': DefaultMetadata(schema.Or(int, float),
                                               default=None,
                                               verbose=verbose),
                'end_time': DefaultMetadata(schema.Or(int, float),
                                            default=None,
                                            verbose=verbose),
                'start_epoch': DefaultMetadata(schema.Schema(int),
                                               default=None,
                                               verbose=verbose),
                'latest_epoch': DefaultMetadata(schema.Schema(int),
                                                default=None,
                                                verbose=verbose),
                'end_epoch': DefaultMetadata(schema.Schema(int),
                                             default=None,
                                             verbose=verbose),
                'latest': DefaultMetadata(schema.Or(str, int),
                                          default=None,
                                          verbose=verbose),
                'checkpoints': Checkpoint(verbose=verbose)
            }
        )

    def validate(self, data):  # noqa: R701
        """Validate a given data against the enclosed schema and checks for various cross-dependencies.

        Args:
            data (Any): The data to validate.

        Raises:
            PlumsModelMetadataValidationError: If any offence is detected in the data.

        """
        data = super(Training, self).validate(data)

        errors = []

        # Times dependencies checks:
        if data['start_time'] is None and data['end_time'] is not None:
            errors.append('end_time provided without a start_time')

        if data['start_time'] is None and data['latest_time'] is not None:
            errors.append('latest_time provided without a start_time')

        if data['latest_time'] is None and data['end_time'] is not None:
            errors.append('end_time provided without a latest_time')

        if data['start_time'] is not None:
            if data['latest_time'] is not None and (data['start_time'] > data['latest_time']):
                errors.append('latest_time happened before start_time')
            if data['start_epoch'] is None:
                errors.append('start_time provided without a start_epoch')
            if data['status'] in ['pending']:
                errors.append('start_time provided with pending status')

        if data['latest_time'] is not None:
            if data['end_time'] is not None and (data['latest_time'] > data['end_time']):
                errors.append('end_time happened before latest_time')
            if data['latest_epoch'] is None:
                errors.append('latest_time provided without a latest_epoch')
            if data['status'] in ['pending']:
                errors.append('latest_time provided with pending status')

        if data['end_time'] is not None:
            if data['end_epoch'] is None:
                errors.append('end_time provided without an end_epoch')
            if data['status'] in ['pending', 'running']:
                errors.append('end_time provided with a running or pending status')

        # Epochs dependencies checks:
        if data['start_epoch'] is None and data['end_epoch'] is not None:
            errors.append('end_epoch provided without a start_epoch')

        if data['start_epoch'] is None and data['latest_epoch'] is not None:
            errors.append('latest_epoch provided without a start_epoch')

        if data['latest_epoch'] is None and data['end_epoch'] is not None:
            errors.append('end_epoch provided without a latest_epoch')

        if data['start_epoch'] is not None:
            if data['latest_epoch'] is not None and (data['start_epoch'] > data['latest_epoch']):
                errors.append('latest_epoch happened before start_epoch')
            if data['start_time'] is None:
                errors.append('start_epoch provided without a start_time')
            if data['status'] in ['pending']:
                errors.append('start_epoch provided with pending status')

        if data['latest_epoch'] is not None:
            if data['end_epoch'] is not None and (data['latest_epoch'] > data['end_epoch']):
                errors.append('end_epoch happened before latest_epoch')
            if data['latest_time'] is None:
                errors.append('latest_epoch provided without a latest_time')
            if data['status'] in ['pending']:
                errors.append('latest_epoch provided with pending status')

        if data['end_epoch'] is not None:
            if data['end_time'] is None:
                errors.append('end_epoch provided without an end_time')
            if data['status'] in ['pending', 'running']:
                errors.append('end_epoch provided with a running or pending status')

        # CheckpointCollection and latest dependency check:
        if data['latest'] is not None and list(data['checkpoints'].keys()) and \
                data['latest'] not in data['checkpoints']:
            errors.append('latest points to an unregistered checkpoint name')

        # CheckpointCollection and latest_epoch check:
        if data['latest_epoch'] is not None and any((data['checkpoints'][ref]['epoch'] > data['latest_epoch']
                                                     for ref in data['checkpoints'].keys())):
            errors.append('at least one registered checkpoint has an epoch greater than latest_epoch')

        if errors:
            raise \
                PlumsModelMetadataValidationError(self._parse_errors(errors,
                                                                     [],
                                                                     'Invalid Training parameters cross-dependencies.'))

        return data


########################################################################################################################
# ---------------------------------------------   Format section   --------------------------------------------------- #
########################################################################################################################
class ProducerVersion(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* format producer version section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        format (:class:`str`): The |ProducerVersion| format.
        value (:class:`str`): The |ProducerVersion| string representation.

    """

    __schema__ = schema.Schema(
        {
            'format': str,
            'value': str
        }
    )


class Producer(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* format producer section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        name (:class:`str`): The |Producer| name.
        version (:class:`~plums.model.validation.metadata.ProducerVersion`): The |Producer| version section.

    """

    def __init__(self, verbose=False):
        super(Producer, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'name': schema.Regex(r'^[a-zA-Z][0-9a-zA-Z_]+$',
                                     error='Invalid name: '
                                           'Expected only alphanumeric characters or "_"'
                                           'and should start with a letter.'),
                'version': ProducerVersion(verbose=verbose)
            })


class Format(MetadataComponent):
    """A 'validatable' component which only accepts valid *PMF* format section.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    Schema:
        version (:class:`str`): The *PMF* format current version.
        version (:class:`~plums.model.validation.metadata.Producer`): The format producer section.

    """

    __version__ = Metadata.__version__

    def __init__(self, verbose=False):
        super(Format, self).__init__(verbose=verbose)
        self.__schema__ = schema.Schema(
            {
                'version': self.__version__,
                'producer': Producer(verbose=verbose)
            }
        )
