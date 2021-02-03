|Plums|
=======

.. include:: include.rst

**PL**\ ayground **U**\ nified **M**\ icrolib **S**\ et : The **Playground ML** python *toolbox* package

.. image:: https://plums-dot-theplayground-ml.appspot.com/badges/python.svg
    :alt: pyversion

.. image:: https://plums-dot-theplayground-ml.appspot.com/badges/pydoc.svg
    :alt: pydoc

.. image:: https://plums-dot-theplayground-ml.appspot.com/badges/pystable.svg
    :alt: stable


The |PLumsTiny| library set aims to define a common set of library to be used by people involved in the PlaygroundML
team.

Those libraries puropose is to set a unique baseline to help make the code base more unified and avoid countless
reimplementation of the same tools which in turns make people waste time and make the code base hard to understand,
debug and reuse.

Because |PLumsTiny| aims to be a library **set**, it is organised in a microlib fashion where each individual library
lives in an independent repository added as a git *submodule*.

.. toctree::
   :maxdepth: 2
   :caption: Plums:

   content/getting_started
   content/quickstart
   content/datamodel

.. toctree::
   :maxdepth: 2
   :caption: Library guides:

   content/dataflow/index
   content/model/index
   content/plot/index

.. toctree::
   :maxdepth: 2
   :caption: References:

   api_doc/plums.commons.data
   api_doc/plums.commons.data.taxonomy
   api_doc/plums.commons.path
   api_doc/plums.dataflow.index
   api_doc/plums.model.index
   api_doc/plums.plot.index
