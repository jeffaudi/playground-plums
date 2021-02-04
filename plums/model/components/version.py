import inspect
import re
import abc
from functools import total_ordering

from packaging.version import Version as PypaVersion


__version_register__ = {}
__version_hook_register__ = {}


def version(format, value):
    """Construct a valid |ProducerVersion| instance with the correct format.

    Args:
        format (str): A snake case registered format identifier.
        value (str): The |ProducerVersion| string representation.

    Returns:
        |ProducerVersion|: A |ProducerVersion| instance with the correct format.

    Raises:
        ValueError: If ``format`` is not a registered version format.

    """
    try:
        format_cls = __version_register__[format]
    except KeyError:
        raise ValueError('Invalid version format provided: {} is unknown.'.format(format))

    format_hook = __version_hook_register__.get(format, lambda instance: instance)

    return format_hook(format_cls(value))


def register(cls, hook=None):
    """Register a |ProducerVersion| class to the |version| function with an optional initialisation hook.

    Args:
        cls (|ProducerVersion|): The |ProducerVersion| class to register.
        hook (Callable): Optional. Default to the identity. An optional initialisation hook.

    """
    __version_register__[cls.format] = cls
    if hook is not None:
        __version_hook_register__[cls.format] = hook
    else:
        if cls.format in __version_hook_register__:
            del __version_hook_register__[cls.format]


_camel_to_snake_re1 = re.compile('(.)([A-Z][a-z]+)')
_camel_to_snake_re2 = re.compile('([a-z0-9])([A-Z])')


def _camel_to_snake(camel_cased_name):
    s1 = _camel_to_snake_re1.sub(r'\1_\2', camel_cased_name)
    return _camel_to_snake_re2.sub(r'\1_\2', s1).lower()


class MetaVersion(abc.ABCMeta):
    """Base meta-class for all |Version|.

    It inherits :class:`abc.ABCMeta` and adds a *class property* format which give the name of the |Version| format
    from the class name.

    """

    def __new__(mcs, name, bases, namespace):  # noqa: N804
        """Construct a Version class with a *class-property* format."""
        namespace.update({'format': MetaVersion.format})
        return super(MetaVersion, mcs).__new__(mcs, name, bases, namespace)

    @property
    def format(cls):  # noqa: N805
        """str: The |Version| corresponding *format*, it is computed from the class name as a snake case."""
        if not inspect.isclass(cls):
            cls = type(cls)
        return _camel_to_snake(cls.__name__)


@total_ordering
class Version(object, metaclass=MetaVersion):
    """Abstract base class for all |Producer| version.

    Subclasses are expected to override the :meth:`__init__`, :meth:`__str__`, :meth:`__eq__` and :meth:`__lt__` magic
    method to make the version format 'registerable' to the |version| factory function.

    Args:
        version (str): A valid version *representation string* with regard to the |Version| format.

    Attributes:
        format (str): The |Version| corresponding *format*, it is computed from the class name as a snake case.

    """

    @property
    def version(self):
        """str: The |Version| *string representation*, it is computed with the :meth:`__str__` method."""
        return self.__str__()

    def __repr__(self):
        """Return a representation of the |Version|."""
        return '{}({})'.format(self.__class__.__name__, str(self))

    @abc.abstractmethod
    def __str__(self):
        """Return the |Version| human-readable representation.

        For example, for a standard *PyPA* package version this would return the *version string*, *e.g.* ``2.0.1.dev0``

        Returns:
            str: The |Version| string representation.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other):
        """Return whether two |Version| are equal.

        Args:
            other (|Version|): Another |Version| to compare to.

        Returns:
            bool: ``True`` if the two version may be considered equal.

        Raises:
            TypeError: If it not possible to compare to ``other``.

        """
        return NotImplemented

    def __ne__(self, other):
        """Return whether two |Version| are not equal.

        Args:
            other (|Version|): Another |Version| to compare to.

        Returns:
            bool: ``True`` if the two version may not be considered equal.

        Raises:
            TypeError: If it not possible to compare to ``other``.

        """
        return not self == other

    @abc.abstractmethod
    def __lt__(self, other):
        """Return whether other |Version| is less than self.

        Args:
            other (|Version|): Another |Version| to compare to.

        Returns:
            bool: ``True`` if ``other`` may be considered less than self.

        Raises:
            TypeError: If it not possible to compare to ``other``.

        """
        return NotImplemented


class PyPA(Version):
    """A |Producer| version following the standard **PyPA** versioning scheme.

    It follows the rules defined in `PEP 440`_ which are grossly similar to `Semantic Versioning`_ with a few notable
    differences and generalisation.

    Args:
        version (str): A valid `PEP 440` version *representation string*.

    Attributes:
        format (str): The |Version| corresponding *format*, it is computed from the class name as a snake case.

    .. _PEP 440:
        https://www.python.org/dev/peps/pep-0440/

    .. _Semantic Versioning:
        https://semver.org/

    """

    def __init__(self, version):
        self._version = PypaVersion(version)

    def __str__(self):
        """Return the |Version| human-readable representation.

        For example, for a standard *PyPA* package version this would return the *version string*, *e.g.* ``2.0.1.dev0``

        Returns:
            str: The |Version| string representation.

        """
        return str(self._version)

    def __eq__(self, other):
        """Return whether two |Version| are equal.

        Args:
            other (|Version|): Another |Version| to compare to.

        Returns:
            bool: ``True`` if the two version may be considered equal.

        Raises:
            TypeError: If it not possible to compare to ``other``.

        """
        return self._version == other

    def __lt__(self, other):
        """Return whether other |Version| is less than self.

        Args:
            other (|Version|): Another |Version| to compare to.

        Returns:
            bool: ``True`` if ``other`` may be considered less than self.

        Raises:
            TypeError: If it not possible to compare to ``other``.

        """
        return self._version < other


register(PyPA)
