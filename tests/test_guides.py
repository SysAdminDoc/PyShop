from pyshop.ui import snap_coordinate, snap_point_to_guides


def test_snap_coordinate_uses_nearest_target_inside_threshold():
    assert snap_coordinate(11, [0, 10, 20], 3) == 10
    assert snap_coordinate(15, [0, 10, 20], 3) == 15


def test_snap_point_to_guides_uses_grid_and_explicit_guides():
    x, y = snap_point_to_guides(58, 97, 32, [("vertical", 60), ("horizontal", 100)], 5)

    assert (x, y) == (60, 96)
