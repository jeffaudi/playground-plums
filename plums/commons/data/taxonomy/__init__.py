import re

from .label import Label
from .tree import Tree


def clean(name):
    """Clean a :class:`str` into a valid variable name.

    Examples:
        >>> clean(' 32v2 g #Gmw845h$W b53wi ')
        'v2_g__Gmw845h_W_b53wi_'

    Args:
        name (str): A string to be cleaned.

    Returns:
        str: A string containing a valid variable name extracted from ``name``.

    Raises:
        ValueError: If name is only composed numbers or other invalid characters.

    """
    if re.match(r'^[^a-zA-Z_]+$\Z', name) is not None:
        raise ValueError('Invalid name: {} is only composed of invalid character and can not be cleaned.')

    # Remove uppercase
    name = name.lower()
    # Remove leading characters until we find a letter or underscore
    name = re.sub('^[^a-zA-Z_]+', '', name)
    # Remove invalid characters
    name = re.sub('[^0-9a-zA-Z_]', '_', name)

    return name


class Taxonomy(Tree):
    """A complete |Label| taxonomy, defined as a set of |Label| trees.

    .. hint::
        To allow an arbitrary number of roots whilst preserving a valid tree structure, an artificial root called
        ``__root__`` is added as the tree's top root |Label| which will *not* be printed out.

    A |Taxonomy| defines hierarchical dependencies between |Label| and in effect defines sets of |Label| as subsets of
    higher-ranked |Label|.

    For example, consider the following |Taxonomy|::

        ├── meat
        │   ├── bacon
        │   ╰── canned-meat
        │       ╰── spam
        ╰── eggs
            ╰── scrambled-eggs

    It can be interpreted as follow:

    * *bacon* and *canned-meat* are defined as special sorts of *meat*
    * *spam* is defined as a special sort of *canned-meat*
    * *scrambled-eggs* are defined as a special sort of *eggs*.

    That is to say that the following can be said:

    * Everything which is a *spam* **is** a *canned-meat* and **is** a *meat*, **but not the reciprocal**.

    Moreover, because taxonomies are a form of *knowledge model*, their are not expected to be *exhaustive*, *e.g.*
    something could be a *meat* but be neither a *bacon* nor a *canned-meat*.

    .. important::
        Taxonomies express what we *know* of a domain but not the *reality of the domain itself*.

    Note that *eggs* and *meat* are defined as **unrelated** concepts with no prior knowledge of any relations they
    might have.

    To go even further, the fact that they both are *true roots* implies that they define different kind of *concepts*
    which are not assumed to be comparable. For example, one could be a *type* and the other a *color*.

    .. note::
        Because of implementation specific reasons, *Plums* imposes stricter unity requirements on |Label| names
        than would technically be adequate. Indeed, because *eggs* and *meat* are assumed to be different and
        **unrelated** concepts, it should be acceptable to have a *raw* being a sort of *eggs* and another type of
        *raw* being a sort of *meat*; however, this is prohibited in *Plums*.

    Those relationships allow for set-aware |Label| lookups (as in :meth:`~plums.commons.Tree.get` or
    :meth:`~plums.commons.Tree.__getitem__`), tree iteration (as in
    :meth:`~plums.commons.Tree.iterate`) and |Label| tuple validation against self's taxonomy.

    Creation of |Taxonomy| is made with the |Label| class which acts as |Tree| nodes. For example, to recreate the
    example from above, one could do:

    .. code-block:: python

        >>> meat = Label('meat')
        >>> bacon = Label('bacon', parent=meat)
        >>> canned_meat = Label('canned-meat', parent=meat)
        >>> spam = Label('spam', parent=canned_meat)
        >>> eggs = Label('eggs')
        >>> scrambled_eggs = Label('scrambled-eggs', parent=eggs)
        >>> taxonomy = Taxonomy(meat, eggs)
        >>> print(taxonomy)
        ├── meat
        │   ├── bacon
        │   ╰── canned-meat
        │       ╰── spam
        ╰── eggs
            ╰── scrambled-eggs

    For more information on |Tree| creation, see the |Label| class API documentation.

    Once the |Taxonomy| is created, apart from the usual |Tree| interfaces, the |Taxonomy| instance exposes every
    *true-roots* |Tree| as attributes and :attr:`~plums.commons.PropertyContainer.properties`:

    .. code-block:: python

        >>> print(taxonomy.meat)
        meat
        ├── bacon
        ╰── canned-meat
            ╰── spam
        >>> print(taxonomy.properties['eggs'])
        eggs
        ╰── scrambled-eggs
        >>> taxonomy.eggs
        Tree(root=Label(name=eggs))

    Args:
        *labels (|Label|): A set of |Label| used as *true roots* for every trees.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |Tree|.

    """

    def __init__(self, *labels, **properties):
        # Names validity sanity check
        for root in labels:
            clean(root.name)

        root = Label('__root__')
        if labels:
            # Detach any previous Taxonomy roots
            for candidates in labels:
                if candidates.ancestors:
                    if candidates.ancestors[-1] == root:
                        candidates.ancestors[-1].detach(candidates)

            # Add new Taxonomy root
            root.add(*labels)
        id = properties.pop('id', None)
        super(Taxonomy, self).__init__(root, id=id, **properties)

    @property
    def properties(self):  # noqa: D401
        """dict: Properties provided as kwargs in the constructor to which are added every *true-roots*."""
        properties = super(Taxonomy, self).properties
        try:
            children = super(Taxonomy, self).__getattribute__('_label').children
        except AttributeError:
            pass
        else:
            _roots = set(children)
            # Cleanup legacy true roots
            for key, value in properties.items():
                if isinstance(value, Tree) and value.root not in _roots:
                    del properties[key]
            properties.update({clean(root.name): Tree(root) for root in _roots})
        return properties

    def __getstate__(self):
        """Return a dictionary of all slotted and in dictionary attributes."""
        dct = {key: value for key, value in self.__dict__.items()}

        for key in self.__all_slots__:
            if self._is_dunder(key):
                continue
            if key == '_properties':
                properties = self._get_slot(key)
                dct[key] = {key: value for key, value in properties.items() if not isinstance(value, Tree)}
            else:
                dct[key] = self._get_slot(key)

        return dct

    def validate(self, *labels):
        """Validate a tuple of |Label| against a |Taxonomy|.

        A tuple is deemed valid if:

        * Each |Label| exists in the |Taxonomy|.
        * Each |Label| is a member of a different *true-root* sub-tree.
        * There are no more |Label| than *true-roots*. This is a corollary of the former point.

        Args:
            *labels (|Label|): A group of |Label| to validate **together**.

        Returns:
            dict: A dictionary of :code:`{label: true-root}` mapping each |Label| to its corresponding true-root.

        Raises:
            ValueError: If the tuple is invalid. The reason is given in the error message.

        """
        if not labels:
            raise ValueError('Invalid label tuple: Empty tuple.')

        if len(labels) > len(self.depth_wise[1]):
            raise ValueError('Invalid label tuple: Expected at most {} labels, got '
                             '{}.'.format(len(self.depth_wise[1]), len(labels)))

        if len(set(labels) & self._label.descendants.keys()) != len(labels):
            raise ValueError('Invalid label tuple: {} are not part of the '
                             'taxonomy.'.format(set(labels) - self._label.descendants.keys()))

        true_roots = set(self.depth_wise[1])
        for label_ in labels:
            label_ = self[label_]
            if ((label_, ) + self.ancestors(label_))[-2] not in true_roots:
                raise ValueError('Invalid label tuple: Some labels are part of the same true-root subtree: '
                                 '{} is not a part of {} subtrees but '
                                 '{} subtree.'.format(label_,
                                                      true_roots,
                                                      ((label_, ) + self.ancestors(label_))[-2]))
            true_roots.remove(((label_, ) + self.ancestors(label_))[-2])
