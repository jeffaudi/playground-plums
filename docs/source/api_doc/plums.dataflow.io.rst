I/O operation
=============

.. include:: ../include.rst

The Plums dataflow module implements a set of IO routine to ease and speed up opening images and json files.

The |TileIO| class and the |ptype|
----------------------------------

The main interface to open and manipulation images in Plums is tthe |TileIO| class. It allows loading images from
disk through a variety of backends (`TurboJPEG <https://github.com/loopbio/PyTurboJPEG>`_,
`Lycon <https://github.com/ethereon/lycon>`_, `OpenCV <https://opencv.org/>`_
and `Pillow <https://pillow.readthedocs.io/en/stable/>`_). It also adds explicit and native support for a variety of
color domain through the |ptype|, which acts as a declination of numpy's :class:`~numpy.dtype` for pixels.

As of now, the list of explicitly supported |ptype| is: |RGB|, |BGR|, |RGBA|, |BGRA|, and |GREY|.

Additional |ptype| may be created on the fly as long as they references existing channels.

.. autoclass:: playground_plums.dataflow.io.Tile
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

.. autoclass:: playground_plums.dataflow.io.ptype
    :members:
    :special-members: __eq__, __contains__
    :undoc-members:
    :show-inheritance:
    :member-order: bysource


Deserialize JSON with the fastest backend
-----------------------------------------

Plums dataflow allows fast JSON deserialization with additional backends on top of the standard :mod:`json`
library if they are available (`OrJSON <https://github.com/ijl/orjson>`_,
`RapidJSON <https://github.com/python-rapidjson/python-rapidjson>`_,
and `SimpleJSON <https://github.com/simplejson/simplejson>`_).

The use ordering is expected to reflect loading speed however, because the relative speed of backends is highly
dependent on data, it is recommended to benchmark all library for specific use-cases to select the best possible
backend.

.. automodule:: playground_plums.dataflow.io.json
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
