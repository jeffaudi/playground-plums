from collections import defaultdict

from ..mixin import IdentifiedMixIn, PropertyContainer
from .accessor import DefaultTreeAccessor
from .iterator import DefaultTreeIterator, TreeIteratorBase, TopDownTreeIterator


class _RepresentationalTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates in a top-down manner and returns a text representation of each nodes.

    It starts at the tree root and go down until it reaches a leaf label. It then steps upward and searches for the
    next leafs.

    For example, given the following::

        f
        ├── b
        │   ├── a
        │   ╰── d
        │       ├── c
        │       ╰── e
        ╰── g
            ╰── i
                ╰── h

    The iterator will yield: ``f``, ``├── b``, ``│   ├── a``, ``│   ╰── d``, ``       ├── c``,
    ``│       ╰── e``, ``╰── g``, ``    ╰── i`` then ``        ╰── h``.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree``
            root) on which to iterate.

    Attributes:
        properties (dict): Properties provided as kwargs in the constructor.

    """

    __blank_separator = u'    '
    __vertical_separator = u'\u2502   '
    __branch_element_separator = u'\u251c\u2500\u2500 '
    __branch_end_separator = u'\u2570\u2500\u2500 '

    def __init__(self, tree, max_depth=None):
        super(_RepresentationalTreeIterator, self).__init__(tree, max_depth=max_depth)
        self._iterator = None
        self._depth_state = None
        self._parent_state = None
        self._branch_position_state = defaultdict(int)
        self._branch_len_state = defaultdict(int)
        self._continue_state = None

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a top-down order.

        Yields (str): A tree |Label| node representation.

        """
        self._iterator = iter(TopDownTreeIterator(self._tree, max_depth=self._max_depth))

        self._depth_state = 1
        self._parent_state = None
        self._branch_position_state = defaultdict(int)
        self._branch_len_state = defaultdict(int)
        self._branch_position_state[None] = 0
        self._branch_len_state[None] = 1
        self._branch_position_state[self._tree.root] = 0
        self._branch_len_state[self._tree.root] = len([label for label in self._tree.depth_wise[1]
                                                       if label.parent == self._tree.root])
        self._continue_state = ''

        return self

    def __next__(self):
        """Iterate through a |Tree| in a top-down order.

        Yields (str): A tree |Label| node representation.

        """
        node = next(self._iterator)

        if node == self._tree.root:
            if node == '__root__':
                return ''
            return node.name

        # Update **depth** and **continue** states.
        depth = self._tree.depth(node)
        parent = node.parent

        # We changed branch
        if parent != self._parent_state:
            # We went down a level
            if depth > self._depth_state:
                # Record branch length
                self._branch_len_state[parent] = len([label for label in self._tree.depth_wise[depth]
                                                      if label.parent == parent])
                # And we were not finished yet
                if self._branch_position_state[self._parent_state] < self._branch_len_state[self._parent_state]:
                    # Add a single vertical separator
                    self._continue_state += self.__vertical_separator
                # And we were finished
                else:
                    # Add a single blank separator
                    self._continue_state += self.__blank_separator
            # We went up a level
            elif depth < self._depth_state:
                # Remove a separator
                self._continue_state = self._continue_state[:(-4 * (self._depth_state - depth))]

        self._depth_state = depth
        self._parent_state = parent

        # Compute appropriate separator
        separator = self.__branch_element_separator \
            if self._branch_position_state[self._parent_state] < self._branch_len_state[self._parent_state] - 1\
            else self.__branch_end_separator

        # Update branch position
        self._branch_position_state[self._parent_state] += 1

        row = self._continue_state + separator + node.name
        return row


