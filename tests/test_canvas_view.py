from PyQt5.QtCore import QPointF

from pyshop.ui import CanvasViewport


def test_canvas_viewport_converts_between_canvas_and_image_points():
    viewport = CanvasViewport(zoom=2.0, pan_offset=QPointF(10, 20))

    image_pos = viewport.canvas_to_image(QPointF(14, 26))
    canvas_pos = viewport.image_to_canvas(image_pos)

    assert image_pos == QPointF(2, 3)
    assert canvas_pos == QPointF(14, 26)


def test_canvas_viewport_fit_centers_image_with_margin():
    viewport = CanvasViewport()

    viewport.fit((100, 50), (300, 300))

    assert viewport.zoom == 2.7
    assert viewport.pan_offset == QPointF(15, 82.5)


def test_canvas_viewport_zoom_at_preserves_anchor_position():
    viewport = CanvasViewport(zoom=1.0, pan_offset=QPointF(0, 0))

    viewport.zoom_at(QPointF(50, 50), 2.0)

    assert viewport.zoom == 2.0
    assert viewport.canvas_to_image(QPointF(50, 50)) == QPointF(50, 50)
