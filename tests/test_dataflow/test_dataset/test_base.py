import pytest
import numpy as np

from plums.dataflow.dataset import Dataset, SizedDataset, Subset, ConcatDataset


class ConcreteDataset(Dataset):
    def __init__(self, array):
        self.array = array

    def __getitem__(self, item):
        return self.array[item]


class ConcreteSizedDataset(SizedDataset):
    def __init__(self, array):
        self.array = array

    def __getitem__(self, item):
        return self.array[item]

    def __len__(self):
        return len(self.array)


class ArrayDataset(SizedDataset):
    def __init__(self, *arrays):
        assert all(arrays[0].shape[0] == array.shape[0] for array in arrays)
        self.arrays = arrays

    def __getitem__(self, index):
        return tuple(array[index] for array in self.arrays)

    def __len__(self):
        return self.arrays[0].shape[0]


def test_abstract():
    with pytest.raises(TypeError):
        _ = Dataset()

    with pytest.raises(TypeError):
        _ = SizedDataset()


def test_subset():
    dataset = ConcreteDataset([1, 2, 3, 4, 5, 6])

    subset = Subset(dataset, [1, 3, 5])
    assert len(subset) == 3

    with pytest.raises(TypeError):
        len(dataset)

    assert dataset[0] == 1
    assert subset[0] == 2
    assert dataset[2] == 3
    assert subset[2] == 6

    assert dataset[3] == 4
    with pytest.raises(IndexError):
        _ = subset[3]

    dataset = ConcreteSizedDataset([1, 2, 3, 4, 5, 6])

    subset = Subset(dataset, [1, 3, 5])
    assert len(dataset) == 6
    assert len(subset) == 3

    assert dataset[0] == 1
    assert subset[0] == 2
    assert dataset[2] == 3
    assert subset[2] == 6

    assert dataset[3] == 4
    with pytest.raises(IndexError):
        _ = subset[3]


