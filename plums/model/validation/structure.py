import schema
import yaml

from plums.commons.path import Path
from plums.model.exception import (
    PlumsValidationError, PlumsModelTreeValidationError, PlumsModelMetadataValidationError
)
from plums.model.validation.metadata import Metadata as MetadataSchema
from plums.model.validation.schema_core import SchemaComponent, Default
from plums.model.validation.utils.checksum import md5_checksum


class TreeComponent(SchemaComponent):
    """A 'validatable' component in a filesystem tree ``schema``-like validation.

    To alleviate complex nested tree creation and validation, one possible solution is to cut it up into semantically
    consistent chunks, each defining its innermost tree and then validate it as a python :class:`dict` schema.

    With this, each component validation might be customized (if one needs to check more than the innermost schema
    data conformity, *e.g.* for data cross-dependencies or to simplify optional or default value definition) and
    it is easier to accumulate and report all offending data elements in one shot.

    The class |TreeComponent| defines a simple building block which allows both static and dynamic tree composition
    by defining its enclosed dict schema respectively as a :obj:`class` attribute or a :obj:`instance` attribute.

    See Also:
        * The `Schema library <https://github.com/keleshev/schema>`_ for more information on the schema validation
          backend.
        * The |make_dict_structure_from_tree| function to translate a filesystem tree into a nested dictionary
          structure to validate against a schema.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. It is up to subclasses to define what
            is considered strict validation, however, it usually leads to significantly longer validation time as it
            might involve costly IO operation.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, strict=False, verbose=False):
        super(TreeComponent, self).__init__(verbose=verbose)
        self._strict = strict

    def validate(self, data):
        """Validate a given data against the enclosed schema.

        Args:
            data (Any): The data to validate.

        Returns:
            Any: The validated data.

        Raises:
            PlumsModelTreeValidationError: If any offence is detected in the filesystem tree data.
            PlumsModelMetadataValidationError: If any offence is detected in the model metadata.

        """
        try:
            return self.__schema__.validate(data)
        # Bubble up metadata errors
        except PlumsModelMetadataValidationError as e:
            raise PlumsModelMetadataValidationError(self._parse_errors(e.errors, e.autos, e.code))
        # Make tree errors from validation errors
        except (schema.SchemaError, PlumsValidationError) as e:
            raise PlumsModelTreeValidationError(self._parse_errors(e.errors, e.autos, e.code))


class DefaultTree(Default, TreeComponent):
    """A 'validatable' component in a ``schema``-like tree validation which accepts a default ``null`` value.

    Args:
        schema_ (Validatable): A schema to enclose.
        default (Any): A default ``null`` value to accept as a valid data.
        strict (bool): Optional. Default to ``True``. Toggle strict validation. It is up to subclasses to define what
            is considered strict validation, however, it usually leads to significantly longer validation time as it
            might involve costly IO operation.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, schema_, default=None, strict=False, verbose=False):
        super(DefaultTree, self).__init__(schema_, default=default, verbose=verbose)
        self._strict = strict


