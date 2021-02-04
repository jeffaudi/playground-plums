from abc import ABCMeta, abstractmethod


class PathComponentResolver(object, metaclass=ABCMeta):
    """A *resolver* is a class which translates to a *regular expresion* depending on a various parameters.

    Args:
        name (str): The resolver's name.

    """

    def __init__(self, name=''):
        self.name = name

    def __str__(self):
        """Return the resolver's regular expresion representation."""
        return self.regex

    def __repr__(self):
        """Return a pythonic representation of the resolver."""
        return '{}({})'.format(self.__class__.__name__, self.name)

    @property
    def pattern(self):
        """str: The resolver's path pattern expression representation."""
        return self._pattern()

    @abstractmethod
    def _pattern(self):
        """Compute a path pattern expression from the resolver's parameters and name."""
        raise NotImplementedError

    @property
    def regex(self):
        """str: The resolver's regular expression representation."""
        return self._regex()

    @abstractmethod
    def _regex(self):
        """Compute a regular expression from the resolver's parameters and name."""
        raise NotImplementedError


class ExtensionResolver(PathComponentResolver):
    """A *resolver* for file extensions.

    It handles both simple and alternative file extensions.

    Args:
        name (str): The resolver's name.

    Attributes:
        alternative (bool): If ``True``, the file extension is considered to be an alternative extension and the
            *regular expresion* is computed using the extensions stored in :attr:`extensions`. If ``False``, the
            extension is assumed to be simple and the :attr:`name` is used instead.
        extensions (list): A list of extensions used with alternative extensions.

    """

    def __init__(self, name=''):
        super(ExtensionResolver, self).__init__(name=name)
        self.alternative = False
        self.extensions = []

    def _regex(self):
        if self.alternative:
            return r'\.(?:{extensions})'.format(extensions='|'.join(self.extensions))
        else:
            return r'\.{name}'.format(name=self.name)

    def _pattern(self):
        if self.alternative:
            return '.[{extensions}]'.format(extensions='|'.join(self.extensions))
        else:
            return '.{name}'.format(name=self.name)


class GroupResolver(PathComponentResolver):
    """A *resolver* for named groups.

    It handles both simple and recursive groups with customized entity regex.

    Args:
        name (str): The resolver's name.

    Attributes:
        recursive (bool): If ``True``, the group is considered recursive and the resulting *regular expresion* will
            accept an arbitrary number of path entities as long as they all match the resolvers :attr:`filter`.
        filter (str): A *regular expression* used to match candidate path entities. If not provided, it defaults to
            ``[^/]+`` which matches everything bu forward-slashes */*.
        extension (ExtensionResolver): If provided, it must be an |ExtensionResolver| and it indicates that the resolver
            will match a file rather than a folder.

    """

    def __init__(self, name=''):
        super(GroupResolver, self).__init__(name=name)
        self.recursive = False
        self.filter = '[^/]+'
        self.extension = None

    def _regex(self, name=''):
        return \
            '(?P<{name}>{entry}{filter}{recursive}){extension}'.format(name=self.name,
                                                                       entry='(?:' if self.recursive else '',
                                                                       filter=self.filter,
                                                                       recursive='/?)+' if self.recursive else '',
                                                                       extension=self.extension
                                                                       if self.extension is not None else '')

    def _pattern(self):
        return \
            '{{{name}{recursive}{regex}}}{extension}'.format(name=self.name,
                                                             recursive='/' if self.recursive else '',
                                                             regex=':{}'.format(self.filter)
                                                             if self.filter != '[^/]+' else '',
                                                             extension=self.extension.pattern
                                                             if self.extension is not None else '')


class ComponentResolver(PathComponentResolver):
    """A *resolver* for components.

    Args:
        name (str): The resolver's name.

    Attributes:
        extension (ExtensionResolver): If provided, it must be an |ExtensionResolver| and it indicates that the resolver
            will match a file rather than a folder.

    """

    def __init__(self, name=''):
        super(ComponentResolver, self).__init__(name=name)
        self.extension = None

    def _regex(self):
        return '{name}{extension}'.format(name=self.name,
                                          extension=self.extension if self.extension is not None else '')

    def _pattern(self):
        return '{name}{extension}'.format(name=self.name,
                                          extension=self.extension.pattern if self.extension is not None else '')
