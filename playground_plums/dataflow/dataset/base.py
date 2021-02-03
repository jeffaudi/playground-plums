from bisect import bisect
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence

import numpy as np


# If PyTorch exists in the current python environment, we make Plums dataset as explicit subclasses to allow
# type-check pass and robust compatibility.
class Dataset(object, metaclass=ABCMeta):
    """Abstract base class for all |Dataset| to inherit from.

    Subclasses must override the :meth:`__getitem__` method to allow |Dataset| to act as a 'non-sized'
    :class:`~collection.abc.Sequence`.

    Although subclasses **should** override the len method, it is deliberately not implemented by default to assert
    valid behaviour with non-sized samplers. If one wants to explicitly signal that the :meth:`__len__` *is* or
    *should be* present in subclasses, use the |SizedDataset| base class instead.

    .. hint::

        Insightful users might notice that the base dataset API closely mimics PyTorch's own
        :class:`~torch.utils.data.Dataset` and Keras's :class:`~tf.keras.utils.Sequence`. This is deliberate so that
        the provided |Dataset| can be used as a stand-in (with some care needed to support
        :meth:`~tf.keras.utils.Sequence.on_epoch_end` callback on the Keras side though). However, to keep class
        inheritance clean and simple, |Dataset| will fail on :func:`isinstance` checks as they only share interfaces
        (duck-typing) with their framework counterparts.

    """

    @abstractmethod
    def __getitem__(self, item):
        """Fetch an indexed item from the |Dataset|.

        Args:
            item (int, Hashable): A valid index for the |Dataset|. Integer are the preferred way to index entries but
                dataset may optionally support map-like index with hashable keys.

        Returns:
            Any: A |Dataset| data-point element.

        """
        raise NotImplementedError

    # Although subclasses SHOULD override the len method, it is deliberately not implemented by default to assert
    # valid behaviour with non-sized samplers. If one wants to explicitly signal that the len is or should be present,
    # use the SizedDataset base class instead.
    # @abstractmethod
    # def __len__(self):  # noqa: E800
    #     raise NotImplementedError


class SizedDataset(Dataset, metaclass=ABCMeta):
    """Abstract base class for all |Dataset| with a known length to inherit from.

    Subclasses must override the :meth:`__getitem__` and :meth:`__len__` methods to allow |Dataset| to act as a
    regular :class:`~collection.abc.Sequence`.

    """

    @abstractmethod
    def __getitem__(self, item):
        """Fetch an indexed item from the |Dataset|.

        Args:
            item (int, Hashable): A valid index for the |Dataset|. Integer are the preferred way to index entries but
                dataset may optionally support map-like index with hashable keys.

        Returns:
            Any: A |Dataset| data-point element.

        """
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        """Return the dataset's number of data-points."""
        raise NotImplementedError

    def __add__(self, other):
        """Concatenate the dataset with another dataset.

        Note:

            No explicit type check is performed on other, which means that technically, any sequence-like object is
            *concatenable* with a dataset.

        Returns:
            |ConcatDataset|: The concatenation of self and another dataset.

        """
        try:
            return ConcatDataset(self, other)
        except (AttributeError, TypeError):
            return NotImplemented

    def cat(self, datasets, *additional_datasets):
        """Concatenate the dataset with any other dataset.

        Args:
            datasets (Sequence[Dataset], Dataset): Either a sequence of datasets or a single dataset to concatenate with
                self.
            *additional_datasets (Dataset): Datasets to concatenate with self.

        Returns:
            |ConcatDataset|: The concatenation of self and other datasets.

        """
        return ConcatDataset(self, datasets, *additional_datasets)


class Subset(SizedDataset):
    """Create a subset of a |Dataset| from a |Dataset| to wrap and a selector container.

    Providing a list of indices is the preferred way to select a subset but any sequence-like or mapping-like object
    may work.

    Args:
        dataset (Dataset): A |Dataset| to wrap as a subset.
        indices (Sequence, Mapping): A selector container, mapping the subset items to the |Dataset| items.

    """

    def __init__(self, dataset, indices):
        self.dataset = dataset
        self.indices = indices

    def __getitem__(self, item):
        """Fetch an indexed item from the registered subset of the enclosed |Dataset|.

        Args:
            item (int, Hashable): A valid index for the :attr:`indices` selector container. Integer are the preferred
                way to index entries but dataset may optionally support map-like index with hashable keys.

        Returns:
            Any: A data-point element from the enclosed |Dataset|.

        """
        return self.dataset[self.indices[item]]

    def __len__(self):
        """Return the subset's length."""
        return len(self.indices)


class ConcatDataset(SizedDataset):
    """Create a |Dataset| as the concatenation of multiple |Dataset|.

    The concatenation involves no copy of any sort as the reindexing happens *on-the-fly* in the :meth:`__getitem__`
    method.

    Warnings:
        An explicit |Dataset| type check is performed on ``datasets`` to sort out the provided argument correct
        signature. If using the class with non-plums datasets (as it may happen implicitly with dataset addition),
        ensure that the argument or either in the correct order to pass the type check or that one uses the
        non-expended form to avoid ambiguities.

    Args:
        datasets (Sequence[Dataset], Dataset): Either a sequence of datasets or a single dataset to concatenate with
            self.
        *additional_datasets (Dataset): Datasets to concatenate with self.

    Raises:
        ValueError: If no dataset or an empty dataset is provided in the constructor's arguments.

    Attributes:
        cumulative_size (tuple): A tuple of the cumulative length of all enclosed |Dataset|.

    """

    def __init__(self, datasets, *additional_datasets):
        if not datasets:
            raise ValueError("'datasets' is expected to be either a Dataset or a non empty iterable of Datasets.")

        if isinstance(datasets, Dataset):
            datasets = (datasets, )
        else:
            if not isinstance(datasets, Sequence):
                raise TypeError('{} object is not iterable'.format(type(datasets)))

        self.datasets = tuple(datasets) + tuple(additional_datasets)
        self.cumulative_size = tuple(np.cumsum([len(dataset) for dataset in self.datasets]).tolist())

    def __getitem__(self, item):
        """Fetch an indexed item from the concatenated |Dataset|.

        The |Dataset| selection is computed *on-the-fly* from the requested item.

        Warnings:
            |ConcatDataset| expects integer items an will fail on mapping-like datasets.

        Args:
            item (int): A valid numerical index for enclosed |Dataset|.

        Returns:
            Any: A data-point element from the enclosed |Dataset|.

        """
        if item == len(self):
            raise IndexError('Dataset index is out of range')

        if abs(item) > len(self):
            raise IndexError('Dataset index is out of range')

        if item < 0:
            item += len(self)

        dataset_item = bisect(self.cumulative_size, item)
        dataset_length = self.cumulative_size[dataset_item - 1] if dataset_item > 0 else 0

        return self.datasets[dataset_item][item - dataset_length]

    def __len__(self):
        """Return the sum of all enclosed |Dataset| length."""
        return self.cumulative_size[-1]
