try:
    import collections.abc as abc_collections
except ImportError:
    import collections as abc_collections

from .base import GeoInterfaced
from .mixin import PropertyContainer
from .taxonomy import Taxonomy, Label, clean


class RecordCollection(GeoInterfaced):
    """Data model class which aggregates multiple |Record| together.

    It also implement list accessors and :meth:`append` to easily edit and access the |RecordCollection|.

    Args:
        *records (|Record|): |Record| instances to aggregate.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        taxonomy (|Taxonomy|): Optional. Default to ``None``. A |Taxonomy| describing the range of possible values
            one may expect as labels in the enclosed |Record|. If not provided a new implicit, "*flat*" |Taxonomy| will
            be constructed on the go.

    Attributes:
        id (str): The instance *uuid*.
        records (list): Stored |Record| instances.

    """

    def __init__(self, *records, **kwargs):
        # Init records list
        self.records = []

        # Init Taxonomy
        taxonomy = kwargs.pop('taxonomy', None)
        self._explicit_taxonomy = False
        self._taxonomy = Taxonomy()
        if taxonomy is not None:
            self.taxonomy = taxonomy

        # Add records to list
        for record in records:
            self.append(record)

        # Init
        super(RecordCollection, self).__init__(**kwargs)

    @property
    def taxonomy(self):
        """|Taxonomy|: The range of possible label values in the enclosed |Record| and their relationships.

        Warnings:
            The *setter* will iterate over **all** enclosed |Record| to assess that the proposed |Taxonomy| is
            compatible with the |RecordCollection|. This might be a *slow* operation.

        Raises:
            ValueError: If trying to set a |Taxonomy| incompatible with the enclosed :attr:`records`.

        .. versionadded:: 0.2.0

        """
        return self._taxonomy

    @taxonomy.setter
    def taxonomy(self, taxonomy):
        for record in self.records:
            taxonomy.validate(*record.labels)
            record.taxonomy = taxonomy

        self._explicit_taxonomy = True
        self._taxonomy = taxonomy

    def _update(self, record):
        """Update either the input |Record| or the :attr:`taxonomy`."""
        # If the record had a taxonomy, we reset it to avoid interferences
        # (The record is contextualized by the record collection).
        if getattr(record, 'taxonomy', None) is not None:
            record.taxonomy = None

        if self._explicit_taxonomy:
            self.taxonomy.validate(*record.labels)
            record.taxonomy = self.taxonomy
        else:
            new_labels = {Label(label.name) for label in set(record.labels) - self.taxonomy.root.descendants.keys()}
            self.taxonomy.root.add(*new_labels)

    def __getitem__(self, index):
        """Access the i-th stored |Record|.

        Returns:
            |Record|: The specified |Record| instance.

        Raises:
            IndexError: If ``index`` is out of :attr:`records` range.

        """
        return self.records[index]

    def __setitem__(self, index, record):
        """Set the i-th |Record|.

        Raises:
            IndexError: If ``index`` is out of :attr:`records` range.
            ValueError: If trying to set a |Record| incompatible with the enclosed :attr:`taxonomy`.

        """
        self._update(record)
        self.records[index] = record

    def __len__(self):
        """Return the number of stored |Record|."""
        return len(self.records)

    def get(self, max_depth=None):
        """Get |Record| and cap their :attr:`~plums.commons.data.record.Record.labels` to a maximum depth.

        See Also:
            The label :meth:`~plums.commons.data.record.Record.get_labels` method which handles the lifting.

        Args:
            max_depth (int, dict): Optional. Default to ``None``.

                * If an integer is provided, |Label| fetched through the attached :attr:`taxonomy` will be capped to
                  the provided maximum tree depth.
                * If a dictionary is provided, it must map :attr:`taxonomy` true-roots to a given integer
                  ``max_depth``. Missing true-root will be interpreted as non-capped.

        Returns:
            (|Label|, ): The |Record| labels as a tuple of |Label|.

        Raises:
            ValueError: If a ``max_depth`` is provided although :attr:`taxonomy` is also ``None``.
            IndexError: If ``index`` is out of :attr:`records` range.

        .. versionadded:: 0.2.0

        """
        class _DepthWiseRecordAccessor(object):
            """Get |Record| and optionally cap their labels to a maximum depth."""

            def __init__(self, record_collection, max_depth=None):
                self.record_collection = record_collection
                self.max_depth = max_depth

            def __getitem__(self, index):
                """Access the i-th stored |Record|.

                Returns:
                    |Record|: The specified |Record| instance.

                Raises:
                    ValueError: If a ``max_depth`` is provided although :attr:`taxonomy` is also ``None``.
                    IndexError: If ``index`` is out of :attr:`records` range.

                """
                if isinstance(index, slice):
                    output = []
                    for i in range(index.start or 0, index.stop or len(self.record_collection), index.step or 1):
                        record = self.record_collection[i]
                        output.append(Record(record.coordinates, record.get_labels(max_depth=self.max_depth),
                                             record.confidence, record.id, self.record_collection.taxonomy,
                                             **record.properties))
                    return output
                else:
                    record = self.record_collection[index]
                    return Record(record.coordinates, record.get_labels(max_depth=self.max_depth),
                                  record.confidence, record.id, self.record_collection.taxonomy,
                                  **record.properties)

        return _DepthWiseRecordAccessor(self, max_depth=max_depth)

    def append(self, record):
        """Append a |Record| to the stored records list.

        Args:
            record (|Record|): A |Record| to append to the collection.

        Raises:
            ValueError: If trying to append a |Record| incompatible with the enclosed :attr:`taxonomy`.

        """
        self._update(record)
        self.records.append(record)

    def to_geojson(self, style='GeoPaaS'):
        """Implement the object conversion into a valid GeoJSON mapping.

        Args:
            style (str): Either 'GeoPaaS' or 'export-service'. Control the GeoJSON representation properties format.

        Returns:
            dict: The GeoJSON representation of the |RecordCollection|.

        """
        return {
            'type': 'FeatureCollection',
            'features': [
                record.to_geojson(style=style) for record in self.records
            ]
        }


