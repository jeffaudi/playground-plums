from copy import deepcopy
from collections import defaultdict

import ordered_set

from plums.plot.engine.descriptor import Descriptor
from plums.plot.engine.color import CategoricalColorMap, LightnessColorMap, Color
from plums.commons.data import RecordCollection


class CategoricalRecordCollection(RecordCollection):
    """Data model class which aggregates multiple |Record| together and split them according to a property value.

    It also implement list accessors and :meth:`append` to easily edit and access the |RecordCollection|.

    Args:
        monitored_property (str): The |Record| property to monitor for the collection split.
        *records (|Record|): |Record| instances to aggregate.

    Attributes:
        id (str): The |RecordCollection| id. If not provided in the constructor, it is automatically generated.
        records (list): Stored |Record| instances.

    """

    def __init__(self, monitored_property, *records, **kwargs):
        self._category_to_index = defaultdict(list)
        self._category_set = ordered_set.OrderedSet()
        super(CategoricalRecordCollection, self).__init__(*records, **kwargs)
        self._split(monitored_property)

    @property
    def categories(self):
        """set: The set of monitored categories found in the |RecordCollection|."""
        return self._category_set

    @classmethod
    def from_record_collection(cls, monitored_property, record_collection):
        """Create a |CategoricalRecordCollection| from a |RecordCollection|.

        Args:
            monitored_property (str): The |Record| property to monitor for the collection split.
            record_collection (|RecordCollection|): |RecordCollection| to split into a |CategoricalRecordCollection|.

        Returns:
            |CategoricalRecordCollection|: The resulting split collection.

        """
        return cls(monitored_property, *record_collection.records, id=record_collection.id)

    def _split(self, monitored_property):
        if self._category_to_index:
            raise ValueError('CategoricalRecordCollection was already split.')

        for i, record in enumerate(self.records):
            property_value = getattr(record, monitored_property)
            self._category_set.add(property_value)
            self._category_to_index[property_value].append(i)

    def __getitem__(self, item):
        """Access the i-th stored |Record| or the j-th stored |Record| from the i-th category.

        Returns:
            (|Record|, List[|Record|]): The specified |Record| instance or list of |Record|.

        Raises:
            IndexError: If ``index`` does is out of :attr:`records` range.

        """
        if isinstance(item, tuple):
            if len(item) > 2:
                raise IndexError('Invalid index provided: Expected at most 2 dimensions, got {}'.format(len(item)))

            if isinstance(item[0], slice):
                raise IndexError('Invalid index provided: First dimension does not support slice indexing.')

            if item[0] >= len(self.categories):
                return ()

            indices = self._category_to_index[self._category_set[item[0]]][item[1]]

            try:
                return [self.records[i] for i in indices]
            except TypeError:
                return self.records[indices]
        else:
            return super(CategoricalRecordCollection, self).__getitem__(item)

    @property
    def loc(self):
        """Access the i-th stored |Record| or the j-th stored |Record| from the ``category_key`` category.

        Returns:
            (|Record|, List[|Record|]): The specified |Record| instance or list of |Record|.

        Raises:
            IndexError: If ``index`` does is out of :attr:`records` range.

        """
        class _LocIndexer(object):
            def __init__(self, categorical_record_collection):
                self._collection = categorical_record_collection

            def __getitem__(self, item):
                if isinstance(item, tuple):
                    if len(item) > 2:
                        raise IndexError('Invalid index provided: Expected at most 2 dimensions, '
                                         'got {}'.format(len(item)))

                    if isinstance(item[0], slice):
                        raise IndexError('Invalid index provided: First dimension does not support slice indexing.')

                    return self._collection[self._collection.categories.index(item[0]), item[1]]
                else:
                    return self._collection[item]

            def __setitem__(self, key, value):
                if isinstance(key, tuple):
                    if len(key) > 2:
                        raise IndexError(
                            'Invalid index provided: Expected at most 2 dimensions, got {}'.format(len(key)))

                    if isinstance(key[0], slice):
                        raise IndexError('Invalid index provided: First dimension does not support slice indexing.')

                    self._collection[self._collection.categories.index(key[0]), key[1]] = value
                else:
                    self._collection[key] = value

        return _LocIndexer(self)

    def __setitem__(self, key, value):
        """Set the i-th stored |Record| or the j-th stored |Record| from the i-th category.

        Raises:
            IndexError: If ``index`` does is out of :attr:`records` range.

        """
        if isinstance(key, tuple):
            if len(key) > 2:
                raise IndexError('Invalid index provided: Expected at most 2 dimensions, got {}'.format(len(key)))

            if isinstance(key[0], slice):
                raise IndexError('Invalid index provided: First dimension does not support slice indexing.')

            indices = self._category_to_index[self._category_set[key[0]]][key[1]]

            try:
                for i, j in enumerate(indices):
                    self.records[j] = value[i]
            except TypeError:
                self.records[indices] = value
        else:
            super(CategoricalRecordCollection, self).__setitem__(key, value)


