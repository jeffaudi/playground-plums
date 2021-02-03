|Plums| Model
=============

.. include:: ../../include.rst

The Plums **model** package aims to offer a framework-agnostic model format specification
(the **P**\ lums **M**\ odel **F**\ ormat) along with its python representation and helper implementation to ease
integration into producer and consumer codebases.

It is composed of two complementary parts:

* An extensive *PMF* validation API, available through the high level |validate| python function and the low-level
  validation :ref:`validation_developer`.

  .. seealso::
      The *PMF* :ref:`pmf_spec` for more information on the *PMF* format.

* A *PMF* model creation and manipulation API, available through the :ref:`model` module and the |Model| class.

  .. seealso::
      The :ref:`quickstart` for a simple tutorial on python model creation and handling.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   quickstart
   plums_model_format
   