import schema

from plums.commons.path import Path as PlumsPath
from plums.model.exception import PlumsValidationError
from plums.model.validation.utils.validate_path import is_pathname_valid


class SchemaComponent(object):
    """A 'validatable' component in a ``schema`` validation.

    To alleviate complex nested schema creation and validation, one possible solution is to cut it up into semantically
    consistent chunks, each defining its innermost schema.

    With this, each component validation might be customized (if one needs to check more than the innermost schema
    data conformity, *e.g.* for data cross-dependencies or to simplify optional or default value definition) and
    it is easier to accumulate and report all offending data elements in one shot.

    The class |SchemaComponent| defines a simple building block which allows both static and dynamic schema composition
    by defining its enclosed schema respectively as a :obj:`class` attribute or a :obj:`instance` attribute.

    See Also:
        The `Schema library <https://github.com/keleshev/schema>`_ for more information on the schema validation
        backend.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    __schema__ = None

    def __init__(self, verbose=False):
        self.__schema__ = self.__schema__ if self.__schema__ is not None else schema.Schema(None)
        self._verbose = verbose

    def _parse_errors(self, errors, autos, code):
        if self._verbose:
            failure_report = ':\n> errors: {}\n> autos: {}'.format(errors, autos)
        else:
            failure_report = ': {}'.format(code)
        return 'Invalid {} provided{}'.format(self.__class__.__name__, failure_report)

    def validate(self, data):
        """Validate a given data against the enclosed schema.

        Args:
            data (Any): The data to validate.

        Returns:
            Any: The validated data.

        Raises:
            PlumsValidationError: If any offence is detected in the data.

        """
        try:
            return self.__schema__.validate(data)
        except (schema.SchemaError, PlumsValidationError) as e:
            # Bubble up eventual subclasses as is.
            if isinstance(e, PlumsValidationError):
                raise e.__class__(self._parse_errors(e.errors, e.autos, e.code))

            raise PlumsValidationError(self._parse_errors(e.errors, e.autos, e.code))

    def is_valid(self, data):
        """Return whether a given data is valid with regard to :attr:`validate`.

        Args:
            data (Any): The data to validate.

        Returns:
            bool: ``True`` if data is valid.

        """
        try:
            self.validate(data)
        except PlumsValidationError:
            return False
        return True


class Default(SchemaComponent):
    """A 'validatable' component in a ``schema`` validation which accepts a default ``null`` value.

    Args:
        schema_ (Validatable): A schema to enclose.
        default (Any): A default ``null`` value to accept as a valid data.
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    def __init__(self, schema_, default=None, verbose=False):
        super(Default, self).__init__(verbose=verbose)
        self.__schema__ = schema_
        self._default = default

    def _parse_errors(self, errors, autos, code):
        if self._verbose:
            failure_report = ':\n> errors: {}\n> autos: {}'.format(errors, autos)
        else:
            failure_report = ': {}'.format(code)
        return 'Invalid {} provided: Invalid value or default ({}){}'.format(self.__class__.__name__,
                                                                             self._default,
                                                                             failure_report)

    def validate(self, data):
        """Validate a given data against the enclosed schema or the default value.

        Args:
            data (Any): The data to validate.

        Returns:
            Any: The validated data.

        Raises:
            PlumsValidationError: If any offence is detected in the data.

        """
        try:
            return super(Default, self).validate(data)
        except (schema.SchemaError, PlumsValidationError) as e:
            if not data == self._default:
                # Bubble up eventual subclasses as is.
                if isinstance(e, PlumsValidationError):
                    raise e.__class__(self._parse_errors(e.errors, e.autos, e.code))

                raise PlumsValidationError(self._parse_errors(e.errors, e.autos, e.code))
            return data


class Path(SchemaComponent):
    """A 'validatable' component in a ``schema`` validation which only accepts syntactically valid *path*.

    Warnings:
        Validation is only performed on syntactical considerations, not on whether the given *path* points to an
        existing location.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    __schema__ = schema.Schema(schema.Or(str, bytes))

    def validate(self, data):
        """Validate a given *path*.

        Args:
            data (Any): The *path* to validate.

        Raises:
            PlumsValidationError: If any offence is detected in the data.

        """
        data = super(Path, self).validate(data)
        if not is_pathname_valid(data):
            raise PlumsValidationError('Invalid Pathname provided.')
        return PlumsPath(data)


class MD5Checksum(SchemaComponent):
    """A 'validatable' component in a ``schema`` validation which only accepts syntactically valid *MD5* hash.

    Args:
        verbose (bool): Optional. Default to ``False``. Toggle exhaustive schema offence reporting.

    """

    __schema__ = schema.Regex(r'^[a-f0-9]{32}$', error='Invalid file checksum provided: Expected a valid MD5 hash.')