class ByCategoryDescriptor(Descriptor):
    """Wrapper class to split a given |Descriptor| interface calls along a set of categories.

    Args:
        monitored_property (str): The |Record| property to monitor for the collection and descriptor split.
        descriptor (|Descriptor|): A |Descriptor| to split along a set of categories.

    """

    def __init__(self, monitored_property, descriptor):
        if not _is_descriptor(descriptor):
            raise TypeError('Invalid argument: descriptor is expected to be a Descriptor')

        super(ByCategoryDescriptor, self).__init__(name=descriptor.__descriptor__['name'])
        self._descriptor = descriptor
        self._monitored_property = monitored_property
        self._per_category_descriptors = defaultdict(lambda: deepcopy(self._descriptor))

    @property
    def property_name(self):
        """str: The |Record| inserted property name after :meth:`compute` call."""
        return self._descriptor.property_name

    @property
    def type(self):
        """str: Either ``categorical`` or ``continuous``. The enclosed |Descriptor| type."""
        return self._descriptor.__descriptor__['type']

    def update(self, *record_collections):
        """Update internal values of category-split |Descriptor| from |Record| descriptions.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| of which |Record| will be used to update
                internals.

        """
        # Split RecordCollection per monitored category
        try:
            split_record_collections = \
                tuple(CategoricalRecordCollection.from_record_collection(self._monitored_property, record_collection)
                      for record_collection in record_collections)
        except AttributeError:
            raise ValueError('Invalid monitored record property name: {} was not found in record.'.format(self.name))

        # Accumulate total monitored category range
        categories = set()
        for record_collection in split_record_collections:
            categories.update(record_collection.categories)

        # Update each sub descriptor with the RecordCollection subsets
        for category in categories:
            record_subcollections = tuple(RecordCollection(*record_collection.loc[category, :],
                                                           id=record_collection.id)
                                          for record_collection in split_record_collections
                                          if record_collection.loc[category, :])
            self._per_category_descriptors[category].update(*record_subcollections)

    def compute(self, *record_collections):
        """Construct new |RecordCollection| where each enclosed |Record| is added a named description property.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| used to construct new |RecordCollection| with
                described |Record|.

        Returns:
            (|RecordCollection|, ): A described |RecordCollection| tuple.

        """
        # Split RecordCollection per monitored category
        try:
            split_record_collections = \
                tuple(CategoricalRecordCollection.from_record_collection(self._monitored_property, record_collection)
                      for record_collection in record_collections)
        except AttributeError:
            raise ValueError('Invalid monitored record property name: {} was not found in record.'.format(self.name))

        # Accumulate total monitored category range
        categories = set()
        for record_collection in split_record_collections:
            categories.update(record_collection.categories)

        # No categories implies empty record collections, then no need to add descriptor property
        if not categories:
            return record_collections

        # Delay init return tuple until we know its length
        record_collections_return = None

        # Compute each sub descriptor with the RecordCollection subsets
        for category in categories:
            sub_record_collections = tuple(RecordCollection(*record_collection.loc[category, :],
                                                            id=record_collection.id)
                                           for record_collection in split_record_collections
                                           if record_collection.loc[category, :])

            sub_record_collections_return = self._per_category_descriptors[category].compute(*sub_record_collections)

            # Init return tuple
            if record_collections_return is None:
                record_collections_return = [RecordCollection() for i in range(len(sub_record_collections_return))]

            # Concatenate RecordCollection subsets into a valid return tuple
            for i, sub_record_collection in enumerate(sub_record_collections_return):
                record_collections_return[i].records.extend(sub_record_collection.records)

        return tuple(record_collections_return)

    def reset(self):
        """Reset |Descriptor| internals to factory values."""
        self._per_category_descriptors = defaultdict(lambda: deepcopy(self._descriptor))

    def _make_interface(self):
        schema = {
            str(category): descriptor.__descriptor__['schema']
            for category, descriptor in self._per_category_descriptors.items()
        }

        return {
            'type': "categorical",
            'schema': schema
        }


