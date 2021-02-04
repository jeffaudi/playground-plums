# coding: utf-8

# flake8: noqa

import pytest
from tests.test_commons.base import mixin_suite

from playground_plums.commons.data.taxonomy import Label, Tree, Taxonomy


@pytest.fixture()
def tree_a():
    a = Label("a")
    a_a = Label("a_a", parent=a)

    a_a_a = Label("a_a_a", parent=a_a)

    a_a_b = Label("a_a_b", parent=a_a)
    a_a_b_a = Label("a_a_b_a", parent=a_a_b)
    a_a_b_b = Label("a_a_b_b", parent=a_a_b)

    a_a_c = Label("a_a_c", parent=a_a)
    a_a_c_a = Label("a_a_c_a")
    a_a_c_b_a = Label("a_a_c_b_a")
    a_a_c_b = Label("a_a_c_b", children=(a_a_c_b_a, ))
    a_a_c_a_a = Label("a_a_c_a_a")
    a_a_c_a_b = Label("a_a_c_a_b")
    a_a_c_a_b_a = Label("a_a_c_a_b_a", parent=a_a_c_a_b)

    a_a_c.add(a_a_c_a, a_a_c_b)
    a_a_c_a_a.attach(a_a_c_a)
    a_a_c_a_b.attach(a_a_c_a)

    a_b = Label("a_b", parent=a)
    a_b_a = Label("a_b_a", parent=a_b)
    a_b_a_a = Label("a_b_a_a", parent=a_b_a)
    a_b_a_b = Label("a_b_a_b", parent=a_b_a)

    return a


tree_a_repr = \
    u"""a
├── a_a
│   ├── a_a_a
│   ├── a_a_b
│   │   ├── a_a_b_a
│   │   ╰── a_a_b_b
│   ╰── a_a_c
│       ├── a_a_c_a
│       │   ├── a_a_c_a_a
│       │   ╰── a_a_c_a_b
│       │       ╰── a_a_c_a_b_a
│       ╰── a_a_c_b
│           ╰── a_a_c_b_a
╰── a_b
    ╰── a_b_a
        ├── a_b_a_a
        ╰── a_b_a_b"""

tree_a_repr_3 = \
    u"""a
├── a_a
│   ├── a_a_a
│   ├── a_a_b
│   │   ├── a_a_b_a
│   │   ╰── a_a_b_b
│   ╰── a_a_c
│       ├── a_a_c_a
│       ╰── a_a_c_b
╰── a_b
    ╰── a_b_a
        ├── a_b_a_a
        ╰── a_b_a_b"""

taxo_repr = \
    u"""
├── a
│   ├── a_a
│   │   ├── a_a_a
│   │   ├── a_a_b
│   │   │   ├── a_a_b_a
│   │   │   ╰── a_a_b_b
│   │   ╰── a_a_c
│   │       ├── a_a_c_a
│   │       │   ├── a_a_c_a_a
│   │       │   ╰── a_a_c_a_b
│   │       │       ╰── a_a_c_a_b_a
│   │       ╰── a_a_c_b
│   │           ╰── a_a_c_b_a
│   ╰── a_b
│       ╰── a_b_a
│           ├── a_b_a_a
│           ╰── a_b_a_b
╰── b
    ├── b_a
    ╰── b_b"""


@pytest.fixture()
def tree_b():
    b = Label('b')
    b_a = Label('b_a', parent=b)
    b_b = Label('b_b', parent=b)

    return b


