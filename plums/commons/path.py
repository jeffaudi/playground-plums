import os
import os.path
import fnmatch
import errno
import stat
from os import scandir, walk


try:
    from os import PathLike
except ImportError:
    PathLike = object


def _fnmatch(root, name, pat):
    if pat == '**':
        p = root + name
        return p.is_dir() and not p.is_symlink()
    else:
        return fnmatch.fnmatch(str(name), str(pat))


class _Stat(object):
    def __init__(self, path):
        """Implement an basic abstraction over :func:`os.stat` related operations and store the originating path hash.

        Args:
            path (|Path|): A |Path| for which to store stat information.

        """
        self._hash = hash(path)
        self._exists = True
        try:
            lstat_result = os.lstat(str(path))
        except OSError:
            self.stat_result = None
            self._exists = False
            self._islink = False
        else:
            self._islink = stat.S_ISLNK(lstat_result.st_mode)
            try:
                self.stat_result = os.stat(str(path))
            except OSError:
                self.stat_result = None
                self._exists = False

    def __hash__(self):
        """Return the originating |Path| python hash."""
        return self._hash

    def exists(self):
        """Return ``True`` if the originating |Path| corresponds to a real location on the filesystem."""
        return self._exists

    def isdir(self):
        """Return ``True`` if the originating |Path| corresponds to a real directory on the filesystem."""
        return self._exists and stat.S_ISDIR(self.stat_result.st_mode)

    def isfile(self):
        """Return ``True`` if the originating |Path| corresponds to a real file on the filesystem."""
        return self._exists and stat.S_ISREG(self.stat_result.st_mode)

    def islink(self):
        """Return whether the originating |Path| corresponds to a symbolic link on the filesystem (broken or not)."""
        return self._islink


