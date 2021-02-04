import re
from copy import copy

from plums.commons.path import Path
from .parser import Parser, ComponentResolver, GroupResolver


class PathResolver(object):
    """Search recursively for |Path| which match a dataset pattern.

    Args:
        pattern (PathLike): A path-like dataset pattern which will be used to find relevant elements.
        reserved (Sequence[str]): If provided, a sequence of words which can not be used as group's name.

    """

    def __init__(self, pattern, reserved=()):
        self._parser_ = Parser(reserved=reserved)

        # Compute resolvers list
        self._resolvers = self._parser_.parse(pattern)
        self._degenerate = False

        # Compute resolvers regex and full regex
        self._regex_path = Path.from_parts([resolver.regex for resolver in self._resolvers])
        self._regex = re.compile(str(self._regex_path))

        # Compute prefix
        for i, resolver in enumerate(self._resolvers):
            if not isinstance(resolver, ComponentResolver):
                self._prefix = self._regex_path[:i]
                break
        else:  # Degenerate one-file path case
            self._degenerate = True
            self._prefix = self._regex_path

    @property
    def degenerate(self):
        """bool: ``True`` if the provided pattern is degenerate, *i.e.* it designate a single file."""
        return self._degenerate

    @property
    def group_names(self):
        """tuple: A tuple containing the names of the named groups found in the path pattern."""
        return tuple(resolver.name for resolver in self._resolvers if isinstance(resolver, GroupResolver))

    def find(self, path=None):
        """Find all |Path| which satisfies the dataset pattern by walking on disk.

        Args:
            path (PathLike): For relative pattern, an entry-point must be provided to avoid walking from root.

        Yields:
            Path: A valid |Path| with named group values stored in a ``match`` dictionary.

        Raises:
            ValueError: If the dataset pattern is relative and no entry point path was provided.
            OSError: If the resolver is degenerate (the pattern has no groups) and the designated file does not exists.

        """
        if self._regex_path[0] != '/':
            if path is None:
                raise ValueError('The dataset pattern to search for is relative but no search path was provided.')
            entry_point = path
            if self._prefix != '.':  # Avoid dangling '.'
                path = path / self._prefix
        else:
            if path is not None:
                raise ValueError('The dataset pattern to search for is absolute but a search path was provided.')
            path = entry_point = self._prefix
            # Update internal full regex from actual entry-point
            self._regex = re.compile(str(self._regex_path.anchor_to_path(entry_point)))

        # Degenerate branch
        if self._degenerate:
            if (path[:-1] / str(path[-1]).replace(r'\.', '.')).exists():
                yield path[:-1] / str(path[-1]).replace(r'\.', '.')
            else:
                raise OSError('Degenerate path pattern points to a non-existing file.')

        # Regular branch
        # Start search
        # +-> Initialise partial pointers
        partials = {}
        partials.setdefault(str(path[:-1]), self._regex_path[:len(self._prefix) + 1])
        # +-> Start walking
        for root, directories, files in path.walk(followlinks=True):
            # +-> Build partial regex for root if is does not exist already
            partials.setdefault(str(root), partials[str(root[:-1])])
            # +-> Fetch partial regex
            partial = partials[str(root)]
            relative_partial = partial.anchor_to_path(entry_point) if partial[0] == '/' else partial
            regex = re.compile(str(relative_partial))
            # +-> Are we still at a directory level ?
            if not partial[-1].filename:
                # +-> Prune non matching directory from walk to avoid visiting known false candidates
                for i, directory in enumerate(copy(directories)):
                    current = root / directory
                    relative_current = current.anchor_to_path(entry_point)
                    # If the current directory does not match partial regex
                    if regex.fullmatch(str(relative_current)) is None:
                        # If we stopped on a recursion, we must try the level under to check
                        # we did not just reached the end of recursion
                        if getattr(self._resolvers[len(partial) - 1], 'recursive', False):
                            # Add a level
                            partial_candidate = partial / self._regex_path[len(partial)]
                            # If we didn't just pop it out
                            if re.fullmatch(str(partial_candidate), str(relative_current)) is None:
                                directories.remove(directory)
                                continue
                            else:  # Move partial regex forward
                                new_partial = partial_candidate / self._regex_path[len(partial) + 1]
                                partials.setdefault(str(current), new_partial)
                        else:  # If we stopped on a non recursion, just pop it out
                            directories.remove(directory)
                            continue
                    else:  # If the current directory match the partial regex
                        # If we stopped on a non recursion, we must advance the partial regex
                        if not getattr(self._resolvers[len(partial) - 1], 'recursive', False):
                            partials.setdefault(str(current), partial / self._regex_path[len(partial)])

            if partial[-1].filename \
                    or (getattr(self._resolvers[len(partial) - 1], 'recursive', False)
                        and self._regex_path[len(partial)].filename):
                # We reached the file level ! \o/
                for file in files:
                    current = root / file
                    relative_current = current.anchor_to_path(entry_point)
                    match = self._regex.fullmatch(str(relative_current))
                    # If the current file matches full regex
                    if match is not None:
                        # +-> Add matched groups to path and yield
                        current.match = match.groupdict()
                        yield current
