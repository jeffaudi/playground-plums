.. _commons_taxonomy:

|Plums| Taxonomy
================

.. include:: ../include.rst

The Plums **taxonomy** module implements a *taxonomy* creation, modification and look-up API.

It mainly consists in 3 classes:

* The |Label| class which is the base class for all |Taxonomy| creation: it implements the actual tree logic and
  the creation API.
* The |Tree| class which is a reader/helper class to facilitate lookups, iterative walks and comparisons.
* The |Taxonomy| class which is a special kind of |Tree| with a fixed, virtual root to allow multiple rooted
  taxonomies.

The Taxonomy API
----------------
.. automodule:: playground_plums.commons
    :members: Taxonomy
    :undoc-members:
    :exclude-members: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
    :special-members: __eq__, __ne__, __contains__, __len__, __getitem__, __setitem__, __str__
    :show-inheritance:
    :member-order: bysource

.. automodule:: playground_plums.commons
    :members: Label
    :undoc-members:
    :exclude-members: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
    :special-members: __eq__, __ne__, __contains__, __len__, __getitem__, __setitem__, __str__, __hash__
    :show-inheritance:
    :member-order: bysource

Trees helper classes
--------------------

.. automodule:: playground_plums.commons
    :members: Tree
    :undoc-members:
    :exclude-members: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
    :special-members: __eq__, __ne__, __contains__, __len__, __getitem__, __setitem__, __str__
    :show-inheritance:
    :member-order: bysource

Taxonomies iterators
....................

.. automodule:: playground_plums.commons.data.taxonomy.iterator
    :members:
    :undoc-members:
    :exclude-members: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
    :special-members: __iter__, __next__
    :show-inheritance:
    :member-order: bysource

Taxonomies accessors
....................

.. automodule:: playground_plums.commons.data.taxonomy.accessor
    :members:
    :undoc-members:
    :exclude-members: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
    :special-members: __getitem__, __setitem__
    :show-inheritance:
    :member-order: bysource
