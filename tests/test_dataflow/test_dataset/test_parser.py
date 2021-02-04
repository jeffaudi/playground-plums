import pytest

from playground_plums.dataflow.utils.parser import Parser, ComponentResolver, GroupResolver, ExtensionResolver, \
    PatternSyntaxError, InvalidGroupConstructSyntaxError, MissingGroupRegexSyntaxError, MissingGroupNameSyntaxError, \
    MissingGroupOpeningSyntaxError, MissingGroupClosingSyntaxError, FileMissingSyntaxError, \
    DuplicateSeparatorSyntaxError, InvalidNameSyntaxError, InvalidExtensionSyntaxError, DuplicateGroupError, \
    ReservedGroupError, RecursiveFileError


def test_component_resolver():
    resolver = ComponentResolver('some_name')
    assert resolver.name == 'some_name'
    assert resolver.extension is None
    assert resolver.regex == 'some_name'
    assert resolver.pattern == 'some_name'

    resolver = ComponentResolver('')
    assert not resolver.name
    assert resolver.extension is None

    resolver.name = 'some_name'
    assert resolver.name == 'some_name'
    assert resolver.regex == 'some_name'
    assert resolver.pattern == 'some_name'


def test_group_resolver():  # noqa: R701
    resolver = GroupResolver('some_name')
    assert resolver.name == 'some_name'
    assert resolver.extension is None
    assert not resolver.recursive
    assert resolver.filter == '[^/]+'
    assert resolver.regex == '(?P<some_name>[^/]+)'
    assert resolver.pattern == '{some_name}'

    resolver = GroupResolver('')
    assert not resolver.name
    assert resolver.extension is None

    resolver.name = 'some_name'
    assert resolver.name == 'some_name'
    assert not resolver.recursive
    assert resolver.filter == '[^/]+'
    assert resolver.regex == '(?P<some_name>[^/]+)'
    assert resolver.pattern == '{some_name}'

    resolver.recursive = True
    assert resolver.recursive
    assert resolver.filter == '[^/]+'
    assert resolver.regex == '(?P<some_name>(?:[^/]+/?)+)'
    assert resolver.pattern == '{some_name/}'

    resolver = GroupResolver('some_name')
    resolver.filter = r'[\w]+'

    assert resolver.name == 'some_name'
    assert not resolver.recursive
    assert resolver.filter == r'[\w]+'
    assert resolver.regex == r'(?P<some_name>[\w]+)'
    assert resolver.pattern == r'{some_name:[\w]+}'

    resolver.recursive = True
    assert resolver.recursive
    assert resolver.filter == r'[\w]+'
    assert resolver.regex == r'(?P<some_name>(?:[\w]+/?)+)'
    assert resolver.pattern == r'{some_name/:[\w]+}'


def test_extension_resolver():
    resolver = ExtensionResolver('some_name')
    assert resolver.name == 'some_name'
    assert not resolver.alternative
    assert not resolver.extensions
    assert resolver.regex == r'\.some_name'
    assert resolver.pattern == '.some_name'

    resolver = ExtensionResolver('')
    assert not resolver.name

    resolver.name = 'some_name'
    assert resolver.name == 'some_name'
    assert not resolver.alternative
    assert not resolver.extensions
    assert resolver.regex == r'\.some_name'
    assert resolver.pattern == '.some_name'

    resolver.alternative = True
    assert resolver.name == 'some_name'
    assert resolver.alternative
    assert not resolver.extensions
    assert resolver.regex == r'\.(?:)'
    assert resolver.pattern == '.[]'

    resolver.extensions = ['some', 'extension']
    assert resolver.name == 'some_name'
    assert resolver.alternative
    assert resolver.extensions
    assert resolver.regex == r'\.(?:some|extension)'
    assert resolver.pattern == '.[some|extension]'


def test_components():  # noqa: R701
    parser = Parser()

    # Relative
    pattern = 'some/simple/relative/pattern.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], ComponentResolver)
    assert resolvers[1].extension is None
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], ComponentResolver)
    assert resolvers[2].extension is None
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], ComponentResolver)
    assert resolvers[3].extension is not None
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative

    # Absolute
    pattern = '/simple/absolute/pattern.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], ComponentResolver)
    assert resolvers[1].extension is None
    assert resolvers[2].name == 'absolute'
    assert isinstance(resolvers[2], ComponentResolver)
    assert resolvers[2].extension is None
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], ComponentResolver)
    assert resolvers[3].extension is not None
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative


