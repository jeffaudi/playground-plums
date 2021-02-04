import abc


class TreeAccessorBase(object, metaclass=abc.ABCMeta):
    """Abstract Base Class for all |Tree| accessor classes.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to allow access.

    """

    def __init__(self, tree, max_depth=None):
        self._tree = tree
        self._max_depth = max_depth if max_depth is not None else self._tree.max_depth

    def __repr__(self):
        """Pythonic representation of the object."""
        return '{}(tree={}, max_depth={})'.format(self.__class__.__name__, repr(self._tree), self._max_depth)

    @abc.abstractmethod
    def __getitem__(self, item):
        """Access a |Label| from a given item in a |Tree|.

        Args:
            item (Any): A |Label| identifier corresponding to the current |TreeAccessorBase|.

        Returns:
            |Label|: A |Label| from the |Tree|.

        Raises:
            KeyError: If the provided item can not be mapped to a |Label| in the |Tree|.

        """
        raise NotImplementedError

    def __setitem__(self, item, label):
        """Set a |Label| from a given item in a |Tree|.

        If ``item`` does not correspond to a known |Label|, ``label`` will be attached to the |Tree| root.
        Otherwise, ``label`` will replace the |Label| corresponding to ``item`` in the |Tree|.

        Args:
            item (Any): A |Label| identifier corresponding to the current |TreeAccessorBase|.
            label (|Label|): A |Label| to insert in the |Tree|.

        """
        try:
            former = self[item]
        except KeyError:
            # If item does not correspond to a known label, attach to the tree root.
            label.attach(self._tree.root)
        else:
            children = former.children.copy()
            former.detach(*children)
            # Attach children
            label.add(*children)
            # Attach to former's parent
            label.attach(former.parent)
            # Detach former from its parent
            if former.parent is not None:
                former.parent.detach(former)


class DefaultTreeAccessor(TreeAccessorBase):
    """|Tree| accessor class which retrieve |Label| from their name and exposes other access flavors as properties.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to allow access.

    """

    @property
    def name(self):
        """|NameTreeAccessor|: Access |Label| from their name."""
        return NameTreeAccessor(self._tree, max_depth=self._max_depth)

    @property
    def id(self):
        """|IdTreeAccessor|: Access |Label| from their id."""
        return IdTreeAccessor(self._tree, max_depth=self._max_depth)

    def __getitem__(self, name):
        """Access a |Label| from a given name in a |Tree|.

        Args:
            name (str): A |Label| name identifier.

        Returns:
            |Label|: A |Label| from the |Tree|.

        Raises:
            KeyError: If the provided item can not be mapped to a |Label| in the |Tree|.

        """
        return NameTreeAccessor(self._tree, max_depth=self._max_depth).__getitem__(name)


class NameTreeAccessor(TreeAccessorBase):
    """|Tree| accessor class which retrieve |Label| from their name.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to allow access.

    """

    def __getitem__(self, name):
        """Access a |Label| from a given name in a |Tree|.

        Args:
            name (str): A |Label| name identifier.

        Returns:
            |Label|: A |Label| from the |Tree|.

        Raises:
            KeyError: If the provided item can not be mapped to a |Label| in the |Tree|.

        """
        if name == self._tree.root or self._max_depth <= 0:
            return self._tree.root

        try:
            label = self._tree.root.descendants[name]
        except KeyError:
            raise KeyError('Invalid identifier: {} does not correspond to any label in the tree.'.format(name))
        else:
            if self._tree.depth(label) > self._max_depth:
                label = self._tree.ancestors(label)[-1 * self._max_depth - 1]

            return label


class IdTreeAccessor(TreeAccessorBase):
    """|Tree| accessor class which retrieve |Label| from their id.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to allow access.

    """

    def __getitem__(self, id_):
        """Access a |Label| from a given id in a |Tree|.

        Args:
            id_ (str): A |Label| id identifier.

        Returns:
            |Label|: A |Label| from the |Tree|.

        Raises:
            KeyError: If the provided item can not be mapped to a |Label| in the |Tree|.

        """
        if id == self._tree.root.id or self._max_depth <= 0:
            return self._tree.root

        def get_label():
            for _label in self._tree.iterate():
                if _label.id == id_:
                    return _label
            return

        label = get_label()

        if label is None:
            raise KeyError('Invalid identifier: {} does not correspond to any label in the tree.'.format(id_))

        if self._tree.depth(label) > self._max_depth:
            label = self._tree.ancestors(label)[-1 * self._max_depth - 1]

        return label
