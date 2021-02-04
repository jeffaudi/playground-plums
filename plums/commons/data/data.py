from warnings import warn
from collections import OrderedDict

from .base import GeoInterfaced
from .mixin import IdentifiedMixIn, PropertyContainer
from .tile import Tile, TileCollection


class DataPoint(PropertyContainer, IdentifiedMixIn):
    """Data model class which aggregates a |Tile| and an |Annotation|, as well as additional properties.

    Args:
        tiles (OrderedDict[|Tile|]): The data-point's tiles as an ordered mapping (See |TileCollection|).
        annotation (|Annotation|): The data-point's annotation.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |DataPoint|.

    Attributes:
        id (str): The instance *uuid*.
        tiles (|TileCollection|): The stored data-point's tiles as an ordered mapping.
        annotation (|Annotation|): The stored data-point's annotation
        properties (dict): Properties provided as kwargs in the constructor.

    """

    def __init__(self, tiles, annotation, id=None, **properties):
        super(DataPoint, self).__init__(id=id, **properties)

        if isinstance(tiles, Tile):
            warn("Feeding a single tile as 'tiles' is deprecated and will be removed in version 0.5.0. "
                 "Use an ordered mapping instead as it supersedes the previous single tile usage.", DeprecationWarning)
            tiles = TileCollection(tiles)

        if not isinstance(tiles, OrderedDict):
            raise TypeError('Expected an ordered dictionary like object as tiles.')

        if not isinstance(annotation, GeoInterfaced):
            raise TypeError('Expected "annotation" to expose the __geo_interface__ attribute')

        self.tiles = TileCollection(*tiles.items())
        self.annotation = annotation

    @property
    def tile(self):
        """|Tile|: The first tile in the :attr:`tiles` collection."""
        warn("The 'tile' attribute is deprecated and will be removed in version 0.5.0. "
             "Use the 'tiles' ordered mapping instead as it supersedes 'tile'.", DeprecationWarning)
        return self.tiles.iloc[0]


class Annotation(PropertyContainer, IdentifiedMixIn):
    """Data model class which aggregates a |RecordCollection| and an |MaskCollection|, as well as additional properties.

    Args:
        record_collection (|RecordCollection|): The annotation's record collection.
        mask_collection (|MaskCollection|): The annotation's mask collection.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |DataPoint|.

    Attributes:
        id (str): The instance *uuid*.
        record_collection (|RecordCollection|): The stored annotation's record collection.
        mask_collection (|MaskCollection|): The stored annotation's mask collection.
        properties (dict): Properties provided as kwargs in the constructor.

    """

    def __init__(self, record_collection, mask_collection=None, id=None, **properties):
        super(Annotation, self).__init__(id=id, **properties)
        if not isinstance(record_collection, GeoInterfaced):
            raise TypeError('Expected "record_collection" to expose the __geo_interface__ attribute')

        self.record_collection = record_collection
        self.mask_collection = mask_collection

    def __getitem__(self, item):
        """Return a record from the stored |RecordCollection|."""
        return self.record_collection[item]

    @property
    def __geo_interface__(self):  # noqa: D401
        """dict: The stored |RecordCollection| :data:`__geo_interface__` property."""
        return self.record_collection.__geo_interface__