def test_groups():  # noqa: R701
    parser = Parser()

    # Relative
    pattern = '{some}/{simple}/{relative}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '[^/]+'
    assert not resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is not None
    assert resolvers[3].filter == '[^/]+'
    assert not resolvers[3].recursive
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative

    # Absolute
    pattern = '/{simple}/{absolute}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'absolute'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is not None
    assert resolvers[3].filter == '[^/]+'
    assert not resolvers[3].recursive
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative


def test_recursive():  # noqa: R701
    parser = Parser()

    # Relative
    pattern = '{some/}/{simple}/{relative/}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '[^/]+'
    assert resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is not None
    assert resolvers[3].filter == '[^/]+'
    assert not resolvers[3].recursive
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative

    # Absolute
    pattern = '/{some/}/{simple}/{absolute/}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'some'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert resolvers[1].recursive
    assert resolvers[2].name == 'simple'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'absolute'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is None
    assert resolvers[3].filter == '[^/]+'
    assert resolvers[3].recursive
    assert resolvers[4].name == 'pattern'
    assert isinstance(resolvers[4], GroupResolver)
    assert resolvers[4].extension is not None
    assert resolvers[4].filter == '[^/]+'
    assert not resolvers[4].recursive
    assert isinstance(resolvers[4].extension, ExtensionResolver)
    assert resolvers[4].extension.name == 'extension'
    assert not resolvers[4].extension.alternative


def test_regex():  # noqa: R701
    parser = Parser()

    # Relative
    pattern = r'{some:.+}/{simple}/{relative/:\w+}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '.+'
    assert not resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == r'\w+'
    assert resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is not None
    assert resolvers[3].filter == '[^/]+'
    assert not resolvers[3].recursive
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative

    # Absolute
    pattern = r'/{some:.+}/{simple}/{absolute/:\w+}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'some'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '.+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'simple'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'absolute'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is None
    assert resolvers[3].filter == r'\w+'
    assert resolvers[3].recursive
    assert resolvers[4].name == 'pattern'
    assert isinstance(resolvers[4], GroupResolver)
    assert resolvers[4].extension is not None
    assert resolvers[4].filter == '[^/]+'
    assert not resolvers[4].recursive
    assert isinstance(resolvers[4].extension, ExtensionResolver)
    assert resolvers[4].extension.name == 'extension'
    assert not resolvers[4].extension.alternative