########################################################################################################################
# ----------------------------------------------   Model section   --------------------------------------------------- #
########################################################################################################################
class Model(TreeComponent):
    """A 'validatable' component which only accepts valid *PMF* model tree structure.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. When performing strict validation,
            the configuration file and all registered checkpoints checksum will be matched against the checksum of the
            corresponding file on the filesystem.
        checkpoints (bool): Whether to check for registered checkpoints existence and validity if ``strict`` is
            ``True``.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, strict=False, verbose=False, checkpoints=True):
        super(Model, self).__init__(strict=strict, verbose=verbose)
        # We define the schema in __init__ because of the recursive nature of model initialisation filesystem trees
        self.__schema__ = schema.Schema(
            {
                'metadata.yaml': Metadata(verbose=verbose),
                'data': Data(strict=strict, verbose=verbose, checkpoints=checkpoints),
                schema.Optional(str): schema.Or(dict, Path)  # Additional files or directories are accepted here
            }
        )
        self._checkpoints = checkpoints

    def validate(self, data):
        """Validate a given tree against the PMF tree schema.

        Args:
            data (Any): The tree to validate.

        Returns:
            Any: The validated tree.

        Raises:
            PlumsModelTreeValidationError: If any offence is detected in the data.

        """
        data = super(Model, self).validate(data)

        # Validate configuration existence
        if data.get(data['metadata.yaml']['model']['configuration']['path']) is None:
            raise PlumsModelTreeValidationError(self._parse_errors(['no configuration file found'],
                                                                   [],
                                                                   'no configuration file found'))

        # Validate registered checkpoints existence
        if self._checkpoints:
            errors = []
            for ref in data['metadata.yaml']['model']['training']['checkpoints']:
                filename = str(Path(data['metadata.yaml']['model']['training']['checkpoints'][ref]['path'])[-1])
                if data['data']['checkpoints'].get(filename) is None:
                    errors.append('missing checkpoint {}'.format(ref))
            if errors:
                raise PlumsModelTreeValidationError(self._parse_errors(errors,
                                                                       [],
                                                                       'missing registered checkpoints'))

        # Check for initialisation discrepancies
        if data['metadata.yaml']['model']['initialisation']:

            # If PMF initialisation:
            if 'pmf' in data['metadata.yaml']['model']['initialisation']:
                # Verify it is PMF (Note that we don't validate the actual 'correctness' of the format,
                # it has been done before if it was PMF)
                if 'metadata.yaml' not in data['data']['initialisation']:
                    message = 'initialisation indicates a PMF model but none was found'
                    raise PlumsModelTreeValidationError(self._parse_errors([message], [], message))

                # Verify checkpoint existence
                meta = data['data']['initialisation']['metadata.yaml']  # Get init metadata
                checkpoint = data['metadata.yaml']['model']['initialisation']['pmf']['checkpoint']
                if checkpoint not in meta['model']['training']['checkpoints']:
                    message = 'initialisation checkpoint not registered in initialisation: {}'.format(checkpoint)
                    raise PlumsModelTreeValidationError(self._parse_errors([message], [], message))

            # If weight file initialisation:
            if 'file' in data['metadata.yaml']['model']['initialisation']:
                # Verify file correctness
                if 'metadata.yaml' in data['data']['initialisation']:
                    message = 'initialisation indicates a weight file but a PMF was found'
                    raise PlumsModelTreeValidationError(self._parse_errors([message], [], message))

                # Verify checkpoint existence
                checkpoint = data['metadata.yaml']['model']['initialisation']['file']['path']
                if Path(checkpoint)[-1] not in data['data']['initialisation']:
                    message = 'initialisation weight not found in initialisation: {}'.format(checkpoint)
                    raise PlumsModelTreeValidationError(self._parse_errors([message], [], message))

        # Strict content checksum verification
        if self._strict:
            # Validate configuration existence checksum
            if md5_checksum(data.get(data['metadata.yaml']['model']['configuration']['path'])) != \
                    data['metadata.yaml']['model']['configuration']['hash']:
                raise PlumsModelTreeValidationError(self._parse_errors(['configuration file checksum mismatch'],
                                                                       [],
                                                                       'configuration file checksum mismatch'))

            # Validate registered checkpoints checksum
            if self._checkpoints:
                errors = []
                for ref in data['metadata.yaml']['model']['training']['checkpoints']:
                    filename = str(Path(data['metadata.yaml']['model']['training']['checkpoints'][ref]['path'])[-1])
                    if md5_checksum(data['data']['checkpoints'].get(filename)) != \
                            data['metadata.yaml']['model']['training']['checkpoints'][ref]['hash']:
                        errors.append('checkpoint {} file checksum mismatch'.format(ref))
                if errors:
                    raise PlumsModelTreeValidationError(self._parse_errors(errors,
                                                                           [],
                                                                           'checkpoints file checksum mismatch'))
            # Check for initialisation discrepancies
            if data['metadata.yaml']['model']['initialisation']:
                # If weight file initialisation:
                if 'file' in data['metadata.yaml']['model']['initialisation']:
                    filename = str(Path(data['metadata.yaml']['model']['initialisation']['file']['path'])[-1])
                    if md5_checksum(data['data']['initialisation'].get(filename)) != \
                            data['metadata.yaml']['model']['initialisation']['file']['hash']:
                        raise \
                            PlumsModelTreeValidationError(self._parse_errors(['initialisation weight '
                                                                              'file checksum mismatch'],
                                                                             [],
                                                                             'initialisation weight '
                                                                             'file checksum mismatch'))
        return data


########################################################################################################################
# --------------------------------------------   Metadata section   -------------------------------------------------- #
########################################################################################################################
class Metadata(MetadataSchema):
    """A 'validatable' component which only accepts filename pointing to valid *PMF* metadata.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def validate(self, data):
        """Validate a PMF metadata from its location.

        Args:
            data (Any): The |Path| to the metadata file to validate.

        Returns:
            Any: The validated metadata.

        Raises:
            PlumsModelMetadataValidationError: If any offence is detected in the metadata.

        """
        with open(str(data), 'r') as f:
            meta = yaml.safe_load(f)
        return super(Metadata, self).validate(meta)


