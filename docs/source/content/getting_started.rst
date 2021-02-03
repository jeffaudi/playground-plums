.. _getting_started:

Getting started
===============

.. include:: ../include.rst

|Plums|

Welcome to *Plums* ! If you are here, it is probably because you work in the field of machine learning, more
specifically on aerial imagery with a strong geo-spatial bias, and you are tired of re-inventing the wheel every time
you start a new data science project or you would like for your team to work on a common ground so that sharing code and
working with other people is actually an *asset* and not a *hassle*. Well in that case, welcome to *Plums*.


What is Plums ?
---------------

Plums stands for the **PL**\ ayground **U**\ nified **M**\ icrolib **S**\ et, and it is a set of geo-spatial oriented
data science *Python* libraries originally built around the *Intelligence Playground* to make the lives of
data-scientists easier. But even more so *Plums* aims to be more of an development and team environment, and is built
as a collection of semi-independent libraries called **microlibs** built on a common data-model.


Installation
------------

Each *Plums* libraries are pip-installable from the Playground ML private *PyPI* repository.

For example, to install the *Plot* library:

.. code-block:: bash

    pip install --extra-index-url https://playground-ml:****@pypi-dot-theplayground-ml.appspot.com/pypi plums-plot

All libraries depend on the *Plums* base library which in turn only depends on **pure python** libraries (and is thus
safe to embed in light weight container images for example).

To install every microlibs in on-go, the base *Plums* package offers the convenient `all` extra keyword, as well as a
keyword every library.

For example to install the base and the *plot* and *dataflow* libraries, one may use:

.. code-block:: bash

    pip install --extra-index-url https://playground-ml:****@pypi-dot-theplayground-ml.appspot.com/pypi plum[plot, dataflow]

And to install everything:

.. code-block:: bash

    pip install --extra-index-url https://playground-ml:****@pypi-dot-theplayground-ml.appspot.com/pypi plum[all]

What's next ?
-------------

The base library :ref:`commons_quickstart` offers a quick glance at the *Plums* data-model and coding philosophy and
is a good start for new *Plums* users.
