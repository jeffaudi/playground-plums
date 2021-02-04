import pytest

from playground_plums.plot.engine.position_generator import (
    SimpleImagePositionGenerator,
    LayoutImagePositionGenerator,
    AdaptiveImagePositionGenerator,
    LegendItemPositionGenerator
)


class TestSimpleImagePositionGenerator:
    def test_constructor(self):
        dummy_datapoints = list(range(150))
        dummy_max_cols = 20
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = SimpleImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check attributes
        assert position_generator._width == 110
        assert position_generator._height == 220
        assert position_generator._n_cols == 20
        assert position_generator._n_rows == 7
        assert position_generator._remainder == 10

        # Change number of datapoints (not enough to completely fill a row)
        dummy_datapoints = list(range(15))

        position_generator = SimpleImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check attributes
        assert position_generator._width == 110
        assert position_generator._height == 220
        assert position_generator._n_cols == 15
        assert position_generator._n_rows == 1
        assert position_generator._remainder == 0

    def test__iter(self):
        dummy_datapoints = list(range(5))
        dummy_max_cols = 2
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = SimpleImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        expected_positions = [(5, 10), (115, 10), (5, 230), (115, 230), (5, 450)]
        for i, position in enumerate(list(position_generator)):
            assert position == expected_positions[i]

    def test_mosaic_size(self):
        dummy_datapoints = list(range(150))
        dummy_max_cols = 20
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = SimpleImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check size
        assert position_generator.mosaic_size == (20 * 110, 8 * 220)

        dummy_datapoints = list(range(15))

        position_generator = SimpleImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check size
        assert position_generator.mosaic_size == (15 * 110, 1 * 220)


