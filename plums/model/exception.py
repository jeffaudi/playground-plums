import abc

from schema import SchemaError


class PlumsError(Exception):
    """Base exception for all Plums specific errors."""

    pass


class PlumsValidationError(SchemaError, PlumsError, metaclass=abc.ABCMeta):
    """Base exception for all Plums schema validation specific errors.

    It inherits from :exc:`schema.SchemaError`.

    """

    pass


class PlumsModelError(PlumsError):
    """Base exception for all Plums Model specific errors."""

    pass


class PlumsModelTreeValidationError(PlumsValidationError, PlumsModelError):
    """Base exception for all Plums Model validation errors specific to filesystem trees validations."""

    pass


class PlumsModelMetadataValidationError(PlumsValidationError, PlumsModelError):
    """Base exception for all Plums Model validation errors specific to filesystem trees validations."""

    pass
