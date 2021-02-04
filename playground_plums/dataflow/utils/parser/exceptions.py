from collections import OrderedDict

from lark import UnexpectedInput

from .parser import PatternParser


class PatternError(Exception):
    """The error raised if an error in the provided dataset pattern syntax or construction is detected."""

    label = None

    def __init__(self, string, position, token):
        self.string = string
        self.position = position
        self.token = token

    def __str__(self):
        """Format the error into a human readable error message."""
        label = self.label.format(token=self.token)
        return '\n' \
               '{string}\n' \
               '{space}^\n' \
               '{pad}{message}'.format(string=self.string, space=' ' * self.position,
                                       pad=' ' * (self.position - len(self.label) // 2), message=label)

    __repr__ = __str__


class GroupError(PatternError):
    """The error raised if a construction error is detected in a group."""

    label = 'Invalid group name "{token}"'


class DuplicateGroupError(GroupError):
    """The error raised if group bares an already taken name."""

    label = 'The group name "{token}" is already defined'


class ReservedGroupError(GroupError):
    """The error raised if a group bares an reserved name."""

    label = 'The group name "{token}" is reserved and may not be defined'


class RecursiveFileError(GroupError):
    """The error raised if the filename's group is flagged as recursive."""

    label = 'A file group may not be recursive'


class PatternSyntaxError(PatternError):
    """The error raised if an error in the provided dataset pattern syntax is detected."""

    label = 'Invalid token "{token}"'


class InvalidGroupConstructSyntaxError(PatternSyntaxError):
    """The error raised if an error in a group syntax is detected."""

    label = 'Invalid group construct'


class MissingGroupNameSyntaxError(InvalidGroupConstructSyntaxError):
    """The error raised if a group declaration is missing a name token."""

    label = 'Missing group name'


class MissingGroupOpeningSyntaxError(InvalidGroupConstructSyntaxError):
    """The error raised if a group declaration an opening curly brace."""

    label = 'Missing group opening "{{"'


class MissingGroupClosingSyntaxError(InvalidGroupConstructSyntaxError):
    """The error raised if a group declaration is missing a closing curly brace."""

    label = 'Missing group closing "}}"'


class MissingGroupRegexSyntaxError(InvalidGroupConstructSyntaxError):
    """The error raised if a group declaration is missing a regular expression declaration."""

    label = 'Missing regex pattern after ":"'


class FileMissingSyntaxError(PatternSyntaxError):
    """The error raised if an error in the provided dataset pattern does not end with a file."""

    label = 'Path pattern must end with a file'


class DuplicateSeparatorSyntaxError(PatternSyntaxError):
    """The error raised if the provided dataset pattern has two subsequent separators at some point."""

    label = 'Either a group or a component must follow a separator token'


class InvalidNameSyntaxError(PatternSyntaxError):
    """The error raised if a name uses invalid characters."""

    label = 'Invalid name: "{token}" is illegal here'


class InvalidExtensionSyntaxError(PatternSyntaxError):
    """The error raised if an alternative extension declaration has syntax errors."""

    label = 'Invalid extension syntax'


_parser = PatternParser()


def parse_with_exception_handling(string, validator=None):
    """Parse a given string using the :class:`~lark.Lark`-based *path pattern* parser.

    Exception raised by the parser are reworked in a error-driven fashion to provide user-friendly exceptions.
    Moreover, if a validator is provided, it will be run against the parsed |PathComponentResolver| list result to
    ensure *semantic* correctness on top of *syntactic* correctness.

    Args:
        string (str): The dataset pattern string to parse.
        validator (Callable): A callable which take the parsed string and the resulting |PathComponentResolver| list
            as inputs to run correctness checks. It is expected to raise :exc:`PatternError` in case of errors.

    Returns:
        [|PathComponentResolver|]: A list of resolvers resulting from the parsing pass.

    Raises:
        PatternError: If the provided string has a construction error.
        PatternSyntaxError: If the provided string has a syntax error.

    """
    try:
        resolvers = _parser.parse(string)
    except UnexpectedInput as error:
        try:
            exc_class = \
                error.match_examples(_parser.parse,
                                     OrderedDict([
                                         (InvalidNameSyntaxError, ['/{gro+up}/somewhere.ext',
                                                                   '/{gro+up:[^\\]+}/somewhere.ext',
                                                                   '/{gr+oup:[^\\]{2}}/somewhere.ext',
                                                                   '/{gro+up/}/somewhere.ext',
                                                                   '/co+mp/{somewhere}.ext',
                                                                   '/co+mp/{somewhere:[^\\]+}.ext',
                                                                   '/c+omp/{somewhere:[^\\]{2}}.ext',
                                                                   '/{group}/some+where.ext',
                                                                   '/{group:[^\\]+}/somew+here.ext',
                                                                   '/{group:[^\\]{2}}/som+ewhere.ext',
                                                                   '/{group/}/some+where.ext',
                                                                   '/comp/{somew+here}.ext',
                                                                   '/comp/{somewh+ere:[^\\]+}.ext',
                                                                   '/comp/{somew+here:[^\\]{2}}.ext']),
                                         (InvalidGroupConstructSyntaxError, ['/{grou/p}/somewhere.ext',
                                                                             '/{grou/p:[^\\]+}/somewhere.ext',
                                                                             '/{grou/p:[^\\]{2}}/somewhere.ext',
                                                                             '/{grou/p/}/somewhere.ext',
                                                                             '/comp/{somewh/ere}.ext',
                                                                             '/comp/{somewh/ere:[^\\]+}.ext',
                                                                             '/comp/{somewh/ere:[^\\]{2}}.ext']),
                                         (MissingGroupOpeningSyntaxError, ['/{group}}/somewhere.ext',
                                                                           '/{group:[^\\]+}}/somewhere.ext',
                                                                           '/{group:[^\\]{2}}}/somewhere.ext',
                                                                           '/{group/}}/somewhere.ext',
                                                                           '/comp/somewhere}.ext',
                                                                           '/comp/somewhere:[^\\]+}.ext',
                                                                           '/comp/somewhere:[^\\]{2}}.ext']),
                                         (MissingGroupNameSyntaxError, ['/{}/somewhere.ext',
                                                                        '/{:[^\\]+}/somewhere.ext',
                                                                        '/{:[^\\]{2}}/somewhere.ext',
                                                                        '/{/}/somewhere.ext',
                                                                        '/comp/{}.ext',
                                                                        '/comp/{:[^\\]+}.ext',
                                                                        '/comp/{:[^\\]{2}}.ext']),
                                         (MissingGroupClosingSyntaxError, ['/{group/somewhere.ext',
                                                                           '/{group:[^\\]+/somewhere.ext',
                                                                           '/{group:[^\\]{2}/somewhere.ext',
                                                                           '/{group//somewhere.ext',
                                                                           '/comp/{somewhere.ext',
                                                                           '/comp/{somewhere:[^\\]+.ext',
                                                                           '/comp/{somewhere:[^\\]{2}.ext']),
                                         (MissingGroupRegexSyntaxError, ['/{group:}/somewhere.ext',
                                                                         '/{group/:}/somewhere.ext',
                                                                         '/comp/{somewhere:}.ext',
                                                                         '/comp/{somewhere/:}.ext']),
                                         (FileMissingSyntaxError, ['/{group}/somewhere',
                                                                   '/{group}/somewhere/',
                                                                   '/{group:[^\\]+}/somewhere',
                                                                   '/{group:[^\\]+}/somewhere/',
                                                                   '/comp/{somewhere}',
                                                                   '/comp/{somewhere/}',
                                                                   '/comp/{somewhere:[^\\]+}',
                                                                   '/comp/{somewhere/:[^\\]+}',
                                                                   '/comp/{somewhere}/',
                                                                   '/comp/{somewhere/}/',
                                                                   '/comp/{somewhere:[^\\]+}/',
                                                                   '/comp/{somewhere/:[^\\]+}/',
                                                                   '/{group}/somewhere[ext|other]',
                                                                   '/{group}/somewhere/[ext|other]',
                                                                   '/{group:[^\\]+}/somewhere[ext|other]',
                                                                   '/{group:[^\\]+}/somewhere/[ext|other]',
                                                                   '/comp/{somewhere}[ext|other]',
                                                                   '/comp/{somewhere/}[ext|other]',
                                                                   '/comp/{somewhere:[^\\]+}[ext|other]',
                                                                   '/comp/{somewhere/:[^\\]+}[ext|other]',
                                                                   '/comp/{somewhere}/[ext|other]',
                                                                   '/comp/{somewhere/}/[ext|other]',
                                                                   '/comp/{somewhere:[^\\]+}/[ext|other]',
                                                                   '/comp/{somewhere/:[^\\]+}/[ext|other]',
                                                                   '/{group}/somewhere.',
                                                                   '/{group:[^\\]+}/somewhere.',
                                                                   '/comp/{somewhere}.',
                                                                   '/comp/{somewhere/}.',
                                                                   '/comp/{somewhere:[^\\]+}.',
                                                                   '/comp/{somewhere/:[^\\]+}.']),
                                         (DuplicateSeparatorSyntaxError, ['/{group}//somewhere.ext',
                                                                          '/{group:[^\\]+}//somewhere.ext',
                                                                          '//comp/{somewhere}.ext',
                                                                          '//comp/{somewhere/}.ext',
                                                                          '//comp/{somewhere:[^\\]+}.ext',
                                                                          '//comp/{somewhere/:[^\\]+}.ext']),
                                         (InvalidExtensionSyntaxError, ['/{group}/somewhere.[ext|other',
                                                                        '/{group}/somewhere.ext|other]',
                                                                        '/{group}/somewhere.[|other]',
                                                                        '/{group}/somewhere.[ext|]',
                                                                        '/comp/{somewhere}.[ext|other',
                                                                        '/comp/{somewhere}.ext|other]',
                                                                        '/comp/{somewhere}.[|other]',
                                                                        '/comp/{somewhere}.[ext|]'])]))
        except AssertionError:
            exc_class = PatternSyntaxError
        if not exc_class:
            exc_class = PatternSyntaxError
        raise exc_class(string, error.pos_in_stream, error.token) from None

    if validator is not None:
        validator(string, resolvers)

    return resolvers