class TestLabelCreation:
    @staticmethod
    def _test_label_link(parent, child):
        # Are they correctly attached ?
        assert child.parent == parent
        assert child in parent.children

        assert parent in child.ancestors
        assert parent.descendants[child.name] == child

        assert child.depth == parent.depth + 1

        # Not fake attach created ?
        assert parent not in child.children
        assert parent.parent != child
        assert child not in parent.ancestors
        assert parent.name not in child.descendants

    @staticmethod
    def _test_label_no_link(label_a, label_b):
        # Are they correctly attached ?
        assert label_a not in label_b.children
        assert label_a.parent != label_b
        assert label_b not in label_a.ancestors
        assert label_a.name not in label_b.descendants

        # Not fake attach created ?
        assert label_b not in label_a.children
        assert label_b.parent != label_a
        assert label_a not in label_b.ancestors
        assert label_b.name not in label_a.descendants

    def test_creation(self):
        label_a = Label('label')
        label_b = Label('label')
        label_c = Label('label', some_property='some_value')
        mixin_suite(label_b)  # Base validity tests
        mixin_suite(label_c)  # Base validity tests

        # Some individual base testing
        assert label_a.name == 'label'
        assert label_a.parent is None
        assert not label_a.children
        assert not label_a.ancestors
        assert label_a.depth == 0
        assert not label_a.descendants
        assert hash(label_a) == hash('label')

        # Some individual base testing
        assert label_b.name == 'label'
        assert label_b.parent is None
        assert not label_b.children
        assert not label_b.ancestors
        assert label_b.depth == 0
        assert not label_b.descendants
        assert hash(label_b) == hash('label')

        # Some individual base testing
        assert label_c.name == 'label'
        assert label_c.parent is None
        assert not label_c.children
        assert not label_c.ancestors
        assert label_c.depth == 0
        assert not label_c.descendants
        assert hash(label_c) == hash('label')
        assert label_c.some_property == 'some_value'

        assert label_a.id != label_b.id != label_c.id
        assert label_a == label_b == label_c
        assert not label_a != label_b != label_c

    def test_equality(self):
        label_a = Label('label_a')
        label_b = Label('label_b', parent=label_a)
        label_c = Label('label_c', children=(label_a, ), some_property='some_value')

        label_d = Label('label_d')
        label_e = Label('label_e', parent=label_d)
        label = Label('label_a', parent=label_d, some_property='some_value')

        assert label_a == label_a
        assert label_a != label_b != label_c != label_d != label_e
        assert label_a == label

        assert label_a == 'label_a'
        assert 'label_a' == label_a
        assert label_a != 'label_b'
        assert 'label_a' != label_b
        assert 'label_a' == label
        assert label == 'label_a'

    def test_dict_keys(self):
        label_a = Label('label_a')
        label_b = Label('label_b', parent=label_a)

        dictionary_labels = {label_a: 0, label_b: 1}
        dictionary_names = {'label_a': 2, 'label_b': 3}

        assert label_a in dictionary_labels
        assert label_a in dictionary_names
        assert label_b in dictionary_labels
        assert label_b in dictionary_names

        assert 'label_a' in dictionary_labels
        assert 'label_a' in dictionary_names
        assert 'label_b' in dictionary_labels
        assert 'label_b' in dictionary_names

        assert dictionary_labels[label_a] == 0
        assert dictionary_labels[label_b] == 1
        assert dictionary_names[label_a] == 2
        assert dictionary_names[label_b] == 3

        assert dictionary_labels['label_a'] == 0
        assert dictionary_labels['label_b'] == 1
        assert dictionary_names['label_a'] == 2
        assert dictionary_names['label_b'] == 3

    def test_set(self):
        label_a = Label('label_a')
        label_b = Label('label_b', parent=label_a)

        set_labels = {label_a, label_b}
        set_names = {'label_a', 'label_b'}

        assert label_a in set_labels
        assert label_a in set_names
        assert label_b in set_labels
        assert label_b in set_names

        assert 'label_a' in set_labels
        assert 'label_a' in set_names
        assert 'label_b' in set_labels
        assert 'label_b' in set_names

        assert {label_a} & set_labels == {label_a}
        assert {label_a} & set_names == {'label_a'}
        assert {'label_a'} & set_labels == {label_a}
        assert {'label_a'} & set_names == {'label_a'}

        assert {label_b} & set_labels == {label_b}
        assert {label_b} & set_names == {'label_b'}
        assert {'label_b'} & set_labels == {label_b}
        assert {'label_b'} & set_names == {'label_b'}

    def test_attach_add_detach(self):
        label_a = Label('label_a')
        label_b = Label('label_b')
        label_c = Label('label_c', some_property='some_value')

        fake_label_a = Label('label_a')

        # Generic link testing
        label_a.attach(label_b)
        self._test_label_link(label_b, label_a)

        # More exact testing here
        assert label_a.depth == 1
        assert label_a.ancestors == (label_b, )
        assert label_b.descendants == {'label_a': label_a}

        # Not fake attach created ?
        assert label_b.parent is None
        assert not label_b.ancestors
        assert label_b.depth == 0
        assert not label_a.children
        assert not label_a.descendants

        # Assert label_c was a simple witness
        self._test_label_no_link(label_c, label_a)
        self._test_label_no_link(label_c, label_b)

        # Add another node
        label_a.add(label_c)
        self._test_label_link(label_a, label_c)

        # More exact testing here
        assert label_a.ancestors == (label_b, )
        assert label_c.ancestors == (label_a, label_b)
        assert label_a.descendants == {'label_c': label_c}
        assert label_b.descendants == {'label_a': label_a, 'label_c': label_c}

        # Not fake attach created ?
        assert label_b.parent is None
        assert not label_b.ancestors
        assert not label_c.children
        assert not label_c.descendants

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: Overlapping tree '
                                             r'(?:{|set\(\[)\'label_a\'[}\])]+ found in'):
            fake_label_a.add(label_b)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: Overlapping tree '
                                             r'(?:{|set\(\[)\'label_a\'[}\])]+ found in'):
            fake_label_a.attach(label_c)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: Overlapping tree '
                                             r'(?:{|set\(\[)\'label_a\'[}\])]+ found in'):
            label_c.add(fake_label_a)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: Overlapping tree '
                                             r'(?:{|set\(\[)\'label_a\'[}\])]+ found in'):
            fake_label_a.add(label_c)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: adding label_a to label_a\'s tree is impossible.'):
            label_a.add(fake_label_a)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: adding label_a to label_a\'s tree is impossible.'):
            label_a.attach(fake_label_a)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: adding label_a to label_a\'s tree is impossible.'):
            fake_label_a.add(label_a)

        # Test name duplicate sanity checks
        with pytest.raises(ValueError, match=r'Invalid tree: adding label_a to label_a\'s tree is impossible.'):
            fake_label_a.attach(label_a)

        # Test name collision is inefficient for add or attach
        label_b.add(fake_label_a)
        assert label_a.id in set([label.id for label in label_b.children])
        assert fake_label_a.id not in set([label.id for label in label_b.children])

        label_c.attach(fake_label_a)
        assert label_c.parent.id != fake_label_a.id
        assert label_c.parent.id == label_a.id

        fake_label_a.attach(label_b)
        assert label_a.id in set([label.id for label in label_b.children])
        assert fake_label_a.id not in set([label.id for label in label_b.children])

        # Remove the a -> b link upward
        label_a.detach(label_b)
        self._test_label_no_link(label_a, label_b)
        self._test_label_link(label_a, label_c)

        assert label_a.parent is None
        assert not label_a.ancestors
        assert label_a.depth == 0
        assert not label_b.children
        assert not label_b.descendants

        # Remove the c -> a link downward
        label_a.detach(label_c)
        self._test_label_no_link(label_a, label_c)

        assert label_c.parent is None
        assert not label_c.ancestors
        assert label_c.depth == 0
        assert not label_a.children
        assert not label_a.descendants

        # Test silent ignore of dubious detach
        label_a.detach(label_c, label_b)

        # Test properties
        label_a.parent = label_b
        self._test_label_link(label_b, label_a)

        # More exact testing here
        assert label_a.depth == 1
        assert label_a.ancestors == (label_b,)
        assert label_b.descendants == {'label_a': label_a}

        # Test properties
        label_a.parent = label_c
        self._test_label_no_link(label_a, label_b)
        self._test_label_link(label_c, label_a)

        # More exact testing here
        assert label_a.depth == 1
        assert label_a.ancestors == (label_c,)
        assert label_c.descendants == {'label_a': label_a}

        label_c.detach(label_a)
        # Test properties
        label_a.children = (label_b, )
        self._test_label_link(label_a, label_b)

        # More exact testing here
        assert label_b.depth == 1
        assert label_b.ancestors == (label_a,)
        assert label_a.descendants == {'label_b': label_b}

        # Test properties
        label_a.children = (label_c, )
        self._test_label_no_link(label_a, label_b)
        self._test_label_link(label_a, label_c)

        # More exact testing here
        assert label_c.depth == 1
        assert label_c.ancestors == (label_a,)
        assert label_a.descendants == {'label_c': label_c}

        # Test constructor
        label_d = Label('label_d', parent=label_a)
        self._test_label_link(label_a, label_c)
        self._test_label_link(label_a, label_d)

        # More exact testing here
        assert label_d.depth == 1
        assert label_d.ancestors == (label_a,)
        assert label_a.descendants == {'label_c': label_c, 'label_d': label_d}

        label_e = Label('label_e', children=(label_a, label_b))
        self._test_label_link(label_e, label_b)
        self._test_label_link(label_e, label_a)
        self._test_label_link(label_a, label_c)
        self._test_label_link(label_a, label_d)

        # More exact testing here
        assert label_b.depth == 1
        assert label_b.ancestors == (label_e,)
        assert label_d.depth == 2
        assert label_d.ancestors == (label_a, label_e)
        assert label_e.descendants == {'label_a': label_a, 'label_b': label_b, 'label_c': label_c, 'label_d': label_d}

    def test_last_common_ancestor(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)
        a_a_c_a = Label("a_a_c_a")
        a_a_c_b_a = Label("a_a_c_b_a")
        a_a_c_b = Label("a_a_c_b", children=(a_a_c_b_a,))
        a_a_c_a_a = Label("a_a_c_a_a")
        a_a_c_a_b = Label("a_a_c_a_b")
        a_a_c_a_b_a = Label("a_a_c_a_b_a", parent=a_a_c_a_b)

        a_a_c.add(a_a_c_a, a_a_c_b)
        a_a_c_a_a.attach(a_a_c_a)
        a_a_c_a_b.attach(a_a_c_a)

        a_b = Label("a_b", parent=a)
        a_b_a = Label("a_b_a", parent=a_b)
        a_b_a_a = Label("a_b_a_a", parent=a_b_a)
        a_b_a_b = Label("a_b_a_b", parent=a_b_a)

        assert a_a_c_b.last_common_ancestor(a_a_c_a_b_a) == a_a_c
        assert a_a_c_a_b_a.last_common_ancestor(a_a_c_b) == a_a_c

        assert a_a_c_a_b_a.last_common_ancestor(a_a_b_a) == a_a
        assert a_a_b_a.last_common_ancestor(a_a_c_a_b_a) == a_a

        assert a_a.last_common_ancestor(a_a) == a_a

        for label_name in a_a.descendants:
            assert a_a.last_common_ancestor(a_a.descendants[label_name]) == a_a

    def test_clade(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)
        a_a_c_a = Label("a_a_c_a")
        a_a_c_b_a = Label("a_a_c_b_a")
        a_a_c_b = Label("a_a_c_b", children=(a_a_c_b_a,))
        a_a_c_a_a = Label("a_a_c_a_a")
        a_a_c_a_b = Label("a_a_c_a_b")
        a_a_c_a_b_a = Label("a_a_c_a_b_a", parent=a_a_c_a_b)

        a_a_c.add(a_a_c_a, a_a_c_b)
        a_a_c_a_a.attach(a_a_c_a)
        a_a_c_a_b.attach(a_a_c_a)

        a_b = Label("a_b", parent=a)
        a_b_a = Label("a_b_a", parent=a_b)
        a_b_a_a = Label("a_b_a_a", parent=a_b_a)
        a_b_a_b = Label("a_b_a_b", parent=a_b_a)

        assert a_a_c_b.clade(a_a_c_a_b_a) == Tree(a_a_c)
        assert a_a_c_a_b_a.clade(a_a_c_b) == Tree(a_a_c)

        assert a_a_c_a_b_a.clade(a_a_b_a) == Tree(a_a)
        assert a_a_b_a.clade(a_a_c_a_b_a) == Tree(a_a)

        assert a_a.clade(a_a) == Tree(a_a)

        for label_name in a_a.descendants:
            assert a_a.clade(a_a.descendants[label_name]) == Tree(a_a)