class TestLayoutImagePositionGenerator:
    def test_constructor(self):
        dummy_datapoints = [list(range(5)) for _ in range(20)]
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = LayoutImagePositionGenerator(
            data_points=dummy_datapoints,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check attributes
        assert position_generator._layout == tuple(5 for _ in range(20))
        assert position_generator._width == 110
        assert position_generator._height == 220
        assert position_generator._n_cols == 5
        assert position_generator._n_rows == 20

        # With unequal number of column per row
        dummy_datapoints = [list(range(3 + j % 3)) for j in range(20)]

        position_generator = LayoutImagePositionGenerator(
            data_points=dummy_datapoints,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check attributes
        assert position_generator._layout == tuple(3 + j % 3 for j in range(20))
        assert position_generator._width == 110
        assert position_generator._height == 220
        assert position_generator._n_cols == 5
        assert position_generator._n_rows == 20

    def test__iter(self):
        tolerance = 1e-8

        dummy_datapoints = [list(range(3 + (j + 2) % 3)) for j in range(4)]
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = LayoutImagePositionGenerator(
            data_points=dummy_datapoints,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        first_margin = 5
        second_margin = (250.0 / 3) / 2
        third_margin = (150.0 / 4) / 2
        fourth_margin = 5

        expected_positions = [(first_margin, 10), (100 + 3 * first_margin, 10), (200 + 5 * first_margin, 10),
                              (300 + 7 * first_margin, 10), (400 + 9 * first_margin, 10),

                              (second_margin, 230), (100 + 3 * second_margin, 230), (200 + 5 * second_margin, 230),

                              (third_margin, 450), (100 + 3 * third_margin, 450), (200 + 5 * third_margin, 450),
                              (300 + 7 * third_margin, 450),

                              (fourth_margin, 670), (100 + 3 * fourth_margin, 670), (200 + 5 * fourth_margin, 670),
                              (300 + 7 * fourth_margin, 670), (400 + 9 * fourth_margin, 670)]
        for i, position in enumerate(list(position_generator)):
            assert (abs(position[0] - expected_positions[i][0]) < tolerance) and \
                (abs(position[1] - expected_positions[i][1]) < tolerance)

    def test_mosaic_size(self):
        dummy_datapoints = [list(range(5)) for _ in range(20)]
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = LayoutImagePositionGenerator(
            data_points=dummy_datapoints,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check size
        assert position_generator.mosaic_size == (5 * 110, 20 * 220)

        dummy_datapoints = [list(range(3 + j % 3)) for j in range(20)]

        position_generator = LayoutImagePositionGenerator(
            data_points=dummy_datapoints,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check size
        assert position_generator.mosaic_size == (5 * 110, 20 * 220)


class TestAdaptiveImagePositionGenerator:
    def test_constructor(self):
        dummy_datapoints = list(range(150))
        dummy_max_cols = 20
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = AdaptiveImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check attributes
        assert position_generator._width == 110
        assert position_generator._height == 220
        assert position_generator._n_cols == 20
        assert position_generator._n_rows == 8

        # Change number of datapoints (not enough to completely fill a row)
        dummy_datapoints = list(range(15))

        position_generator = AdaptiveImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check attributes
        assert position_generator._width == 110
        assert position_generator._height == 220
        assert position_generator._n_cols == 15
        assert position_generator._n_rows == 1

    def test__iter(self):
        dummy_datapoints = list(range(5))
        dummy_max_cols = 2
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = AdaptiveImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        expected_positions = [(5, 10), (115, 10),
                              (5, 230), (115, 230),
                              (60, 450)]
        for i, position in enumerate(list(position_generator)):
            assert position == expected_positions[i]

    def test_mosaic_size(self):
        dummy_datapoints = list(range(150))
        dummy_max_cols = 20
        dummy_margins = (5, 10)
        dummy_max_image_size = (100, 200)

        position_generator = AdaptiveImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check size
        assert position_generator.mosaic_size == (20 * 110, 8 * 220)

        dummy_datapoints = list(range(15))

        position_generator = AdaptiveImagePositionGenerator(
            data_points=dummy_datapoints,
            max_cols=dummy_max_cols,
            margins=dummy_margins,
            max_image_size=dummy_max_image_size
        )

        # Check size
        assert position_generator.mosaic_size == (15 * 110, 1 * 220)


class TestLegendItemPositionGenerator:

    def test_constructor(self):
        # Parameters
        item_sizes = [(100, 100), (50, 100), (100, 50), (200, 100), (20, 300)]
        axis = 0
        max_size_along_axis = 350
        main_axis_align = 'start'
        minor_axis_align = 'start'

        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        # Check attributes
        assert position_generator._cell_size == (200, 300)
        assert position_generator._new_positions == (1, 0)
        assert position_generator._n_items_along_main_axis == 1
        assert position_generator._n_items_along_minor_axis == 5
        assert position_generator._remainder == 0

        # Check invalid items_sizes
        with pytest.raises(ValueError):
            LegendItemPositionGenerator(
                items_sizes=[],
                axis=axis,
                max_size_along_axis=200,
                main_axis_align=main_axis_align,
                minor_axis_align=minor_axis_align
            )

        with pytest.raises(ValueError):
            LegendItemPositionGenerator(
                items_sizes=None,
                axis=axis,
                max_size_along_axis=200,
                main_axis_align=main_axis_align,
                minor_axis_align=minor_axis_align
            )

        # Check that items fits in the legend
        with pytest.raises(ValueError):
            LegendItemPositionGenerator(
                items_sizes=item_sizes,
                axis=axis,
                max_size_along_axis=200,
                main_axis_align=main_axis_align,
                minor_axis_align=minor_axis_align
            )

    def test__iter(self):
        # Vertically
        # Parameters
        item_sizes = [(100, 100), (50, 100), (100, 50), (200, 100), (20, 300)]
        axis = 0
        max_size_along_axis = 600
        main_axis_align = 'start'
        minor_axis_align = 'start'

        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        expected_positions = [(0, 0), (0, 300), (200, 0), (200, 300), (400, 0)]
        for i, position in enumerate(list(position_generator)):
            assert position == expected_positions[i]

        # Horizontally
        axis = 1

        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align=main_axis_align,
            minor_axis_align=minor_axis_align
        )

        expected_positions = [(0, 0), (200, 0), (400, 0), (0, 300), (200, 300)]
        for i, position in enumerate(list(position_generator)):
            assert position == expected_positions[i]

    def test_align_cell_in_box(self):
        # Vertically
        # Parameters
        item_sizes = [(100, 100), (50, 100), (100, 50), (200, 100), (20, 300)]
        axis = 0
        max_size_along_axis = 600

        top_left_positions = [(0, 0), (0, 300), (200, 0), (200, 300), (400, 0)]

        # Start - start
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align='start',
            minor_axis_align='start'
        )

        expected_positions = [(0, 0), (0, 300), (200, 0), (200, 300), (400, 0)]
        for i, item_size in enumerate(item_sizes):
            coordinates = position_generator.align_cell_in_box(
                main_axis_coordinate=top_left_positions[i][1],
                minor_axis_coordinate=top_left_positions[i][0],
                item_size=item_size
            )
            assert expected_positions[i] == coordinates

        # Center - start
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align='center',
            minor_axis_align='start'
        )

        expected_positions = [(0, 100), (0, 400), (200, 125), (200, 400), (400, 0)]
        for i, item_size in enumerate(item_sizes):
            coordinates = position_generator.align_cell_in_box(
                main_axis_coordinate=top_left_positions[i][1],
                minor_axis_coordinate=top_left_positions[i][0],
                item_size=item_size
            )
            assert expected_positions[i] == coordinates

        # End - start
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align='end',
            minor_axis_align='start'
        )

        expected_positions = [(0, 200), (0, 500), (200, 250), (200, 500), (400, 0)]
        for i, item_size in enumerate(item_sizes):
            coordinates = position_generator.align_cell_in_box(
                main_axis_coordinate=top_left_positions[i][1],
                minor_axis_coordinate=top_left_positions[i][0],
                item_size=item_size
            )
            assert expected_positions[i] == coordinates

        # Start - center
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align='start',
            minor_axis_align='center'
        )

        expected_positions = [(50, 0), (75, 300), (250, 0), (200, 300), (490, 0)]
        for i, item_size in enumerate(item_sizes):
            coordinates = position_generator.align_cell_in_box(
                main_axis_coordinate=top_left_positions[i][1],
                minor_axis_coordinate=top_left_positions[i][0],
                item_size=item_size
            )
            assert expected_positions[i] == coordinates

        # Start - end
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align='start',
            minor_axis_align='end'
        )

        expected_positions = [(100, 0), (150, 300), (300, 0), (200, 300), (580, 0)]
        for i, item_size in enumerate(item_sizes):
            coordinates = position_generator.align_cell_in_box(
                main_axis_coordinate=top_left_positions[i][1],
                minor_axis_coordinate=top_left_positions[i][0],
                item_size=item_size
            )
            assert expected_positions[i] == coordinates

        # Center - end
        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis,
            main_axis_align='center',
            minor_axis_align='end'
        )

        expected_positions = [(100, 100), (150, 400), (300, 125), (200, 400), (580, 0)]
        for i, item_size in enumerate(item_sizes):
            coordinates = position_generator.align_cell_in_box(
                main_axis_coordinate=top_left_positions[i][1],
                minor_axis_coordinate=top_left_positions[i][0],
                item_size=item_size
            )
            assert expected_positions[i] == coordinates

    def test_cell_size(self):
        # Parameters
        item_sizes = [(100, 100), (50, 100), (100, 50), (200, 100), (20, 300)]
        axis = 0
        max_size_along_axis = 600

        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis
        )

        assert position_generator.cell_size == (200, 300)

    def test_legend_size(self):
        # Parameters (with remainder)
        item_sizes = [(100, 100), (50, 100), (100, 50), (200, 100), (20, 300)]
        axis = 0
        max_size_along_axis = 600

        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis
        )

        assert position_generator.legend_size == (600, 600)

        # Parameters (no remainder)
        item_sizes = [(100, 100), (100, 50), (200, 100), (20, 300)]
        axis = 0
        max_size_along_axis = 600

        position_generator = LegendItemPositionGenerator(
            items_sizes=item_sizes,
            axis=axis,
            max_size_along_axis=max_size_along_axis
        )

        assert position_generator.legend_size == (400, 600)