########################################################################################################################
# -----------------------------------------   Initialisation section   ----------------------------------------------- #
########################################################################################################################
class InitialisationPath(TreeComponent):
    """A 'validatable' component which only accepts valid *PMF* model data 'initialisation from *file*' tree structure.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. When performing strict validation,
            the configuration file and all registered checkpoints checksum will be matched against the checksum of the
            corresponding file on the filesystem.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    __schema__ = schema.Schema({str: Path})  # Does it only have files ?


class InitialisationPMF(Model):  # For user-friendly offence reporting purpose and documentation only
    """A 'validatable' component which only accepts valid *PMF* model data 'initialisation from *PMF* model'.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. When performing strict validation,
            the configuration file and all registered checkpoints checksum will be matched against the checksum of the
            corresponding file on the filesystem.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, strict=False, verbose=False):
        super(InitialisationPMF, self).__init__(strict=strict, verbose=verbose, checkpoints=False)


class Initialisation(DefaultTree):
    """A 'validatable' component which only accepts valid *PMF* model data initialisation tree structure.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. When performing strict validation,
            the configuration file and all registered checkpoints checksum will be matched against the checksum of the
            corresponding file on the filesystem.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, strict=False, verbose=False):
        super(Initialisation, self).__init__(schema.Or({str: Path}, {str: schema.Or(Path, dict)}),
                                             verbose=verbose, strict=strict,
                                             default={})

        self._pmf_schema = InitialisationPMF(strict=strict, verbose=verbose)
        self._path_schema = InitialisationPath(strict=strict, verbose=verbose)

    def validate(self, data):
        """Validate a given tree against the default value or one of  the *pmf* or *file* enclosed tree schema.

        Args:
            data (Any): The tree to validate.

        Returns:
            Any: The validated tree.

        Raises:
            PlumsModelTreeValidationError: If any offence is detected in the data.

        """
        super(Initialisation, self).validate(data)

        if data == self._default:
            return

        if not schema.Schema({'metadata.yaml': Path}, ignore_extra_keys=True).is_valid(data):
            return self._path_schema.validate(data)
        else:
            return self._pmf_schema.validate(data)


########################################################################################################################
# ----------------------------------------------   Data section   ---------------------------------------------------- #
########################################################################################################################
class Checkpoint(DefaultTree):
    """A 'validatable' component which only accepts valid *PMF* model data checkpoints tree structure.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. When performing strict validation,
            the configuration file and all registered checkpoints checksum will be matched against the checksum of the
            corresponding file on the filesystem.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    __schema__ = schema.Schema({str: Path})  # Does it only have files ?

    def __init__(self, strict=False, verbose=False):
        super(Checkpoint, self).__init__(self.__schema__,
                                         verbose=verbose,
                                         strict=strict,
                                         default={})


class Data(TreeComponent):
    """A 'validatable' component which only accepts valid *PMF* model data tree structure.

    Args:
        strict (bool): Optional. Default to ``True``. Toggle strict validation. When performing strict validation,
            the configuration file and all registered checkpoints checksum will be matched against the checksum of the
            corresponding file on the filesystem.
        checkpoints (bool): Whether to check for checkpoints existence.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, strict=False, verbose=False, checkpoints=True):
        super(Data, self).__init__(verbose=verbose, strict=strict)
        self._checkpoints = checkpoints
        self.__schema__ = None

    def validate(self, data):
        """Validate a given tree against the PMF data tree schema.

        Args:
            data (Any): The tree to validate.

        Returns:
            Any: The validated tree.

        Raises:
            PlumsModelTreeValidationError: If any offence is detected in the data.

        """
        if self.__schema__ is None:
            # We delay in validate because of the recursive nature of model initialisation filesystem trees
            if self._checkpoints:
                self.__schema__ = schema.Schema(
                    {
                        'build_parameters.yaml': Path,
                        'initialisation': Initialisation(strict=self._strict, verbose=self._verbose),
                        'checkpoints': Checkpoint(strict=self._strict, verbose=self._verbose),
                        schema.Optional(str): schema.Or(dict, Path)  # Additional files or directories are accepted here
                    }
                )
            else:
                self.__schema__ = schema.Schema(
                    {
                        'build_parameters.yaml': Path,
                        'initialisation': Initialisation(strict=self._strict, verbose=self._verbose),
                        schema.Optional(str): schema.Or(dict, Path)  # Additional files or directories are accepted here
                    }
                )
        return super(Data, self).validate(data)