def _is_descriptor(candidate):
    return hasattr(candidate, '__descriptor__') and \
        hasattr(candidate, 'update') and \
        hasattr(candidate, 'compute')


class ColorEngine(Descriptor):
    """A special |Descriptor| used to generate |Color| from one or two |Descriptor|.

    More specifically, a |ColorEngine| is used in two phases:

    * In a first time, enclosed |Descriptor| internals are updated and/or accumulated over the entire collection of
      |RecordCollection| tuples.
    * In a second time, the |ColorEngine| is used to construct a new |RecordCollection| where each enclosed |Record|
      is added a property called ``color`` containing a |Color| instance computed from the properties computed by the
      enclosed |Descriptor|.

    Args:
        main_descriptor (|Descriptor|): The principal |Descriptor|. It might be a *categorical* descriptor or a
            *continuous* descriptor, in which case no *secondary_descriptor* can be provided.
        secondary_descriptor (|Descriptor|): Optional. Default to None. A refinement |Descriptor|. It might be a
            *categorical* descriptor or a *continuous* descriptor.
        ctype (str): The color space the generated |Color| will live in (*e.g.* "sRGB255" or "JCh").

    """

    def __init__(self, main_descriptor, secondary_descriptor=None, ctype='sRGB255'):
        self._ctype = ctype

        if not _is_descriptor(main_descriptor):
            raise TypeError('Invalid argument: main_descriptor is expected to be a Descriptor')

        if secondary_descriptor is not None:
            if not _is_descriptor(secondary_descriptor):
                raise TypeError('Invalid argument: secondary_descriptor is expected to be a Descriptor')

            if main_descriptor.__descriptor__['type'] != 'categorical':
                raise TypeError('Invalid argument: main_descriptor is expected to be a CategoricalDescriptor')

        self._main_descriptor = main_descriptor
        self._secondary_descriptor = ByCategoryDescriptor(main_descriptor.property_name, secondary_descriptor) \
            if secondary_descriptor else secondary_descriptor

        self.__primary_color_map = None
        self.__secondary_color_map = None

        super(ColorEngine, self).__init__('color_engine({})'
                                          ''.format(', '.join([interface['name']
                                                               for interface in [self._main_interface,
                                                                                 self._secondary_interface]
                                                               if interface is not None])))

    @property
    def _primary_color_map(self):
        if self.__primary_color_map is None:
            self._make_color_maps()
        return self.__primary_color_map

    @_primary_color_map.setter
    def _primary_color_map(self, value):
        self.__primary_color_map = value

    @property
    def _secondary_color_map(self):
        if self.__primary_color_map is None:
            self._make_color_maps()
        return self.__secondary_color_map

    @_secondary_color_map.setter
    def _secondary_color_map(self, value):
        self.__secondary_color_map = value

    @property
    def _main_interface(self):
        return self._main_descriptor.__descriptor__

    @property
    def _secondary_interface(self):
        if self._secondary_descriptor:
            return self._secondary_descriptor.__descriptor__
        return None

    @property
    def property_name(self):
        """str: The |Record| inserted property name after :meth:`compute` call."""
        return 'color'

    @property
    def ctype(self):
        """str: The color space the |ColorMap| lives in (*e.g.* "sRGB255" or "JCh").

        See Also:
            For more information on valid color spaces, please see |Color|.

        """
        return self._ctype

    @ctype.setter
    def ctype(self, new_ctype):
        self._ctype = new_ctype
        self._primary_color_map.ctype = new_ctype
        if self._secondary_color_map is not None:
            for key, colormap in self._secondary_color_map.items():
                colormap.ctype = new_ctype

    def update(self, *record_collections):
        """Update the enclosed |Descriptor| from |Record| property :attr:`name` value.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| of which |Record| will be used to update the
                enclosed |Descriptor|.

        """
        self._main_descriptor.update(*record_collections)
        if self._secondary_descriptor is not None:
            self._secondary_descriptor.update(*self._main_descriptor.compute(*record_collections))

        self.__primary_color_map = None
        self.__secondary_color_map = None

    def compute(self, *record_collections):
        """Construct a new |RecordCollection| where each enclosed |Record| is added a |Color| as a property.

        Args:
            **record_collections (|RecordCollection|): |RecordCollection| used to construct new |RecordCollection| with
                described |Record|.

        Returns:
            (|RecordCollection|, ): A tuple containing one |RecordCollection| with colors.

        """
        record_collections = self._main_descriptor.compute(*record_collections)
        if self._secondary_descriptor is not None:
            record_collections = self._secondary_descriptor.compute(*record_collections)
        if len(record_collections) > 1:
            raise ValueError('Invalid description: Expected only one record collection is expected after running the '
                             'enclosed descriptors, got {}'.format(len(record_collections)))

        record_collection = record_collections[0]

        main_property = self._main_interface['property']
        secondary_property = self._secondary_interface['property'] if self._secondary_descriptor else None

        for record in record_collection:
            main_value = getattr(record, main_property)
            secondary_value = getattr(record, secondary_property) if secondary_property else None

            if secondary_value is not None:
                color = self._secondary_color_map[main_value].get_color(secondary_value)
            else:
                color = self._primary_color_map.get_color(main_value)

            record.properties['color'] = color

        return record_collection,

    def reset(self):
        """Reset |Descriptor| enclosed |Descriptor| to factory values."""
        self._main_descriptor.reset()
        if self._secondary_descriptor is not None:
            self._secondary_descriptor.reset()

        self.__primary_color_map = None
        self.__secondary_color_map = None

    def _make_interface(self):
        if self._secondary_descriptor is None:
            if self._main_interface['type'] == 'categorical':
                schema = {
                    key:
                        self._primary_color_map.get_color(self._main_interface['schema'][key])
                    for key in self._main_interface['schema'].keys()
                }
            else:
                schema = self._primary_color_map
        else:
            if self._secondary_descriptor.type == 'categorical':
                schema = \
                    {
                        key: {
                            s_key: self._secondary_color_map[value].get_color(
                                self._secondary_interface['schema'][str(value)][s_key]
                            )
                            for s_key in self._secondary_interface['schema'][str(value)].keys()
                        }
                        for key, value in self._main_interface['schema'].items()
                    }
            else:
                schema = {
                    key: self._secondary_color_map[value]
                    for key, value in self._main_interface['schema'].items()
                }

        return {
            'type': self._main_interface['type'],
            'schema': schema
        }

    def _make_secondary_color_map(self, color, category):
        if self._secondary_descriptor.type == 'categorical':
            cmap = LightnessColorMap(color,
                                     ctype=self.ctype,
                                     lightness_range=(0.5, 0.7),
                                     data_range=(0, len(self._secondary_interface['schema'][category].keys()) - 1))
            return cmap.discretize(len(self._secondary_interface['schema'][category].keys()) or 1)
        else:
            cmap = LightnessColorMap(color,
                                     ctype=self.ctype,
                                     lightness_range=(0.5, 0.7),
                                     data_range=self._secondary_interface['schema'][category]).discretize()
            return cmap

    def _make_color_maps(self):
        if self._main_interface['type'] == 'categorical':
            self._primary_color_map = CategoricalColorMap(len(self._main_interface['schema'].keys()) or 1,
                                                          ctype=self.ctype)

            _schema = self._main_interface['schema']

            if self._secondary_descriptor is not None:
                self._secondary_color_map = {
                    value: self._make_secondary_color_map(self._primary_color_map.get_color(_schema[key]), str(value))
                    for key, value in _schema.items()
                }

        if self._main_interface['type'] == 'continuous':
            self._primary_color_map = LightnessColorMap(Color(50, 78, 50, ctype='JCh'),
                                                        lightness_range=(0.8, 0.9),
                                                        chroma_range=(-0.3, -0.1),
                                                        data_range=self._main_interface['schema'],
                                                        ctype=self.ctype).discretize()