class TestConcatDataset:
    def test_concat_two_singletons(self):
        result = ConcatDataset([[0], [1]])
        assert len(result) == 2
        assert result.cumulative_size == (1, 2)
        assert result[0] == 0
        assert result[1] == 1
        assert result[0] == result[-2]

        result = ConcatDataset(ConcreteSizedDataset([0]), [1])
        assert len(result) == 2
        assert result.cumulative_size == (1, 2)
        assert result[0] == 0
        assert result[1] == 1
        assert result[0] == result[-2]

    def test_concat_two_non_singletons(self):
        result = ConcatDataset([[0, 1, 2, 3, 4],
                                [5, 6, 7, 8, 9]])
        assert len(result) == 10
        assert result.cumulative_size == (5, 10)
        assert result[0] == 0
        assert result[5] == 5
        assert result[0] == result[-10]

        result = ConcatDataset(ConcreteSizedDataset([0, 1, 2, 3, 4]),
                               [5, 6, 7, 8, 9])
        assert len(result) == 10
        assert result.cumulative_size == (5, 10)
        assert result[0] == 0
        assert result[5] == 5
        assert result[0] == result[-10]

    def test_concat_two_non_singletons_with_empty(self):
        # Adding an empty dataset somewhere is correctly handled
        result = ConcatDataset([[0, 1, 2, 3, 4],
                                [],
                                [5, 6, 7, 8, 9]])
        assert len(result) == 10
        assert result.cumulative_size == (5, 5, 10)
        assert result[0] == 0
        assert result[5] == 5
        assert result[0] == result[-10]

        result = ConcatDataset(ConcreteSizedDataset([0, 1, 2, 3, 4]),
                               [],
                               [5, 6, 7, 8, 9])
        assert len(result) == 10
        assert result.cumulative_size == (5, 5, 10)
        assert result[0] == 0
        assert result[5] == 5
        assert result[0] == result[-10]

    def test_concat_raises_index_error(self):
        result = ConcatDataset([[0, 1, 2, 3, 4],
                                [5, 6, 7, 8, 9]])
        with pytest.raises(IndexError):
            _ = result[10]

        with pytest.raises(IndexError):
            _ = result[11]

        with pytest.raises(IndexError):
            _ = result[-11]

        result = ConcatDataset(ConcreteSizedDataset([0, 1, 2, 3, 4]),
                               [5, 6, 7, 8, 9])
        with pytest.raises(IndexError):
            _ = result[10]

        with pytest.raises(IndexError):
            _ = result[11]

        with pytest.raises(IndexError):
            _ = result[-11]

    def test_non_iterable_raises_type_error(self):
        with pytest.raises(TypeError):
            _ = ConcatDataset(1, ConcreteSizedDataset([2, 3]))

    def test_false_raises_value_error(self):
        with pytest.raises(ValueError):
            _ = ConcatDataset((), ConcreteSizedDataset([2, 3]))

        with pytest.raises(ValueError):
            _ = ConcatDataset(0, ConcreteSizedDataset([2, 3]))

    def test_non_sized_raises_type_error(self):
        with pytest.raises(TypeError):
            _ = ConcatDataset([ConcreteDataset([0, 1]), ConcreteSizedDataset([2, 3])])
        with pytest.raises(TypeError):
            _ = ConcatDataset([ConcreteSizedDataset([0, 1]), ConcreteDataset([2, 3])])
        with pytest.raises(TypeError):
            _ = ConcatDataset([ConcreteDataset([0, 1]), ConcreteDataset([2, 3])])

        with pytest.raises(TypeError):
            _ = ConcatDataset([ConcreteDataset([0, 1]), ConcreteSizedDataset([2, 3])])
        with pytest.raises(TypeError):
            _ = ConcatDataset([ConcreteSizedDataset([0, 1]), ConcreteDataset([2, 3])])
        with pytest.raises(TypeError):
            _ = ConcatDataset([ConcreteDataset([0, 1]), ConcreteDataset([2, 3])])

    def test_add_dataset(self):
        dataset_1 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_2 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_3 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        result = dataset_1 + dataset_2 + dataset_3
        assert len(result) == 21
        assert result.cumulative_size == (14, 21)
        assert np.absolute(dataset_1[0][0] - result[0][0]).sum() == 0
        assert np.absolute(dataset_2[0][0] - result[7][0]).sum() == 0
        assert np.absolute(dataset_3[0][0] - result[14][0]).sum() == 0

    def test_cat_dataset(self):
        dataset_1 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_2 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_3 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        result = dataset_1.cat(dataset_2, dataset_3)
        assert len(result) == 21
        assert result.cumulative_size == (7, 14, 21)
        assert np.absolute(dataset_1[0][0] - result[0][0]).sum() == 0
        assert np.absolute(dataset_2[0][0] - result[7][0]).sum() == 0
        assert np.absolute(dataset_3[0][0] - result[14][0]).sum() == 0

    def test_cat_add_dataset(self):
        dataset_1 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_2 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_3 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        result = dataset_1.cat(dataset_2 + dataset_3)
        assert len(result) == 21
        assert result.cumulative_size == (7, 21)
        assert np.absolute(dataset_1[0][0] - result[0][0]).sum() == 0
        assert np.absolute(dataset_2[0][0] - result[7][0]).sum() == 0
        assert np.absolute(dataset_3[0][0] - result[14][0]).sum() == 0

    def test_add_cat_dataset(self):
        dataset_1 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_2 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        dataset_3 = ArrayDataset(np.random.rand(7, 3, 28, 28))
        result = dataset_1 + dataset_2.cat(dataset_3)
        assert len(result) == 21
        assert result.cumulative_size == (7, 21)
        assert np.absolute(dataset_1[0][0] - result[0][0]).sum() == 0
        assert np.absolute(dataset_2[0][0] - result[7][0]).sum() == 0
        assert np.absolute(dataset_3[0][0] - result[14][0]).sum() == 0

    def test_add_non_sized_raises(self):
        with pytest.raises(TypeError):
            _ = ConcreteSizedDataset([0, 1]) + ConcreteDataset([2, 3])

        with pytest.raises(TypeError):
            _ = ConcreteDataset([0, 1]) + ConcreteSizedDataset([2, 3])
