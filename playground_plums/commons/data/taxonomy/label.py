from copy import deepcopy

from ordered_set import OrderedSet

from ..mixin import IdentifiedMixIn, PropertyContainer
from .tree import Tree


class Label(PropertyContainer, IdentifiedMixIn):
    """A |Label| class which acts as a |Tree| node and stores a name.

    The :attr:`name` is assumed to be the |Label| true content and its :func:`hash` value will reflect that.

    The |Label| acts as the core body of any |Tree| creation and modification. In fact, |Label| are what defines
    **actual** trees of which the |Tree| class acts as **views**.

    To define a tree, simply links two |Label| together:

    .. code-block:: python

        >>> label_a = Label('a')
        >>> label_b = Label('b')
        >>> label_a.add(label_b) # We have a tree !
        >>> print(Tree(label_a))
        a
        ╰── b
        >>> label_c = Label('c')
        >>> label_c.attach(label_a)
        >>> print(Tree(label_a))
        a
        ├── b
        ╰── c

    .. hint::

        Note that a single |Label| is a valid |Tree| in itself with a single element. More generally, any |Label|
        defines its own |Tree|, which is called the |Label|'s `clade`_.

    Because |Tree| are dynamic in nature, any attach between two |Label| can be undone with the :meth:`detach` method,
    *e.g.*:

    .. code-block:: python

        >>> label_a.detach(label_c)
        >>> print(Tree(label_a))
        a
        ╰── b
        >>> label_b.detach(label_a)
        >>> print(Tree(label_a))
        a

    Args:
        name (str): The |Label| name. This is the actual value that is "tagged" on |Record|.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        parent (|Label|): Optional. Default to ``None``. A |Label| to be registered as self's parent.
        children (Iterable[|Label|]): Optional. Default to ``{}``. An iterable of |Label| to be registered as
            self's children.
        **properties (Any): Additional properties to store alongside the |Label|.

    .. _clade: https://en.wikipedia.org/wiki/Clade

    Attributes:
        properties (dict): Properties provided as kwargs in the constructor.

    """

    __slots__ = '_parent', '_children', '_name', '_hash', '_depth', '_ancestors', '_descendants'

    def __new__(cls, name, *args, **kwargs):
        """Create a new hashable |Label| instance."""
        label = super(Label, cls).__new__(cls)
        label._name = name
        label._hash = None
        return label

    def __init__(self, name, id=None, parent=None, children=None, **properties):
        super(Label, self).__init__(id=id, **properties)

        self._children = OrderedSet()
        self._parent = None
        self._depth = 0
        self._ancestors = ()
        self._descendants = {}

        # Setup attributes
        self._name = name

        # Setup hash
        self._hash = None

        # Setup Label position in Label tree
        self.parent = parent
        self.children = children

    @property
    def name(self):
        """str: The |Label| name. This is the actual value that is "tagged" on |Record|.

        Note:
            It is a *read-only* property because a |Label| is assumed to be immutable.

        """
        return self._name

    @property
    def id(self):
        """str: An identifier unique for all |Label| instance *independent* on content."""
        return self._id

    @property
    def parent(self):
        """|Label|: A |Label| registered as self's parent or ``None`` if self is a tree root.

        Using the property's *setter* is equivalent to a call of :meth:`attach`.

        """
        return self._parent

    @parent.setter
    def parent(self, label):
        if label is None:
            return
        if self._parent is not None:
            self.detach(self._parent)
        self.attach(label)

    @property
    def children(self):
        """list: A list of |Label| which are registered as self's children.

        Using the property's *setter* is equivalent to a joint call of :meth:`detach(self.children) <children>`
        and :meth:`add`.

        """
        return self._children

    @children.setter
    def children(self, labels):
        if labels is None or not labels:
            return

        self.detach(*self._children)
        self.add(*labels)

    @property
    def ancestors(self):
        """(|Label|, ): All of self's ancestors up to the root, going upward from :attr:`parent`."""
        return self._ancestors

    @property
    def descendants(self):  # noqa: D401
        """dict: All of self's descendants as a flattened dictionary of the form :code:`{name: label}`."""
        return self._descendants

    @property
    def depth(self):
        """int: The |label| absolute depth in the global implicit label tree."""
        return self._depth

    def __getnewargs__(self):
        """Pass name and identifier as :meth:`~object.__new__` arguments to pickle."""
        return self._name,

    def __setstate__(self, state):
        """Set attributes values from a dictionary of all slotted and in dictionary attributes."""
        for key, value in state.items():
            if key == '_hash':
                value = None
            setattr(self, key, value)

    def __deepcopy__(self, memo=None):
        """Construct a deep copy of a :class:`SlottedDict`."""
        memo = {} if memo is None else memo

        # Make semi-empty Label
        cls = self.__class__
        result = cls.__new__(cls, deepcopy(self._name, memo))
        result._properties = deepcopy(self._properties, memo)
        result._id = deepcopy(self._id, memo)
        result._name = deepcopy(self._name, memo)
        result._hash = None
        result._depth = deepcopy(self._depth, memo)
        result._children = OrderedSet()
        result._parent = None
        result._ancestors = ()
        result._descendants = {}

        # Update memo with semi-empty Label
        memo[id(self)] = result

        # Recursively copy Label tree
        result._children = deepcopy(self._children, memo)
        result._descendants = deepcopy(self._descendants, memo)
        result._parent = deepcopy(self._parent, memo)
        result._ancestors = deepcopy(self._ancestors, memo)

        return result

    def attach(self, label):
        """Attach a parent |Label| to self.

        Args:
            label (|Label|): A |Label| to register as self's parent.

        """
        if label is None or label == self.parent:
            return

        label.add(self)

        # If for some reason (most probably name collision) nothing happened in label realm we'd better back off too...
        if self.id not in {_label.id for _label in label.children}:  # True id match to avoid name collision here
            return

        self._parent = label
        self.update_ancestry()

    def add(self, *labels):
        """Attach a child or a group of children |Label| to self.

        Args:
            *labels (|Label|): A |Label| to register as self's child.

        """
        for label in labels:
            if label in self._children:
                continue

            if label == self:
                raise ValueError('Invalid tree: adding {} to {}\'s tree is impossible.'.format(label, self))

            self_root = self._ancestors[-1] if self._ancestors else self
            label_root = label.ancestors[-1] if label.ancestors else label
            overlap = dict({self_root.name: self_root}, **self_root.descendants).keys() \
                & dict({label_root.name: label_root}, **label_root.descendants).keys()

            if overlap:
                raise ValueError('Invalid tree: Overlapping tree {} found in:\n'
                                 '{}\n{}.'.format(overlap,
                                                  Tree(self_root),
                                                  Tree(label_root)))

            self._children.add(label)
            self.update_descent()

            label.attach(self)

    def detach(self, *labels):
        """Detach one or a group of |Label| as self's parent or child.

        If a |Label| was never attached to self to begin with, it is silently ignored.

        Args:
            *labels (|Label|): A |Label| to be detached as either self's parent or self's child.

        """
        for label in labels:
            if label == self._parent:
                # If it is the parent we force remove it (by-passing the property which would lead to recursion)
                self._parent = None
                self.update_ancestry()
                label.detach(self)
            elif label in self._children:
                # If it is a child we force remove it (by-passing the property which would lead to recursion)
                self._children.remove(label)
                self.update_descent()
                label.detach(self)
            # If it is nothing we silently ignore it (thus ending the recursion)

    def __repr__(self):
        """Pythonic representation of the object."""
        return '{}(name={})'.format(self.__class__.__name__, self.name)

    def __str__(self):
        """Return the |Label| :attr:`name`."""
        return self.name

    def __hash__(self):
        """Return the python hash of the |Label| :attr:`name`."""
        if self._hash is None:
            self._hash = hash(self._name)
        return self._hash

    def __eq__(self, other):
        """Return whether two |Label| have the same name and id.

        Args:
            other (|Label|): Another |Label| to compare itself to.

        Returns:
            bool: ``True`` if ``other`` is a |Label| and have the same name as self, or is a :class:`str` which equals
            :attr:`name`.

        """
        try:
            return self.name == other.name
        except AttributeError:
            return self.name == other

    def __ne__(self, other):
        """Return whether two |Label| do not have the same name and id.

        Args:
            other (|Label|): Another |Label| to compare itself to.

        Returns:
            bool: ``True`` if ``other`` is not a |Label| or do not have the same name as self, or is a :class:`str`
            which does not equal :attr:`name`.

        """
        return not self == other

    def last_common_ancestor(self, other):
        """Return the *most downward* |Label| encountered in self and other :attr:`ancestors`.

        Args:
            other (|Label|): Another |Label| to compare ancestors with.

        Returns:
            |Label|: The `last common parent`_, or ``None`` if both |Label| share no family.


        .. _last common parent: https://en.wikipedia.org/wiki/Most_recent_common_ancestor

        """
        family = OrderedSet((self, ) + self._ancestors).intersection(OrderedSet((other, ) + other.ancestors))
        if family:
            family = sorted(family,
                            key=lambda x: ((self, ) + self._ancestors).index(x))
            return family[0]
        return None

    def clade(self, other):
        """Return the common `clade`_ enclosing both self and other.

        Args:
            other (|Label|): Another |Label| to compare ancestors with.

        Returns:
            |Tree|: A |Tree| rooted in self and other :meth:`last_common_ancestor`, effectively representing
            their common `clade`_, or ``None`` if both |Label| share no family.

        .. _clade: https://en.wikipedia.org/wiki/Clade

        """
        last_common_ancestor = self.last_common_ancestor(other)
        if last_common_ancestor is None:
            return None

        return Tree(last_common_ancestor, type='clade', enclosed=(self, other))

    def update_ancestry(self):
        """Update :attr:`ancestors` attribute alongside the label's `clade`_.

        .. _clade: https://en.wikipedia.org/wiki/Clade

        """
        if self.parent is None:
            self._ancestors = ()
        else:
            self._ancestors = (self.parent,) + self.parent.ancestors
        self._depth = len(self._ancestors)
        for child in self._children:
            child.update_ancestry()

    def update_descent(self):
        """Update :attr:`descendants` attribute alongside the label's ancestry."""
        self._descendants = {}
        for child in self._children:
            self._descendants[child.name] = child
            self._descendants.update(child.descendants)
        if self._parent is not None:
            self._parent.update_descent()
