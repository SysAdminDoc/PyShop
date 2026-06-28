from PIL import Image
from PyQt5.QtCore import QPointF, Qt

from pyshop.core import Layer
from pyshop.tools import CanvasToolHandler
from pyshop.tools.handlers import CanvasToolEvent, build_default_tool_handlers


def tool_event(x=1, y=1, buttons=Qt.LeftButton, modifiers=Qt.NoModifier):
    point = QPointF(x, y)
    return CanvasToolEvent(point, point, buttons=buttons, modifiers=modifiers)


class FakeHistory:
    def __init__(self):
        self.calls = 0

    def save_state(self, layers, active_layer_index):
        self.calls += 1


class FakeStatus:
    def __init__(self):
        self.messages = []

    def showMessage(self, message):
        self.messages.append(message)


class FakeEditor:
    def __init__(self):
        self.layers = [Layer("Layer", image=Image.new("RGBA", (6, 6), (0, 0, 0, 0)))]
        self.active_layer_index = 0
        self.history = FakeHistory()
        self.current_path = []
        self.text_points = []
        self.shape_rects = []
        self.clone_source = None
        self.status = FakeStatus()

    def active_layer(self):
        return self.layers[self.active_layer_index]

    def add_path_point(self, x, y):
        self.current_path.append((x, y))

    def insert_text_at(self, x, y):
        self.text_points.append((x, y))

    def add_shape_layer(self, rect):
        self.shape_rects.append(rect)

    def statusBar(self):
        return self.status


class FakeCanvas:
    def __init__(self):
        self.editor = FakeEditor()
        self.drawing = False
        self.last_pos = None
        self.selection_start = None
        self.selection_rect = None
        self.crop_rect = None
        self.shape_rect = None
        self.selection_mask = None
        self._lasso_points = []
        self.calls = []
        self.updates = 0

    def update(self):
        self.updates += 1

    def set_selection_mask(self, mask):
        self.selection_mask = mask

    def _draw_brush(self, x, y):
        self.calls.append(("brush", x, y))

    def _draw_brush_line(self, start, end):
        self.calls.append(("brush_line", int(start.x()), int(start.y()), int(end.x()), int(end.y())))
        return end

    def _draw_eraser(self, x, y):
        self.calls.append(("eraser", x, y))

    def _draw_eraser_line(self, start, end):
        self.calls.append(("eraser_line", int(start.x()), int(start.y()), int(end.x()), int(end.y())))
        return end

    def _flood_fill(self, x, y):
        self.calls.append(("fill", x, y))

    def _magic_wand_select(self, x, y):
        self.calls.append(("magic_wand", x, y))

    def _draw_retouch(self, x, y, mode):
        self.calls.append(("retouch", mode, x, y))

    def _draw_retouch_line(self, start, end, mode):
        self.calls.append(("retouch_line", mode, int(start.x()), int(start.y()), int(end.x()), int(end.y())))
        return end


def test_default_tool_handlers_cover_canvas_workflows():
    handlers = build_default_tool_handlers()

    for tool_id in [
        "brush",
        "eraser",
        "fill",
        "select_rect",
        "select_ellipse",
        "lasso",
        "crop",
        "pen",
        "text",
        "shape",
        "blur",
        "sharpen_tool",
        "healing",
        "dodge",
        "burn",
        "sponge",
    ]:
        assert isinstance(handlers[tool_id], CanvasToolHandler)


def test_brush_handler_press_and_move_dispatch_to_canvas_stroke_helpers():
    canvas = FakeCanvas()
    handler = build_default_tool_handlers()["brush"]

    assert handler.press(canvas, tool_event(2, 2)) is True
    assert canvas.editor.history.calls == 1
    assert canvas.drawing is True
    assert canvas.calls == [("brush", 2, 2)]

    assert handler.move(canvas, tool_event(4, 5)) is True
    assert canvas.last_pos == QPointF(4, 5)
    assert canvas.calls[-1] == ("brush_line", 2, 2, 4, 5)


def test_selection_handler_press_move_release_creates_selection_mask():
    canvas = FakeCanvas()
    handler = build_default_tool_handlers()["select_rect"]

    assert handler.press(canvas, tool_event(1, 1)) is True
    assert handler.move(canvas, tool_event(3, 4)) is True
    assert canvas.selection_rect.width() == 2
    assert canvas.selection_rect.height() == 3

    assert handler.release(canvas, tool_event(3, 4, buttons=Qt.NoButton)) is True
    assert canvas.selection_mask.getpixel((1, 1)) == 255
    assert canvas.selection_mask.getpixel((5, 5)) == 0
    assert canvas.drawing is False


def test_crop_pen_text_and_shape_handlers_delegate_editor_actions():
    canvas = FakeCanvas()
    handlers = build_default_tool_handlers()

    assert handlers["crop"].press(canvas, tool_event(0, 0)) is True
    assert handlers["crop"].move(canvas, tool_event(4, 3)) is True
    assert canvas.crop_rect.width() == 4
    assert canvas.crop_rect.height() == 3

    assert handlers["pen"].press(canvas, tool_event(2, 3)) is True
    assert canvas.editor.current_path == [(2, 3)]

    assert handlers["text"].press(canvas, tool_event(4, 5)) is True
    assert canvas.editor.text_points == [(4, 5)]

    assert handlers["shape"].press(canvas, tool_event(1, 1)) is True
    assert handlers["shape"].move(canvas, tool_event(4, 4)) is True
    assert handlers["shape"].release(canvas, tool_event(4, 4, buttons=Qt.NoButton)) is True
    assert len(canvas.editor.shape_rects) == 1
    assert canvas.editor.shape_rects[0].width() == 3


def test_retouch_handler_press_and_move_dispatches_mode():
    canvas = FakeCanvas()
    handler = build_default_tool_handlers()["dodge"]

    assert handler.press(canvas, tool_event(2, 2)) is True
    assert canvas.editor.history.calls == 1
    assert canvas.calls == [("retouch", "dodge", 2, 2)]

    assert handler.move(canvas, tool_event(3, 2)) is True
    assert canvas.calls[-1] == ("retouch_line", "dodge", 2, 2, 3, 2)