def test_extensions():  # noqa: R701
    parser = Parser()

    # Simple extension
    # GroupResolver
    # Relative
    pattern = r'{some:.+}/{simple}/{relative/:\w+}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '.+'
    assert not resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == r'\w+'
    assert resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is not None
    assert resolvers[3].filter == '[^/]+'
    assert not resolvers[3].recursive
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative

    # Absolute
    pattern = r'/{some:.+}/{simple}/{absolute/:\w+}/{pattern}.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'some'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '.+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'simple'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'absolute'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is None
    assert resolvers[3].filter == r'\w+'
    assert resolvers[3].recursive
    assert resolvers[4].name == 'pattern'
    assert isinstance(resolvers[4], GroupResolver)
    assert resolvers[4].extension is not None
    assert resolvers[4].filter == '[^/]+'
    assert not resolvers[4].recursive
    assert isinstance(resolvers[4].extension, ExtensionResolver)
    assert resolvers[4].extension.name == 'extension'
    assert not resolvers[4].extension.alternative

    # Simple extension
    # ComponentResolver
    # Relative
    pattern = r'{some:.+}/{simple}/{relative/:\w+}/pattern.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '.+'
    assert not resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == r'\w+'
    assert resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], ComponentResolver)
    assert resolvers[3].extension is not None
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert not resolvers[3].extension.alternative

    # Absolute
    pattern = r'/{some:.+}/{simple}/{absolute/:\w+}/pattern.extension'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'some'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '.+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'simple'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'absolute'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is None
    assert resolvers[3].filter == r'\w+'
    assert resolvers[3].recursive
    assert resolvers[4].name == 'pattern'
    assert isinstance(resolvers[4], ComponentResolver)
    assert resolvers[4].extension is not None
    assert isinstance(resolvers[4].extension, ExtensionResolver)
    assert resolvers[4].extension.name == 'extension'
    assert not resolvers[4].extension.alternative

    # Alternative extension
    # GroupResolver
    # Relative
    pattern = r'{some:.+}/{simple}/{relative/:\w+}/{pattern}.[extension|other|last]'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '.+'
    assert not resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == r'\w+'
    assert resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is not None
    assert resolvers[3].filter == '[^/]+'
    assert not resolvers[3].recursive
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert resolvers[3].extension.alternative
    assert resolvers[3].extension.extensions == ['extension', 'other', 'last']

    # Absolute
    pattern = r'/{some:.+}/{simple}/{absolute/:\w+}/{pattern}.[extension|other|last]'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'some'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '.+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'simple'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'absolute'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is None
    assert resolvers[3].filter == r'\w+'
    assert resolvers[3].recursive
    assert resolvers[4].name == 'pattern'
    assert isinstance(resolvers[4], GroupResolver)
    assert resolvers[4].extension is not None
    assert resolvers[4].filter == '[^/]+'
    assert not resolvers[4].recursive
    assert isinstance(resolvers[4].extension, ExtensionResolver)
    assert resolvers[4].extension.name == 'extension'
    assert resolvers[4].extension.alternative
    assert resolvers[4].extension.extensions == ['extension', 'other', 'last']

    # Simple extension
    # ComponentResolver
    # Relative
    pattern = r'{some:.+}/{simple}/{relative/:\w+}/pattern.[extension|other|last]'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == 'some'
    assert isinstance(resolvers[0], GroupResolver)
    assert resolvers[0].extension is None
    assert resolvers[0].filter == '.+'
    assert not resolvers[0].recursive
    assert resolvers[1].name == 'simple'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '[^/]+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'relative'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == r'\w+'
    assert resolvers[2].recursive
    assert resolvers[3].name == 'pattern'
    assert isinstance(resolvers[3], ComponentResolver)
    assert resolvers[3].extension is not None
    assert isinstance(resolvers[3].extension, ExtensionResolver)
    assert resolvers[3].extension.name == 'extension'
    assert resolvers[3].extension.alternative
    assert resolvers[3].extension.extensions == ['extension', 'other', 'last']

    # Absolute
    pattern = r'/{some:.+}/{simple}/{absolute/:\w+}/pattern.[extension|other|last]'
    resolvers = parser.parse(pattern)
    assert resolvers[0].name == '/'
    assert isinstance(resolvers[0], ComponentResolver)
    assert resolvers[0].extension is None
    assert resolvers[1].name == 'some'
    assert isinstance(resolvers[1], GroupResolver)
    assert resolvers[1].extension is None
    assert resolvers[1].filter == '.+'
    assert not resolvers[1].recursive
    assert resolvers[2].name == 'simple'
    assert isinstance(resolvers[2], GroupResolver)
    assert resolvers[2].extension is None
    assert resolvers[2].filter == '[^/]+'
    assert not resolvers[2].recursive
    assert resolvers[3].name == 'absolute'
    assert isinstance(resolvers[3], GroupResolver)
    assert resolvers[3].extension is None
    assert resolvers[3].filter == r'\w+'
    assert resolvers[3].recursive
    assert resolvers[4].name == 'pattern'
    assert isinstance(resolvers[4], ComponentResolver)
    assert resolvers[4].extension is not None
    assert isinstance(resolvers[4].extension, ExtensionResolver)
    assert resolvers[4].extension.name == 'extension'
    assert resolvers[4].extension.alternative
    assert resolvers[4].extension.extensions == ['extension', 'other', 'last']


