from .exceptions import parse_with_exception_handling, PatternError, PatternSyntaxError, \
    InvalidGroupConstructSyntaxError, MissingGroupRegexSyntaxError, MissingGroupNameSyntaxError, \
    MissingGroupOpeningSyntaxError, MissingGroupClosingSyntaxError, FileMissingSyntaxError, \
    DuplicateSeparatorSyntaxError, InvalidNameSyntaxError, InvalidExtensionSyntaxError, DuplicateGroupError, \
    ReservedGroupError, RecursiveFileError
from .resolver import ComponentResolver, GroupResolver, ExtensionResolver
from .validator import Validator


class Parser(object):
    """The |Parser| class is used to parse a dataset pattern into a list of |PathComponentResolver|.

    It parses the dataset pattern micro-language which support a limited set of basic constructs.

    More information on the micro-language grammar and specification can be found in the |PatternDataset| documentation.

    Args:
        reserved (Sequence[str]): If provided, a sequence of words which can not be used as group's name.

    """

    def __init__(self, reserved=()):
        self._resolvers = []
        self._validator = Validator(reserved=reserved)

    @property
    def resolvers(self):
        """[|PathComponentResolver|]: A list of resolvers resulting from the last parsing pass."""
        return self._resolvers

    def reset(self):
        """Reset the |Parser| to its factory state."""
        # Reset resolver list
        self._resolvers = []

    def parse(self, string):
        """Parse a dataset pattern string into a list of |PathComponentResolver|.

        Args:
            string (str): The dataset pattern string to parse.

        Returns:
            [|PathComponentResolver|]: A list of resolvers resulting from the parsing pass.

        Raises:
            PatternError: If the provided string has a construction error.
            PatternSyntaxError: If the provided string has a syntax error.

        """
        self.reset()
        self._resolvers = parse_with_exception_handling(string, validator=self._validator)
        return self._resolvers
