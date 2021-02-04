from plums.commons.path import Path


def make_dict_structure_from_tree(path):
    """Construct a nested dictionary structure from a filesystem tree.

    Args:
        path (Pathlike): The filesystem tree root.

    Returns:
        dict: A nested dict structure where each element is a key to its |Path| for files and to another dict for
        directories.

    """
    path = Path(path)

    tree = path.rglob('*')

    dict_tree = {}

    for element in tree:
        if not element.is_symlink() and element.is_dir():
            value = {}
        elif element.is_symlink() or element.is_file():
            value = element
        else:
            raise ValueError('Invalid element in filesystem tree: '
                             '{} is neither a file/symlink nor a directory.'.format(element))

        dictionary = dict_tree
        for part in element.anchor_to_path(path)[:-1]:
            if part == '.':
                continue
            dictionary = dictionary[part]

        dictionary[str(element[-1])] = value

    return dict_tree
