import os

import pytest

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

try:
    from os import fspath
except ImportError:
    fspath = str

from plums.commons.path import Path


@pytest.fixture(params=["pathlib", "Path", "str"])
def make_path(request):
    def _make_path(path):
        if request.param == 'pathlib':
            return pathlib.Path(str(path))
        elif request.param == 'Path':
            return Path(str(path))
        else:
            return str(path)

    return _make_path


class TestPathCreation(object):
    def test_make_part_dir_relative(self, make_path):
        path = make_path('dummy/relative/dir/path')
        path_instance = Path(path)
        assert path_instance.parts == ('dummy', 'relative', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        path = make_path('dummy/relative//dir/path')
        path_instance = Path(path)
        assert path_instance.parts == ('dummy', 'relative', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        path = make_path('dummy////relative//dir/path')
        path_instance = Path(path)
        assert path_instance.parts == ('dummy', 'relative', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        with pytest.raises(TypeError, match='Can not change filename as self is represents a directory'):
            _ = path_instance.with_filename('filename')

        with pytest.raises(TypeError, match='Can not change extension as self is represents a directory'):
            _ = path_instance.with_ext('json')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('some/invalid/file.json')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('file')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('file.')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('/file.json')

        new_path = path_instance.with_file('filename.json')
        assert new_path.parts == ('dummy', 'relative', 'dir', 'path', 'filename.json')
        assert path_instance.parts == ('dummy', 'relative', 'dir', 'path')
        assert new_path.filename == 'filename'
        assert path_instance.filename == ''
        assert new_path.ext == 'json'
        assert path_instance.ext == ''

    def test_make_part_dir_absolute(self, make_path):
        path = make_path('/dummy/absolute/dir/path')
        path_instance = Path(path)
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        path = make_path('/dummy/absolute//dir/path')
        path_instance = Path(path)
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        path = make_path('/dummy///absolute/dir/path')
        path_instance = Path(path)
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        with pytest.raises(TypeError, match='Can not change filename as self is represents a directory'):
            _ = path_instance.with_filename('filename')

        with pytest.raises(TypeError, match='Can not change extension as self is represents a directory'):
            _ = path_instance.with_ext('json')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('some/invalid/file.json')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('file')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('file.')

        with pytest.raises(ValueError, match='Invalid file provided: Expected a single file, got'):
            _ = path_instance.with_file('/file.json')

        new_path = path_instance.with_file('filename.json')
        assert new_path.parts == ('/', 'dummy', 'absolute', 'dir', 'path', 'filename.json')
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'dir', 'path')
        assert new_path.filename == 'filename'
        assert path_instance.filename == ''
        assert new_path.ext == 'json'
        assert path_instance.ext == ''

    def test_make_part_file_relative(self, make_path):  # noqa: R701
        path = make_path('dummy/relative/file/path/file.ext')
        path_instance = Path(path)
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        path = make_path('dummy/relative/file//path/file.ext')
        path_instance = Path(path)
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        path = make_path('dummy///relative/file/path/file.ext')
        path_instance = Path(path)
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        new_path = path_instance.with_filename('filename')
        assert new_path.parts == ('dummy', 'relative', 'file', 'path', 'filename.ext')
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert new_path.filename == 'filename'
        assert path_instance.filename == 'file'
        assert new_path.ext == 'ext'
        assert path_instance.ext == 'ext'

        new_path = path_instance.with_ext('json')
        assert new_path.parts == ('dummy', 'relative', 'file', 'path', 'file.json')
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert new_path.filename == 'file'
        assert path_instance.filename == 'file'
        assert new_path.ext == 'json'
        assert path_instance.ext == 'ext'

        new_path = path_instance.with_file('filename.json')
        assert new_path.parts == ('dummy', 'relative', 'file', 'path', 'filename.json')
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert new_path.filename == 'filename'
        assert path_instance.filename == 'file'
        assert new_path.ext == 'json'
        assert path_instance.ext == 'ext'

    def test_make_part_file_absolute(self, make_path):  # noqa: R701
        path = make_path('/dummy/absolute/file/path/file.ext')
        path_instance = Path(path)
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        path = make_path('/dummy/absolute/file//path/file.ext')
        path_instance = Path(path)
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        path = make_path('/dummy///absolute/file/path/file.ext')
        path_instance = Path(path)
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        new_path = path_instance.with_filename('filename')
        assert new_path.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'filename.ext')
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert new_path.filename == 'filename'
        assert path_instance.filename == 'file'
        assert new_path.ext == 'ext'
        assert path_instance.ext == 'ext'

        new_path = path_instance.with_ext('json')
        assert new_path.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.json')
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert new_path.filename == 'file'
        assert path_instance.filename == 'file'
        assert new_path.ext == 'json'
        assert path_instance.ext == 'ext'

        new_path = path_instance.with_file('filename.json')
        assert new_path.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'filename.json')
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert new_path.filename == 'filename'
        assert path_instance.filename == 'file'
        assert new_path.ext == 'json'
        assert path_instance.ext == 'ext'

    def test_make_part_dir_relative_from_parts(self):
        path_instance = Path.from_parts(['dummy', 'relative', 'dir', 'path'])
        assert path_instance.parts == ('dummy', 'relative', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        path_instance = Path.from_parts(['dummy', '', 'relative', 'dir', 'path'])
        assert path_instance.parts == ('dummy', 'relative', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

    def test_make_part_dir_absolute_from_parts(self):
        path_instance = Path.from_parts(['/', 'dummy', 'absolute', 'dir', 'path'])
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

        path_instance = Path.from_parts(['/', '', 'dummy', 'absolute', 'dir', 'path'])
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'dir', 'path')
        assert path_instance.filename == ''
        assert path_instance.ext == ''

    def test_make_part_file_relative_from_parts(self):
        path_instance = Path.from_parts(['dummy', 'relative', 'file', 'path', 'file.ext'])
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

        path_instance = Path.from_parts(['dummy', '', 'relative', 'file', 'path', 'file.ext'])
        assert path_instance.parts == ('dummy', 'relative', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

    def test_make_part_file_absolute_from_parts(self):
        path_instance = Path.from_parts(['/', 'dummy', 'absolute', 'file', 'path', 'file.ext'])
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'

        path_instance = Path.from_parts(['/', 'dummy', '', 'absolute', 'file', 'path', 'file.ext'])
        assert path_instance.parts == ('/', 'dummy', 'absolute', 'file', 'path', 'file.ext')
        assert path_instance.filename == 'file'
        assert path_instance.ext == 'ext'

    def test_invalid_types(self):
        with pytest.raises(TypeError, match='expected str, bytes or os.PathLike object, not'):
            Path(1)
        with pytest.raises(TypeError, match='expected str, bytes or os.PathLike object, not'):
            Path((1, ))
        with pytest.raises(TypeError, match='expected str, bytes or os.PathLike object, not'):
            Path([1])
        with pytest.raises(TypeError, match='expected str, bytes or os.PathLike object, not'):
            Path(0)
        with pytest.raises(TypeError, match='expected str, bytes or os.PathLike object, not'):
            Path([])

    def test_empty_path(self):
        p = Path('')
        assert p.parts == ('.', )
        assert p.filename == ''
        assert p.ext == ''


class TestPathRepr(object):
    def test_repr_dir_relative(self, make_path):
        path = make_path('dummy/relative/dir/path')
        path_instance = Path(path)
        assert str(path_instance) == str(path)

    def test_repr_dir_absolute(self, make_path):
        path = make_path('/dummy/absolute/dir/path')
        path_instance = Path(path)
        assert str(path_instance) == str(path)

    def test_repr_file_relative(self, make_path):
        path = make_path('dummy/relative/file/path/file.ext')
        path_instance = Path(path)
        assert str(path_instance) == str(path)

    def test_repr_file_absolute(self, make_path):
        path = make_path('/dummy/absolute/file/path/file.ext')
        path_instance = Path(path)
        assert str(path_instance) == str(path)

    def test_slice_dir_relative(self, make_path):
        path = make_path('dummy/relative/dir/path')
        path_slice = make_path('dummy/relative')
        path_instance = Path(path)
        assert path_instance[:2] == Path(path_slice)

    def test_slice_dir_absolute(self, make_path):
        path = make_path('/dummy/absolute/dir/path')
        path_slice = make_path('/dummy/absolute')
        path_instance = Path(path)
        assert path_instance[:3] == Path(path_slice)

    def test_slice_file_relative(self, make_path):
        path = make_path('dummy/relative/file/path/file.ext')
        path_slice = make_path('dummy/relative')
        path_instance = Path(path)
        assert path_instance[:2] == Path(path_slice)

    def test_slice_file_absolute(self, make_path):
        path = make_path('/dummy/absolute/file/path/file.ext')
        path_slice = make_path('/dummy/absolute')
        path_instance = Path(path)
        assert path_instance[:3] == Path(path_slice)

    def test_fspath(self, make_path):
        path = make_path('/dummy/absolute/file/path/file.ext')
        assert str(Path(path)) == fspath(path)

    def test_repr(self, make_path):
        path = make_path('/dummy/absolute/file/path/file.ext')
        assert repr(Path(path)) == 'Path(\'{}\')'.format(path)


class TestPathBinary(object):
    def test_equality(self, make_path):
        path = make_path('dummy/relative/dir/path')
        path_instance = Path(path)
        assert path_instance == Path(path)
        assert not path_instance != Path(path)

    def test_contain(self, make_path):
        path = make_path('a/long/dummy/relative/dir/path')
        path_instance = Path(path)
        assert path in path_instance
        assert path_instance in Path(path)
        assert 'dummy/relative' in path_instance
        assert path_instance not in Path('dummy/relative')
        assert 'dummy/relative/path' not in path_instance
        assert path_instance not in Path('dummy/relative/path')
        assert 'relative/dummy' not in path_instance
        assert path_instance not in Path('relative/dummy')

    def test_contain_absolute(self, make_path):
        path = make_path('/a/long/dummy/absolute/dir/path')
        path_instance = Path(path)
        assert path in path_instance
        assert path_instance in Path(path)
        assert 'dummy/absolute' in path_instance
        assert path_instance not in Path('dummy/absolute')
        assert 'dummy/absolute/path' not in path_instance
        assert path_instance not in Path('dummy/absolute/path')
        assert 'absolute/dummy' not in path_instance
        assert path_instance not in Path('absolute/dummy')

    def test_invalid_types(self, make_path):
        path_left = Path(make_path('dummy/path/left'))
        with pytest.raises(TypeError):
            path_left + 1
        with pytest.raises(TypeError):
            path_left + (1,)
        with pytest.raises(TypeError):
            path_left + [1]
        with pytest.raises(TypeError):
            path_left + 0
        with pytest.raises(TypeError):
            path_left + []
        with pytest.raises(TypeError):
            1 + path_left
        with pytest.raises(TypeError):
            (1,) + path_left
        with pytest.raises(TypeError):
            [1] + path_left
        with pytest.raises(TypeError):
            0 + path_left
        with pytest.raises(TypeError):
            [] + path_left

    def test_addition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert Path(path_left) + Path(path_right) == str(path_left) + '/' + str(path_right)

    def test_raddition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert Path(path_right) + Path(path_left) == str(path_right) + '/' + str(path_left)

    def test_str_addition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert Path(path_left) + path_right == str(path_left) + '/' + str(path_right)

    def test_str_raddition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert path_left + Path(path_right) == str(path_left) + '/' + str(path_right)

    def test_non_commutative_addition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert Path(path_right) + Path(path_left) != Path(path_left) + Path(path_right)

    def test_str_non_commutative_addition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert Path(path_left) + path_right != Path(path_right) + path_left

    def test_str_non_commutative_raddition_dir(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right')
        assert path_left + Path(path_right) != path_right + Path(path_left)

    def test_addition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        assert Path(path_left) + Path(path_right) == str(path_left) + '/' + str(path_right)

    def test_raddition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        with pytest.raises(ValueError, match='It is impossible to left join a file-path: '):
            Path(path_right) + Path(path_left)

    def test_str_addition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        assert Path(path_left) + path_right == str(path_left) + '/' + str(path_right)

    def test_str_raddition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        assert path_left + Path(path_right) == str(path_left) + '/' + str(path_right)

    def test_non_commutative_addition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        with pytest.raises(ValueError, match='It is impossible to left join a file-path: '):
            Path(path_right) + Path(path_left)

    def test_str_non_commutative_addition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        with pytest.raises(ValueError, match='It is impossible to left join a file-path: '):
            Path(path_right) + path_left

    def test_str_non_commutative_raddition_file(self, make_path):
        path_left = make_path('dummy/path/left')
        path_right = make_path('dummy/path/right.ext')
        with pytest.raises(ValueError, match='It is impossible to left join a file-path: '):
            path_right + Path(path_left)

    def test_associativity_absolute(self, make_path):
        path = make_path('dummy')
        absolute_path = make_path('/dummy')
        assert Path(path) + Path(path) + Path(absolute_path) + Path(path) == str(absolute_path) + '/' + str(path)

    def test_associativity(self, make_path):
        path = make_path('dummy')
        assert Path(path) + Path(path) + Path(path) + Path(path) == \
            str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)

    def test_str_associativity(self, make_path):
        path = make_path('dummy')
        assert path + Path(path) + Path(path) + Path(path) ==\
            str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert Path(path) + path + Path(path) + Path(path) == \
            str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert Path(path) + Path(path) + path + Path(path) == \
            str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert Path(path) + Path(path) + Path(path) + path == \
            str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert Path(path) + path + path + path == str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert path + Path(path) + path + path == str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert path + (path + Path(path)) + path == str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)
        assert path + (path + (path + Path(path))) == str(path) + '/' + str(path) + '/' + str(path) + '/' + str(path)


class TestPathPrefix(object):
    def test_common_prefix(self, make_path):
        path = Path(make_path('/some/absolute/path/to/somewhere.ext'))
        assert path.common_prefix('/some/absolute/path/to/elsewhere.ext') == Path('/some/absolute/path/to')
        with pytest.raises(ValueError, match='No common prefix found between'):
            path.common_prefix('path/to')
        with pytest.raises(ValueError, match='No common prefix found between'):
            path.common_prefix('some/relative/path/to/elsewhere.ext')

        path = Path(str('/some/absolute/path/to/somewhere.ext'))
        assert path.common_prefix(make_path('/some/absolute/path/to/elsewhere.ext')) == Path('/some/absolute/path/to')
        with pytest.raises(ValueError, match='No common prefix found between'):
            path.common_prefix(make_path('path/to'))
        with pytest.raises(ValueError, match='No common prefix found between'):
            path.common_prefix(make_path('some/relative/path/to/elsewhere.ext'))

    def test_anchor_to_path(self, make_path):
        path = Path(make_path('/some/absolute/path/to/somewhere.ext'))

        for i, e in enumerate(path[:-1]):
            assert path.anchor_to_path(e) == path[i + 1:]

        with pytest.raises(ValueError):
            path.anchor_to_path('non_existing_anchor')

        path = Path(make_path('/some/absolute/path/to/path/to/somewhere.ext'))

        for i, e in enumerate(path[:-1]):
            assert path.anchor_to_path(path[:i + 1]) == path[i + 1:]

        assert path.anchor_to_path('path/to') == path[5:]

    def test_root_to_anchor(self, make_path):
        path = Path(make_path('/some/absolute/path/to/somewhere.ext'))

        for i, e in enumerate(path[1:]):
            assert path.root_to_anchor(e) == path[:i + 1]

        with pytest.raises(ValueError):
            path.root_to_anchor('non_existing_anchor')

        path = Path(make_path('/some/absolute/path/to/path/to/somewhere.ext'))

        for i, e in enumerate(path[1:]):
            assert path.root_to_anchor(path[i + 1:]) == path[:i + 1]

        assert path.root_to_anchor('path/to') == path[:5]


class TestPathOS(object):
    # BASE
    #  |
    #  |-- dirA/
    #  |    |-- linkC -> "../dirB"
    #  |-- dirB/
    #  |    |-- fileB
    #  |    |-- linkD -> "../dirB"
    #  |-- dir.C/
    #  |    |-- fileC
    #  |    |-- fileD
    #  |    |-- dirD/
    #  |    |    |-- fileD
    #  |-- fileA
    #  |-- linkA -> "fileA"
    #  |-- linkB -> "dirB"
    #
    @pytest.fixture(params=["pathlib", "Path", "str"])
    def tmp_dir_structure(self, tmp_path, request):
        base = str(tmp_path)
        os.mkdir(os.path.join(base, 'dirA'))
        os.mkdir(os.path.join(base, 'dirB'))
        os.mkdir(os.path.join(base, 'dir.C'))
        os.mkdir(os.path.join(base, 'dir.C', 'dirD'))
        with open(os.path.join(base, 'fileA'), 'wb') as f:
            f.write(b"this is file A\n")
        with open(os.path.join(base, 'dirB', 'fileB'), 'wb') as f:
            f.write(b"this is file B\n")
        with open(os.path.join(base, 'dir.C', 'fileC'), 'wb') as f:
            f.write(b"this is file C\n")
        with open(os.path.join(base, 'dir.C', 'dirD', 'fileD'), 'wb') as f:
            f.write(b"this is file D\n")

        def dirlink(src, dest):
            os.symlink(src, dest)

        # Relative symlinks
        os.symlink('fileA', os.path.join(base, 'linkA'))
        os.symlink('non-existing', os.path.join(base, 'brokenLink'))
        dirlink('dirB', os.path.join(base, 'linkB'))
        dirlink(os.path.join('..', 'dirB'), os.path.join(base, 'dirA', 'linkC'))
        # This one goes upwards but doesn't create a loop
        dirlink(os.path.join('..', 'dirB'), os.path.join(base, 'dirB', 'linkD'))

        if request.param == 'pathlib':
            yield pathlib.Path(str(base))
        elif request.param == 'Path':
            yield Path(str(base))
        else:
            yield str(base)

        os.remove(os.path.join(base, 'dirB', 'linkD'))
        os.remove(os.path.join(base, 'dirA', 'linkC'))
        os.remove(os.path.join(base, 'linkB'))
        os.remove(os.path.join(base, 'brokenLink'))
        os.remove(os.path.join(base, 'linkA'))

        os.remove(os.path.join(base, 'dir.C', 'dirD', 'fileD'))
        os.remove(os.path.join(base, 'dir.C', 'fileC'))
        os.remove(os.path.join(base, 'dirB', 'fileB'))
        os.remove(os.path.join(base, 'fileA'))

        os.rmdir(os.path.join(base, 'dir.C', 'dirD'))
        os.rmdir(os.path.join(base, 'dir.C'))
        os.rmdir(os.path.join(base, 'dirB'))
        os.rmdir(os.path.join(base, 'dirA'))

    def test_filename(self, tmp_dir_structure):
        p = Path(tmp_dir_structure) / 'dir.C'
        assert p.filename == ''
        assert p.ext == ''

        with pytest.raises(AttributeError, match='can\'t set attribute'):
            p.filename = 'file'
        with pytest.raises(AttributeError, match='can\'t set attribute'):
            p.ext = 'ext'

        p = p / 'fileC'

        assert p.filename == 'fileC'
        assert p.ext == ''

        with pytest.raises(ValueError, match='It is impossible to left join a file-path:'):
            p = p / 'file'

        p = p[:-2] / 'brokenLink'

        assert p.filename == ''
        assert p.ext == ''

    def test_glob_rglob(self, tmp_dir_structure):
        assert {str(p) for p in Path(tmp_dir_structure).rglob('*')} == \
            {str(p) for p in Path(tmp_dir_structure).glob('**/*')}

        assert {str(p) for p in Path(tmp_dir_structure).rglob('*')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).rglob('*')}

        assert {str(p) for p in Path(tmp_dir_structure).glob('dirB/*')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).glob('dirB/*')}

        assert {str(p) for p in Path(tmp_dir_structure).glob('**')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).glob('**')}

        assert {str(p) for p in Path(tmp_dir_structure).glob('**/**')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).glob('**/**')}

        assert {str(p) for p in Path(tmp_dir_structure).glob('**/**/*')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).glob('**/**/*')}

        assert {str(p) for p in Path(tmp_dir_structure).glob('dirB/**/*')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).glob('dirB/**/*')}

        assert {str(p) for p in Path(tmp_dir_structure).glob('**/dirD/*')} == \
            {str(p) for p in pathlib.Path(str(tmp_dir_structure)).glob('**/dirD/*')}

    def test_listdir(self, tmp_dir_structure):
        assert {str(p) for p in Path(tmp_dir_structure).listdir()} == \
            {str(p) for p in os.listdir(str(tmp_dir_structure))}

    def test_mkdir(self, tmp_dir_structure):
        with pytest.raises(OSError):
            (Path(tmp_dir_structure) / 'dirA').mkdir()

        (Path(tmp_dir_structure) / 'dirA').mkdir(exist_ok=True)

        with pytest.raises(OSError):
            (Path(tmp_dir_structure) / 'dir0' / 'dir1').mkdir()

        (Path(tmp_dir_structure) / 'dir0' / 'dir1').mkdir(parents=True)

        assert (Path(tmp_dir_structure) / 'dir0').is_dir()
        assert (Path(tmp_dir_structure) / 'dir0' / 'dir1').is_dir()

        with pytest.raises(OSError):
            (Path(tmp_dir_structure) / 'dir0' / 'dir1').mkdir(parents=True)

        (Path(tmp_dir_structure) / 'dir0' / 'dir1').mkdir(parents=True, exist_ok=True)

        with pytest.raises(OSError):
            (Path(tmp_dir_structure) / 'dirA' / 'file.ext').mkdir()

        (Path(tmp_dir_structure) / 'dirA' / 'file.ext').mkdir(exist_ok=True)

        with pytest.raises(OSError):
            (Path(tmp_dir_structure) / 'dir2' / 'dir3' / 'file.ext').mkdir()

        (Path(tmp_dir_structure) / 'dir2' / 'dir3' / 'file.ext').mkdir(parents=True)

        assert (Path(tmp_dir_structure) / 'dir2').is_dir()
        assert (Path(tmp_dir_structure) / 'dir2' / 'dir3').is_dir()

        with pytest.raises(OSError):
            (Path(tmp_dir_structure) / 'dir2' / 'dir3' / 'file.ext').mkdir(parents=True)

        (Path(tmp_dir_structure) / 'dir2' / 'dir3' / 'file.ext').mkdir(parents=True, exist_ok=True)

    def test_walk(self, tmp_dir_structure):
        assert {(str(r), tuple(str(d) for d in dirnames), tuple(str(f) for f in filenames))
                for r, dirnames, filenames in Path(tmp_dir_structure).walk()} == \
               {(str(r), tuple(str(d) for d in dirnames), tuple(str(f) for f in filenames))
                for r, dirnames, filenames in os.walk(str(tmp_dir_structure))}

    def test_is_dir(self, tmp_dir_structure):
        assert (Path(tmp_dir_structure) / 'dirA').is_dir() == \
            os.path.isdir(os.path.join(str(tmp_dir_structure), 'dirA'))

    def test_is_file(self, tmp_dir_structure):
        assert (Path(tmp_dir_structure) / 'fileA').is_file() == \
            os.path.isfile(os.path.join(str(tmp_dir_structure), 'fileA'))

    def test_is_symlink(self, tmp_dir_structure):
        assert (Path(tmp_dir_structure) / 'dirA').is_symlink() == \
            os.path.islink(os.path.join(str(tmp_dir_structure), 'dirA'))

    def test_exists(self, tmp_dir_structure):
        assert (Path(tmp_dir_structure) / 'dirA').exists() == \
            os.path.exists(os.path.join(str(tmp_dir_structure), 'dirA'))

    def test_stat(self, tmp_dir_structure):
        for path in Path(tmp_dir_structure).rglob('*'):
            if path.exists():
                assert path.stat() == os.stat(str(path))
