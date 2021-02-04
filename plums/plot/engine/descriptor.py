import re
import abc

import schema
import numpy as np
from ordered_set import OrderedSet

from plums.plot.engine.utils import dict_equal
from plums.plot.engine.color import Color
from plums.plot.engine.color.color_map import ColorMap, identity

_camel_to_snake_re1 = re.compile('(.)([A-Z][a-z]+)')
_camel_to_snake_re2 = re.compile('([a-z0-9])([A-Z])')


def _camel_to_snake(camel_cased_name):
    s1 = _camel_to_snake_re1.sub(r'\1_\2', camel_cased_name)
    return _camel_to_snake_re2.sub(r'\1_\2', s1).lower()


_continuous_schema = schema.Schema(
    schema.Or(
        schema.And((schema.Or(int, float), ), lambda x: len(x) == 2),
        ColorMap
    )
)

_categorical_schema = schema.Schema(
    schema.Or(
        {
            str: schema.Or(int,
                           float,
                           Color,
                           _continuous_schema,
                           {
                               str: schema.Or(int, float, Color, _continuous_schema)
                           })
        }, {})
)


class Descriptor(object, metaclass=abc.ABCMeta):
    """Abstract base class for all |Descriptor|.

    A |Descriptor| is a class used to extract relevant information from a collection of |Record|.

    More specifically, a |Descriptor| is used in two phases:

    * In a first time, optional internals are updated and/or accumulated over the entire collection of
      |RecordCollection| tuples. Those internals will be used to tailor the |Descriptor| to the description task
      specific context (*e.g.* like updating a range of possible value to later normalize or clip a property value).
    * In a second time, the descriptor is used to construct a new |RecordCollection| or a tuple of |RecordCollection|
      where each enclosed |Record| is added a named property containing the adequate description of the |Record|
      from a tuple of |RecordCollection|.

    Subclasses must override the two interfaces used to do so: :meth:`update(*record_collections) <update>` and
    :meth:`compute(*record_collections) <compute>` as well as the :meth:`reset` method and
    the :meth:`_make_interface` private method.

    Args:
        name (str): The |Descriptor| name.

    Attributes:
        name (str): The |Descriptor| name.

    """

    __interface_schema__ = schema.Schema(
        schema.Or(
            {
                'name': schema.Regex(r'^[(),a-zA-Z_ ]+$'),
                'type': 'categorical',
                'property': schema.Regex(r'^[a-z][a-z_]+[a-z]$'),
                'schema': _categorical_schema
            },
            {
                'name': schema.Regex(r'^[(),a-zA-Z_ ]+$'),
                'type': 'continuous',
                'property': schema.Regex(r'^[a-z][a-z_]+[a-z]$'),
                'schema': _continuous_schema
            }
        )
    )

    def __init__(self, name):
        self.name = name

    @property
    def property_name(self):
        """str: The |Record| inserted property name after :meth:`compute` call."""
        return '_'.join((_camel_to_snake(self.__class__.__name__), _camel_to_snake(self.name)))

    @property
    def __descriptor__(self):  # noqa: D401
        """dict: A dictionary which summarizes the internal state of the |Descriptor| instance.

        Keys:
            name (str): The descriptor name. Note that in some |Descriptor|, it conjointly designates the
                descriptor name **and** the name of the property read from each |Record| to describe it.
            property (str): The name of the property written out by the |Descriptor| in each |Record|.
            type (str): Either ``categorical`` or ``continuous``.
            schema (dict, tuple, ColorMap): For ``categorical`` descriptors, it must be a dict mapping each
                ``category name`` to its relevant value (*e.g.* its index or |Color|). For ``continuous`` descriptors,
                it must be a range description (*i.e.* either a ``(start, end)`` tuple or a object with a ``range``
                attribute like a |ColorMap|).

        See Also:
            For more information on how :attr:`__descriptor__` is constructed, please see :ref:`descriptor`.

        """
        interface = self._make_interface()
        interface.update({'name': self.name.title().replace('_', ' '), 'property': self.property_name})
        try:
            self.__interface_schema__.validate(interface)
        except schema.SchemaError as e:
            raise ValueError('Invalid __descriptor__ returned:\n'
                             '{}\n{}'.format(e.errors, e.autos))
        return interface

    def __repr__(self):
        """Return a python representation of the |Descriptor|."""
        return '{}(name={})'.format(self.__class__.__name__, self.name)

    def __str__(self):
        """Return the |Descriptor| representation."""
        return self.__repr__()

    def __eq__(self, other):
        """Return ``True`` if two |Descriptor| have the same attributes and class."""
        if self.__class__ == other.__class__:
            return dict_equal(self.__dict__, other.__dict__)
        return False

    def __ne__(self, other):
        """Return ``True`` if two |Descriptor| do not have the same attributes and class."""
        return not self == other

    @abc.abstractmethod
    def update(self, *record_collections):
        """Update internal values from |Record| descriptions.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| of which |Record| will be used to update
                internals.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def compute(self, *record_collections):
        """Construct new |RecordCollection| where each enclosed |Record| is added a named description property.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| used to construct new |RecordCollection| with
                described |Record|.

        Returns:
            (|RecordCollection|, ): A described |RecordCollection| tuple.

        """
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        """Reset |Descriptor| internals to factory values."""
        raise NotImplementedError

    @abc.abstractmethod
    def _make_interface(self):
        """Build a summary of hte internal state of the |Descriptor|.

        It is used as a unified interface for all descriptors to describe and explicit their description.

        As an example, for a typical |CategoricalDescriptor|, the interface dictionary would contain:

        * The |Descriptor| name
        * The |Descriptor| property name
        * The |Descriptor| type, *i.e.* ``'categorical'`` here
        * The category name to category index mapping.

        As for a typical |ContinuousDescriptor|, it would contain:

        * The |Descriptor| name
        * The |Descriptor| property name
        * The |Descriptor| type, *i.e.* ``'continuous'`` here
        * The value range.

        See Also:
            The :attr:`__descriptor__` for more information.

        Returns:
            dict: A valid |Descriptor| :attr:`__descriptor__`.

        """
        raise NotImplementedError


class CategoricalDescriptor(Descriptor):
    """A |Descriptor| used to extract a categorical property from a collection of |Record|.

    Args:
        name (str): The |Record| property to describe name.
        fetch_fn (Callable): Optional. Default to identity. An optional function applied to the |Record| property
            before it is counted in a category.

    Attributes:
        name (str): The |Record| property to describe name.

    """

    def __init__(self, name, fetch_fn=None):
        super(CategoricalDescriptor, self).__init__(name)
        self._categories = OrderedSet()
        self._fetch_fn = fetch_fn or identity

    def update(self, *record_collections):
        """Update the set of known categories from |Record| property :attr:`name` value.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| of which |Record| will be used to update
                set of known categories.

        """
        records = (record for record_collection in record_collections for record in record_collection)
        try:
            for record in records:
                self._categories.add(str(self._fetch_fn(getattr(record, self.name))))
        except AttributeError:
            raise ValueError('Invalid record property name: {} was not found in record.'.format(self.name))

    def compute(self, *record_collections):
        """Construct new |RecordCollection| where each enclosed |Record| is added a category number as a property.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| used to construct new |RecordCollection| with
                described |Record|.

        Returns:
            (|RecordCollection|, ): A described |RecordCollection| tuple.

        """
        for record_collection in record_collections:
            for record in record_collection:
                try:
                    record.properties[self.property_name] = \
                        self._categories.index(str(self._fetch_fn(getattr(record, self.name)))) + 0.5
                except AttributeError:
                    raise ValueError('Invalid record property name: {} was not found in record.'.format(self.name))
                except KeyError:
                    raise ValueError('Invalid record property value: '
                                     '{} is out of known property range of values.'.format(getattr(record, self.name)))
        return record_collections

    def reset(self):
        """Reset |CategoricalDescriptor| set of known categories to factory values."""
        self._categories = OrderedSet()

    def _make_interface(self):
        return {
            'type': 'categorical',
            'schema': {category: index + 0.5 for index, category in enumerate(self._categories)}
        }


class ContinuousDescriptor(Descriptor):
    """A |Descriptor| used to extract a continuous property from a collection of |Record| with an optional scaling.

    Args:
        name (str): The |Record| property to describe name.
        scale (tuple): Optional. Default to ``None``. If given, it must be an interval :math:`[a, b]` over which the
            extracted property will be scaled.
        data_range(tuple): Optional. Default to ``None``. If provided, it is used to initialise internal
            start and end values instead of ``(0, 0)``

    Attributes:
        name (str): The |Record| property to describe name.
        scale (tuple): An interval :math:`[a, b]` over which the extracted property will be scaled.

    """

    def __init__(self, name, scale=None, data_range=None, fetch_fn=None):
        super(ContinuousDescriptor, self).__init__(name)
        if data_range:
            self._start = data_range[0]
            self._end = data_range[1]
        else:
            self._start = float('Inf')
            self._end = -float('Inf')
        self._data_range = data_range
        self.scale = scale
        self._fetch_fn = fetch_fn or identity

    def update(self, *record_collections):
        """Update the know descriptor range from |Record| property :attr:`name` value.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| of which |Record| will be used to update
                set of known categories.

        """
        records = (record for record_collection in record_collections for record in record_collection)
        try:
            for record in records:
                property_ = self._fetch_fn(getattr(record, self.name))
                self._start = min(self._start, property_)
                self._end = max(self._end, property_)
        except AttributeError:
            raise ValueError('Invalid record property name: {} was not found in record.'.format(self.name))

    def compute(self, *record_collections):
        """Construct new |RecordCollection| where each enclosed |Record| is added the descriptor value as a property.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| used to construct new |RecordCollection| with
                described |Record|.

        Returns:
            (|RecordCollection|, ): A described |RecordCollection| tuple.

        """
        for record_collection in record_collections:
            for record in record_collection:
                try:
                    property_ = self._fetch_fn(getattr(record, self.name))
                    if property_ > self._end or property_ < self._start:
                        raise ValueError('Invalid record property value: '
                                         '{} is out of known property range '
                                         '[{}, {}].'.format(getattr(record, self.name), self._start, self._end))
                    if self.scale:
                        property_ = ((float(property_) - self._start) / (self._end - self._start)) * \
                                    (self.scale[1] - self.scale[0]) + self.scale[0]
                    record.properties[self.property_name] = property_
                except AttributeError:
                    raise ValueError('Invalid record property name: {} was not found in record.'.format(self.name))
        return record_collections

    def reset(self):
        """Reset |Descriptor| know descriptor range to factory values."""
        if self._data_range:
            self._start = self._data_range[0]
            self._end = self._data_range[1]
        else:
            self._start = float('Inf')
            self._end = -float('Inf')

    def _make_interface(self):
        return {
            'type': 'continuous',
            'schema': (self._start, self._end)
        }


class IntervalDescriptor(CategoricalDescriptor):
    """A |CategoricalDescriptor| used to extract a continuous property from a collection of |Record| into a category.

    Args:
        name (str): The |Record| property to describe name.
        n (int): Optional. Default to ``5``.The number of bins used to categorise the continuous property.
        data_range(tuple): Optional. Default to ``None``. If provided, it is used to initialise internal
            start and end values instead of ``(0, 0)``

    Attributes:
        name (str): The |Record| property to describe name.
        n (str): The number of bins used to categorise the continuous property.

    """

    def __init__(self, name, n=5, data_range=None, fetch_fn=None):
        super(CategoricalDescriptor, self).__init__(name)
        self.n = n
        if data_range:
            self._start = data_range[0]
            self._end = data_range[1]
        else:
            self._start = float('Inf')
            self._end = -float('Inf')
        self._data_range = data_range
        self._fetch_fn = fetch_fn or identity

    @property
    def _range(self):
        return self._end - self._start

    @property
    def _step(self):
        return max(round(self._range / float(self.n), 8), 1e-10)

    def _get_interval_bound(self, i):
        if i < self.n:
            return self._start + i * self._step
        elif i == self.n:
            return self._end
        else:
            raise IndexError('Out of bound index {} to get interval bound value.'.format(i))

    @property
    def _categories(self):
        return tuple('[{:.2f}, {:.2f}['.format(self._get_interval_bound(i), self._get_interval_bound(i + 1))
                     for i in range(self.n))

    def update(self, *record_collections):
        """Update the know descriptor range from |Record| property :attr:`name` value.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| of which |Record| will be used to update
                set of known categories.

        """
        records = (record for record_collection in record_collections for record in record_collection)
        try:
            for record in records:
                property_ = self._fetch_fn(getattr(record, self.name))
                self._start = min(self._start, property_)
                self._end = max(self._end, property_ + 1e-8)
        except AttributeError:
            raise ValueError('Invalid record property name: {} was not found in record.'.format(self.name))

    def compute(self, *record_collections):
        """Construct new |RecordCollection| where each enclosed |Record| is added a category number as a property.

        Args:
            *record_collections (|RecordCollection|): |RecordCollection| used to construct new |RecordCollection| with
                described |Record|.

        Returns:
            (|RecordCollection|, ): A described |RecordCollection| tuple.

        """
        for record_collection in record_collections:
            for record in record_collection:
                try:
                    property_ = self._fetch_fn(getattr(record, self.name))
                    if property_ > self._end or property_ < self._start:
                        raise ValueError('Invalid record property value: '
                                         '{} is out of known property range '
                                         '[{}, {}].'.format(getattr(record, self.name), self._start, self._end))
                    record.properties[self.property_name] = min(int((property_ - self._start) // self._step),
                                                                len(self._categories) - 1) + 0.5
                except AttributeError:
                    raise ValueError('Invalid record property name: {} was not found in record.'.format(self.name))

        return record_collections

    def reset(self):
        """Reset |Descriptor| know descriptor range to factory values."""
        if self._data_range:
            self._start = self._data_range[0]
            self._end = self._data_range[1]
        else:
            self._start = float('Inf')
            self._end = -float('Inf')


class Labels(CategoricalDescriptor):
    """Extract a categorical property from :attr:`~plums.commons.data.record.Record.labels`."""

    def __init__(self):
        super(Labels, self).__init__(name='labels', fetch_fn=self._fetch_fn)

    @staticmethod
    def _fetch_fn(labels):
        return ', '.join([str(e) for e in labels])


class Confidence(ContinuousDescriptor):
    """Extract a continuous property from :attr:`~plums.commons.data.record.Record.confidence`.

    Args:
        scale (tuple): Optional. Default to ``None``. If given, it must be an interval :math:`[a, b]` over which the
            extracted property will be scaled.

    """

    def __init__(self, scale=None):
        super(Confidence, self).__init__(name='confidence', scale=scale, data_range=(0, 1))


class IntervalConfidence(IntervalDescriptor):
    """Extract a interval property from :attr:`~plums.commons.data.record.Record.confidence`.

    Args:
        n (int): Optional. Default to ``5``.The number of bins used to categorise the continuous property.

    """

    def __init__(self, n=5):
        super(IntervalConfidence, self).__init__(name='confidence', data_range=(0, 1), n=n)


def _shoelace_formula(x, y):
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def _area(coordinates):
    coordinates = tuple(coordinates)
    outer = np.array(coordinates[0])
    inners = None
    if len(coordinates) > 1:
        inners = [np.array(coordinates[i]) for i in range(1, len(coordinates))]
    area = _shoelace_formula(outer[:, 0], outer[:, 1])
    if inners:
        for inner in inners:
            area -= _shoelace_formula(inner[:, 0], inner[:, 1])
    return area


class Area(ContinuousDescriptor):
    """Extract an area property from :attr:`~plums.commons.data.record.Record.coordinates`.

    Args:
        scale (tuple): Optional. Default to ``None``. If given, it must be an interval :math:`[a, b]` over which the
            extracted property will be scaled.

    """

    def __init__(self, scale=None):
        super(Area, self).__init__(name='coordinates', scale=scale, fetch_fn=_area)

    @property
    def __descriptor__(self):  # noqa: D401
        """dict: A dictionary which summarizes the internal state of the |Descriptor| instance.

        Keys:
            name (str): The descriptor name. Note that in some |Descriptor|, it conjointly designates the
                descriptor name **and** the name of the property read from each |Record| to describe it.
            property (str): The name of the property written out by the |Descriptor| in each |Record|.
            type (str): Either ``categorical`` or ``continuous``.
            schema (dict, tuple, ColorMap): For ``categorical`` descriptors, it must be a dict mapping each
                ``category name`` to its relevant value (*e.g.* its index or |Color|). For ``continuous`` descriptors,
                it must be a range description (*i.e.* either a ``(start, end)`` tuple or a object with a ``range``
                attribute like a |ColorMap|).

        See Also:
            For more information on how :attr:`__descriptor__` is constructed, please see :ref:`descriptor`.

        """
        interface = self._make_interface()
        interface.update({'name': 'Area', 'property': self.property_name})
        try:
            self.__interface_schema__.validate(interface)
        except schema.SchemaError as e:
            raise ValueError('Invalid __descriptor__ returned:\n'
                             '{}\n{}'.format(e.errors, e.autos))
        return interface


class IntervalArea(IntervalDescriptor):
    """Extract an area property from :attr:`~plums.commons.data.record.Record.coordinates`.

    Args:
        n (int): Optional. Default to ``5``.The number of bins used to categorise the continuous property.

    """

    def __init__(self, n=5):
        super(IntervalArea, self).__init__(name='coordinates', n=n, fetch_fn=_area)

    @property
    def __descriptor__(self):  # noqa: D401
        """dict: A dictionary which summarizes the internal state of the |Descriptor| instance.

        Keys:
            name (str): The descriptor name. Note that in some |Descriptor|, it conjointly designates the
                descriptor name **and** the name of the property read from each |Record| to describe it.
            property (str): The name of the property written out by the |Descriptor| in each |Record|.
            type (str): Either ``categorical`` or ``continuous``.
            schema (dict, tuple, ColorMap): For ``categorical`` descriptors, it must be a dict mapping each
                ``category name`` to its relevant value (*e.g.* its index or |Color|). For ``continuous`` descriptors,
                it must be a range description (*i.e.* either a ``(start, end)`` tuple or a object with a ``range``
                attribute like a |ColorMap|).

        See Also:
            For more information on how :attr:`__descriptor__` is constructed, please see :ref:`descriptor`.

        """
        interface = self._make_interface()
        interface.update({'name': 'Area', 'property': self.property_name})
        try:
            self.__interface_schema__.validate(interface)
        except schema.SchemaError as e:
            raise ValueError('Invalid __descriptor__ returned:\n'
                             '{}\n{}'.format(e.errors, e.autos))
        return interface
