import pytest

from plums.commons.path import Path
from plums.dataflow.utils.path import PathResolver


def test_resolver_init():
    resolver = PathResolver('data/images/{dataset}/{aoi}/{source}/{tile}.jpg')
    assert resolver._regex.pattern \
        == r'data/images/(?P<dataset>[^/]+)/(?P<aoi>[^/]+)/(?P<source>[^/]+)/(?P<tile>[^/]+)\.jpg'
    assert resolver._prefix == Path('data/images/')

    resolver = PathResolver('/home/user/{dataset}/{aoi}/{source}/{tile}.jpg')
    assert resolver._regex.pattern \
        == r'/home/user/(?P<dataset>[^/]+)/(?P<aoi>[^/]+)/(?P<source>[^/]+)/(?P<tile>[^/]+)\.jpg'
    assert resolver._prefix == Path('/home/user')


def test_degenerate(complex_tree):
    root, path_list = complex_tree

    resolver = PathResolver('data/images/dataset_0/labeled/tile_83.jpg')
    with pytest.raises(OSError, match='Degenerate path pattern points to a non-existing file'):
        _ = list(resolver.find(root))

    resolver = PathResolver('data/images/dataset_0/labeled/tile_23.jpg')

    resolved = list(resolver.find(root))

    assert len(resolved) == 1
    assert resolved[0] == root / 'data/images/dataset_0/labeled/tile_23.jpg'


def test_absolute_degenerate(complex_tree):
    root, path_list = complex_tree

    resolver = PathResolver(str(root / 'data/images/dataset_0/labeled/tile_83.jpg'))
    with pytest.raises(OSError, match='Degenerate path pattern points to a non-existing file'):
        _ = list(resolver.find())

    resolver = PathResolver(str(root / 'data/images/dataset_0/labeled/tile_23.jpg'))

    resolved = list(resolver.find())

    assert len(resolved) == 1
    assert resolved[0] == root / 'data/images/dataset_0/labeled/tile_23.jpg'


def test_absolute_group_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver(str(root / 'data/images/{dataset}/{aoi}/{source}/{tile}.jpg'))

    # Test raise on absolute + root find
    with pytest.raises(ValueError, match='The dataset pattern to search for is '
                                         'absolute but a search path was provided'):
        _ = list(resolver.find(root))

    ground_truth = [root / path for path in path_list if 'dataset_1' in path]
    resolved = list(resolver.find())

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)

    # Test capture
    for path in resolved:
        assert hasattr(path, 'match')
        assert path.match['dataset'] == 'dataset_1'
        assert path.match['aoi'] in ('aoi_0', 'aoi_3')
        assert path.match['source'] in ('labeled', 'simulated')
        assert 'tile_' in path.match['tile']


def test_group_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver('data/images/{dataset}/{aoi}/{source}/{tile}.jpg')

    # Test raise on relative - root find
    with pytest.raises(ValueError, match='The dataset pattern to search for is '
                                         'relative but no search path was provided'):
        _ = list(resolver.find())

    ground_truth = [path for path in path_list if 'dataset_1' in path]
    resolved = list(resolver.find(root))

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)

    # Test capture
    for path in resolved:
        assert hasattr(path, 'match')
        assert path.match['dataset'] == 'dataset_1'
        assert path.match['aoi'] in ('aoi_0', 'aoi_3')
        assert path.match['source'] in ('labeled', 'simulated')
        assert 'tile_' in path.match['tile']


def test_composed_group_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver('data/images/{dataset}/aoi_0/{source}/{tile}.jpg')

    ground_truth = [path for path in path_list if 'dataset_1' in path and 'aoi_0' in path]
    resolved = list(resolver.find(root))

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)

    # Test capture
    for path in resolved:
        assert hasattr(path, 'match')
        assert path.match['dataset'] == 'dataset_1'
        assert path.match['source'] in ('labeled', 'simulated')
        assert 'tile_' in path.match['tile']


def test_loose_regex_recursive_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver('data/images/{path/:(?!.*added.*).*}/{tile}.jpg')

    ground_truth = [path for path in path_list if 'added' not in path and path.ext == '.jpg']
    resolved = list(resolver.find(root))

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)


def test_strict_regex_recursive_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver('data/images/{path/:[a-z]+_[0-9]+}/{tile}.jpg')

    ground_truth = [path for path in path_list if 'dataset_3' in path and 'added' not in path]
    resolved = list(resolver.find(root))

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)


def test_composed_strict_regex_recursive_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver('data/images/{path/:[a-z]+_[0-9]+}/added/{tile}.jpg')

    ground_truth = [path for path in path_list if 'dataset_3' in path and 'added' in path]
    resolved = list(resolver.find(root))

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)


def test_loose_recursive_walk(complex_tree):
    root, path_list = complex_tree
    resolver = PathResolver('data/images/{path/}/{tile}.jpg')

    ground_truth = [path for path in path_list if path.ext == '.jpg']
    resolved = list(resolver.find(root))

    # Test unordered equality
    assert len(resolved) == len(ground_truth)
    assert all(path in ground_truth for path in resolved)