class Tree(PropertyContainer, IdentifiedMixIn):
    """A |Label| tree viewer and helper class.

    It implements a set of accessor and viewer methods as well as a few useful tree manipulation routines.

    Args:
        label (|Label|): The |Label| used to root the tree.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |Tree|.

    """

    __slots__ = '_label'

    def __init__(self, label, id=None, **properties):
        self._label = label
        super(Tree, self).__init__(id=id, **properties)

    def _top_down(self, label):
        yield label
        for children in label.children:
            for element in self._top_down(children):
                yield element

    @property
    def root(self):
        """|Label|: The |Tree| root |Label|."""
        return self._label

    @property
    def id(self):
        """str: An identifier unique for all |Tree| instance *independent* on content."""
        return self._id

    @property
    def max_depth(self):
        """int: The maximum  |Label| depth (0-based) relative to the tree root."""
        return max(tuple(depth for depth in self.depth_wise))

    @property
    def depth_wise(self):  # noqa: D401
        """dict: A dictionary of the form :code:`{depth: (*labels)}`.

        For example, given the following::

            f
            ├── b
            │   ├── a
            │   ╰── d
            │       ├── c
            │       ╰── e
            ╰── g
                ╰── i
                    ╰── h

        It will return:

        .. code-block:: python

            {
                0: (f, ),
                1: (b, g),
                3: (a, d, i),
                4: (c, e, h)
            }

        """
        depth_wise = defaultdict(tuple)
        for label in iter(self._top_down(self._label)):
            depth_wise[self.depth(label)] += (label, )
        return dict(depth_wise)

    def __repr__(self):
        """Pythonic representation of the object."""
        return '{}(root={})'.format(self.__class__.__name__, repr(self._label))

    def __str__(self):
        """Return a textual representation of the |Tree| where each node is represented by the |Label| name.

        See Also:
            The :meth:`represent` method which is the actual method called by ``__str__``.

        """
        return self.represent()

    def __eq__(self, other):
        """Return whether two |Tree| have the same *content* and *structure*.

        Args:
            other (|Tree|): Another tree to compare oneself to.

        Returns:
            bool: ``True`` if both tree contains the same |Label| and have the same tree structure.

        """
        try:
            return self.to_dict() == other.to_dict()
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        """Return whether two |Tree| do not have the same *content* and *structure*.

        Args:
            other (|Tree|): Another tree to compare oneself to.

        Returns:
            bool: ``True`` if both tree does not contains the same |Label| or do not have the same tree structure.

        """
        return not self == other

    def __contains__(self, label):
        """Return whether a |Label| is contained within self's tree.

        Args:
            label (|Label|): A label to look up inside the label tree.

        Returns:
            bool: ``True`` is the |Label| can be found somewhere inside the tree.

        """
        child = label in self._label.descendants
        if not child:
            return label == self._label
        return child

    def __len__(self):
        """Return the number of node in the |Tree| including the root."""
        return len(self._label.descendants) + 1

    def __getitem__(self, name):
        """Access |Label| from their name using a |DefaultTreeAccessor|.

        Args:
            name (str): A |Label| name identifier.

        Returns:
            |Label|: A |Label| from the |Tree|.

        Raises:
            KeyError: If the provided item can not be mapped to a |Label| in the |Tree|.

        """
        return DefaultTreeAccessor(self).__getitem__(name)

    def __setitem__(self, name, label):
        """Set a |Label| from a given name in a |Tree| using a |DefaultTreeAccessor|.

        If ``name`` does not correspond to a known |Label|, ``label`` will be attached to the |Tree| root.
        Otherwise, ``label`` will replace the |Label| corresponding to ``name`` in the |Tree|.

        Args:
            name (str): A |Label| name.
            label (|Label|): A |Label| to insert in the |Tree|.

        """
        return DefaultTreeAccessor(self).__setitem__(name, label)

    def represent(self, max_depth=None):
        """Make a textual representation of the |Tree| where each node is represented by the |Label| name.

        For example, a simple |Tree| with 3 elements, two of which are the others children will print as::

            b
            ├── a
            ╰── d

        It is possible to control the depth of recursion in the tree used for pretty printing with the ``max_depth``
        argument.

        Args:
            max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree``
            root) on which to iterate.

        Returns:
            str: A textual representation of a tree.

        """
        if not self._label.children:
            return self._label.name

        iterator = _RepresentationalTreeIterator(self, max_depth=max_depth)
        return '\n'.join(iterator)

    def ancestors(self, label):
        """All of labels's ancestors going upward from label :attr:`~plums.commons.data.taxonomy.label.Label.parent`.

        Args:
            label (|Label|): A |Label| somewhere in self's tree.

        Returns:
            (|Label|, ):  A tuple of |Label| retracing the |label| family history.

        Raises:
            ValueError: If ``label`` is not contained is self's tree.

        """
        if self._label.depth == 0:
            return label.ancestors

        return label.ancestors[:-1 * self._label.depth]

    def depth(self, label):
        """Compute the |Label| depth—as a 0-based index—relative to the tree root.

        Args:
            label (|Label|): A |Label| somewhere in self's tree.

        Returns:
            int:  The |Label| depth relative to the tree.

        """
        return label.depth - self._label.depth

    def siblings(self, label):
        """Compute the siblings of a given |Label|.

        A sibling is a |Label| of the same depth which shares parent with the provided |Label|.

        Args:
            label (|Label|): A |Label| somewhere in self's tree.

        Returns:
            (|Label|, ):  A tuple of sibling |Label|.

        """
        return tuple(element for element in self.depth_wise[self.depth(label)] if (element.parent == label.parent
                                                                                   and not element == label))

    def iterate(self, max_depth=None):
        """Iterate through the tree in a top-down manner and give interfaces to other iteration flavors.

        It starts at the tree root and go down until it reaches a leaf label. It then steps upward and searches for the
        next leafs.

        For example, given the following::

            f
            ├── b
            │   ├── a
            │   ╰── d
            │       ├── c
            │       ╰── e
            ╰── g
                ╰── i
                    ╰── h

        The iterator will yield: ``f``, ``b``, ``a``, ``d``, ``c``, ``e``, ``g``, ``i`` then ``h``.

        Args:
            max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree``
                root) on which to iterate.

        Returns:
            |DefaultTreeIterator|: An top-down tree iterator with interfaces to different iteration flavors.

        """
        return DefaultTreeIterator(self, max_depth=max_depth)

    def get(self, max_depth=None):
        """Access |Label| from their name and give interfaces other access flavors as properties.

        Args:
            max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree``
                root) on which to allow access.

        Returns:
            |DefaultTreeAccessor|: A name tree accessor with interfaces to different accessor flavors.

        """
        return DefaultTreeAccessor(self, max_depth=max_depth)

    def to_dict(self, max_depth=None):
        """Represent the |Tree| up to a given depth as a nested dictionary structure.

        For example, given the following::

            f
            ├── b
            │   ├── a
            │   ╰── d
            │       ├── c
            │       ╰── e
            ╰── g
                ╰── i
                    ╰── h

        Then ``to_dict`` will return the following structure:

        .. code-block:: python

            {
                Label(name="f") : {
                    Label(name="b") : {
                        Label(name="a") : {},
                        Label(name="d") : {
                            Label(name="c") : {},
                            Label(name="e") : {},
                        }
                    },
                    Label(name="g") : {
                        Label(name="i") : {
                            Label(name="h") : {}
                        }

                    }
                }
            }

        Args:
            max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree``
                root) on which to iterate.

        Returns:
            dict: A nested dictionary structure representing each |label| node as a ``label: {}`` entry.

        """
        def get_dict(label):
            dictionary = output
            for ancestor in self.ancestors(label)[::-1]:
                dictionary = dictionary[ancestor]
            return dictionary

        output = {self._label: {}}
        for label in self.iterate(max_depth=max_depth):
            if label == self._label:
                continue
            get_dict(label).update({label: {}})
        return output
