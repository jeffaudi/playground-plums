|Plums| Plot API Doc
====================

.. include:: ../include.rst

You will find the API Doc for each module in Plums plot below.

.. toctree::
   :maxdepth: 2
   :caption: User API:

   plums.plot.plot
   plums.plot.descriptor.user

The *User* API exposes a set of pre-defined high level constructors and utils aimed at allowing easy and fast
visualisation generation at the expense of possible customisations. It should be the preferred API for normal day-to-day
use.

.. toctree::
   :maxdepth: 2
   :caption: Developer API:

   plums.plot.orchestrator
   plums.plot.descriptor.dev
   plums.plot.compositor
   plums.plot.legend_painter
   plums.plot.painter
   plums.plot.color.colormap

The *Developer* API exposes the inner workings of the *User* API. As such, it is easy to customize to a surprising
extend although it is significantly less trivial to use. Nonetheless, it offers powerful capabilities and it might
come handy for iconoclast visualisation which fall outside the *User* API intended purpose.
