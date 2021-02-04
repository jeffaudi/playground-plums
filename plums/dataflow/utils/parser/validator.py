from .resolver import GroupResolver
from .exceptions import ReservedGroupError, DuplicateGroupError, RecursiveFileError


class Validator:
    """A class which validates a *path pattern* *semantically*.

    It is used as a callable which take the parsed string and the resulting |PathComponentResolver| list as inputs to
    run  correctness checks. It is expected to raise :exc:`PatternError` in case of errors.

    Args:
        reserved (Sequence[str]): If provided, a sequence of words which can not be used as group's name.

    """

    def __init__(self, reserved=()):
        self._reserved = set(reserved)

    @staticmethod
    def _raise(string, exception_class, resolver, token=None):
        position = string.rfind(resolver.pattern)

        if position == -1:
            position = len(string) - 1

        raise exception_class(string, position, resolver.pattern if token is None else token)

    def __call__(self, string, resolvers):
        """Validate a pattern semantically."""
        names = set()

        if isinstance(resolvers[-1], GroupResolver) and resolvers[-1].recursive:
            self._raise(string, RecursiveFileError, resolvers[-1])

        for resolver in resolvers:
            if isinstance(resolver, GroupResolver):
                if resolver.name in self._reserved:
                    self._raise(string, ReservedGroupError, resolver, resolver.name)
                if resolver.name in names:
                    self._raise(string, DuplicateGroupError, resolver, resolver.name)
                names.add(resolver.name)