class Path(PathLike):
    """A container class allowing list-like access, addition, and contain logic to path parts.

    Args:
        path (PathLike): The path to encode

    Note:
        * If given a |Path|, the constructor construct a copy of the path.
        * If given a :class:`~pathlib.PurePath`, a quick copy and convert is performed.
        * Otherwise, the path is constructed from either its :func:`os.fspath` representation or its :obj:`str`
          representation for Python 3.5 and before.

    Examples:
        >>> # Create a Path object from a string
        >>> path = Path('/an/absolute/path/to/somewhere.txt')
        >>> # Get its repr
        >>> path
        Path('/an/absolute/path/to/somewhere.txt')
        >>> # And its string representation
        >>> print(path)
        /an/absolute/path/to/somewhere.txt
        >>> # Its filename
        >>> path.filename
        'somewhere'
        >>> # And extension without the dot
        >>> path.ext
        'txt'
        >>> # It supports list arithmetic and indexing
        >>> path[:3]
        Path('/an/absolute')
        >>> path[:3] + 'path_somewhere/else.json'
        Path('/an/absolute/path_somewhere/else.json')
        >>> # And pathlib-like division
        >>> path[:3] / 'path_somewhere/else.json'
        Path('/an/absolute/path_somewhere/else.json')

    """

    def __init__(self, path):
        super(Path, self).__init__()
        if hasattr(path, 'parts'):
            if path.parts:
                self._parts = path.parts
            else:
                # To be coherent with PurePath implementation choices
                self._parts = ['.']
        else:
            path = path.__fspath__() if hasattr(path, "__fspath__") else path

            # Not a fan of explicit type testing however this is the actual test of os.fspath on with all path handling
            # in Python 3.6+ are based.
            if not isinstance(path, (str, bytes)):
                raise TypeError("expected str, bytes or os.PathLike object, not " + type(path).__name__)

            if path:
                self._parts = self._filter_empty(self._make_parts(path))
            else:
                # To be coherent with PurePath implementation choices
                self._parts = ['.']

        self.__stat = _Stat(self)

    @property
    def parts(self):
        """tuple: The list of the |Path| components."""
        return tuple(self._parts)

    @property
    def filename(self):
        """str: The |Path| filename-if any-without the extension."""
        if self.is_dir():
            return ''

        if self.is_file():
            filename, ext = os.path.splitext(os.path.basename(str(self[-1])))
            return filename

        if os.path.splitext(str(self[-1]))[1] != '':
            filename, ext = os.path.splitext(os.path.basename(str(self[-1])))
            return filename

        else:
            return ''

    @property
    def ext(self):
        """str: The |Path| file ending extension (if any) without the dot."""
        if self.is_dir():
            return ''

        if self.is_file():
            filename, ext = os.path.splitext(os.path.basename(str(self[-1])))
            return ext

        if os.path.splitext(str(self[-1]))[1] != '':
            filename, ext = os.path.splitext(os.path.basename(str(self[-1])))
            return ext[1:]

        else:
            return ''

    @property
    def _stat(self):
        """:class:`~plums.commons.path._Stat`: ``self`` corresponding object."""
        if hash(self) != hash(self.__stat):
            self.__stat = _Stat(self)
        return self.__stat

    @classmethod
    def from_parts(cls, parts):
        """Construct a |Path| from a sequence of components.

        Args:
            parts (Sequence): An ordered |Path| component sequence

        Examples:
            >>> # Create a Path object from a string
            >>> path = Path.from_parts(['/', 'an', 'absolute', 'path', 'to', 'somewhere.txt'])
            >>> # Get its repr
            >>> path
            Path('/an/absolute/path/to/somewhere.txt')
            >>> # And its string representation
            >>> print(path)
            /an/absolute/path/to/somewhere.txt
            >>> # Its filename
            >>> path.filename
            'somewhere'
            >>> # And extension without the dot
            >>> path.ext
            'txt'
            >>> # It supports list arithmetic and indexing
            >>> path[:3]
            Path('/an/absolute')
            >>> path[:3] + 'path_somewhere/else.json'
            Path('/an/absolute/path_somewhere/else.json')
            >>> # And pathlib-like division
            >>> path[:3] / 'path_somewhere/else.json'
            Path('/an/absolute/path_somewhere/else.json')

        """
        class PathComponent(object):
            def __init__(self, parts_):
                self.parts = cls._filter_empty(parts_)

        return cls(PathComponent(parts))

    @staticmethod
    def _make_parts(path):
        parts = []
        temp = path
        while os.path.dirname(temp) != '' and os.path.dirname(temp) != '/':
            parts.append(os.path.basename(temp))
            temp = os.path.dirname(temp)
        if temp and temp == '/':
            parts.append(temp[0])
        elif temp and temp[0] == '/':
            parts.append(temp[1:])
            parts.append(temp[0])
        else:
            parts.append(temp)
        parts.reverse()
        return parts

    @staticmethod
    def _filter_empty(value):
        return tuple(filter(bool, value))

    def __fspath__(self):
        """Implement the ``PathLike`` protocol."""
        return self.__str__()

    def __hash__(self):
        """Return the path python hash."""
        return hash(str(self))

    def __eq__(self, other):
        """Return ``True`` if 2 |Path| are equal."""
        return str(self) == str(other)

    def __ne__(self, other):
        """Return ``True`` if 2 |Path| are not equal."""
        return not self == other

    def __str__(self):
        """Get a string representation of the |Path|."""
        return os.path.join(*self.parts)

    def __repr__(self):
        """Get a pythonic representation of th |Path|."""
        return "{}('{}')".format(self.__class__.__name__, self)

    def __getitem__(self, item):
        """Get the component at ```key``` position."""
        if isinstance(item, slice):
            return Path.from_parts(self.parts[item.start:item.stop:item.step])
        else:
            return Path.from_parts([self.parts[item]])

    def __len__(self):
        """Return the number of components in self."""
        return len(self.parts)

    def __add__(self, other):
        """Left-concatenate two path together.

        Args:
            other (PathLike): A path to right-concatenate self with

        Returns:
            |Path|: The concatenation result

        Raises:
            ValueError: If self represents a file
            TypeError: If ``other`` can not be converted to a valid |Path|

        """
        if hasattr(other, 'parts'):
            if not self.is_file() and self.ext == '':
                return Path.from_parts(self.parts + tuple(other.parts))
            else:
                raise ValueError('It is impossible to left join a file-path: {} -\\- {}.'.format(self, other))
        else:
            try:
                return self.__add__(Path(other))
            except TypeError:
                raise TypeError("unsupported operand type(s) for +: '{0}' and '{1}'".format(self.__class__.__name__,
                                                                                            other.__class__.__name__))

    def __radd__(self, other):
        """Right-concatenate two path together.

        Args:
            other (PathLike): A path to right-concatenate self with

        Returns:
            |Path|: The concatenation result

        Raises:
            ValueError: If other represents a file
            TypeError: If ``other`` can not be converted to a valid |Path|

        """
        if hasattr(other, 'parts') and hasattr(other, 'ext') and hasattr(other, 'is_file'):
            if not other.is_file() and other.ext == '':
                return Path.from_parts(tuple(other.parts) + self.parts)
            else:
                raise ValueError('It is impossible to left join a file-path: {} -\\- {}.'.format(other, self))
        else:
            try:
                return self.__radd__(Path(other))
            except TypeError:
                raise TypeError("unsupported operand type(s) for +: '{0}' and '{1}'".format(other.__class__.__name__,
                                                                                            self.__class__.__name__))

    __truediv__ = __add__
    __rtruediv__ = __radd__

    __div__ = __add__
    __rdiv__ = __radd__

    @staticmethod
    def _find_secondary_in_primary(secondary_list, primary_list):
        len_primary, len_secondary = len(primary_list), len(secondary_list)
        i, last = 0, len_primary - len_secondary + 1
        while True:
            try:
                found = primary_list.index(secondary_list[0], i, last)  # find first elem in secondary_list
            except ValueError:
                return None
            if primary_list[found:found + len_secondary] == secondary_list:
                return found, found + len_secondary
            else:
                i = found + 1

    def __contains__(self, item):
        """Return ``True`` if ``item`` is a path subset of self."""
        return self._find_secondary_in_primary(Path(item).parts, self.parts) is not None

    def exists(self):
        """Return ``True`` if the |Path| corresponds to a real location on the filesystem."""
        self.__stat = _Stat(self)
        return self._stat.exists()

    def is_dir(self):
        """Return ``True`` if the |Path| corresponds to a real directory on the filesystem."""
        return self._stat.isdir()

    def is_file(self):
        """Return ``True`` if the |Path| corresponds to a real file on the filesystem."""
        return self._stat.isfile()

    def is_symlink(self):
        """Return ``True`` if the |Path| corresponds to a symbolic link on the filesystem (broken or not)."""
        return self._stat.islink()

    def stat(self):
        """Return information about this path (similarly to :func:`os.stat`).

        Returns:
            :class:`os.stat_result`, ``None``: The result of an :func:`os.stat` call or ``None`` is the |Path|
            corresponds to a real location on the filesystem.

        """
        return self._stat.stat_result

    def mkdir(self, parents=False, exist_ok=False):
        """Make a directory at the location specified by |Path|.

        Args:
            parents (bool): If ``True``, any missing parents of this path are created as needed.
            exist_ok (bool): If ``True`` (the default), ``OSError`` is not raised if the target directory
                already exists.

        Raises:
            OSError: If ``parents`` is ``False`` and a parent is missing. If ``exist_ok`` is ``False`` and the target
                directory already exists.

        """
        if self.ext:
            path = self[:-1]
        else:
            path = self
        try:
            if parents:
                os.makedirs(str(path))
            else:
                os.mkdir(str(path))
        except OSError as exc:
            if exist_ok and (exc.errno == errno.EEXIST and path.is_dir()):
                pass
            else:
                raise exc

    def listdir(self):
        """List elements found in |Path|.

        Yields:
            :class:`~plums.commons.Path`: Each element found in |Path|.

        """
        for path in os.listdir(str(self)):
            yield Path(path)

    def walk(self, topdown=True, onerror=None, followlinks=False):
        """Recursively list elements found in |Path|.

        Args:
            topdown (bool): If ``True`` or not specified, the triple for a directory is generated before the triples
                for any of its subdirectories (directories are generated top-down). If topdown is False, the triple for
                a directory is generated after the triples for all of its subdirectories (directories are
                generated bottom-up). No matter the value of topdown, the list of subdirectories is retrieved before
                the tuples for the directory and its subdirectories are generated.
            onerror (Callable): By default, errors from the scandir() call are ignored. If specified, it should be a
                function; it will be called with one argument, an OSError instance. It can report the error to continue
                with the walk, or raise the exception to abort the walk. Note that the filename is available as the
                filename attribute of the exception object.
            followlinks (bool): Whether to follow symbolic links whilst recursing through the directories.

        Yields:
            (:class:`~plums.commons.Path` , [:class:`~plums.commons.Path`],
            [:class:`~plums.commons.Path`]):
            A triple containing the current root directory, a list of found directories inside and a list of found
            files inside.

        Warnings:
            Be aware that setting ``followlinks`` to ``True`` can lead to infinite recursion if a link points to a
            parent directory of itself. walk() does not keep track of the directories it visited already.

        Note:
            When topdown is ``True``, the caller can modify the dirnames list in-place (perhaps using del or slice
            assignment), and walk() will only recurse into the subdirectories whose names remain in dirnames.
            This can be used to prune the search, impose a specific order of visiting, or even to inform walk()
            about directories the caller creates or renames before it resumes walk() again. Modifying dirnames when
            topdown is ``False`` has no effect on the behavior of the walk, because in bottom-up mode the directories in
            dirnames are generated before dirpath itself is generated.

        """
        for root, dirnames, filenames in walk(str(self), topdown=topdown, onerror=onerror, followlinks=followlinks):
            root = Path(root)
            yield root, [Path(d) for d in dirnames], [Path(f) for f in filenames]

    def glob(self, pattern):
        """Glob the given pattern in the directory represented by |Path|, yielding all matching files (of any kind).

        Args:
            pattern (PathLike): A globing pattern to match against all elements in |Path|.

        Yields:
            :class:`~plums.commons.Path`: Matching files.

        Note:
            The ``**`` pattern means "this directory and all subdirectories, recursively". In other words, it enables
            recursive globing.

        Warnings:
            Using the ``**`` pattern in large directory trees may consume an inordinate amount of time.

        """
        if pattern == '**':
            for e in self.rglob(pattern):
                yield e
            return

        pattern = Path(pattern)

        if pattern[0] == '**':
            for e in self.rglob(pattern[1:]):
                yield e
            return
        for dir_entry in scandir(str(self)):
            if _fnmatch(self, dir_entry.name, pattern[0]):
                if dir_entry.is_file() or dir_entry.is_symlink():
                    yield self + dir_entry.name
                else:
                    if len(pattern) > 1:
                        for e in (self + dir_entry.name).glob(pattern[1:]):
                            yield e

    def rglob(self, pattern):
        """Equivalent to calling :meth:`Path.glob` with ``**`` added in front of the given pattern.

        Args:
            pattern (PathLike): A globing pattern to recursively match against all elements in |Path|.

        Yields:
            :class:`~plums.commons.Path`: Matching files.

        Note:
            The ``**`` pattern means "this directory and all subdirectories, recursively". In other words, it enables
            recursive globing.

        Warnings:
            Using the ``**`` pattern in large directory trees may consume an inordinate amount of time.

        """
        if pattern == '**':
            yield self

        pattern = Path(pattern)

        while pattern[0] == '**' and len(pattern) > 1:
            pattern = pattern[1:]

        # We have to go deeper !
        for root, dirnames, filenames in self.walk():
            if len(pattern) == 1:
                for element in filenames:
                    if _fnmatch(root, element, pattern[0]):
                        yield root + element
            for element in dirnames:
                if _fnmatch(root, element, pattern[0]):
                    if len(pattern) == 1:
                        # If it matches and pattern is length 1 we yield no matter what
                        yield root + element
                    else:
                        # We have to check the whole pattern and descend in directories
                        if not (root + element).is_symlink():
                            # We have to go deeper to check for the whole glob pattern
                            for e in (root + element).glob(pattern[1:]):
                                yield e

    def common_prefix(self, other):
        """Given a other path, returns the common prefix between the two.

        Examples:
            >>> path = Path('/some/absolute/path/to/somewhere.ext')
            >>> path.common_prefix('/some/absolute/path/to/elsewhere.ext')
            Path('/some/absolute/path/to')
            >>> path.common_prefix('some/relative/path.ext')
            Traceback (most recent call last):
                ...
            ValueError: No common prefix found between /some/absolute/path/to/somewhere.ext and some/relative/path.ext
            >>> path.common_prefix('path/to')
            Traceback (most recent call last):
                ...
            ValueError: No common prefix found between /some/absolute/path/to/somewhere.ext and path/to

        Args:
            other (PathLike): A path to search the common prefix with

        Returns:
            |Path|: The common prefix between the paths

        Raises:
            ValueError: If no common prefix is found

        """
        other = Path(other)
        commonprefix = os.path.dirname(os.path.commonprefix((str(self), str(other))))
        if not commonprefix:
            raise ValueError('No common prefix found between {} and {}'.format(self, other))
        return Path(commonprefix)

    def anchor_to_path(self, anchor):
        """Given an anchor inside the complete path, returns the rightmost part.

        Examples:
            >>> p = Path('/some/absolute/path/to/somewhere/far/away.ext')
            >>> p.anchor_to_path('path')
            Path('to/somewhere/far/away.ext')

        If given a valid path, the entire path section is used as the anchor, e.g:
        .. python:

            >>> p = Path('/some/absolute/path/to/somewhere/far/away.ext')
            >>> p.anchor_to_path('absolute/path/to')
            Path('somewhere/far/away.ext')

        Args:
            anchor (PathLike): An anchor in the path

        Returns:
            |Path|: The rightmost part of the path relative to the anchor

        Raises:
            ValueError: If the anchor is not contained in self

        """
        anchor = Path(anchor)
        possible_position = self._find_secondary_in_primary(anchor.parts, self.parts)
        if possible_position is not None:
            i = possible_position[1]
        else:
            raise ValueError('The anchor provided cannot be found in path: {} not in {}.'.format(anchor, self))
        return self[i:]

    def root_to_anchor(self, anchor):
        """Given an anchor inside the complete path, returns the leftmost part.

        Examples:
            >>> p = Path('/some/absolute/path/to/somewhere/far/away.ext')
            >>> p.root_to_anchor('path')
            Path('/some/absolute')

        If given a valid path, the entire path section is used as the anchor, e.g:
        .. python:

            >>> p = Path('/some/absolute/path/to/somewhere/far/away.ext')
            >>> p.root_to_anchor('absolute/path/to')
            Path('/some')

        Args:
            anchor (str): An anchor in the path

        Returns:
            |Path|: The rightmost part of the path relative to the anchor

        Raises:
            ValueError: If the anchor is not contained in self

        """
        anchor = Path(anchor)
        new_position, past_position = (0, 0), (-1, 0)
        while True:
            new_position = self._find_secondary_in_primary(anchor.parts, self.parts[past_position[1]:])
            if new_position is None:
                break
            past_position = (new_position[0] + past_position[1], new_position[1] + past_position[1])
        if past_position == (-1, 0):
            raise ValueError('The path provided cannot be found in path: {} not in {}.'.format(anchor, self))
        else:
            return self[:past_position[0]]

    def with_file(self, file):
        """Construct a new |Path| with the file swapped with provided file.

        Args:
            file (str): An file to append to the new |Path|.

        Returns:
            |Path|: A new |Path| with a different file.

        Raises:
            ValueError: If the provided file is not a valid filename.

        """
        file = Path(file)
        if not file.filename or not file.ext or len(file) >= 2:
            raise ValueError('Invalid file provided: Expected a single file, got {}.'.format(file))

        if not self.filename:
            return self / file

        return self[:-1] / file

    def with_filename(self, filename):
        """Construct a new |Path| with the filename swapped with provided filename.

        Args:
            filename (str): A filename to append to the new |Path|.

        Returns:
            |Path|: A new |Path| with a different filename.

        Raises:
            TypeError: If self is a directory path.

        """
        if not self.filename:
            raise TypeError('Can not change filename as self is represents a directory.')
        return self.with_file('.'.join((filename, self.ext)))

    def with_ext(self, ext):
        """Construct a new |Path| with the extension swapped with provided extension.

        Args:
            ext (str): An extension (without the dot) to append to the new |Path|.

        Returns:
            |Path|: A new |Path| with a different filename.

        Raises:
            TypeError: If self is a directory path.

        """
        if not self.filename:
            raise TypeError('Can not change extension as self is represents a directory.')
        return self.with_file('.'.join((self.filename, ext)))
