import abc


class TreeIteratorBase(object, metaclass=abc.ABCMeta):
    """Abstract Base Class for all |Tree| iterator classes.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to iterate.

    """

    def __init__(self, tree, max_depth=None):
        self._tree = tree
        self._max_depth = max_depth if max_depth is not None else self._tree.max_depth

    def __repr__(self):
        """Pythonic representation of the object."""
        return '{}(tree={}, max_depth={})'.format(self.__class__.__name__, repr(self._tree), self._max_depth)

    @abc.abstractmethod
    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a select order.

        Yields (:class:`~plums.commons.Label`, Iterable[:class:`~plums.commons.Label`]):
            Either a tree node or an ensemble of nodes.

        """
        raise NotImplementedError


class DefaultTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates in a top-down manner and gives interfaces to other iteration flavors.

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
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
        on which to iterate.

    """

    def __init__(self, tree, max_depth=None):
        super(DefaultTreeIterator, self).__init__(tree, max_depth=max_depth)
        self._iterator = None

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a top-down order.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        self._iterator = iter(TopDownTreeIterator(self._tree, max_depth=self._max_depth))
        return self

    def __next__(self):
        """Iterate through a |Tree| in a top-down order.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        return next(self._iterator)

    def top_down(self):
        """Make an iterator which iterate through a |Tree| in a top-down order.

        See Also:
            The |TopDownTreeIterator| class.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        return iter(self)

    def bottom_up(self):
        """Make an iterator which iterate through a |Tree| in a bottom-up order.

        See Also:
            The |BottomUpTreeIterator| class.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        return iter(BottomUpTreeIterator(self._tree, self._max_depth))

    def depth_wise_top_down(self):
        """Make an iterator which iterate through a |Tree| in a depth-wise top-down order.

        See Also:
            The |TopDownDepthWiseTreeIterator| class.

        Yields (Iterable[:class:`~plums.commons.Label`]): An iterator over an ensemble of |Label| nodes.

        """
        return iter(TopDownDepthWiseTreeIterator(self._tree, self._max_depth))

    def depth_wise_bottom_up(self):
        """Make an iterator which iterate through a |Tree| in a depth-wise bottom-up order.

        See Also:
            The |BottomUpDepthWiseTreeIterator| class.

        Yields (Iterable[:class:`~plums.commons.Label`]): An iterator over an ensemble of |Label| nodes.

        """
        return iter(BottomUpDepthWiseTreeIterator(self._tree, self._max_depth))

    def floor(self, depth):
        """Make an iterator which iterate through a |Tree| given depth floor.

        Args:
            depth (int): The |Label| depth (relative to ``tree`` root) on which to iterate.

        See Also:
            The |FloorTreeIterator| class.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        return iter(FloorTreeIterator(self._tree, depth))


class TopDownTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates in a top-down manner.

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
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to iterate.

    """

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a top-down order.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        def top_down(label):
            yield label

            if self._tree.depth(label) < self._max_depth:
                for children in label.children:
                    for element in top_down(children):
                        yield element

        return top_down(self._tree.root)


class BottomUpTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates in a bottom-up manner.

    It starts at a leaf and go up until it reaches the tree root. It then steps downward and searches for the
    next leafs to start from.

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

    The iterator will yield: ``h``, ``i``, ``g``, ``e``, ``c``, ``d``, ``a``, ``b`` then ``f``.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
        on which to iterate.

    """

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a bottom-up order.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        return \
            reversed(
                tuple(
                    iter(TopDownTreeIterator(self._tree, self._max_depth))
                )
            )


class FloorTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates over all labels in a given depth.

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

    If depth is 2, the iterator will yield: ``a``, ``d`` then ``i``.

    Args:
        tree (|Tree|): The tree on which to iterate.
        depth (int): The |Label| depth (relative to ``tree`` root) on which to iterate.

    """

    def __init__(self, tree, depth):
        self._depth = depth
        super(FloorTreeIterator, self).__init__(tree)

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| given depth floor.

        Yields (:class:`~plums.commons.Label`): A tree |Label| node.

        """
        return iter(self._tree.depth_wise[self._depth])


class TopDownDepthWiseTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates through a |Tree| in a depth-wise top-down manner.

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

    The iterator will yield: ``(f, )``, ``(b, g)``, ``(a, d, i)`` then ``(c, e, h)``.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to iterate.

    """

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a depth-wise top-down order.

        Yields (Iterable[:class:`~plums.commons.Label`]): An iterator over an ensemble of |Label| nodes.

        """
        def depth_wise():
            for depth in range(min(self._max_depth, self._tree.max_depth) + 1):
                yield iter(FloorTreeIterator(self._tree, depth))

        return depth_wise()


class BottomUpDepthWiseTreeIterator(TreeIteratorBase):
    """A |Tree| iterator class which iterates through a |Tree| in a depth-wise bottom-up manner.

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

    The iterator will yield: ``(c, e, h)``, ``(a, d, i)``, ``(b, g)`` then ``(f, )``.

    Args:
        tree (|Tree|): The tree on which to iterate.
        max_depth (int): Optional. Default to None. If provided, the maximum |Label| depth (relative to ``tree`` root)
            on which to iterate.

    """

    def __iter__(self):
        """Make an iterator which iterate through a |Tree| in a depth-wise bottom-up order.

        Yields (Iterable[:class:`~plums.commons.Label`]): An iterator over an ensemble of |Label| nodes.

        """
        return \
            reversed(
                tuple(
                    iter(TopDownDepthWiseTreeIterator(self._tree, self._max_depth))
                )
            )