class TestTree:
    def test_creation(self, tree_a):
        tree = Tree(tree_a)
        mixin_suite(tree)  # Base validity tests
        assert tree.root == tree_a

    def test_represent(self, tree_a):
        tree = Tree(tree_a)
        assert tree.represent() == tree_a_repr
        assert str(tree) == tree_a_repr
        assert tree.represent(max_depth=3) == tree_a_repr_3
        assert tree.represent(max_depth=0) == "a"

    def test_iteration(self, tree_a):
        tree = Tree(tree_a)

        assert tuple(tree.iterate()) == tuple(tree.iterate().top_down())
        assert tuple(tree.iterate()) == (Label('a'),
                                         Label('a_a'),
                                         Label('a_a_a'),
                                         Label('a_a_b'),
                                         Label('a_a_b_a'),
                                         Label('a_a_b_b'),
                                         Label('a_a_c'),
                                         Label('a_a_c_a'),
                                         Label('a_a_c_a_a'),
                                         Label('a_a_c_a_b'),
                                         Label('a_a_c_a_b_a'),
                                         Label('a_a_c_b'),
                                         Label('a_a_c_b_a'),
                                         Label('a_b'),
                                         Label('a_b_a'),
                                         Label('a_b_a_a'),
                                         Label('a_b_a_b'))

        assert tuple(tree.iterate().bottom_up()) == (Label('a'),
                                                     Label('a_a'),
                                                     Label('a_a_a'),
                                                     Label('a_a_b'),
                                                     Label('a_a_b_a'),
                                                     Label('a_a_b_b'),
                                                     Label('a_a_c'),
                                                     Label('a_a_c_a'),
                                                     Label('a_a_c_a_a'),
                                                     Label('a_a_c_a_b'),
                                                     Label('a_a_c_a_b_a'),
                                                     Label('a_a_c_b'),
                                                     Label('a_a_c_b_a'),
                                                     Label('a_b'),
                                                     Label('a_b_a'),
                                                     Label('a_b_a_a'),
                                                     Label('a_b_a_b'))[::-1]

        assert tuple(tuple(e) for e in tree.iterate().depth_wise_top_down()) == ((Label('a'), ),
                                                                                 (Label('a_a'),
                                                                                  Label('a_b')),
                                                                                 (Label('a_a_a'),
                                                                                  Label('a_a_b'),
                                                                                  Label('a_a_c'),
                                                                                  Label('a_b_a')),
                                                                                 (Label('a_a_b_a'),
                                                                                  Label('a_a_b_b'),
                                                                                  Label('a_a_c_a'),
                                                                                  Label('a_a_c_b'),
                                                                                  Label('a_b_a_a'),
                                                                                  Label('a_b_a_b')),
                                                                                 (Label('a_a_c_a_a'),
                                                                                  Label('a_a_c_a_b'),
                                                                                  Label('a_a_c_b_a')),
                                                                                 (Label('a_a_c_a_b_a'), ))

        assert tuple(tuple(e) for e in tree.iterate().depth_wise_bottom_up()) == ((Label('a'), ),
                                                                                  (Label('a_a'),
                                                                                   Label('a_b')),
                                                                                  (Label('a_a_a'),
                                                                                   Label('a_a_b'),
                                                                                   Label('a_a_c'),
                                                                                   Label('a_b_a')),
                                                                                  (Label('a_a_b_a'),
                                                                                   Label('a_a_b_b'),
                                                                                   Label('a_a_c_a'),
                                                                                   Label('a_a_c_b'),
                                                                                   Label('a_b_a_a'),
                                                                                   Label('a_b_a_b')),
                                                                                  (Label('a_a_c_a_a'),
                                                                                   Label('a_a_c_a_b'),
                                                                                   Label('a_a_c_b_a')),
                                                                                  (Label('a_a_c_a_b_a'), ))[::-1]

        assert tuple(tree.iterate(max_depth=3)) == tuple(tree.iterate(max_depth=3).top_down())
        assert tuple(tree.iterate(max_depth=3)) == (Label('a'),
                                                    Label('a_a'),
                                                    Label('a_a_a'),
                                                    Label('a_a_b'),
                                                    Label('a_a_b_a'),
                                                    Label('a_a_b_b'),
                                                    Label('a_a_c'),
                                                    Label('a_a_c_a'),
                                                    Label('a_a_c_b'),
                                                    Label('a_b'),
                                                    Label('a_b_a'),
                                                    Label('a_b_a_a'),
                                                    Label('a_b_a_b'))

        assert tuple(tree.iterate(max_depth=3).bottom_up()) == (Label('a'),
                                                                Label('a_a'),
                                                                Label('a_a_a'),
                                                                Label('a_a_b'),
                                                                Label('a_a_b_a'),
                                                                Label('a_a_b_b'),
                                                                Label('a_a_c'),
                                                                Label('a_a_c_a'),
                                                                Label('a_a_c_b'),
                                                                Label('a_b'),
                                                                Label('a_b_a'),
                                                                Label('a_b_a_a'),
                                                                Label('a_b_a_b'))[::-1]

        assert tuple(tuple(e) for e in tree.iterate(max_depth=3).depth_wise_top_down()) == ((Label('a'), ),
                                                                                            (Label('a_a'),
                                                                                             Label('a_b')),
                                                                                            (Label('a_a_a'),
                                                                                             Label('a_a_b'),
                                                                                             Label('a_a_c'),
                                                                                             Label('a_b_a')),
                                                                                            (Label('a_a_b_a'),
                                                                                             Label('a_a_b_b'),
                                                                                             Label('a_a_c_a'),
                                                                                             Label('a_a_c_b'),
                                                                                             Label('a_b_a_a'),
                                                                                             Label('a_b_a_b')))

        assert tuple(tuple(e) for e in tree.iterate(max_depth=3).depth_wise_bottom_up()) == ((Label('a'), ),
                                                                                             (Label('a_a'),
                                                                                              Label('a_b')),
                                                                                             (Label('a_a_a'),
                                                                                              Label('a_a_b'),
                                                                                              Label('a_a_c'),
                                                                                              Label('a_b_a')),
                                                                                             (Label('a_a_b_a'),
                                                                                              Label('a_a_b_b'),
                                                                                              Label('a_a_c_a'),
                                                                                              Label('a_a_c_b'),
                                                                                              Label('a_b_a_a'),
                                                                                              Label('a_b_a_b')))[::-1]

        assert tuple(tree.iterate(max_depth=3).floor(4)) == (Label('a_a_c_a_a'),
                                                             Label('a_a_c_a_b'),
                                                             Label('a_a_c_b_a'))

        assert tuple(tree.iterate().floor(3)) == (Label('a_a_b_a'),
                                                  Label('a_a_b_b'),
                                                  Label('a_a_c_a'),
                                                  Label('a_a_c_b'),
                                                  Label('a_b_a_a'),
                                                  Label('a_b_a_b'))

    def test_to_dict(self, tree_a):
        results = {
            Label('a'): {
                Label('a_a'): {
                    Label('a_a_a'): {},
                    Label('a_a_b'): {
                        Label('a_a_b_a'): {},
                        Label('a_a_b_b'): {}
                    },
                    Label('a_a_c'): {
                        Label('a_a_c_a'): {
                            Label('a_a_c_a_a'): {},
                            Label('a_a_c_a_b'): {
                                Label('a_a_c_a_b_a'): {}
                            }
                        },
                        Label('a_a_c_b'): {
                            Label('a_a_c_b_a'): {}
                        }
                    }
                },
                Label('a_b'): {
                    Label('a_b_a'): {
                        Label('a_b_a_a'): {},
                        Label('a_b_a_b'): {}
                    }
                }
            }
        }
        assert Tree(tree_a).to_dict() == results

    def test_equality(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)

        # Unordered
        b = Label("a")
        b_a = Label("a_a", parent=b)

        b_a_c = Label("a_a_c", parent=b_a)

        b_a_b_b = Label("a_a_b_b")
        b_a_b_a = Label("a_a_b_a")
        b_a_b = Label("a_a_b", parent=b_a, children=(b_a_b_b, b_a_b_a))
        b_a_a = Label("a_a_a", parent=b_a)

        assert Tree(a) == Tree(b)
        assert not Tree(a) != Tree(b)

        # Structure change
        b = Label("a")
        b_a = Label("a_a", parent=b)

        b_a_c = Label("a_a_c", parent=b_a)
        b_a_a = Label("a_a_a", parent=b_a)

        b_a_b_b = Label("a_a_b_b")
        b_a_b = Label("a_a_b", parent=b_a, children=(b_a_b_b, ))

        assert not Tree(a) == Tree(b)
        assert Tree(a) != Tree(b)

        # Content change
        b = Label("a")
        b_a = Label("a_a", parent=b)

        b_a_c = Label("a_a_c", parent=b_a)
        b_a_a = Label("a_a_e", parent=b_a)

        b_a_b_b = Label("a_a_b_b")
        b_a_b_a = Label("a_a_b_a")
        b_a_b = Label("a_a_b", parent=b_a, children=(b_a_b_b, b_a_b_a))

        assert not Tree(a) == Tree(b)
        assert Tree(a) != Tree(b)

    def test_accessor(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)

        tree_a = Tree(a)
        tree_a_a_b = Tree(a_a_b)

        assert tree_a['a_a_b_a'] == tree_a_a_b['a_a_b_a'] == a_a_b_a
        assert tree_a['a_a_b_a'].id == tree_a_a_b['a_a_b_a'].id == a_a_b_a.id

        assert tree_a.get()['a_a_b_a'] == tree_a_a_b.get()['a_a_b_a'] == a_a_b_a
        assert tree_a.get()['a_a_b_a'].id == tree_a_a_b.get()['a_a_b_a'].id == a_a_b_a.id

        assert tree_a.get(max_depth=1)['a_a_b_a'] == a_a
        assert tree_a.get(max_depth=1)['a_a_b_a'].id == a_a.id

        assert tree_a_a_b.get(max_depth=0)['a_a_b_a'] == a_a_b
        assert tree_a_a_b.get(max_depth=0)['a_a_b_a'].id == a_a_b.id

        assert tree_a.get().name['a_a_b_a'] == tree_a_a_b.get()['a_a_b_a'] == a_a_b_a
        assert tree_a.get().name['a_a_b_a'].id == tree_a_a_b.get()['a_a_b_a'].id == a_a_b_a.id

        assert tree_a.get(max_depth=1).name['a_a_b_a'] == a_a
        assert tree_a.get(max_depth=1).name['a_a_b_a'].id == a_a.id

        assert tree_a_a_b.get(max_depth=0).name['a_a_b_a'] == a_a_b
        assert tree_a_a_b.get(max_depth=0).name['a_a_b_a'].id == a_a_b.id

        assert tree_a.get().id[a_a_b_a.id] == tree_a_a_b.get().id[a_a_b_a.id] == a_a_b_a
        assert tree_a.get().id[a_a_b_a.id].id == tree_a_a_b.get().id[a_a_b_a.id].id == a_a_b_a.id

        assert tree_a.get(max_depth=1).id[a_a_b_a.id] == a_a
        assert tree_a.get(max_depth=1).id[a_a_b_a.id].id == a_a.id

        assert tree_a_a_b.get(max_depth=0).id[a_a_b_a.id] == a_a_b
        assert tree_a_a_b.get(max_depth=0).id[a_a_b_a.id].id == a_a_b.id

        new_a_a_b = Label("new_a_a_b")
        new_a_a_b_name = Label("new_a_a_b_name")
        new_a_a_b_id = Label("new_a_a_b_id")
        c = Label("c")

        tree_a.get()['a_a_b'] = new_a_a_b
        assert new_a_a_b in a_a.children
        assert a_a_b_a.parent == new_a_a_b
        assert a_a_b_b.parent == new_a_a_b
        assert a_a_b.parent is None
        assert not a_a_b.children

        tree_a.get().name['new_a_a_b'] = new_a_a_b_name
        assert new_a_a_b_name in a_a.children
        assert a_a_b_a.parent == new_a_a_b_name
        assert a_a_b_b.parent == new_a_a_b_name
        assert new_a_a_b.parent is None
        assert not new_a_a_b.children

        tree_a.get().id[new_a_a_b_name.id] = new_a_a_b_id
        assert new_a_a_b_id in a_a.children
        assert a_a_b_a.parent == new_a_a_b_id
        assert a_a_b_b.parent == new_a_a_b_id
        assert new_a_a_b_name.parent is None
        assert not new_a_a_b_name.children

        tree_a['new_a_a_b_id'] = new_a_a_b
        assert new_a_a_b in a_a.children
        assert a_a_b_a.parent == new_a_a_b
        assert a_a_b_b.parent == new_a_a_b
        assert new_a_a_b_id.parent is None
        assert not new_a_a_b_id.children

        tree_a.get()['label'] = c
        assert c in a.children
        assert c.parent == a

        with pytest.raises(KeyError, match='Invalid identifier: label does not correspond to any label in the tree.'):
            print(tree_a.get()['label'])

        with pytest.raises(KeyError, match='Invalid identifier: label does not correspond to any label in the tree.'):
            print(tree_a.get().name['label'])

        with pytest.raises(KeyError, match='Invalid identifier: label does not correspond to any label in the tree.'):
            print(tree_a.get().id['label'])

    def test_depth(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)

        tree_a_a = Tree(a_a)
        tree_a_a_b = Tree(a_a_b)

        assert a_a_b_a.depth > tree_a_a.depth(a_a_b_a) > tree_a_a_b.depth(a_a_b_a)
        assert a_a_b_a.depth == 3
        assert tree_a_a.depth(a_a_b_a) == 2
        assert tree_a_a_b.depth(a_a_b_a) == 1

    def test_ancestors(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)

        tree_a_a = Tree(a_a)
        tree_a_a_b = Tree(a_a_b)

        assert a_a_b_a.ancestors == (a_a_b, a_a, a)
        assert tree_a_a.ancestors(a_a_b_a) == (a_a_b, a_a)
        assert tree_a_a_b.ancestors(a_a_b_a) == (a_a_b, )

    def test_depth_wise(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)

        tree_a = Tree(a)
        tree_a_a = Tree(a_a)
        tree_a_a_b = Tree(a_a_b)

        assert tree_a.depth_wise == {0: (a, ),
                                     1: (a_a, ),
                                     2: (a_a_a, a_a_b, a_a_c),
                                     3: (a_a_b_a, a_a_b_b)}

        assert tree_a_a.depth_wise == {0: (a_a, ),
                                       1: (a_a_a, a_a_b, a_a_c),
                                       2: (a_a_b_a, a_a_b_b)}

        assert tree_a_a_b.depth_wise == {0: (a_a_b, ),
                                         1: (a_a_b_a, a_a_b_b)}

    def test_siblings(self):
        a = Label("a")
        a_a = Label("a_a", parent=a)

        a_a_a = Label("a_a_a", parent=a_a)

        a_a_b = Label("a_a_b", parent=a_a)
        a_a_b_a = Label("a_a_b_a", parent=a_a_b)
        a_a_b_b = Label("a_a_b_b", parent=a_a_b)

        a_a_c = Label("a_a_c", parent=a_a)

        tree_a = Tree(a)
        tree_a_a = Tree(a_a)
        tree_a_a_b = Tree(a_a_b)

        assert set(tree_a.siblings(a_a_b)) == {a_a_a, a_a_c}
        assert set(tree_a_a.siblings(a_a_b)) == {a_a_a, a_a_c}
        assert set(tree_a_a_b.siblings(a_a_b)) == set()

    def test_contains(self, tree_a):
        tree = Tree(tree_a)

        assert Label('a_a_c_a_b') in tree
        assert not Label('c_a_c_a_b') in tree

        assert Label('a') in tree
        assert not Label('c') in tree

    def test_len(self, tree_a):
        tree = Tree(tree_a)
        assert len(tree) == 17


