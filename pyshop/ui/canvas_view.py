from dataclasses import dataclass

from PyQt5.QtCore import QPointF


@dataclass
class CanvasViewport:
    zoom: float = 1.0
    pan_offset: QPointF = None
    min_zoom: float = 0.05
    max_zoom: float = 50.0

    def __post_init__(self):
        if self.pan_offset is None:
            self.pan_offset = QPointF(0, 0)

    def canvas_to_image(self, pos: QPointF) -> QPointF:
        return QPointF((pos.x() - self.pan_offset.x()) / self.zoom, (pos.y() - self.pan_offset.y()) / self.zoom)

    def image_to_canvas(self, pos: QPointF) -> QPointF:
        return QPointF(pos.x() * self.zoom + self.pan_offset.x(), pos.y() * self.zoom + self.pan_offset.y())

    def fit(self, image_size, view_size, margin: float = 0.9):
        image_width, image_height = image_size
        view_width, view_height = view_size
        if image_width <= 0 or image_height <= 0 or view_width <= 0 or view_height <= 0:
            return
        self.zoom = min(view_width / image_width, view_height / image_height) * margin
        self.pan_offset = QPointF((view_width - image_width * self.zoom) / 2, (view_height - image_height * self.zoom) / 2)

    def zoom_at(self, canvas_pos: QPointF, factor: float):
        old_zoom = self.zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * factor))
        self.pan_offset = canvas_pos - (canvas_pos - self.pan_offset) * (self.zoom / old_zoom)
