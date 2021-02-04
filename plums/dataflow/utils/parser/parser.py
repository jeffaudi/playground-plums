from lark import Lark, Transformer

from plums.commons.path import Path
from .resolver import ComponentResolver, GroupResolver, ExtensionResolver


class PatternTransformer(Transformer):
    """A class which recurse through the *path pattern* AST_ and construct a list of |PathComponentResolver|.

    .. AST_: https://en.wikipedia.org/wiki/Abstract_syntax_tree

    """

    def component(self, name):
        """Construct a |ComponentResolver| from the abstract syntax tree."""
        return ComponentResolver(str(name[0]))

    def group(self, data):
        """Construct a |ComponentResolver| from the abstract syntax tree."""
        group = GroupResolver(str(data[0]))
        group.recursive = data[1] is not None

        if data[2] is not None:
            group.filter = str(data[2])

        return group

    def simple_extension(self, name):
        """Construct a |ExtensionResolver| with a simple syntax from the abstract syntax tree."""
        return ExtensionResolver(str(name[0]))

    def alternative_extension(self, data):
        """Construct a |ExtensionResolver| with an alternative syntax from the abstract syntax tree."""
        extension = ExtensionResolver(str(data[0]))

        if len(data) >= 2:
            extension.alternative = True
            extension.extensions = list(map(str, data))

        return extension

    def file(self, data):
        """Construct a |PathComponentResolver| with an attached |ExtensionResolver| from the abstract syntax tree."""
        entry, extension = data

        entry.extension = extension
        return entry

    def folder(self, entry):
        """Construct a |PathComponentResolver| for a folder from the abstract syntax tree."""
        return entry[0]

    def absolute(self, data):
        """Construct a |ComponentResolver| with the absolute root "/" from the abstract syntax tree."""
        return ComponentResolver(str(data[0]))

    def pattern(self, tree):
        """Construct a list of |PathComponentResolver| from the abstract syntax tree."""
        return tree


class PatternParser:
    """The |Parser| class is used to parse a dataset pattern using :class:`~lark.Lark`-based *EBNF*-driven parser."""

    def __init__(self):
        self._transformer = PatternTransformer()
        with open(str(Path(__file__)[:-1] / 'grammar.lark'), 'r') as f:
            self._parser = Lark(f, start='pattern', parser='lalr',
                                maybe_placeholders=True, transformer=self._transformer)

    def parse(self, string):
        """Parse a dataset pattern string into a list of |PathComponentResolver|.

        Args:
            string (str): The dataset pattern string to parse.

        Returns:
            [|PathComponentResolver|]: A list of resolvers resulting from the parsing pass.

        Raises:
            PatternSyntaxError: If the provided string has a syntax error.

        """
        tree = self._parser.parse(string)
        return tree