class TestTaxonomy:
    def test_creation(self, tree_a, tree_b):
        taxo = Taxonomy(tree_a, tree_b)
        mixin_suite(taxo)  # Base validity tests
        assert taxo.root == Label('__root__')
        assert taxo.root.children == {tree_a, tree_b}

    def test_representation(self, tree_a, tree_b):
        taxo = Taxonomy(tree_a, tree_b)
        assert taxo.represent() == str(taxo) == taxo_repr

    def test_properties(self, tree_a, tree_b):
        tree_d = Label('#05-0*+"0560&&45')  # Invalid true root label name !
        tree_e = Label('#05-valid name-overall')
        with pytest.raises(ValueError, match='Invalid name'):
            invalid_taxo = Taxonomy(tree_e, tree_d)

        tree_c = Label('#-*65623&}-5_44tree c-with 3 Invalid$chAr')
        taxo = Taxonomy(tree_a, tree_b, tree_c)

        assert tree_a in taxo.properties
        assert hasattr(taxo, tree_a.name)
        assert isinstance(getattr(taxo, tree_a.name), Tree)
        assert isinstance(taxo.properties[tree_a], Tree)

        assert tree_b in taxo.properties
        assert hasattr(taxo, tree_b.name)
        assert isinstance(getattr(taxo, tree_b.name), Tree)
        assert isinstance(taxo.properties[tree_b], Tree)

        # Using cleaned name ex-nihilo here. If one wants to do it programmatically, use the clean() function.
        assert '_44tree_c_with_3_invalid_char' in taxo.properties
        assert hasattr(taxo, '_44tree_c_with_3_invalid_char')
        assert isinstance(getattr(taxo, '_44tree_c_with_3_invalid_char'), Tree)
        assert isinstance(taxo.properties['_44tree_c_with_3_invalid_char'], Tree)

        assert 'tree_d' not in taxo.properties
        assert not hasattr(taxo, 'tree_d')

    def test_validate(self, tree_a, tree_b):
        taxo = Taxonomy(tree_a, tree_b)

        with pytest.raises(ValueError, match=r'Invalid label tuple: Empty tuple'):
            taxo.validate()

        with pytest.raises(ValueError, match=r'Expected at most \d+ labels'):
            taxo.validate(Label(''), Label(''), Label(''))

        with pytest.raises(ValueError, match=r'(?:{|set\(\[)Label\(name=label_a\)[}\])]+ are not part of the taxonomy'):
            taxo.validate(Label('label_a'), Label('a_a'))

        with pytest.raises(ValueError, match=r'(?:{|set\(\[)Label\(name=label_a\)[}\])]+ are not part of the taxonomy'):
            taxo.validate(Label('a_a'), Label('label_a'))

        with pytest.raises(ValueError, match=r'Some labels are part of the same true-root subtree: a_a_c'):
            taxo.validate(Label('a_a'), Label('a_a_c'))

        with pytest.raises(ValueError, match=r'Some labels are part of the same true-root subtree: a_a_c'):
            taxo.validate(Label('a_a_b_a'), Label('a_a_c'))

        taxo.validate(Label('a_a_b_a'), Label('b_b'))
        taxo.validate(Label('b_a'), Label('a_a_b'))
        taxo.validate(Label('b_a'))
        taxo.validate(Label('a_a_b_a'))

        # Verify that taxonomies validation is pickle compatible
        import pickle
        from pickle import loads, dumps
        taxo_pickle = loads(dumps(taxo, protocol=max(2, getattr(pickle, 'DEFAULT_PROTOCOL', 0))))

        with pytest.raises(ValueError, match=r'Invalid label tuple: Empty tuple'):
            taxo_pickle.validate()

        with pytest.raises(ValueError, match=r'Expected at most \d+ labels'):
            taxo_pickle.validate(Label(''), Label(''), Label(''))

        with pytest.raises(ValueError, match=r'(?:{|set\(\[)Label\(name=label_a\)[}\])]+ are not part of the taxonomy'):
            taxo_pickle.validate(Label('label_a'), Label('a_a'))

        with pytest.raises(ValueError, match=r'(?:{|set\(\[)Label\(name=label_a\)[}\])]+ are not part of the taxonomy'):
            taxo_pickle.validate(Label('a_a'), Label('label_a'))

        with pytest.raises(ValueError, match=r'Some labels are part of the same true-root subtree: a_a_c'):
            taxo_pickle.validate(Label('a_a'), Label('a_a_c'))

        with pytest.raises(ValueError, match=r'Some labels are part of the same true-root subtree: a_a_c'):
            taxo_pickle.validate(Label('a_a_b_a'), Label('a_a_c'))

        taxo_pickle.validate(Label('a_a_b_a'), Label('b_b'))
        taxo_pickle.validate(Label('b_a'), Label('a_a_b'))
        taxo_pickle.validate(Label('b_a'))
        taxo_pickle.validate(Label('a_a_b_a'))
