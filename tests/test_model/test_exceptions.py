import pytest
from schema import SchemaError, SchemaForbiddenKeyError, SchemaMissingKeyError, \
    SchemaOnlyOneAllowedError, SchemaUnexpectedTypeError, SchemaWrongKeyError

from playground_plums.model.exception import PlumsError, PlumsValidationError, PlumsModelError, \
    PlumsModelMetadataValidationError, PlumsModelTreeValidationError


__schema_errors_list = [SchemaError, SchemaUnexpectedTypeError, SchemaWrongKeyError, SchemaMissingKeyError,
                        SchemaOnlyOneAllowedError, SchemaForbiddenKeyError]
__schema_errors_name = [error.__name__ for error in __schema_errors_list]

__plums_errors_list = [PlumsError, PlumsValidationError, PlumsModelError,
                       PlumsModelMetadataValidationError, PlumsModelTreeValidationError]
__plums_errors_name = [error.__name__ for error in __plums_errors_list]

__schema_errors = {name: error for name, error in zip(__schema_errors_name, __schema_errors_list)}
__plums_errors = {name: error for name, error in zip(__plums_errors_name, __plums_errors_list)}


@pytest.fixture(params=__plums_errors_name)
def plums_error(request):
    return __plums_errors[request.param]('Some plums error.')


@pytest.fixture(params=__schema_errors_name)
def schema_error(request):
    return __schema_errors[request.param]('Some schema error.')


class TestExceptions:
    def test_plums_inheritance(self, plums_error):
        assert isinstance(plums_error, PlumsError)

    # Useless due to: https://bugs.python.org/issue12029
    # Awaiting status on: https://github.com/python/cpython/pull/6461
    # def test_plus_validation_inheritance(self, schema_error):  # noqa: E800
    #     assert isinstance(schema_error, PlumsValidationError)  # noqa: E800
    #     assert not isinstance(schema_error, PlumsModelTreeValidationError)  # noqa: E800
    #     assert not isinstance(schema_error, PlumsModelMetadataValidationError)  # noqa: E800

    def test_attributes(self, plums_error):
        if isinstance(plums_error, PlumsValidationError):
            assert hasattr(plums_error, 'errors')
            assert hasattr(plums_error, 'autos')
            assert hasattr(plums_error, 'code')

    # def test_plums_except(self, schema_error):  # noqa: E800
    #     with pytest.raises(PlumsValidationError):  # noqa: E800
    #         raise schema_error  # noqa: E800
    #
    #     # Fails due to: https://bugs.python.org/issue12029
    #     # Awaiting status on: https://github.com/python/cpython/pull/6461
    #     # try:  # noqa: E800
    #     #     raise schema_error  # noqa: E800
    #     # except PlumsValidationError:  # noqa: E800
    #     #     pass  # noqa: E800
    #     # except Exception as e:  # noqa: E800
    #     #     raise e  # noqa: E800

    def test_schema_except(self, plums_error):
        if isinstance(plums_error, PlumsValidationError):
            with pytest.raises(SchemaError):
                raise plums_error

            try:
                raise plums_error
            except SchemaError:
                pass
            except Exception as e:
                raise e
