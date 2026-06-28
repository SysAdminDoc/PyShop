from dataclasses import dataclass

from PIL import Image, ImageDraw
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor


@dataclass(frozen=True)
class CanvasToolEvent:
    image_pos: QPointF
    widget_pos: QPointF
    button: object = None
    buttons: object = None
    modifiers: object = None

    @property
    def ix(self) -> int:
        return int(self.image_pos.x())

    @property
    def iy(self) -> int:
        return int(self.image_pos.y())


class CanvasToolHandler:
    def press(self, canvas, event: CanvasToolEvent) -> bool:
        return False

    def move(self, canvas, event: CanvasToolEvent) -> bool:
        return False

    def release(self, canvas, event: CanvasToolEvent) -> bool:
        return False


def _active_layer(canvas):
    return canvas.editor.active_layer()


def _save_history(canvas):
    canvas.editor.history.save_state(canvas.editor.layers, canvas.editor.active_layer_index)


def _left_button_down(event: CanvasToolEvent) -> bool:
    return bool((event.buttons or Qt.NoButton) & Qt.LeftButton)


class MoveToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        canvas.last_pos = event.image_pos
        canvas.drawing = True
        return True

    def move(self, canvas, event):
        if not canvas.drawing or not _left_button_down(event):
            return False
        layer = _active_layer(canvas)
        if not layer or layer.locked:
            return False
        dx = event.image_pos.x() - canvas.last_pos.x()
        dy = event.image_pos.y() - canvas.last_pos.y()
        _save_history(canvas)
        new_img = Image.new("RGBA", layer.image.size, (0, 0, 0, 0))
        new_img.paste(layer.image, (int(dx), int(dy)))
        layer.image = new_img
        canvas.last_pos = event.image_pos
        canvas.update()
        return True


class StrokeToolHandler(CanvasToolHandler):
    def __init__(self, dab_method: str, line_method: str):
        self.dab_method = dab_method
        self.line_method = line_method

    def press(self, canvas, event):
        layer = _active_layer(canvas)
        if not layer:
            return False
        _save_history(canvas)
        canvas.drawing = True
        canvas.last_pos = event.image_pos
        getattr(canvas, self.dab_method)(event.ix, event.iy)
        canvas.update()
        return True

    def move(self, canvas, event):
        if not canvas.drawing or not _left_button_down(event):
            return False
        canvas.last_pos = getattr(canvas, self.line_method)(canvas.last_pos, event.image_pos)
        canvas.update()
        return True


class FillToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        layer = _active_layer(canvas)
        if not layer:
            return False
        _save_history(canvas)
        canvas._flood_fill(event.ix, event.iy)
        canvas.update()
        return True


class MagicWandToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        canvas._magic_wand_select(event.ix, event.iy)
        canvas.update()
        return True


class RectSelectionToolHandler(CanvasToolHandler):
    def __init__(self, shape: str):
        self.shape = shape

    def press(self, canvas, event):
        canvas.selection_start = event.image_pos
        canvas.selection_rect = None
        canvas.set_selection_mask(None)
        canvas.drawing = True
        return True

    def move(self, canvas, event):
        if not canvas.drawing or canvas.selection_start is None or not _left_button_down(event):
            return False
        x1, y1 = canvas.selection_start.x(), canvas.selection_start.y()
        x2, y2 = event.image_pos.x(), event.image_pos.y()
        canvas.selection_rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        canvas.update()
        return True

    def release(self, canvas, event):
        if not canvas.selection_rect:
            return False
        layer = _active_layer(canvas)
        if not layer:
            return False
        width, height = layer.image.size
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        rect = canvas.selection_rect
        box = (int(rect.x()), int(rect.y()), int(rect.x() + rect.width()), int(rect.y() + rect.height()))
        if self.shape == "rectangle":
            draw.rectangle(box, fill=255)
        else:
            draw.ellipse(box, fill=255)
        canvas.set_selection_mask(mask)
        canvas.selection_rect = None
        canvas.drawing = False
        return True


class LassoToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        canvas._lasso_points = [event.image_pos]
        canvas.drawing = True
        return True

    def move(self, canvas, event):
        if not canvas.drawing or not _left_button_down(event):
            return False
        canvas._lasso_points.append(event.image_pos)
        canvas.update()
        return True

    def release(self, canvas, event):
        if len(canvas._lasso_points) <= 2:
            canvas._lasso_points = []
            return False
        layer = _active_layer(canvas)
        if not layer:
            return False
        width, height = layer.image.size
        mask = Image.new("L", (width, height), 0)
        points = [(int(point.x()), int(point.y())) for point in canvas._lasso_points]
        ImageDraw.Draw(mask).polygon(points, fill=255)
        canvas.set_selection_mask(mask)
        canvas.selection_rect = None
        canvas._lasso_points = []
        canvas.drawing = False
        return True


class CropToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        canvas.selection_start = event.image_pos
        canvas.crop_rect = None
        canvas.drawing = True
        return True

    def move(self, canvas, event):
        if not canvas.drawing or canvas.selection_start is None or not _left_button_down(event):
            return False
        x1, y1 = canvas.selection_start.x(), canvas.selection_start.y()
        x2, y2 = event.image_pos.x(), event.image_pos.y()
        canvas.crop_rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        canvas.update()
        return True


class ShapeToolHandler(CropToolHandler):
    def press(self, canvas, event):
        canvas.selection_start = event.image_pos
        canvas.shape_rect = None
        canvas.drawing = True
        return True

    def move(self, canvas, event):
        if not canvas.drawing or canvas.selection_start is None or not _left_button_down(event):
            return False
        x1, y1 = canvas.selection_start.x(), canvas.selection_start.y()
        x2, y2 = event.image_pos.x(), event.image_pos.y()
        canvas.shape_rect = QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        canvas.update()
        return True

    def release(self, canvas, event):
        if not canvas.shape_rect:
            return False
        canvas.editor.add_shape_layer(canvas.shape_rect)
        canvas.shape_rect = None
        canvas.drawing = False
        return True


class PenToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        canvas.editor.add_path_point(event.ix, event.iy)
        return True


class TextToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        canvas.editor.insert_text_at(event.ix, event.iy)
        return True


class RetouchToolHandler(CanvasToolHandler):
    def __init__(self, mode: str):
        self.mode = mode

    def press(self, canvas, event):
        layer = _active_layer(canvas)
        if not layer:
            return False
        _save_history(canvas)
        canvas.drawing = True
        canvas.last_pos = event.image_pos
        canvas._draw_retouch(event.ix, event.iy, self.mode)
        canvas.update()
        return True

    def move(self, canvas, event):
        if not canvas.drawing or not _left_button_down(event):
            return False
        canvas.last_pos = canvas._draw_retouch_line(canvas.last_pos, event.image_pos, self.mode)
        canvas.update()
        return True


class EyedropperToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        layer = _active_layer(canvas)
        if not layer:
            return False
        width, height = layer.image.size
        if not (0 <= event.ix < width and 0 <= event.iy < height):
            return False
        composite = canvas.editor.get_composite()
        if composite:
            red, green, blue, _alpha = composite.getpixel((event.ix, event.iy))
            canvas.color_picked.emit(QColor(red, green, blue))
        return True


class CloneStampToolHandler(CanvasToolHandler):
    def press(self, canvas, event):
        if (event.modifiers or Qt.NoModifier) & Qt.AltModifier:
            canvas.editor.clone_source = (event.ix, event.iy)
            canvas.editor.statusBar().showMessage(f"Clone source set to ({event.ix}, {event.iy})")
            return True
        if not canvas.editor.clone_source:
            return False
        _save_history(canvas)
        canvas.drawing = True
        canvas.last_pos = event.image_pos
        canvas._draw_clone_stamp(event.ix, event.iy)
        return True

    def move(self, canvas, event):
        if not canvas.drawing or not _left_button_down(event):
            return False
        canvas._draw_clone_stamp(event.ix, event.iy)
        canvas.last_pos = event.image_pos
        canvas.update()
        return True


def build_default_tool_handlers():
    return {
        "move": MoveToolHandler(),
        "brush": StrokeToolHandler("_draw_brush", "_draw_brush_line"),
        "eraser": StrokeToolHandler("_draw_eraser", "_draw_eraser_line"),
        "fill": FillToolHandler(),
        "magic_wand": MagicWandToolHandler(),
        "select_rect": RectSelectionToolHandler("rectangle"),
        "select_ellipse": RectSelectionToolHandler("ellipse"),
        "lasso": LassoToolHandler(),
        "crop": CropToolHandler(),
        "pen": PenToolHandler(),
        "text": TextToolHandler(),
        "shape": ShapeToolHandler(),
        "blur": RetouchToolHandler("blur"),
        "sharpen_tool": RetouchToolHandler("sharpen_tool"),
        "healing": RetouchToolHandler("healing"),
        "dodge": RetouchToolHandler("dodge"),
        "burn": RetouchToolHandler("burn"),
        "sponge": RetouchToolHandler("sponge"),
        "eyedropper": EyedropperToolHandler(),
        "clone_stamp": CloneStampToolHandler(),
    }
