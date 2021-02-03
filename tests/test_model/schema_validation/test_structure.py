import os

import pytest
from tests.test_model.conftest import __metadata__, __metadata_empty__

from playground_plums.model.exception import PlumsModelTreeValidationError, PlumsValidationError
from playground_plums.commons.path import Path
from playground_plums.model.validation import validate
from playground_plums.model.validation.utils.dict_from_tree import make_dict_structure_from_tree


@pytest.fixture()
def tmp_dir_structure(tmp_path):
    base = str(tmp_path)
    os.mkdir(os.path.join(base, 'dirA'))
    os.mkdir(os.path.join(base, 'dirB'))
    os.mkdir(os.path.join(base, 'dirC'))
    os.mkdir(os.path.join(base, 'dirC', 'dirD'))
    with open(os.path.join(base, 'fileA'), 'wb') as f:
        f.write(b"this is file A\n")
    with open(os.path.join(base, 'dirB', 'fileB'), 'wb') as f:
        f.write(b"this is file B\n")
    with open(os.path.join(base, 'dirC', 'fileC'), 'wb') as f:
        f.write(b"this is file C\n")
    with open(os.path.join(base, 'dirC', 'dirD', 'fileD'), 'wb') as f:
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

    yield Path(str(base))

    os.remove(os.path.join(base, 'dirB', 'linkD'))
    os.remove(os.path.join(base, 'dirA', 'linkC'))
    os.remove(os.path.join(base, 'linkB'))
    os.remove(os.path.join(base, 'brokenLink'))
    os.remove(os.path.join(base, 'linkA'))

    os.remove(os.path.join(base, 'dirC', 'dirD', 'fileD'))
    os.remove(os.path.join(base, 'dirC', 'fileC'))
    os.remove(os.path.join(base, 'dirB', 'fileB'))
    os.remove(os.path.join(base, 'fileA'))

    os.rmdir(os.path.join(base, 'dirC', 'dirD'))
    os.rmdir(os.path.join(base, 'dirC'))
    os.rmdir(os.path.join(base, 'dirB'))
    os.rmdir(os.path.join(base, 'dirA'))


def test_make_dict_structure_from_tree(tmp_dir_structure):
    # BASE
    #  |
    #  |-- dirA/
    #  |    |-- linkC -> "../dirB"
    #  |-- dirB/
    #  |    |-- fileB
    #  |    |-- linkD -> "../dirB"
    #  |-- dirC/
    #  |    |-- fileC
    #  |    |-- dirD/
    #  |    |    |-- fileD
    #  |-- fileA
    #  |-- linkA -> "fileA"
    #  |-- linkB -> "dirB"
    #  |-- brokenLink -> "non-existing"
    assert make_dict_structure_from_tree(tmp_dir_structure) == \
        {
            'dirA': {
                'linkC': tmp_dir_structure / 'dirA' / 'linkC'
            },
            'dirB': {
                'fileB': tmp_dir_structure / 'dirB' / 'fileB',
                'linkD': tmp_dir_structure / 'dirB' / 'linkD',
            },
            'dirC': {
                'fileC': tmp_dir_structure / 'dirC' / 'fileC',
                'dirD': {
                    'fileD': tmp_dir_structure / 'dirC' / 'dirD' / 'fileD',
                }
            },
            'fileA': tmp_dir_structure / 'fileA',
            'linkA': tmp_dir_structure / 'linkA',
            'linkB': tmp_dir_structure / 'linkB',
            'brokenLink': tmp_dir_structure / 'brokenLink',
    }


class TestStructure:
    def test_valid_empty(self, valid_tree_empty):
        assert validate(valid_tree_empty) == __metadata_empty__
        assert validate(valid_tree_empty, strict=True) == __metadata_empty__

    def test_valid(self, valid_tree):
        assert validate(valid_tree) == __metadata__
        assert validate(valid_tree, strict=True) == __metadata__

    def test_valid_extra(self, valid_tree_extra):
        assert validate(valid_tree_extra) == __metadata__
        assert validate(valid_tree_extra, strict=True) == __metadata__

    def test_invalid(self, invalid_tree):
        with pytest.raises(PlumsValidationError) as e:
            validate(invalid_tree)
        print(e.value)

        with pytest.raises(PlumsModelTreeValidationError) as e:
            validate(invalid_tree, strict=True)
        print(e.value)

    def test_invalid_scrict(self, invalid_tree_strict):
        validate(invalid_tree_strict)

        with pytest.raises(PlumsModelTreeValidationError) as e:
            validate(invalid_tree_strict, strict=True)
        print(e.value)