class Record(PropertyContainer, GeoInterfaced):
    """Data model class which represents a |Record|.

    It implements the :data:`__geo_interface__` and represents itself as a GeoJSON *Feature*.

    Args:
        coordinates (list, tuple): A GeoJSON-valid coordinate sequence describing the |Record| shape.
        labels (list, tuple): The |Record| labels as a sequence.
        confidence (float): Optional. Default to None. A |Record| confidence score.
        id (str): Optional. Default to a random *UUID4*. An id to store along the instance.
        **properties (Any): Additional properties to store alongside the |VectorMask|.

    Attributes:
        id (str): The instance *uuid*.
        taxonomy (|Taxonomy|): If not ``None``, a |Taxonomy| through which :attr:`labels` will be looked up.

            .. important::

                The optionally attached :attr:`taxonomy` is **only** used to fetch :attr:`labels` and any discrepancies
                between the taxonomy and the stored labels will be **silently swallowed** unless the |Record| and its
                |Taxonomy| are part of a |RecordCollection|. This is because a |Record| by itself is assumed to be
                context-agnostic and the ability to attach to a :attr:`taxonomy` is an implementation convenience
                but **not** a part of the **data-model**.

            .. versionadded:: 0.2.0

        coordinates (list, tuple): A GeoJSON-valid coordinate sequence describing the |Record| shape.
        confidence (float): The |Record| confidence score.
        properties (dict): Additional properties stored alongside the |Record|.

            Warnings:
                The :attr:`properties` attribute does not corresponds to the GeoJSON representation properties which
                also include the :attr:`labels` and the :attr:`confidence` score.

    """

    def __init__(self, coordinates, labels, confidence=None, id=None, taxonomy=None, **properties):
        if not labels:
            raise ValueError('Expected at least 1 label, got: {}'.format(len(labels)))

        super(Record, self).__init__(id=id, **properties)
        self.labels = labels
        self.taxonomy = taxonomy
        self.confidence = confidence
        self.coordinates = coordinates
        self.properties = properties

    @property
    def labels(self):
        """(|Label|, ): The |Record| labels as a tuple of |Label|.

        If a |Taxonomy| is attached to the |Record|, the |Label| returned are fetched through the attached |Taxonomy|.

        .. versionchanged:: 0.2.0

        """
        if self.taxonomy is None:
            return self._labels
        return tuple(self.taxonomy[label] for label in self._labels)

    @labels.setter
    def labels(self, labels):
        self._labels = tuple(Label(str(label)) for label in labels)

    @property
    def type(self):
        """str: Either "Point" or "Polygon", it is computed according to the ``coordinates`` structure."""
        if isinstance(self.coordinates[0], abc_collections.Sized):
            return 'Polygon'
        else:
            return 'Point'

    def get_labels(self, max_depth=None):
        """Get the record :attr:`labels` and optionally cap them to a maximum depth.

        .. hint::

            The way max_depth provided are interpreted depends on what was provided:

                * If an integer, the whole |Taxonomy| is taken into account and ``0`` corresponds to ``__root__``
                  whereas ``1`` corresponds to the |Taxonomy| *true-roots*.
                * If a dictionary, the corresponding true-root *sub-trees* are taken into account and ``0``
                  corresponds to the *true-root* whereas ``1`` is the *first level underneath it*.

        Args:
            max_depth (int, dict): Optional. Default to ``None``.

                * If an integer is provided, |Label| fetched through the attached :attr:`taxonomy` will be capped to
                  the provided maximum tree depth.
                * If a dictionary is provided, it must map :attr:`taxonomy` true-roots to a given integer ``max_depth``.
                  Missing true-root will be interpreted as non-capped.

        Returns:
            (|Label|, ): The |Record| labels as a tuple of |Label|.

        Raises:
            ValueError: If a ``max_depth`` is provided although :attr:`taxonomy` is also ``None``.

        .. versionadded:: 0.2.0

        """
        # If not taxonomy and no depth are provided, fail silently and returns what we do know.
        if self.taxonomy is None:
            if max_depth is not None:
                raise ValueError('Invalid arguments: No taxonomy exists for this record but a max_depth was provided.')
            return self._labels

        if isinstance(max_depth, abc_collections.MutableMapping):
            output = []
            for label in self._labels:
                patriarch = ((label, ) + self.taxonomy.ancestors(self.taxonomy[label]))[-2]
                root_tree = self.taxonomy.properties[clean(patriarch.name)]
                output.append(root_tree.get(max_depth=max_depth.get(patriarch)).name[label])

            return output

        return tuple(self.taxonomy.get(max_depth=max_depth).name[label] for label in self._labels)

    def to_geojson(self, style='GeoPaaS'):
        """Implement the object conversion into a valid GeoJSON mapping.

        Args:
            style (str): Either 'GeoPaaS' or 'export-service'. Control the GeoJSON representation properties format.

        Returns:
            dict: The GeoJSON representation of the |Record|.

        """
        if style == 'GeoPaaS':  # TODO: Check w/ Playground label format
            label_key = 'category'

            def label_fn(labels):
                return [str(name) for name in labels]

            confidence_key = 'confidence'
        elif style == 'export-service':
            label_key = 'tags'

            def label_fn(labels):
                return ','.join([str(name) for name in labels])  # noqa: E731

            confidence_key = 'score'
        else:
            raise ValueError('Invalid style: Expected "GeoPaaS" or "export-service", got {}'.format(style))

        prop_dict = {
            label_key: label_fn(self.labels),
            confidence_key: self.confidence
        }

        prop_dict.update(self.properties)

        return {
            'type': 'Feature',
            'geometry': {
                'type': self.type,
                'coordinates': self.coordinates
            },
            'properties': prop_dict
        }