def test_parse_errors():
    parser = Parser(reserved=('reserved', 'words'))

    # Subsequent /
    pattern = r'/{some/}/simple//{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(DuplicateSeparatorSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}//simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(DuplicateSeparatorSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'//{some/}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(DuplicateSeparatorSyntaxError):
        _ = parser.parse(pattern)

    # / in braces
    pattern = r'/{some/not}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(InvalidGroupConstructSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute/beginner:\w+}/{pattern}.extension'
    with pytest.raises(InvalidGroupConstructSyntaxError):
        _ = parser.parse(pattern)

    # Duplicate group name
    pattern = r'{some/}/simple/{absolute:\w+}/{some}.extension'
    with pytest.raises(DuplicateGroupError):
        _ = parser.parse(pattern)

    pattern = r'{some/}/simple/{some:\w+}/{pattern}.extension'
    with pytest.raises(DuplicateGroupError):
        _ = parser.parse(pattern)

    pattern = r'/{absolute/}/simple/{absolute:\w+}/{pattern}.extension'
    with pytest.raises(DuplicateGroupError):
        _ = parser.parse(pattern)

    # Reserved group name
    pattern = r'{reserved/}/simple/{absolute:\w+}/{some}.extension'
    with pytest.raises(ReservedGroupError):
        _ = parser.parse(pattern)

    pattern = r'/{reserved}/simple/{some:\w+}/{pattern}.extension'
    with pytest.raises(ReservedGroupError):
        _ = parser.parse(pattern)

    pattern = r'{absolute/}/simple/{words:\w+}/{pattern}.extension'
    with pytest.raises(ReservedGroupError):
        _ = parser.parse(pattern)

    pattern = r'/{absolute/}/simple/{some:\w+}/{words}.extension'
    with pytest.raises(ReservedGroupError):
        _ = parser.parse(pattern)

    # Missing group name
    pattern = r'{/}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{/}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{}.extension'
    with pytest.raises(MissingGroupNameSyntaxError):
        _ = parser.parse(pattern)

    # Bad group name
    pattern = r'{name.error/}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(InvalidNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{name/}/simple/{abs*olute/:\w+}/{pattern}.extension'
    with pytest.raises(InvalidNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{err+or:\w+}/{pattern}.extension'
    with pytest.raises(InvalidNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{invalid.file}.extension'
    with pytest.raises(InvalidNameSyntaxError):
        _ = parser.parse(pattern)

    # Curly-braces mismatch
    pattern = r'/{some/}/simple/{absolute/:\w+/{pattern}.extension'
    with pytest.raises(PatternSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some//simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupClosingSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute/:\w+{}/{pattern}.extension'
    with pytest.raises(PatternSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute/:\w+}/{{pattern}.extension'
    with pytest.raises(MissingGroupNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{{some/}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple}/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupOpeningSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute/:\w+}/{pattern}}.extension'
    with pytest.raises(MissingGroupOpeningSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}}/simple/{absolute/:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupOpeningSyntaxError):
        _ = parser.parse(pattern)

    # Regex token missing
    pattern = r'/{some/}/simple/{absolute\w+}/{pattern}.extension'
    with pytest.raises(InvalidNameSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/\w?}/simple/{absolute:\w+}/{pattern}.extension'
    with pytest.raises(InvalidGroupConstructSyntaxError):
        _ = parser.parse(pattern)

    # Regex missing
    pattern = r'/{some/}/simple/{absolute:}/{pattern}.extension'
    with pytest.raises(MissingGroupRegexSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/:}/simple/{absolute:\w+}/{pattern}.extension'
    with pytest.raises(MissingGroupRegexSyntaxError):
        _ = parser.parse(pattern)

    # Recursive file
    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern/}.extension'
    with pytest.raises(RecursiveFileError):
        _ = parser.parse(pattern)

    # Missing extension
    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}'
    with pytest.raises(FileMissingSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.'
    with pytest.raises(FileMissingSyntaxError):
        _ = parser.parse(pattern)

    # Bad alternative extension format
    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.[extension|other'
    with pytest.raises(InvalidExtensionSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.extension|other]'
    with pytest.raises(InvalidExtensionSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.[extension|]'
    with pytest.raises(InvalidExtensionSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.[|other]'
    with pytest.raises(InvalidExtensionSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.extension|other'
    with pytest.raises(InvalidExtensionSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.{extension|other}'
    with pytest.raises(FileMissingSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.[extension/|other]'
    with pytest.raises(PatternSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.[extension:\w+|other]'
    with pytest.raises(PatternSyntaxError):
        _ = parser.parse(pattern)

    pattern = r'/{some/}/simple/{absolute:\w+}/{pattern}.[]'
    with pytest.raises(InvalidExtensionSyntaxError):
        _ = parser.parse(pattern)
