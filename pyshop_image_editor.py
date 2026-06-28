#!/usr/bin/env python3
"""
PyShop - A Photoshop-like Image Editor
Built with PyQt5 and Pillow
"""

import sys
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageChops
from pyshop import APP_DISPLAY_NAME, APP_VERSION, __version__
from pyshop.app_info import app_icon_path
from pyshop.core import (
    BrushSettings,
    HistoryManager,
    Layer,
    apply_channel_visibility,
    build_marching_ants_path,
    composite_layers,
    create_document_layers,
    apply_retouch_dab,
    erase_brush_stroke,
    flattened_document_layers,
    image_document_layers,
    iter_brush_dabs,
    iter_intersecting_tile_boxes,
    is_project_path,
    load_project,
    named_background_rgba,
    open_raster_image,
    paint_brush_stroke,
    PROJECT_FILE_SUFFIX,
    qcolor_to_rgba,
    selection_mask_bounds,
    load_psd_layers,
    save_flattened_psd,
    save_project,
    smoothed_brush_point,
    TiledCompositeCache,
)
from pyshop.tools import DEFAULT_TOOL_REGISTRY
from pyshop.ui import CanvasViewport, snap_point_to_guides


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QAction, QActionGroup, QFileDialog, QLabel, QSlider,
    QSpinBox, QDoubleSpinBox, QColorDialog, QDockWidget, QListWidget,
    QListWidgetItem, QPushButton, QCheckBox, QComboBox, QScrollArea,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QMenu,
    QMenuBar, QStatusBar, QSplitter, QFrame, QInputDialog,
    QMessageBox, QSizePolicy, QToolButton, QWidgetAction, QGridLayout,
    QLineEdit, QTextEdit, QAbstractItemView, QTabWidget, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QPoint, QRect, QSize, QTimer, pyqtSignal, QPointF, QRectF
)
from PyQt5.QtGui import (
    QImage, QPixmap, QPainter, QPen, QBrush, QColor, QIcon,
    QCursor, QFont, QPainterPath, QTransform,
    qRgba, qRed, qGreen, qBlue, qAlpha, QPolygon, QFontMetrics,
    QLinearGradient, QRadialGradient, QPolygonF
)


# ---- Dark Theme Stylesheet ------------------------------------------------
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e; color: #cccccc;
    font-family: 'Segoe UI', sans-serif; font-size: 12px;
}
QMenuBar { background-color: #2b2b2b; color: #cccccc; border-bottom: 1px solid #3a3a3a; }
QMenuBar::item:selected { background-color: #3a3a3a; }
QMenu { background-color: #2b2b2b; color: #cccccc; border: 1px solid #3a3a3a; }
QMenu::item:selected { background-color: #0078d4; }
QMenu::separator { height: 1px; background: #3a3a3a; margin: 4px 8px; }
QToolBar { background-color: #252526; border: 1px solid #3a3a3a; spacing: 2px; padding: 2px; }
QToolButton {
    background-color: transparent; border: 1px solid transparent;
    border-radius: 3px; padding: 4px; color: #cccccc; min-width: 28px; min-height: 28px;
}
QToolButton:hover { background-color: #3a3a3a; border-color: #4a4a4a; }
QToolButton:checked { background-color: #0078d4; border-color: #0078d4; }
QToolButton:pressed { background-color: #005a9e; }
QDockWidget { color: #cccccc; }
QDockWidget::title { background-color: #2b2b2b; padding: 6px; border: 1px solid #3a3a3a; }
QListWidget { background-color: #252526; color: #cccccc; border: 1px solid #3a3a3a; outline: none; }
QListWidget::item { padding: 4px; border-bottom: 1px solid #2a2a2a; }
QListWidget::item:selected { background-color: #0078d4; }
QListWidget::item:hover { background-color: #2a2d2e; }
QPushButton {
    background-color: #333333; color: #cccccc; border: 1px solid #3a3a3a;
    border-radius: 3px; padding: 5px 12px; min-height: 22px;
}
QPushButton:hover { background-color: #3a3a3a; border-color: #4a4a4a; }
QPushButton:pressed { background-color: #0078d4; }
QSlider::groove:horizontal { height: 4px; background: #3a3a3a; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #0078d4; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: #1a8cff; }
QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
    background-color: #333333; color: #cccccc; border: 1px solid #3a3a3a;
    border-radius: 3px; padding: 3px 6px;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #2b2b2b; color: #cccccc;
    selection-background-color: #0078d4; border: 1px solid #3a3a3a;
}
QScrollBar:vertical { background: #1e1e1e; width: 12px; border: none; }
QScrollBar::handle:vertical { background: #3a3a3a; min-height: 20px; border-radius: 4px; margin: 2px; }
QScrollBar::handle:vertical:hover { background: #4a4a4a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1e1e1e; height: 12px; border: none; }
QScrollBar::handle:horizontal { background: #3a3a3a; min-width: 20px; border-radius: 4px; margin: 2px; }
QScrollBar::handle:horizontal:hover { background: #4a4a4a; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QStatusBar { background-color: #007acc; color: white; border: none; }
QLabel { color: #cccccc; }
QCheckBox { color: #cccccc; spacing: 6px; }
QCheckBox::indicator { width: 14px; height: 14px; border: 1px solid #555; border-radius: 2px; background: #333; }
QCheckBox::indicator:checked { background: #0078d4; border-color: #0078d4; }
QGroupBox { color: #cccccc; border: 1px solid #3a3a3a; border-radius: 4px; margin-top: 8px; padding-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QTabWidget::pane { border: 1px solid #3a3a3a; background: #1e1e1e; }
QTabBar::tab { background: #252526; color: #999; padding: 6px 14px; border: 1px solid #3a3a3a; border-bottom: none; }
QTabBar::tab:selected { background: #1e1e1e; color: #fff; }
QTabBar::tab:hover { background: #2d2d2d; }
"""


# ---- Tool Icon Generator ---------------------------------------------------
def make_tool_icon(tool_id, size=24):
    """Generate a crisp QPainter-drawn icon for each tool."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    fg = QColor("#cccccc")
    hi = QColor("#60b0ff")
    s = size

    pen = QPen(fg, 2.0)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)

    if tool_id == "move":
        cx, cy = s // 2, s // 2
        L = s * 0.35
        ah = 4
        p.setPen(QPen(fg, 2.0))
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            ex, ey = cx + dx * L, cy + dy * L
            p.drawLine(QPointF(cx, cy), QPointF(ex, ey))
            if dx == 0:
                p.drawLine(QPointF(ex, ey), QPointF(ex - ah, ey + dy * -ah))
                p.drawLine(QPointF(ex, ey), QPointF(ex + ah, ey + dy * -ah))
            else:
                p.drawLine(QPointF(ex, ey), QPointF(ex + dx * -ah, ey - ah))
                p.drawLine(QPointF(ex, ey), QPointF(ex + dx * -ah, ey + ah))

    elif tool_id == "brush":
        p.setPen(QPen(fg, 2.0))
        p.drawLine(QPointF(s*0.7, s*0.15), QPointF(s*0.35, s*0.55))
        p.setPen(QPen(QColor("#999"), 2.5))
        p.drawLine(QPointF(s*0.38, s*0.50), QPointF(s*0.28, s*0.62))
        p.setPen(QPen(hi, 2.5))
        p.setBrush(hi)
        path = QPainterPath()
        path.moveTo(s*0.30, s*0.58)
        path.lineTo(s*0.15, s*0.85)
        path.lineTo(s*0.25, s*0.75)
        path.lineTo(s*0.38, s*0.62)
        path.closeSubpath()
        p.drawPath(path)

    elif tool_id == "eraser":
        p.setPen(QPen(fg, 1.5))
        pts = [QPointF(s*0.2,s*0.75), QPointF(s*0.55,s*0.35),
               QPointF(s*0.8,s*0.55), QPointF(s*0.45,s*0.95)]
        p.setBrush(QColor("#d48080"))
        p.drawPolygon(QPolygonF(pts))
        mid1 = QPointF((pts[0].x()+pts[1].x())/2+0.08*s, (pts[0].y()+pts[1].y())/2+0.08*s)
        mid2 = QPointF((pts[2].x()+pts[3].x())/2+0.08*s, (pts[2].y()+pts[3].y())/2+0.08*s)
        p.setPen(QPen(fg, 1))
        p.drawLine(mid1, mid2)

    elif tool_id == "fill":
        p.setPen(QPen(fg, 1.5))
        p.setBrush(QColor("#666"))
        p.drawRect(QRectF(s*0.25, s*0.35, s*0.45, s*0.45))
        p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(s*0.5, s*0.15, s*0.3, s*0.35), 0, 180*16)
        p.setPen(QPen(hi, 2))
        p.setBrush(hi)
        p.drawEllipse(QPointF(s*0.18, s*0.82), 3, 4)

    elif tool_id == "eyedropper":
        p.setPen(QPen(fg, 1.5))
        p.drawLine(QPointF(s*0.65, s*0.15), QPointF(s*0.35, s*0.55))
        p.setBrush(QColor("#888"))
        p.drawEllipse(QPointF(s*0.72, s*0.12), s*0.1, s*0.08)
        p.setPen(QPen(hi, 2))
        p.drawLine(QPointF(s*0.35, s*0.55), QPointF(s*0.22, s*0.85))

    elif tool_id == "magic_wand":
        p.setPen(QPen(QColor("#e0c050"), 2.0))
        p.drawLine(QPointF(s*0.65, s*0.75), QPointF(s*0.3, s*0.2))
        cx2, cy2 = s*0.25, s*0.15
        p.setPen(QPen(QColor("#ffe44d"), 1.5))
        for angle in range(0, 360, 45):
            r = s*0.12 if angle % 90 == 0 else s*0.06
            ex = cx2 + r * math.cos(math.radians(angle))
            ey = cy2 + r * math.sin(math.radians(angle))
            p.drawLine(QPointF(cx2, cy2), QPointF(ex, ey))
        for sx2, sy2, r2 in [(s*0.55, s*0.3, 2.5), (s*0.7, s*0.45, 2)]:
            p.drawLine(QPointF(sx2-r2, sy2), QPointF(sx2+r2, sy2))
            p.drawLine(QPointF(sx2, sy2-r2), QPointF(sx2, sy2+r2))

    elif tool_id == "select_rect":
        pen2 = QPen(fg, 1.5, Qt.DashLine)
        pen2.setDashPattern([3, 3])
        p.setPen(pen2)
        p.drawRect(QRectF(s*0.15, s*0.2, s*0.7, s*0.6))

    elif tool_id == "select_ellipse":
        pen2 = QPen(fg, 1.5, Qt.DashLine)
        pen2.setDashPattern([3, 3])
        p.setPen(pen2)
        p.drawEllipse(QRectF(s*0.12, s*0.2, s*0.76, s*0.6))

    elif tool_id == "lasso":
        path = QPainterPath()
        path.moveTo(s*0.3, s*0.7)
        path.cubicTo(s*0.1, s*0.3, s*0.5, s*0.05, s*0.75, s*0.3)
        path.cubicTo(s*0.9, s*0.5, s*0.6, s*0.9, s*0.3, s*0.7)
        pen2 = QPen(fg, 1.5, Qt.DashLine)
        pen2.setDashPattern([3, 2])
        p.setPen(pen2)
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        p.setBrush(fg)
        p.drawEllipse(QPointF(s*0.3, s*0.7), 2, 2)

    elif tool_id == "crop":
        p.setPen(QPen(fg, 2))
        m, e = s*0.2, s*0.8
        cl = s*0.18
        p.drawLine(QPointF(m, m), QPointF(m+cl, m))
        p.drawLine(QPointF(m, m), QPointF(m, m+cl))
        p.drawLine(QPointF(e, m), QPointF(e-cl, m))
        p.drawLine(QPointF(e, m), QPointF(e, m+cl))
        p.drawLine(QPointF(m, e), QPointF(m+cl, e))
        p.drawLine(QPointF(m, e), QPointF(m, e-cl))
        p.drawLine(QPointF(e, e), QPointF(e-cl, e))
        p.drawLine(QPointF(e, e), QPointF(e, e-cl))

    elif tool_id == "text":
        p.setPen(QPen(fg, 2.5))
        p.drawLine(QPointF(s*0.2, s*0.2), QPointF(s*0.8, s*0.2))
        p.drawLine(QPointF(s*0.5, s*0.2), QPointF(s*0.5, s*0.85))
        p.setPen(QPen(fg, 1.5))
        p.drawLine(QPointF(s*0.38, s*0.85), QPointF(s*0.62, s*0.85))

    elif tool_id == "clone_stamp":
        p.setPen(QPen(fg, 1.5))
        p.drawLine(QPointF(s*0.5, s*0.1), QPointF(s*0.5, s*0.4))
        p.setBrush(QColor("#666"))
        p.drawRect(QRectF(s*0.25, s*0.4, s*0.5, s*0.2))
        p.setBrush(QColor("#555"))
        p.drawRect(QRectF(s*0.15, s*0.7, s*0.7, s*0.15))
        p.drawLine(QPointF(s*0.38, s*0.1), QPointF(s*0.62, s*0.1))

    else:
        p.setPen(QPen(fg, 1.5))
        p.setFont(QFont("Segoe UI", max(8, int(s * 0.34)), QFont.Bold))
        label = tool_id.replace("_tool", "").replace("_", " ")[:2].upper()
        p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, label)

    p.end()
    return QIcon(pix)


# ---- Canvas Widget ---------------------------------------------------------
class CanvasWidget(QWidget):
    color_picked = pyqtSignal(QColor)

    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.viewport = CanvasViewport()
        self.panning = False
        self.pan_start = QPointF()
        self.last_pos = None
        self.drawing = False
        self.selection_start = None
        self.selection_rect = None
        self.selection_mask = None
        self.marching_ants_path = None
        self.marching_offset = 0
        self.crop_rect = None
        self.shape_rect = None
        self._lasso_points = []
        self._checker_tile = None
        self.tile_cache = TiledCompositeCache()
        self.tablet_pressure = 1.0
        self._snap_tools = {"move", "select_rect", "select_ellipse", "crop", "text", "fill", "magic_wand"}
        self._retouch_tools = {"blur", "sharpen_tool", "healing", "dodge", "burn", "sponge"}

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.march_timer = QTimer()
        self.march_timer.timeout.connect(self._march_tick)
        self.march_timer.start(100)

    @property
    def zoom(self):
        return self.viewport.zoom

    @zoom.setter
    def zoom(self, value):
        self.viewport.zoom = value

    @property
    def pan_offset(self):
        return self.viewport.pan_offset

    @pan_offset.setter
    def pan_offset(self, value):
        self.viewport.pan_offset = value

    def _march_tick(self):
        if self.marching_ants_path is not None or self.selection_rect is not None:
            self.marching_offset = (self.marching_offset + 1) % 12
            self.update()

    def _update_marching_path(self):
        if self.selection_mask is None:
            self.marching_ants_path = None
            return
        self.marching_ants_path = build_marching_ants_path(np.array(self.selection_mask))

    def set_selection_mask(self, mask):
        self.selection_mask = mask
        self._update_marching_path()

    def canvas_to_image(self, pos):
        return self.viewport.canvas_to_image(pos)

    def image_to_canvas(self, pos):
        return self.viewport.image_to_canvas(pos)

    def snap_image_pos(self, pos, tool):
        if not self.editor.snap_enabled or tool not in self._snap_tools:
            return pos
        threshold = max(2.0, 8.0 / max(self.zoom, 0.01))
        x, y = snap_point_to_guides(pos.x(), pos.y(), self.editor.grid_size, self.editor.guides, threshold)
        return QPointF(x, y)

    def fit_in_view(self):
        if not self.editor.layers: return
        iw, ih = self.editor.layers[0].image.size
        vw, vh = self.width(), self.height()
        self.viewport.fit((iw, ih), (vw, vh))
        self.update()

    def _get_checker(self):
        if self._checker_tile is None:
            cs = 16
            self._checker_tile = QPixmap(cs*2, cs*2)
            tp = QPainter(self._checker_tile)
            tp.fillRect(0, 0, cs, cs, QColor("#404040"))
            tp.fillRect(cs, 0, cs, cs, QColor("#333333"))
            tp.fillRect(0, cs, cs, cs, QColor("#333333"))
            tp.fillRect(cs, cs, cs, cs, QColor("#404040"))
            tp.end()
        return self._checker_tile

    def _draw_grid_and_guides(self, painter, doc_width, doc_height, visible_bounds):
        left, top, right, bottom = visible_bounds
        if self.editor.show_grid and self.editor.grid_size > 0:
            pen = QPen(QColor(255, 255, 255, 35), 1.0)
            pen.setCosmetic(True)
            painter.setPen(pen)
            grid = self.editor.grid_size
            start_x = (left // grid) * grid
            start_y = (top // grid) * grid
            for x in range(start_x, right + 1, grid):
                painter.drawLine(QPointF(x, 0), QPointF(x, doc_height))
            for y in range(start_y, bottom + 1, grid):
                painter.drawLine(QPointF(0, y), QPointF(doc_width, y))

        if self.editor.show_guides and self.editor.guides:
            pen = QPen(QColor("#00aaff"), 1.0, Qt.DashLine)
            pen.setCosmetic(True)
            painter.setPen(pen)
            for orientation, value in self.editor.guides:
                if orientation == "vertical" and left <= value <= right:
                    painter.drawLine(QPointF(value, 0), QPointF(value, doc_height))
                elif orientation == "horizontal" and top <= value <= bottom:
                    painter.drawLine(QPointF(0, value), QPointF(doc_width, value))

    def _draw_rulers(self, painter, doc_width, doc_height):
        if not self.editor.show_rulers:
            return
        ruler_h = 22
        ruler_w = 36
        painter.fillRect(0, 0, self.width(), ruler_h, QColor("#252526"))
        painter.fillRect(0, 0, ruler_w, self.height(), QColor("#252526"))
        painter.setPen(QColor("#777"))
        painter.drawLine(0, ruler_h, self.width(), ruler_h)
        painter.drawLine(ruler_w, 0, ruler_w, self.height())
        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QColor("#bdbdbd"))
        step = 100 if self.zoom >= 0.5 else 250
        for x in range(0, doc_width + 1, step):
            cx = self.image_to_canvas(QPointF(x, 0)).x()
            if ruler_w <= cx <= self.width():
                painter.drawLine(QPointF(cx, ruler_h - 6), QPointF(cx, ruler_h))
                painter.drawText(int(cx + 2), 10, str(x))
        for y in range(0, doc_height + 1, step):
            cy = self.image_to_canvas(QPointF(0, y)).y()
            if ruler_h <= cy <= self.height():
                painter.drawLine(QPointF(ruler_w - 6, cy), QPointF(ruler_w, cy))
                painter.drawText(2, int(cy - 2), str(y))

    def _draw_path_preview(self, painter):
        points = self.editor.current_path
        if not points:
            return
        pen = QPen(QColor("#ff4fd8"), 1.2, Qt.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(QColor("#ff4fd8"))
        qpoints = [QPointF(x, y) for x, y in points]
        for point in qpoints:
            painter.drawEllipse(point, 2.5, 2.5)
        for index in range(len(qpoints) - 1):
            painter.drawLine(qpoints[index], qpoints[index + 1])
        if self.editor.current_path_closed and len(qpoints) > 2:
            painter.drawLine(qpoints[-1], qpoints[0])

    def update(self, *args, **kwargs):
        self.tile_cache.invalidate()
        return super().update(*args, **kwargs)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        if not self.editor.layers:
            painter.setPen(QColor("#555"))
            painter.setFont(QFont("Segoe UI", 16))
            painter.drawText(self.rect(), Qt.AlignCenter, "Open or create an image to begin")
            painter.end()
            return

        doc_width, doc_height = self.editor.layers[0].image.size
        visible_bounds = self.viewport.visible_image_bounds((doc_width, doc_height), (self.width(), self.height()))

        painter.save()
        painter.translate(self.pan_offset)
        painter.scale(self.zoom, self.zoom)

        if visible_bounds is not None:
            left, top, right, bottom = visible_bounds

            tile = self._get_checker()
            tw, th = tile.width(), tile.height()
            start_x = (left // tw) * tw
            start_y = (top // th) * th
            for y in range(start_y, bottom, th):
                for x in range(start_x, right, tw):
                    dw = min(tw, doc_width - x)
                    dh = min(th, doc_height - y)
                    painter.drawPixmap(x, y, dw, dh, tile, 0, 0, dw, dh)

            for box in iter_intersecting_tile_boxes(doc_width, doc_height, visible_bounds):
                tile_image = self.tile_cache.get_tile(self.editor.layers, box)
                tile_data = tile_image.tobytes("raw", "RGBA")
                qimg = QImage(tile_data, box.width, box.height, QImage.Format_RGBA8888)
                painter.drawImage(box.x, box.y, qimg)

            self._draw_grid_and_guides(painter, doc_width, doc_height, visible_bounds)

        # ---- Marching Ants ----
        if self.marching_ants_path is not None:
            pen_black = QPen(QColor(0, 0, 0), 1.0)
            pen_black.setCosmetic(True)
            painter.setPen(pen_black)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.marching_ants_path)

            pen_white = QPen(QColor(255, 255, 255), 1.0, Qt.DashLine)
            pen_white.setCosmetic(True)
            pen_white.setDashPattern([4, 4])
            pen_white.setDashOffset(self.marching_offset)
            painter.setPen(pen_white)
            painter.drawPath(self.marching_ants_path)

        elif self.selection_rect is not None:
            pen_b = QPen(QColor(0,0,0), 1.0); pen_b.setCosmetic(True)
            painter.setPen(pen_b); painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.selection_rect)
            pen_w = QPen(QColor(255,255,255), 1.0, Qt.DashLine); pen_w.setCosmetic(True)
            pen_w.setDashPattern([4,4]); pen_w.setDashOffset(self.marching_offset)
            painter.setPen(pen_w)
            painter.drawRect(self.selection_rect)

        # Lasso in-progress
        if self.drawing and self.editor.current_tool == "lasso" and len(self._lasso_points) > 1:
            pen_l = QPen(QColor(255,255,255), 1.0, Qt.DashLine); pen_l.setCosmetic(True)
            painter.setPen(pen_l)
            for i in range(len(self._lasso_points) - 1):
                painter.drawLine(self._lasso_points[i], self._lasso_points[i+1])

        self._draw_path_preview(painter)

        # Crop overlay
        if self.crop_rect is not None:
            pen_c = QPen(QColor("#00aaff"), 2.0); pen_c.setCosmetic(True)
            painter.setPen(pen_c); painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.crop_rect)
            ov = QPainterPath()
            ov.addRect(QRectF(0, 0, doc_width, doc_height))
            inn = QPainterPath(); inn.addRect(self.crop_rect)
            painter.fillPath(ov.subtracted(inn), QColor(0, 0, 0, 120))

        if self.shape_rect is not None:
            pen_s = QPen(QColor("#f5c542"), 1.5, Qt.DashLine); pen_s.setCosmetic(True)
            painter.setPen(pen_s); painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.shape_rect)

        painter.restore()
        self._draw_rulers(painter, doc_width, doc_height)
        painter.end()

    def mousePressEvent(self, event):
        img_pos = self.canvas_to_image(QPointF(event.pos()))
        tool = self.editor.current_tool
        img_pos = self.snap_image_pos(img_pos, tool)

        if event.button() == Qt.LeftButton and tool == "zoom":
            self.viewport.zoom_at(QPointF(event.pos()), 1.25)
            self.update()
            return

        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and tool == "hand") or (event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier and tool != "clone_stamp"):
            self.panning = True
            self.pan_start = QPointF(event.pos()) - self.pan_offset
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() == Qt.LeftButton:
            if not self.editor.layers: return
            ix, iy = int(img_pos.x()), int(img_pos.y())
            layer = self.editor.active_layer()
            if layer is None: return
            w, h = layer.image.size

            if tool == "move":
                self.last_pos = img_pos; self.drawing = True
            elif tool == "brush":
                self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
                self.drawing = True; self.last_pos = img_pos
                self._draw_brush(ix, iy); self.update()
            elif tool == "eraser":
                self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
                self.drawing = True; self.last_pos = img_pos
                self._draw_eraser(ix, iy); self.update()
            elif tool == "eyedropper":
                if 0 <= ix < w and 0 <= iy < h:
                    comp = self.editor.get_composite()
                    if comp:
                        r, g, b, a = comp.getpixel((ix, iy))
                        self.color_picked.emit(QColor(r, g, b))
            elif tool == "fill":
                self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
                self._flood_fill(ix, iy); self.update()
            elif tool == "magic_wand":
                self._magic_wand_select(ix, iy); self.update()
            elif tool in ("select_rect", "select_ellipse"):
                self.selection_start = img_pos
                self.selection_rect = None; self.set_selection_mask(None)
                self.drawing = True
            elif tool == "crop":
                self.selection_start = img_pos; self.crop_rect = None; self.drawing = True
            elif tool == "shape":
                self.selection_start = img_pos; self.shape_rect = None; self.drawing = True
            elif tool == "pen":
                self.editor.add_path_point(ix, iy)
            elif tool == "text":
                self.editor.insert_text_at(ix, iy)
            elif tool == "lasso":
                self._lasso_points = [img_pos]; self.drawing = True
            elif tool == "clone_stamp":
                if event.modifiers() & Qt.AltModifier:
                    self.editor.clone_source = (ix, iy)
                    self.editor.statusBar().showMessage(f"Clone source set to ({ix}, {iy})")
                elif self.editor.clone_source:
                    self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
                    self.drawing = True; self.last_pos = img_pos
                    self._draw_clone_stamp(ix, iy)
            elif tool in self._retouch_tools:
                self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
                self.drawing = True; self.last_pos = img_pos
                self._draw_retouch(ix, iy, tool); self.update()

    def mouseMoveEvent(self, event):
        img_pos = self.canvas_to_image(QPointF(event.pos()))
        tool = self.editor.current_tool
        img_pos = self.snap_image_pos(img_pos, tool)
        ix, iy = int(img_pos.x()), int(img_pos.y())

        if self.editor.layers:
            layer = self.editor.active_layer()
            if layer:
                w, h = layer.image.size
                if 0 <= ix < w and 0 <= iy < h:
                    self.editor.update_info_panel(ix, iy, layer.image.getpixel((ix, iy)))
                    self.editor.statusBar().showMessage(
                        f"X: {ix}  Y: {iy}  |  Zoom: {self.zoom:.0%}  |  Tool: {self.editor.current_tool}")

        if self.panning:
            self.pan_offset = QPointF(event.pos()) - self.pan_start; self.update(); return

        if self.drawing and event.buttons() & Qt.LeftButton:
            if tool == "brush":
                self.last_pos = self._draw_brush_line(self.last_pos, img_pos); self.update()
            elif tool == "eraser":
                self.last_pos = self._draw_eraser_line(self.last_pos, img_pos); self.update()
            elif tool == "move":
                dx, dy = img_pos.x() - self.last_pos.x(), img_pos.y() - self.last_pos.y()
                layer = self.editor.active_layer()
                if layer and not layer.locked:
                    self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
                    new_img = Image.new("RGBA", layer.image.size, (0,0,0,0))
                    new_img.paste(layer.image, (int(dx), int(dy)))
                    layer.image = new_img; self.last_pos = img_pos; self.update()
            elif tool in ("select_rect", "select_ellipse") and self.selection_start:
                x1, y1 = self.selection_start.x(), self.selection_start.y()
                x2, y2 = img_pos.x(), img_pos.y()
                self.selection_rect = QRectF(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
                self.update()
            elif tool == "crop" and self.selection_start:
                x1, y1 = self.selection_start.x(), self.selection_start.y()
                x2, y2 = img_pos.x(), img_pos.y()
                self.crop_rect = QRectF(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
                self.update()
            elif tool == "shape" and self.selection_start:
                x1, y1 = self.selection_start.x(), self.selection_start.y()
                x2, y2 = img_pos.x(), img_pos.y()
                self.shape_rect = QRectF(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
                self.update()
            elif tool == "lasso":
                self._lasso_points.append(img_pos); self.update()
            elif tool == "clone_stamp":
                self._draw_clone_stamp(ix, iy); self.last_pos = img_pos; self.update()
            elif tool in self._retouch_tools:
                self.last_pos = self._draw_retouch_line(self.last_pos, img_pos, tool); self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton or (self.panning and event.button() == Qt.LeftButton):
            self.panning = False; self.setCursor(Qt.ArrowCursor); return

        if event.button() == Qt.LeftButton:
            tool = self.editor.current_tool

            if tool in ("select_rect", "select_ellipse") and self.selection_rect:
                layer = self.editor.active_layer()
                if layer:
                    w, h = layer.image.size
                    mask = Image.new("L", (w, h), 0)
                    draw = ImageDraw.Draw(mask)
                    r = self.selection_rect
                    box = (int(r.x()), int(r.y()), int(r.x()+r.width()), int(r.y()+r.height()))
                    if tool == "select_rect":
                        draw.rectangle(box, fill=255)
                    else:
                        draw.ellipse(box, fill=255)
                    self.set_selection_mask(mask)
                    self.selection_rect = None

            elif tool == "lasso" and len(self._lasso_points) > 2:
                layer = self.editor.active_layer()
                if layer:
                    w, h = layer.image.size
                    mask = Image.new("L", (w, h), 0)
                    draw = ImageDraw.Draw(mask)
                    pts = [(int(pt.x()), int(pt.y())) for pt in self._lasso_points]
                    draw.polygon(pts, fill=255)
                    self.set_selection_mask(mask)
                    self.selection_rect = None
                self._lasso_points = []

            elif tool == "shape" and self.shape_rect:
                self.editor.add_shape_layer(self.shape_rect)
                self.shape_rect = None

            self.drawing = False
            self.update()
            self.editor.update_layer_panel()

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        cp = QPointF(event.pos())
        self.viewport.zoom_at(cp, factor)
        self.update()

    def tabletEvent(self, event):
        pressure = float(event.pressure())
        self.tablet_pressure = 1.0 if pressure <= 0 else max(0.01, min(1.0, pressure))
        event.ignore()

    # Drawing helpers
    def _draw_brush(self, x, y):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return
        color = qcolor_to_rgba(self.editor.fg_color, self.editor.brush_opacity)
        settings = self.editor.brush_settings()
        paint_brush_stroke(layer.image, x, y, x, y, settings, color, self.tablet_pressure)

    def _draw_brush_line(self, p1, p2):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return p2
        settings = self.editor.brush_settings()
        p2 = self._smooth_brush_point(p1, p2, settings)
        color = qcolor_to_rgba(self.editor.fg_color, self.editor.brush_opacity)
        x1, y1, x2, y2 = int(p1.x()), int(p1.y()), int(p2.x()), int(p2.y())
        paint_brush_stroke(layer.image, x1, y1, x2, y2, settings, color, self.tablet_pressure)
        return p2

    def _draw_eraser(self, x, y):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return
        erase_brush_stroke(layer.image, x, y, x, y, self.editor.brush_settings(), self.tablet_pressure)

    def _draw_eraser_line(self, p1, p2):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return p2
        settings = self.editor.brush_settings()
        p2 = self._smooth_brush_point(p1, p2, settings)
        x1, y1, x2, y2 = int(p1.x()), int(p1.y()), int(p2.x()), int(p2.y())
        erase_brush_stroke(layer.image, x1, y1, x2, y2, settings, self.tablet_pressure)
        return p2

    def _smooth_brush_point(self, p1, p2, settings):
        x, y = smoothed_brush_point((p1.x(), p1.y()), (p2.x(), p2.y()), settings.smoothing)
        return QPointF(x, y)

    def _draw_retouch(self, x, y, mode):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return
        apply_retouch_dab(layer.image, x, y, self.editor.brush_size, mode)

    def _draw_retouch_line(self, p1, p2, mode):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return p2
        settings = self.editor.brush_settings()
        p2 = self._smooth_brush_point(p1, p2, settings)
        for x, y, size, _index in iter_brush_dabs(int(p1.x()), int(p1.y()), int(p2.x()), int(p2.y()), settings, self.tablet_pressure):
            apply_retouch_dab(layer.image, x, y, size, mode)
        return p2

    def _flood_fill(self, x, y):
        layer = self.editor.active_layer()
        if not layer or layer.locked: return
        w, h = layer.image.size
        if x < 0 or x >= w or y < 0 or y >= h: return
        pixels = layer.image.load()
        target = pixels[x, y]
        fill_color = qcolor_to_rgba(self.editor.fg_color, self.editor.brush_opacity)
        if target == fill_color: return
        tol = self.editor.magic_wand_tolerance
        def match(c1, c2): return all(abs(a-b) <= tol for a, b in zip(c1[:3], c2[:3]))
        visited = set(); stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited: continue
            if cx < 0 or cx >= w or cy < 0 or cy >= h: continue
            if not match(pixels[cx, cy], target): continue
            visited.add((cx, cy)); pixels[cx, cy] = fill_color
            stack.extend([(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)])

    def _magic_wand_select(self, x, y):
        """Magic wand selection - fast scanline flood fill for contiguous, vectorized for non-contiguous."""
        layer = self.editor.active_layer()
        if not layer: return
        w, h = layer.image.size
        if x < 0 or x >= w or y < 0 or y >= h: return

        source = self.editor.get_composite() if self.editor.magic_wand_sample_all else layer.image
        src_np = np.array(source).astype(np.int16)
        target = src_np[y, x, :3].copy()
        tol = self.editor.magic_wand_tolerance

        # Vectorized color match for ALL pixels at once
        diff = np.abs(src_np[:, :, :3] - target.reshape(1, 1, 3))
        match_all = np.all(diff <= tol, axis=2)  # boolean (h, w)

        if self.editor.magic_wand_contiguous:
            # Fast scanline flood fill on the boolean match mask
            mask = np.zeros((h, w), dtype=np.uint8)
            if not match_all[y, x]:
                new_mask = Image.fromarray(mask, "L")
            else:
                # Scanline fill using a stack of (x, y) seed points
                stack = [(x, y)]
                mask[y, x] = 255
                while stack:
                    sx, sy = stack.pop()
                    # Scan left
                    lx = sx
                    while lx > 0 and match_all[sy, lx - 1] and mask[sy, lx - 1] == 0:
                        lx -= 1
                        mask[sy, lx] = 255
                    # Scan right
                    rx = sx
                    while rx < w - 1 and match_all[sy, rx + 1] and mask[sy, rx + 1] == 0:
                        rx += 1
                        mask[sy, rx] = 255
                    # Check rows above and below for new seeds
                    for ny in [sy - 1, sy + 1]:
                        if ny < 0 or ny >= h:
                            continue
                        span_started = False
                        for nx in range(lx, rx + 1):
                            if match_all[ny, nx] and mask[ny, nx] == 0:
                                if not span_started:
                                    stack.append((nx, ny))
                                    mask[ny, nx] = 255
                                    span_started = True
                            else:
                                span_started = False
                new_mask = Image.fromarray(mask, "L")
        else:
            mask = np.where(match_all, 255, 0).astype(np.uint8)
            new_mask = Image.fromarray(mask, "L")

        mods = QApplication.keyboardModifiers()
        if mods & Qt.ShiftModifier and self.selection_mask is not None:
            self.set_selection_mask(ImageChops.lighter(self.selection_mask, new_mask))
        elif mods & Qt.AltModifier and self.selection_mask is not None:
            self.set_selection_mask(ImageChops.darker(self.selection_mask, ImageChops.invert(new_mask)))
        else:
            self.set_selection_mask(new_mask)

        self.selection_rect = None
        count = np.count_nonzero(mask)
        self.editor.statusBar().showMessage(
            f"Magic Wand: {count} pixels selected (tolerance={tol})")

    def _draw_clone_stamp(self, x, y):
        layer = self.editor.active_layer()
        if not layer or layer.locked or not self.editor.clone_source: return
        sx, sy = self.editor.clone_source
        if self.last_pos:
            dx, dy = x - int(self.last_pos.x()), y - int(self.last_pos.y())
        else:
            dx, dy = 0, 0
        self.editor.clone_source = (sx+dx, sy+dy)
        sz = self.editor.brush_size
        try:
            src = layer.image.crop((sx-sz//2, sy-sz//2, sx+sz//2, sy+sz//2))
            m = Image.new("L", (sz, sz), 0)
            ImageDraw.Draw(m).ellipse((0, 0, sz, sz), fill=255)
            layer.image.paste(src, (x-sz//2, y-sz//2), m)
        except: pass

    def clear_selection(self):
        self.selection_mask = None; self.marching_ants_path = None
        self.selection_rect = None; self.update()


def pil_to_qpixmap(image, max_size):
    if image is None:
        return QPixmap()
    preview = image.copy()
    preview.thumbnail(max_size, Image.LANCZOS)
    data = preview.tobytes("raw", "RGBA")
    qimg = QImage(data, preview.width, preview.height, QImage.Format_RGBA8888).copy()
    return QPixmap.fromImage(qimg)


class NavigatorPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.preview = QLabel("No image")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(120)
        layout.addWidget(self.preview)

    def refresh(self):
        composite = self.editor.get_composite()
        if composite is None:
            self.preview.setText("No image")
            self.preview.setPixmap(QPixmap())
            return
        self.preview.setText("")
        self.preview.setPixmap(pil_to_qpixmap(composite, (220, 140)))


class HistogramPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.histogram = QLabel("No image")
        self.histogram.setAlignment(Qt.AlignCenter)
        self.histogram.setMinimumHeight(90)
        layout.addWidget(self.histogram)

    def refresh(self):
        composite = self.editor.get_composite()
        if composite is None:
            self.histogram.setText("No image")
            self.histogram.setPixmap(QPixmap())
            return
        pixmap = QPixmap(220, 90)
        pixmap.fill(QColor("#1e1e1e"))
        painter = QPainter(pixmap)
        rgb_hist = composite.convert("RGB").histogram()
        colors = [QColor(255, 80, 80, 150), QColor(80, 220, 120, 150), QColor(80, 160, 255, 150)]
        width, height = pixmap.width(), pixmap.height()
        for channel in range(3):
            hist = rgb_hist[channel * 256:(channel + 1) * 256]
            peak = max(hist) or 1
            painter.setPen(colors[channel])
            for x in range(width):
                bucket = min(255, int(x * 256 / width))
                bar = int(hist[bucket] / peak * (height - 8))
                painter.drawLine(x, height - 4, x, height - 4 - bar)
        painter.end()
        self.histogram.setText("")
        self.histogram.setPixmap(pixmap)


class InfoPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.document_label = QLabel("Document: -")
        self.cursor_label = QLabel("Cursor: -")
        self.color_label = QLabel("Color: -")
        self.zoom_label = QLabel("Zoom: 100%")
        self.layer_label = QLabel("Layer: -")
        for label in [self.document_label, self.cursor_label, self.color_label, self.zoom_label, self.layer_label]:
            layout.addWidget(label)
        layout.addStretch(1)

    def refresh_document(self):
        if self.editor.layers:
            width, height = self.editor.layers[0].image.size
            self.document_label.setText(f"Document: {width} x {height}")
        else:
            self.document_label.setText("Document: -")
        layer = self.editor.active_layer()
        self.layer_label.setText(f"Layer: {layer.name}" if layer else "Layer: -")
        self.zoom_label.setText(f"Zoom: {self.editor.canvas.zoom:.0%}")

    def update_cursor(self, x, y, color=None):
        self.cursor_label.setText(f"Cursor: {x}, {y}")
        if color is None:
            self.color_label.setText("Color: -")
        else:
            red, green, blue, alpha = color
            self.color_label.setText(f"Color: {red}, {green}, {blue}, {alpha}")


class ChannelPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.checks = {}
        for key, label in [("red", "Red"), ("green", "Green"), ("blue", "Blue"), ("alpha", "Alpha")]:
            check = QCheckBox(label)
            check.setChecked(True)
            check.toggled.connect(lambda value, channel=key: self.set_channel(channel, value))
            self.checks[key] = check
            layout.addWidget(check)
        layout.addStretch(1)

    def set_channel(self, channel, visible):
        self.editor.channel_visibility[channel] = visible
        self.editor.canvas.update()
        self.editor.refresh_analysis_panels()

    def refresh(self):
        for channel, check in self.checks.items():
            check.blockSignals(True)
            check.setChecked(self.editor.channel_visibility.get(channel, True))
            check.blockSignals(False)


class PathsPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.status = QLabel("Path: 0 points")
        layout.addWidget(self.status)
        row = QHBoxLayout()
        for label, callback in [("Close", self.editor.close_path), ("Select", self.editor.path_to_selection), ("Clear", self.editor.clear_path)]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)
        layout.addStretch(1)

    def refresh(self):
        suffix = " closed" if self.editor.current_path_closed else ""
        self.status.setText(f"Path: {len(self.editor.current_path)} points{suffix}")


# ---- Layer Panel -----------------------------------------------------------
class LayerPanel(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4,4,4,4); layout.setSpacing(4)

        top = QHBoxLayout()
        self.blend_combo = QComboBox()
        self.blend_combo.addItems(Layer.BLEND_MODES)
        self.blend_combo.currentTextChanged.connect(self.on_blend_change)
        top.addWidget(QLabel("Blend:")); top.addWidget(self.blend_combo)
        layout.addLayout(top)

        orow = QHBoxLayout(); orow.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal); self.opacity_slider.setRange(0,255); self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self.on_opacity_change)
        orow.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("100%"); self.opacity_label.setFixedWidth(40)
        orow.addWidget(self.opacity_label); layout.addLayout(orow)

        self.layer_list = QListWidget()
        self.layer_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.layer_list.currentRowChanged.connect(self.on_layer_selected)
        self.layer_list.model().rowsMoved.connect(self.on_layers_reordered)
        layout.addWidget(self.layer_list)

        bl = QHBoxLayout()
        for t, cb in [("+", self.add_layer), ("-", self.remove_layer),
                       ("Dup", self.duplicate_layer), ("Up", self.move_up), ("Dn", self.move_down)]:
            b = QPushButton(t); b.setFixedWidth(40); b.clicked.connect(cb); bl.addWidget(b)
        layout.addLayout(bl)

        vl = QHBoxLayout()
        self.vis_check = QCheckBox("Visible"); self.vis_check.setChecked(True)
        self.vis_check.toggled.connect(self.on_visibility_toggle); vl.addWidget(self.vis_check)
        self.lock_check = QCheckBox("Lock")
        self.lock_check.toggled.connect(self.on_lock_toggle); vl.addWidget(self.lock_check)
        self.clip_check = QCheckBox("Clip")
        self.clip_check.toggled.connect(self.on_clipping_toggle); vl.addWidget(self.clip_check)
        layout.addLayout(vl)

        ml = QHBoxLayout()
        self.group_btn = QPushButton("Group"); self.group_btn.clicked.connect(self.group_active_layer); ml.addWidget(self.group_btn)
        self.adjustment_btn = QPushButton("Adj"); self.adjustment_btn.clicked.connect(self.add_adjustment_layer); ml.addWidget(self.adjustment_btn)
        self.mask_btn = QPushButton("Mask"); self.mask_btn.clicked.connect(self.add_layer_mask); ml.addWidget(self.mask_btn)
        ml.addWidget(QLabel("Density:"))
        self.mask_density_slider = QSlider(Qt.Horizontal); self.mask_density_slider.setRange(0, 100); self.mask_density_slider.setValue(100)
        self.mask_density_slider.valueChanged.connect(self.on_mask_density_change); ml.addWidget(self.mask_density_slider)
        layout.addLayout(ml)

        fl = QHBoxLayout(); fl.addWidget(QLabel("Feather:"))
        self.mask_feather_spin = QSpinBox(); self.mask_feather_spin.setRange(0, 100)
        self.mask_feather_spin.valueChanged.connect(self.on_mask_feather_change); fl.addWidget(self.mask_feather_spin)
        layout.addLayout(fl)

    def refresh(self):
        self.layer_list.blockSignals(True); self.layer_list.clear()
        for i, layer in enumerate(reversed(self.editor.layers)):
            idx = len(self.editor.layers) - 1 - i
            vis = "V " if layer.visible else "  "
            lock = " [L]" if layer.locked else ""
            mask = " [M]" if layer.mask is not None else ""
            clip = " [C]" if layer.clipping else ""
            adjustment = " [A]" if layer.adjustment else ""
            group = " [G]" if layer.is_group else ""
            vector = " [V]" if layer.vector_shape else ""
            text = " [T]" if layer.text_item else ""
            prefix = "  " if layer.group_id and not layer.is_group else ""
            item = QListWidgetItem(f"{prefix}{vis}{layer.name}{lock}{mask}{clip}{adjustment}{group}{vector}{text}")
            item.setData(Qt.UserRole, idx)
            self.layer_list.addItem(item)
        active = self.editor.active_layer_index
        di = len(self.editor.layers) - 1 - active
        if 0 <= di < self.layer_list.count(): self.layer_list.setCurrentRow(di)
        layer = self.editor.active_layer()
        if layer:
            self.opacity_slider.blockSignals(True); self.opacity_slider.setValue(layer.opacity); self.opacity_slider.blockSignals(False)
            self.opacity_label.setText(f"{layer.opacity*100//255}%")
            self.vis_check.blockSignals(True); self.vis_check.setChecked(layer.visible); self.vis_check.blockSignals(False)
            self.lock_check.blockSignals(True); self.lock_check.setChecked(layer.locked); self.lock_check.blockSignals(False)
            self.clip_check.blockSignals(True); self.clip_check.setChecked(layer.clipping); self.clip_check.blockSignals(False)
            has_mask = layer.mask is not None
            self.mask_density_slider.blockSignals(True); self.mask_density_slider.setValue(layer.mask_density); self.mask_density_slider.blockSignals(False)
            self.mask_density_slider.setEnabled(has_mask)
            self.mask_feather_spin.blockSignals(True); self.mask_feather_spin.setValue(layer.mask_feather); self.mask_feather_spin.blockSignals(False)
            self.mask_feather_spin.setEnabled(has_mask)
            self.blend_combo.blockSignals(True)
            idx = self.blend_combo.findText(layer.blend_mode)
            if idx >= 0: self.blend_combo.setCurrentIndex(idx)
            self.blend_combo.blockSignals(False)
        self.layer_list.blockSignals(False)

    def on_layer_selected(self, row):
        if row < 0: return
        item = self.layer_list.item(row)
        if item:
            self.editor.set_active_layer_index(item.data(Qt.UserRole))
            self.editor.canvas.update()

    def on_layers_reordered(self):
        new = []
        for i in range(self.layer_list.count()):
            new.append(self.editor.layers[self.layer_list.item(i).data(Qt.UserRole)])
        new.reverse(); self.editor.layers = new
        self.editor.set_active_layer_index(self.editor.active_layer_index)
        self.editor.notify_layers_changed(); self.editor.canvas.update()

    def on_opacity_change(self, v):
        layer = self.editor.active_layer()
        if layer: layer.opacity = v; self.opacity_label.setText(f"{v*100//255}%"); self.editor.canvas.update()

    def on_blend_change(self, mode):
        layer = self.editor.active_layer()
        if layer: layer.blend_mode = mode; self.editor.canvas.update()

    def on_visibility_toggle(self, checked):
        layer = self.editor.active_layer()
        if layer: layer.visible = checked; self.editor.notify_layers_changed(); self.editor.canvas.update()

    def on_lock_toggle(self, checked):
        layer = self.editor.active_layer()
        if layer: layer.locked = checked; self.editor.notify_layers_changed()

    def on_clipping_toggle(self, checked):
        layer = self.editor.active_layer()
        if layer:
            layer.clipping = checked
            self.editor.notify_layers_changed(); self.editor.canvas.update()

    def add_layer_mask(self):
        layer = self.editor.active_layer()
        if not layer: return
        self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
        if self.editor.canvas.selection_mask is not None:
            layer.mask = self.editor.canvas.selection_mask.convert("L").copy()
        else:
            layer.mask = Image.new("L", layer.image.size, 255)
        layer.mask_density = 100
        layer.mask_feather = 0
        self.editor.notify_layers_changed(); self.editor.canvas.update()

    def add_adjustment_layer(self):
        if not self.editor.layers: return
        dlg = QDialog(self); dlg.setWindowTitle("New Adjustment Layer"); form = QFormLayout(dlg)
        kind = QComboBox(); kind.addItems(["Brightness/Contrast", "Hue/Saturation", "Invert", "Grayscale"])
        form.addRow("Type:", kind)
        brightness = QSpinBox(); brightness.setRange(-100, 100); form.addRow("Brightness:", brightness)
        contrast = QSpinBox(); contrast.setRange(-100, 100); form.addRow("Contrast:", contrast)
        hue = QSpinBox(); hue.setRange(-180, 180); form.addRow("Hue:", hue)
        saturation = QSpinBox(); saturation.setRange(-100, 100); form.addRow("Saturation:", saturation)
        lightness = QSpinBox(); lightness.setRange(-100, 100); form.addRow("Lightness:", lightness)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() != QDialog.Accepted:
            return

        selected = kind.currentText()
        if selected == "Brightness/Contrast":
            adjustment = {"type": "brightness_contrast", "brightness": brightness.value(), "contrast": contrast.value()}
        elif selected == "Hue/Saturation":
            adjustment = {"type": "hue_saturation", "hue": hue.value(), "saturation": saturation.value(), "lightness": lightness.value()}
        elif selected == "Invert":
            adjustment = {"type": "invert"}
        else:
            adjustment = {"type": "grayscale"}

        w, h = self.editor.layers[0].image.size
        layer = Layer(f"{selected} Adjustment", w, h)
        layer.adjustment = adjustment
        self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
        insert_at = self.editor.active_layer_index + 1
        self.editor.layers.insert(insert_at, layer)
        self.editor.set_active_layer_index(insert_at)
        self.editor.notify_layers_changed(); self.editor.canvas.update()

    def group_active_layer(self):
        layer = self.editor.active_layer()
        if not layer or layer.is_group:
            return
        w, h = self.editor.layers[0].image.size
        group_number = 1 + sum(1 for existing in self.editor.layers if existing.is_group)
        group_id = f"group-{group_number}"
        self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)

        group = Layer(f"Group {group_number}", w, h)
        group.is_group = True
        group.group_id = group_id
        layer.group_id = group_id

        insert_at = self.editor.active_layer_index
        self.editor.layers.insert(insert_at, group)
        self.editor.set_active_layer_index(insert_at)
        self.editor.notify_layers_changed(); self.editor.canvas.update()

    def on_mask_density_change(self, value):
        layer = self.editor.active_layer()
        if layer and layer.mask is not None:
            layer.mask_density = value
            self.editor.notify_layers_changed(); self.editor.canvas.update()

    def on_mask_feather_change(self, value):
        layer = self.editor.active_layer()
        if layer and layer.mask is not None:
            layer.mask_feather = value
            self.editor.notify_layers_changed(); self.editor.canvas.update()

    def add_layer(self):
        if not self.editor.layers: return
        w, h = self.editor.layers[0].image.size
        self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
        name, ok = QInputDialog.getText(self, "New Layer", "Layer name:", text=f"Layer {len(self.editor.layers)+1}")
        if ok and name:
            self.editor.layers.append(Layer(name, w, h))
            self.editor.set_active_layer_index(len(self.editor.layers) - 1)
            self.editor.notify_layers_changed(); self.editor.canvas.update()

    def remove_layer(self):
        if len(self.editor.layers) <= 1: return
        self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
        del self.editor.layers[self.editor.active_layer_index]
        self.editor.set_active_layer_index(max(0, self.editor.active_layer_index - 1))
        self.editor.notify_layers_changed(); self.editor.canvas.update()

    def duplicate_layer(self):
        layer = self.editor.active_layer()
        if layer:
            self.editor.history.save_state(self.editor.layers, self.editor.active_layer_index)
            self.editor.layers.insert(self.editor.active_layer_index + 1, layer.copy())
            self.editor.set_active_layer_index(self.editor.active_layer_index + 1)
            self.editor.notify_layers_changed(); self.editor.canvas.update()

    def move_up(self):
        idx = self.editor.active_layer_index
        if idx < len(self.editor.layers) - 1:
            self.editor.layers[idx], self.editor.layers[idx+1] = self.editor.layers[idx+1], self.editor.layers[idx]
            self.editor.set_active_layer_index(idx + 1); self.editor.notify_layers_changed(); self.editor.canvas.update()

    def move_down(self):
        idx = self.editor.active_layer_index
        if idx > 0:
            self.editor.layers[idx], self.editor.layers[idx-1] = self.editor.layers[idx-1], self.editor.layers[idx]
            self.editor.set_active_layer_index(idx - 1); self.editor.notify_layers_changed(); self.editor.canvas.update()


# ---- Main Editor -----------------------------------------------------------
class ImageEditor(QMainWindow):
    layers_changed = pyqtSignal()
    active_layer_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_DISPLAY_NAME} - Image Editor")
        self.setMinimumSize(1200, 800)
        self.layers = []; self.active_layer_index = 0
        self.current_tool = "brush"
        self.fg_color = QColor(255,255,255); self.bg_color = QColor(0,0,0)
        self.brush_size = 10; self.brush_opacity = 255
        self.brush_spacing = 25; self.brush_smoothing = 0; self.brush_scatter = 0
        self.brush_texture = 0; self.brush_color_jitter = 0
        self.brush_pressure_size = False; self.brush_pressure_opacity = False
        self.magic_wand_tolerance = 32; self.magic_wand_contiguous = True; self.magic_wand_sample_all = False
        self.show_grid = False; self.show_guides = True; self.show_rulers = True; self.snap_enabled = True
        self.grid_size = 64; self.guides = []
        self.channel_visibility = {"red": True, "green": True, "blue": True, "alpha": True}
        self.current_path = []; self.current_path_closed = False
        self.macro_recording = False; self.macro_replaying = False; self.macro_steps = []
        self.workspace_preset = None; self.docks = {}
        self.clone_source = None; self.history = HistoryManager(); self.file_path = None
        self.init_ui(); self.showMaximized()

    def active_layer(self):
        if 0 <= self.active_layer_index < len(self.layers): return self.layers[self.active_layer_index]
        return None

    def brush_settings(self):
        return BrushSettings(
            size=self.brush_size,
            opacity=self.brush_opacity,
            spacing=self.brush_spacing,
            smoothing=self.brush_smoothing,
            scatter=self.brush_scatter,
            texture=self.brush_texture,
            color_jitter=self.brush_color_jitter,
            pressure_size=self.brush_pressure_size,
            pressure_opacity=self.brush_pressure_opacity,
        )

    def init_ui(self):
        self.canvas = CanvasWidget(self)
        self.canvas.color_picked.connect(self.set_fg_color)
        self.setCentralWidget(self.canvas)
        self.create_menus(); self.create_toolbars(); self.create_panels()
        self.statusBar().showMessage("Ready")

    def create_menus(self):
        mb = self.menuBar()
        fm = mb.addMenu("&File")
        self._act(fm, "&New...", "Ctrl+N", self.new_image)
        self._act(fm, "&Open...", "Ctrl+O", self.open_image)
        fm.addSeparator()
        self._act(fm, "&Save", "Ctrl+S", self.save_image)
        self._act(fm, "Save &As...", "Ctrl+Shift+S", self.save_image_as)
        self._act(fm, "E&xport PNG...", "", self.export_png)
        self._act(fm, "Export Flattened PSD...", "", self.export_flattened_psd)
        fm.addSeparator()
        self._act(fm, "E&xit", "Ctrl+Q", self.close)

        em = mb.addMenu("&Edit")
        self._act(em, "&Undo", "Ctrl+Z", self.undo)
        self._act(em, "&Redo", "Ctrl+Y", self.redo)
        em.addSeparator()
        self._act(em, "Cu&t", "Ctrl+X", self.cut_selection)
        self._act(em, "&Copy", "Ctrl+C", self.copy_selection)
        self._act(em, "&Paste", "Ctrl+V", self.paste_clipboard)
        self._act(em, "&Delete", "Delete", self.delete_selection)
        em.addSeparator()
        self._act(em, "Select &All", "Ctrl+A", self.select_all)
        self._act(em, "&Deselect", "Ctrl+D", self.deselect)
        self._act(em, "&Invert Selection", "Ctrl+Shift+I", self.invert_selection)

        im = mb.addMenu("&Image")
        self._act(im, "&Resize Canvas...", "", self.resize_canvas)
        self._act(im, "Resize &Image...", "", self.resize_image)
        im.addSeparator()
        self._act(im, "Rotate 90 CW", "", lambda: self.rotate_image(90))
        self._act(im, "Rotate 90 CCW", "", lambda: self.rotate_image(-90))
        self._act(im, "Rotate 180", "", lambda: self.rotate_image(180))
        im.addSeparator()
        self._act(im, "Flip Horizontal", "", lambda: self.flip_image("h"))
        self._act(im, "Flip Vertical", "", lambda: self.flip_image("v"))
        im.addSeparator()
        self._act(im, "Flatten Image", "", self.flatten_image)
        self._act(im, "Merge Down", "", self.merge_down)
        im.addSeparator()
        self._act(im, "Crop to Selection", "", self.crop_to_selection)
        self._act(im, "Apply Crop", "", self.apply_crop)

        lm = mb.addMenu("&Layer")
        self._act(lm, "New Layer...", "", lambda: self.layer_panel.add_layer())
        self._act(lm, "Duplicate Layer", "", lambda: self.layer_panel.duplicate_layer())
        self._act(lm, "Delete Layer", "", lambda: self.layer_panel.remove_layer())
        lm.addSeparator()
        self._act(lm, "Group Active Layer", "", lambda: self.layer_panel.group_active_layer())
        self._act(lm, "Layer Mask From Selection", "", lambda: self.layer_panel.add_layer_mask())
        self._act(lm, "New Adjustment Layer...", "", lambda: self.layer_panel.add_adjustment_layer())
        self._act(lm, "Toggle Clipping Mask", "", self.toggle_active_clipping)
        lm.addSeparator()
        self._act(lm, "Merge Down", "", self.merge_down)
        self._act(lm, "Flatten Image", "", self.flatten_image)

        tm = mb.addMenu("&Type")
        self._act(tm, "Text Tool", "", lambda: self.set_tool("text"))
        self._act(tm, "Insert Text at Origin...", "", lambda: self.insert_text_at(10, 10))

        smenu = mb.addMenu("&Select")
        self._act(smenu, "Select All", "", self.select_all)
        self._act(smenu, "Deselect", "", self.deselect)
        self._act(smenu, "Invert Selection", "", self.invert_selection)

        am = mb.addMenu("&Adjustments")
        self._act(am, "&Brightness/Contrast...", "", self.adjust_brightness_contrast)
        self._act(am, "&Hue/Saturation...", "", self.adjust_hue_saturation)
        self._act(am, "&Levels...", "", self.adjust_levels)
        self._act(am, "&Invert Colors", "Ctrl+I", self.invert_colors)
        self._act(am, "&Grayscale", "", self.grayscale)
        self._act(am, "&Auto Contrast", "", self.auto_contrast)
        self._act(am, "Color &Balance...", "", self.color_balance)

        flm = mb.addMenu("&Filter")
        bm = flm.addMenu("Blur")
        self._act(bm, "Gaussian Blur...", "", self.gaussian_blur)
        self._act(bm, "Box Blur...", "", self.box_blur)
        self._act(bm, "Motion Blur...", "", self.motion_blur)
        sm = flm.addMenu("Sharpen")
        self._act(sm, "Sharpen", "", self.sharpen)
        self._act(sm, "Unsharp Mask...", "", self.unsharp_mask)
        flm.addSeparator()
        self._act(flm, "Edge Detect", "", self.edge_detect)
        self._act(flm, "Emboss", "", self.emboss)
        self._act(flm, "Contour", "", self.contour)
        flm.addSeparator()
        self._act(flm, "Posterize...", "", self.posterize)
        self._act(flm, "Solarize...", "", self.solarize)
        self._act(flm, "Pixelate...", "", self.pixelate)

        vm = mb.addMenu("&View")
        self._act(vm, "Fit in &Window", "Ctrl+0", self.canvas.fit_in_view)
        self._act(vm, "Zoom &In", "Ctrl+=", lambda: self._zoom(1.25))
        self._act(vm, "Zoom &Out", "Ctrl+-", lambda: self._zoom(0.8))
        self._act(vm, "&Actual Size", "Ctrl+1", lambda: self._set_zoom(1.0))
        vm.addSeparator()
        self.rulers_action = self._check_act(vm, "Show Rulers", self.show_rulers, self.set_show_rulers)
        self.grid_action = self._check_act(vm, "Show Grid", self.show_grid, self.set_show_grid)
        self.guides_action = self._check_act(vm, "Show Guides", self.show_guides, self.set_show_guides)
        self.snap_action = self._check_act(vm, "Snap", self.snap_enabled, self.set_snap_enabled)
        self._act(vm, "Grid Size...", "", self.set_grid_size)
        self._act(vm, "Add Vertical Guide...", "", lambda: self.add_guide("vertical"))
        self._act(vm, "Add Horizontal Guide...", "", lambda: self.add_guide("horizontal"))
        self._act(vm, "Clear Guides", "", self.clear_guides)

        self.window_menu = mb.addMenu("&Window")
        self._act(self.window_menu, "Save Workspace Preset", "", self.save_workspace_preset)
        self._act(self.window_menu, "Restore Workspace Preset", "", self.restore_workspace_preset)
        self.window_menu.addSeparator()

        amenu = mb.addMenu("&Actions")
        self._act(amenu, "Start Macro Recording", "", self.start_macro_recording)
        self._act(amenu, "Stop Macro Recording", "", self.stop_macro_recording)
        self._act(amenu, "Replay Macro", "", self.replay_macro)
        self._act(amenu, "Clear Macro", "", self.clear_macro)

        hm = mb.addMenu("&Help")
        self._act(hm, "About PyShop", "", self.show_about)

    def _act(self, menu, name, shortcut, cb):
        a = QAction(name, self)
        a.triggered.connect(cb); menu.addAction(a); return a

    def _check_act(self, menu, name, checked, cb):
        action = QAction(name, self)
        action.setCheckable(True)
        action.setChecked(checked)
        action.toggled.connect(cb)
        menu.addAction(action)
        return action

    def create_toolbars(self):
        self.tool_bar = QToolBar("Tools")
        self.tool_bar.setMovable(False); self.tool_bar.setOrientation(Qt.Vertical)
        self.tool_bar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.LeftToolBarArea, self.tool_bar)

        self.tool_group = QActionGroup(self)
        last_group = None
        for tool in DEFAULT_TOOL_REGISTRY:
            if last_group is not None and tool.toolbar_group != last_group:
                self.tool_bar.addSeparator()
            last_group = tool.toolbar_group
            icon = make_tool_icon(tool.icon_id, 32)
            a = QAction(icon, "", self); a.setToolTip(tool.label); a.setCheckable(True); a.setData(tool.tool_id)
            a.triggered.connect(lambda checked, t=tool.tool_id: self.set_tool(t))
            self.tool_group.addAction(a); self.tool_bar.addAction(a)
            if tool.tool_id == "brush": a.setChecked(True)

        self.tool_bar.addSeparator()
        self.fg_btn = QPushButton(); self.fg_btn.setFixedSize(32,32)
        self.fg_btn.setToolTip("Foreground Color"); self.fg_btn.clicked.connect(self.pick_fg_color)
        self.tool_bar.addWidget(self.fg_btn)
        self.bg_btn = QPushButton(); self.bg_btn.setFixedSize(32,32)
        self.bg_btn.setToolTip("Background Color"); self.bg_btn.clicked.connect(self.pick_bg_color)
        self.tool_bar.addWidget(self.bg_btn)
        self.update_color_buttons()
        sb = QPushButton("Swap"); sb.setFixedWidth(36); sb.setToolTip("Swap Colors")
        sb.clicked.connect(self.swap_colors)
        self.tool_bar.addWidget(sb)

        self.options_bar = QToolBar("Tool Options"); self.options_bar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.options_bar)
        self.options_bar.addWidget(QLabel("  Size: "))
        self.size_spin = QSpinBox(); self.size_spin.setRange(1,500); self.size_spin.setValue(self.brush_size)
        self.size_spin.valueChanged.connect(lambda v: setattr(self, 'brush_size', v))
        self.options_bar.addWidget(self.size_spin)
        self.options_bar.addWidget(QLabel("  Opacity: "))
        self.opacity_spin = QSpinBox(); self.opacity_spin.setRange(0,100); self.opacity_spin.setValue(100)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.valueChanged.connect(lambda v: setattr(self, 'brush_opacity', int(v*255/100)))
        self.options_bar.addWidget(self.opacity_spin)
        self.options_bar.addWidget(QLabel("  Spacing: "))
        self.spacing_spin = QSpinBox(); self.spacing_spin.setRange(1,300); self.spacing_spin.setValue(self.brush_spacing)
        self.spacing_spin.setSuffix("%")
        self.spacing_spin.valueChanged.connect(lambda v: setattr(self, 'brush_spacing', v))
        self.options_bar.addWidget(self.spacing_spin)
        self.options_bar.addWidget(QLabel("  Smooth: "))
        self.smoothing_spin = QSpinBox(); self.smoothing_spin.setRange(0,95); self.smoothing_spin.setValue(self.brush_smoothing)
        self.smoothing_spin.setSuffix("%")
        self.smoothing_spin.valueChanged.connect(lambda v: setattr(self, 'brush_smoothing', v))
        self.options_bar.addWidget(self.smoothing_spin)
        self.options_bar.addWidget(QLabel("  Scatter: "))
        self.scatter_spin = QSpinBox(); self.scatter_spin.setRange(0,300); self.scatter_spin.setValue(self.brush_scatter)
        self.scatter_spin.setSuffix("%")
        self.scatter_spin.valueChanged.connect(lambda v: setattr(self, 'brush_scatter', v))
        self.options_bar.addWidget(self.scatter_spin)
        self.options_bar.addWidget(QLabel("  Texture: "))
        self.texture_spin = QSpinBox(); self.texture_spin.setRange(0,100); self.texture_spin.setValue(self.brush_texture)
        self.texture_spin.setSuffix("%")
        self.texture_spin.valueChanged.connect(lambda v: setattr(self, 'brush_texture', v))
        self.options_bar.addWidget(self.texture_spin)
        self.options_bar.addWidget(QLabel("  Jitter: "))
        self.jitter_spin = QSpinBox(); self.jitter_spin.setRange(0,100); self.jitter_spin.setValue(self.brush_color_jitter)
        self.jitter_spin.setSuffix("%")
        self.jitter_spin.valueChanged.connect(lambda v: setattr(self, 'brush_color_jitter', v))
        self.options_bar.addWidget(self.jitter_spin)
        self.pressure_size_check = QCheckBox("Pressure Size")
        self.pressure_size_check.toggled.connect(lambda v: setattr(self, 'brush_pressure_size', v))
        self.options_bar.addWidget(self.pressure_size_check)
        self.pressure_opacity_check = QCheckBox("Pressure Opacity")
        self.pressure_opacity_check.toggled.connect(lambda v: setattr(self, 'brush_pressure_opacity', v))
        self.options_bar.addWidget(self.pressure_opacity_check)
        self.options_bar.addSeparator()
        self.options_bar.addWidget(QLabel("  Tolerance: "))
        self.tolerance_spin = QSpinBox(); self.tolerance_spin.setRange(0,255); self.tolerance_spin.setValue(self.magic_wand_tolerance)
        self.tolerance_spin.valueChanged.connect(lambda v: setattr(self, 'magic_wand_tolerance', v))
        self.options_bar.addWidget(self.tolerance_spin)
        self.contiguous_check = QCheckBox("Contiguous"); self.contiguous_check.setChecked(True)
        self.contiguous_check.toggled.connect(lambda v: setattr(self, 'magic_wand_contiguous', v))
        self.options_bar.addWidget(self.contiguous_check)
        self.sample_all_check = QCheckBox("Sample All")
        self.sample_all_check.toggled.connect(lambda v: setattr(self, 'magic_wand_sample_all', v))
        self.options_bar.addWidget(self.sample_all_check)

    def create_panels(self):
        self.layer_panel = LayerPanel(self)
        self.layers_changed.connect(self.layer_panel.refresh)
        self.active_layer_changed.connect(lambda _index: self.layer_panel.refresh())
        ld = QDockWidget("Layers", self); ld.setWidget(self.layer_panel); ld.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, ld)
        self.history_list = QListWidget()
        hd = QDockWidget("History", self); hd.setWidget(self.history_list); hd.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, hd)
        self.navigator_panel = NavigatorPanel(self)
        nd = QDockWidget("Navigator", self); nd.setWidget(self.navigator_panel); nd.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, nd)
        self.histogram_panel = HistogramPanel(self)
        hgd = QDockWidget("Histogram", self); hgd.setWidget(self.histogram_panel); hgd.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, hgd)
        self.info_panel = InfoPanel(self)
        infod = QDockWidget("Info", self); infod.setWidget(self.info_panel); infod.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, infod)
        self.channel_panel = ChannelPanel(self)
        cd = QDockWidget("Channels", self); cd.setWidget(self.channel_panel); cd.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, cd)
        self.paths_panel = PathsPanel(self)
        pd = QDockWidget("Paths", self); pd.setWidget(self.paths_panel); pd.setMinimumWidth(220)
        self.addDockWidget(Qt.RightDockWidgetArea, pd)
        self.docks = {
            "Layers": ld,
            "History": hd,
            "Navigator": nd,
            "Histogram": hgd,
            "Info": infod,
            "Channels": cd,
            "Paths": pd,
        }
        self.layers_changed.connect(self.refresh_analysis_panels)
        self.active_layer_changed.connect(lambda _index: self.refresh_analysis_panels())
        for dock in self.docks.values():
            self.window_menu.addAction(dock.toggleViewAction())

    def set_tool(self, tool):
        self.current_tool = tool; self.record_macro_step("set_tool", tool); self.statusBar().showMessage(f"Tool: {tool}")

    def record_macro_step(self, command, *args):
        if self.macro_recording and not self.macro_replaying:
            self.macro_steps.append((command, args))

    def start_macro_recording(self):
        self.macro_steps = []
        self.macro_recording = True
        self.statusBar().showMessage("Macro recording started")

    def stop_macro_recording(self):
        self.macro_recording = False
        self.statusBar().showMessage(f"Macro recording stopped ({len(self.macro_steps)} steps)")

    def clear_macro(self):
        self.macro_steps = []
        self.macro_recording = False
        self.statusBar().showMessage("Macro cleared")

    def replay_macro(self):
        if not self.macro_steps:
            self.statusBar().showMessage("No macro steps recorded")
            return
        self.macro_replaying = True
        try:
            for command, args in list(self.macro_steps):
                if command == "set_tool":
                    self.set_tool(*args)
                elif command == "set_show_grid":
                    self.set_show_grid(*args)
                elif command == "set_show_guides":
                    self.set_show_guides(*args)
                elif command == "set_show_rulers":
                    self.set_show_rulers(*args)
                elif command == "set_snap_enabled":
                    self.set_snap_enabled(*args)
        finally:
            self.macro_replaying = False
        self.statusBar().showMessage(f"Replayed {len(self.macro_steps)} macro steps")

    def save_workspace_preset(self):
        self.workspace_preset = {name: dock.isVisible() for name, dock in self.docks.items()}
        self.statusBar().showMessage("Workspace preset saved")

    def restore_workspace_preset(self):
        if not self.workspace_preset:
            self.statusBar().showMessage("No workspace preset saved")
            return
        for name, visible in self.workspace_preset.items():
            dock = self.docks.get(name)
            if dock:
                dock.setVisible(visible)
        self.statusBar().showMessage("Workspace preset restored")

    def set_fg_color(self, c): self.fg_color = c; self.update_color_buttons()

    def update_color_buttons(self):
        self.fg_btn.setStyleSheet(f"background-color: {self.fg_color.name()}; border: 2px solid #888; border-radius: 3px;")
        self.bg_btn.setStyleSheet(f"background-color: {self.bg_color.name()}; border: 2px solid #555; border-radius: 3px;")

    def pick_fg_color(self):
        c = QColorDialog.getColor(self.fg_color, self, "Foreground Color")
        if c.isValid(): self.fg_color = c; self.update_color_buttons()

    def pick_bg_color(self):
        c = QColorDialog.getColor(self.bg_color, self, "Background Color")
        if c.isValid(): self.bg_color = c; self.update_color_buttons()

    def swap_colors(self):
        self.fg_color, self.bg_color = self.bg_color, self.fg_color; self.update_color_buttons()

    def set_active_layer_index(self, index):
        if not self.layers:
            self.active_layer_index = 0
        else:
            self.active_layer_index = max(0, min(index, len(self.layers)-1))
        self.active_layer_changed.emit(self.active_layer_index)

    def notify_layers_changed(self):
        self.layers_changed.emit()

    def update_layer_panel(self): self.notify_layers_changed()

    def refresh_analysis_panels(self):
        if hasattr(self, "navigator_panel"):
            self.navigator_panel.refresh()
            self.histogram_panel.refresh()
            self.info_panel.refresh_document()

    def update_info_panel(self, x, y, color=None):
        if hasattr(self, "info_panel"):
            self.info_panel.update_cursor(x, y, color)

    def refresh_paths_panel(self):
        if hasattr(self, "paths_panel"):
            self.paths_panel.refresh()

    def refresh_channel_panel(self):
        if hasattr(self, "channel_panel"):
            self.channel_panel.refresh()

    def reset_document_metadata(self):
        self.guides.clear()
        self.channel_visibility = {"red": True, "green": True, "blue": True, "alpha": True}
        self.current_path = []
        self.current_path_closed = False
        self.macro_recording = False
        self.macro_replaying = False
        self.macro_steps = []
        self.refresh_paths_panel()
        self.refresh_channel_panel()

    def apply_project_state(self, state, path):
        self.layers = state.layers
        self.set_active_layer_index(state.active_layer_index)
        self.channel_visibility = state.channel_visibility
        self.guides = state.guides
        self.current_path = state.current_path
        self.current_path_closed = state.current_path_closed
        self.macro_recording = False
        self.macro_replaying = False
        self.macro_steps = state.macro_steps
        self.history = HistoryManager()
        self.file_path = path
        self.refresh_paths_panel()
        self.refresh_channel_panel()
        self.canvas.clear_selection()
        self.update_layer_panel()
        self.canvas.fit_in_view()

    def project_save_kwargs(self):
        return {
            "layers": self.layers,
            "active_layer_index": self.active_layer_index,
            "channel_visibility": self.channel_visibility,
            "guides": self.guides,
            "current_path": self.current_path,
            "current_path_closed": self.current_path_closed,
            "macro_steps": self.macro_steps,
        }

    def add_path_point(self, x, y):
        self.current_path.append((x, y))
        self.current_path_closed = False
        self.refresh_paths_panel(); self.canvas.update()

    def close_path(self):
        if len(self.current_path) >= 3:
            self.current_path_closed = True
            self.refresh_paths_panel(); self.canvas.update()

    def clear_path(self):
        self.current_path = []
        self.current_path_closed = False
        self.canvas.clear_selection()
        self.refresh_paths_panel(); self.canvas.update()

    def path_to_selection(self):
        if not self.layers or len(self.current_path) < 3:
            return
        width, height = self.layers[0].image.size
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).polygon(self.current_path, fill=255)
        self.canvas.set_selection_mask(mask)
        self.canvas.update()

    def toggle_active_clipping(self):
        layer = self.active_layer()
        if layer:
            layer.clipping = not layer.clipping
            self.notify_layers_changed(); self.canvas.update()

    def show_about(self):
        QMessageBox.about(self, "About PyShop", f"{APP_DISPLAY_NAME}\nNative Python image editor.")

    # Compositing
    def get_composite(self):
        composite = composite_layers(self.layers)
        if composite is not None:
            return apply_channel_visibility(composite, self.channel_visibility)
        return None

    # File ops
    def new_image(self):
        dlg = QDialog(self); dlg.setWindowTitle("New Image"); form = QFormLayout(dlg)
        ws = QSpinBox(); ws.setRange(1,10000); ws.setValue(1920)
        hs = QSpinBox(); hs.setRange(1,10000); hs.setValue(1080)
        form.addRow("Width:", ws); form.addRow("Height:", hs)
        bg = QComboBox(); bg.addItems(["White","Black","Transparent"]); form.addRow("Background:", bg)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            w, h = ws.value(), hs.value()
            self.layers = create_document_layers(w, h, named_background_rgba(bg.currentText()))
            self.set_active_layer_index(0); self.history = HistoryManager(); self.file_path = None
            self.reset_document_metadata()
            self.canvas.clear_selection(); self.update_layer_panel(); self.canvas.fit_in_view()
            self.setWindowTitle(f"{APP_DISPLAY_NAME} - Untitled")

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
            "PyShop Projects (*.pyshop);;Images (*.psd *.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;All Files (*)")
        if path:
            try:
                if is_project_path(path):
                    state = load_project(path)
                    self.apply_project_state(state, path)
                    title_prefix = APP_DISPLAY_NAME
                    self.statusBar().showMessage(f"Opened PyShop project {path}")
                elif path.lower().endswith(".psd"):
                    self.layers = load_psd_layers(path)
                    title_prefix = "Imported PSD"
                    self.set_active_layer_index(0); self.history = HistoryManager(); self.file_path = None
                    self.reset_document_metadata()
                    self.canvas.clear_selection(); self.update_layer_panel(); self.canvas.fit_in_view()
                    self.statusBar().showMessage("PSD imported as PyShop layers; save as a PyShop project or export a flattened PSD")
                else:
                    img = open_raster_image(path)
                    self.layers = image_document_layers(img)
                    title_prefix = "Imported Image"
                    self.set_active_layer_index(0); self.history = HistoryManager(); self.file_path = None
                    self.reset_document_metadata()
                    self.canvas.clear_selection(); self.update_layer_panel(); self.canvas.fit_in_view()
                    self.statusBar().showMessage("Raster imported; save as a PyShop project or export a flattened image")
                self.setWindowTitle(f"{title_prefix} - {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open image:\n{e}")

    def save_image(self):
        if self.file_path: self._save_to(self.file_path)
        else: self.save_image_as()

    def save_image_as(self):
        path, selected_filter = QFileDialog.getSaveFileName(self, "Save Image", "",
            "PyShop Project (*.pyshop);;PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)")
        if path:
            path = self.path_for_selected_save_filter(path, selected_filter)
            if self._save_to(path):
                if is_project_path(path):
                    self.file_path = path
                    self.setWindowTitle(f"{APP_DISPLAY_NAME} - {os.path.basename(path)}")
                else:
                    self.file_path = None

    def _save_to(self, path):
        try:
            if is_project_path(path):
                save_project(path, **self.project_save_kwargs())
                self.statusBar().showMessage(f"Saved PyShop project to {path}")
                return True
            c = self.get_composite()
            if not c:
                return False
            if path.lower().endswith(".psd"):
                raise RuntimeError("Save does not write PSD because it would flatten layer metadata. Use Export Flattened PSD instead.")
            if path.lower().endswith(('.jpg','.jpeg')): c = c.convert("RGB")
            c.save(path); self.statusBar().showMessage(f"Saved flattened image to {path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")
            return False

    def path_for_selected_save_filter(self, path, selected_filter):
        if os.path.splitext(path)[1]:
            return path
        if "PNG" in selected_filter:
            return f"{path}.png"
        if "JPEG" in selected_filter:
            return f"{path}.jpg"
        if "BMP" in selected_filter:
            return f"{path}.bmp"
        return f"{path}{PROJECT_FILE_SUFFIX}"

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export PNG", "", "PNG (*.png)")
        if path:
            c = self.get_composite()
            if c: c.save(path, "PNG"); self.statusBar().showMessage(f"Exported to {path}")

    def export_flattened_psd(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Flattened PSD", "", "Flattened PSD (*.psd)")
        if path:
            if not path.lower().endswith(".psd"):
                path += ".psd"
            try:
                c = self.get_composite()
                if c:
                    save_flattened_psd(path, c)
                    self.statusBar().showMessage(f"Exported flattened PSD to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export flattened PSD:\n{e}")

    # Edit ops
    def undo(self):
        s, i = self.history.undo(self.layers, self.active_layer_index)
        if s: self.layers = s; self.set_active_layer_index(i); self.update_layer_panel(); self.canvas.update()

    def redo(self):
        s, i = self.history.redo(self.layers, self.active_layer_index)
        if s: self.layers = s; self.set_active_layer_index(i); self.update_layer_panel(); self.canvas.update()

    def select_all(self):
        l = self.active_layer()
        if l:
            w,h = l.image.size; self.canvas.set_selection_mask(Image.new("L",(w,h),255))
            self.canvas.selection_rect = None; self.canvas.update()

    def deselect(self): self.canvas.clear_selection()

    def invert_selection(self):
        if self.canvas.selection_mask:
            self.canvas.set_selection_mask(ImageChops.invert(self.canvas.selection_mask)); self.canvas.update()

    def delete_selection(self):
        l = self.active_layer()
        if l and self.canvas.selection_mask:
            self.history.save_state(self.layers, self.active_layer_index)
            r,g,b,a = l.image.split()
            a = ImageChops.darker(a, ImageChops.invert(self.canvas.selection_mask))
            l.image = Image.merge("RGBA", (r,g,b,a)); self.canvas.update()

    def copy_selection(self):
        l = self.active_layer()
        if l and self.canvas.selection_mask:
            self._clipboard = l.image.copy()
            r,g,b,a = self._clipboard.split()
            a = ImageChops.darker(a, self.canvas.selection_mask)
            self._clipboard = Image.merge("RGBA", (r,g,b,a))

    def cut_selection(self): self.copy_selection(); self.delete_selection()

    def paste_clipboard(self):
        if hasattr(self, '_clipboard') and self._clipboard:
            self.history.save_state(self.layers, self.active_layer_index)
            nl = Layer("Pasted Layer"); nl.image = self._clipboard.copy()
            self.layers.append(nl); self.set_active_layer_index(len(self.layers)-1)
            self.update_layer_panel(); self.canvas.update()

    # Image ops
    def resize_canvas(self):
        if not self.layers: return
        w,h = self.layers[0].image.size
        dlg = QDialog(self); dlg.setWindowTitle("Resize Canvas"); form = QFormLayout(dlg)
        ws = QSpinBox(); ws.setRange(1,20000); ws.setValue(w)
        hs = QSpinBox(); hs.setRange(1,20000); hs.setValue(h)
        form.addRow("Width:", ws); form.addRow("Height:", hs)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            nw, nh = ws.value(), hs.value()
            self.history.save_state(self.layers, self.active_layer_index)
            for l in self.layers:
                ni = Image.new("RGBA",(nw,nh),(0,0,0,0)); ni.paste(l.image,(0,0)); l.image = ni
                if l.mask is not None:
                    nm = Image.new("L", (nw, nh), 0); nm.paste(l.mask, (0, 0)); l.mask = nm
            self.canvas.clear_selection(); self.canvas.fit_in_view(); self.update_layer_panel()

    def resize_image(self):
        if not self.layers: return
        w,h = self.layers[0].image.size
        dlg = QDialog(self); dlg.setWindowTitle("Resize Image"); form = QFormLayout(dlg)
        ws = QSpinBox(); ws.setRange(1,20000); ws.setValue(w)
        hs = QSpinBox(); hs.setRange(1,20000); hs.setValue(h)
        form.addRow("Width:", ws); form.addRow("Height:", hs)
        mt = QComboBox(); mt.addItems(["Lanczos","Bilinear","Bicubic","Nearest"]); form.addRow("Method:", mt)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            nw, nh = ws.value(), hs.value()
            rs = {"Lanczos":Image.LANCZOS,"Bilinear":Image.BILINEAR,"Bicubic":Image.BICUBIC,"Nearest":Image.NEAREST}[mt.currentText()]
            self.history.save_state(self.layers, self.active_layer_index)
            for l in self.layers:
                l.image = l.image.resize((nw,nh), rs)
                if l.mask is not None:
                    l.mask = l.mask.resize((nw, nh), Image.NEAREST)
            self.canvas.clear_selection(); self.canvas.fit_in_view(); self.update_layer_panel()

    def rotate_image(self, deg):
        if not self.layers: return
        self.history.save_state(self.layers, self.active_layer_index)
        for l in self.layers:
            l.image = l.image.rotate(-deg, expand=True, fillcolor=(0,0,0,0))
            if l.mask is not None:
                l.mask = l.mask.rotate(-deg, expand=True, fillcolor=0)
        self.canvas.clear_selection(); self.canvas.fit_in_view(); self.update_layer_panel()

    def flip_image(self, d):
        if not self.layers: return
        self.history.save_state(self.layers, self.active_layer_index)
        for l in self.layers:
            l.image = ImageOps.mirror(l.image) if d == "h" else ImageOps.flip(l.image)
            if l.mask is not None:
                l.mask = ImageOps.mirror(l.mask) if d == "h" else ImageOps.flip(l.mask)
        self.canvas.update()

    def flatten_image(self):
        if not self.layers: return
        self.history.save_state(self.layers, self.active_layer_index)
        self.layers = flattened_document_layers(self.get_composite())
        self.set_active_layer_index(0); self.update_layer_panel(); self.canvas.update()

    def merge_down(self):
        idx = self.active_layer_index
        if idx <= 0 or idx >= len(self.layers): return
        self.history.save_state(self.layers, self.active_layer_index)
        top, bot = self.layers[idx], self.layers[idx-1]
        bot.image = composite_layers([bot, top])
        bot.mask = None
        bot.clipping = False
        bot.name = f"{bot.name} + {top.name}"
        del self.layers[idx]; self.set_active_layer_index(idx-1)
        self.update_layer_panel(); self.canvas.update()

    def crop_to_selection(self):
        if self.canvas.selection_mask:
            bounds = selection_mask_bounds(self.canvas.selection_mask)
            if bounds: self._do_crop(*bounds)
        elif self.canvas.selection_rect:
            r = self.canvas.selection_rect
            self._do_crop(int(r.x()), int(r.y()), int(r.x()+r.width()), int(r.y()+r.height()))

    def apply_crop(self):
        if self.canvas.crop_rect:
            r = self.canvas.crop_rect
            self._do_crop(int(r.x()), int(r.y()), int(r.x()+r.width()), int(r.y()+r.height()))
            self.canvas.crop_rect = None

    def _do_crop(self, x1, y1, x2, y2):
        if not self.layers: return
        self.history.save_state(self.layers, self.active_layer_index)
        for l in self.layers:
            l.image = l.image.crop((x1,y1,x2,y2))
            if l.mask is not None:
                l.mask = l.mask.crop((x1,y1,x2,y2))
        self.canvas.clear_selection(); self.canvas.fit_in_view(); self.update_layer_panel()

    # Text
    def add_shape_layer(self, rect):
        if not self.layers or rect.width() < 1 or rect.height() < 1:
            return
        self.history.save_state(self.layers, self.active_layer_index)
        width, height = self.layers[0].image.size
        layer = Layer(f"Shape {len(self.layers) + 1}", width, height)
        color = qcolor_to_rgba(self.fg_color, self.brush_opacity)
        layer.vector_shape = {
            "type": "rectangle",
            "box": (int(rect.x()), int(rect.y()), int(rect.x() + rect.width()), int(rect.y() + rect.height())),
            "fill": color,
            "stroke": qcolor_to_rgba(self.bg_color, 255),
            "stroke_width": 0,
        }
        self.layers.append(layer)
        self.set_active_layer_index(len(self.layers) - 1)
        self.update_layer_panel(); self.canvas.update()

    def insert_text_at(self, x, y):
        dlg = QDialog(self); dlg.setWindowTitle("Insert Text"); form = QFormLayout(dlg)
        te = QTextEdit(); te.setPlaceholderText("Enter text..."); form.addRow("Text:", te)
        fs = QSpinBox(); fs.setRange(8,500); fs.setValue(36); form.addRow("Size:", fs)
        bc = QCheckBox("Bold"); form.addRow(bc)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            text = te.toPlainText()
            if not text: return
            self.history.save_state(self.layers, self.active_layer_index)
            if not self.layers: return
            w, h = self.layers[0].image.size
            l = Layer(f"Text {len(self.layers) + 1}", w, h)
            color = qcolor_to_rgba(self.fg_color, self.brush_opacity)
            l.text_item = {"text": text, "x": x, "y": y, "size": fs.value(), "bold": bc.isChecked(), "fill": color}
            self.layers.append(l)
            self.set_active_layer_index(len(self.layers) - 1)
            self.update_layer_panel(); self.canvas.update()

    # Adjustments
    def _apply_to_active(self, func):
        l = self.active_layer()
        if not l: return
        self.history.save_state(self.layers, self.active_layer_index)
        if self.canvas.selection_mask:
            orig = l.image.copy(); l.image = func(l.image)
            l.image = Image.composite(l.image, orig, self.canvas.selection_mask)
        else:
            l.image = func(l.image)
        self.canvas.update()

    def adjust_brightness_contrast(self):
        dlg = QDialog(self); dlg.setWindowTitle("Brightness / Contrast"); form = QFormLayout(dlg)
        bs = QSlider(Qt.Horizontal); bs.setRange(-100,100); bs.setValue(0)
        cs = QSlider(Qt.Horizontal); cs.setRange(-100,100); cs.setValue(0)
        bl = QLabel("0"); cl = QLabel("0")
        bs.valueChanged.connect(lambda v: bl.setText(str(v)))
        cs.valueChanged.connect(lambda v: cl.setText(str(v)))
        bh = QHBoxLayout(); bh.addWidget(bs); bh.addWidget(bl)
        ch = QHBoxLayout(); ch.addWidget(cs); ch.addWidget(cl)
        form.addRow("Brightness:", bh); form.addRow("Contrast:", ch)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            bv, cv = bs.value(), cs.value()
            def apply(img):
                r = img
                if bv != 0: r = ImageEnhance.Brightness(r).enhance(1+bv/100)
                if cv != 0: r = ImageEnhance.Contrast(r).enhance(1+cv/100)
                return r
            self._apply_to_active(apply)

    def adjust_hue_saturation(self):
        dlg = QDialog(self); dlg.setWindowTitle("Hue / Saturation"); form = QFormLayout(dlg)
        hs = QSlider(Qt.Horizontal); hs.setRange(-180,180); hs.setValue(0)
        ss = QSlider(Qt.Horizontal); ss.setRange(-100,100); ss.setValue(0)
        ls = QSlider(Qt.Horizontal); ls.setRange(-100,100); ls.setValue(0)
        form.addRow("Hue:", hs); form.addRow("Saturation:", ss); form.addRow("Lightness:", ls)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            hv, sv, lv = hs.value(), ss.value(), ls.value()
            def apply(img):
                r,g,b,a = img.split(); rgb = Image.merge("RGB",(r,g,b))
                if sv != 0: rgb = ImageEnhance.Color(rgb).enhance(1+sv/100)
                if lv != 0: rgb = ImageEnhance.Brightness(rgb).enhance(1+lv/100)
                if hv != 0:
                    hsv = rgb.convert("HSV"); hc,sc,vc = hsv.split()
                    hc = hc.point(lambda x: (x+hv)%256)
                    rgb = Image.merge("HSV",(hc,sc,vc)).convert("RGB")
                rr,gg,bb = rgb.split(); return Image.merge("RGBA",(rr,gg,bb,a))
            self._apply_to_active(apply)

    def adjust_levels(self):
        dlg = QDialog(self); dlg.setWindowTitle("Levels"); form = QFormLayout(dlg)
        bsp = QSpinBox(); bsp.setRange(0,254); bsp.setValue(0)
        wsp = QSpinBox(); wsp.setRange(1,255); wsp.setValue(255)
        gsp = QDoubleSpinBox(); gsp.setRange(0.1,10.0); gsp.setValue(1.0); gsp.setSingleStep(0.1)
        form.addRow("Black Point:", bsp); form.addRow("White Point:", wsp); form.addRow("Gamma:", gsp)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            bp, wp, gm = bsp.value(), wsp.value(), gsp.value()
            def apply(img):
                r,g,b,a = img.split()
                def lv(ch): return ch.point(lambda x: int(255*max(0,min(1,((x-bp)/max(1,wp-bp))))**(1/gm)))
                return Image.merge("RGBA",(lv(r),lv(g),lv(b),a))
            self._apply_to_active(apply)

    def invert_colors(self):
        def apply(img):
            r,g,b,a = img.split()
            return Image.merge("RGBA",(ImageChops.invert(r),ImageChops.invert(g),ImageChops.invert(b),a))
        self._apply_to_active(apply)

    def grayscale(self):
        def apply(img):
            r,g,b,a = img.split(); gray = img.convert("L").convert("RGB")
            rr,gg,bb = gray.split(); return Image.merge("RGBA",(rr,gg,bb,a))
        self._apply_to_active(apply)

    def auto_contrast(self):
        def apply(img):
            r,g,b,a = img.split()
            rgb = ImageOps.autocontrast(Image.merge("RGB",(r,g,b)))
            rr,gg,bb = rgb.split(); return Image.merge("RGBA",(rr,gg,bb,a))
        self._apply_to_active(apply)

    def color_balance(self):
        dlg = QDialog(self); dlg.setWindowTitle("Color Balance"); form = QFormLayout(dlg)
        rs = QSlider(Qt.Horizontal); rs.setRange(-100,100); rs.setValue(0)
        gs = QSlider(Qt.Horizontal); gs.setRange(-100,100); gs.setValue(0)
        bs = QSlider(Qt.Horizontal); bs.setRange(-100,100); bs.setValue(0)
        form.addRow("Red:", rs); form.addRow("Green:", gs); form.addRow("Blue:", bs)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            rv, gv, bv = rs.value(), gs.value(), bs.value()
            def apply(img):
                r,g,b,a = img.split()
                r = r.point(lambda x: max(0,min(255,x+rv)))
                g = g.point(lambda x: max(0,min(255,x+gv)))
                b = b.point(lambda x: max(0,min(255,x+bv)))
                return Image.merge("RGBA",(r,g,b,a))
            self._apply_to_active(apply)

    # Filters
    def gaussian_blur(self):
        v, ok = QInputDialog.getDouble(self, "Gaussian Blur", "Radius:", 3.0, 0.1, 100.0, 1)
        if ok: self._apply_to_active(lambda img: img.filter(ImageFilter.GaussianBlur(v)))

    def box_blur(self):
        v, ok = QInputDialog.getInt(self, "Box Blur", "Radius:", 3, 1, 100)
        if ok: self._apply_to_active(lambda img: img.filter(ImageFilter.BoxBlur(v)))

    def motion_blur(self):
        v, ok = QInputDialog.getInt(self, "Motion Blur", "Size:", 10, 1, 100)
        if ok:
            k = [0]*(v*v); c = v//2
            for i in range(v): k[c*v+i] = 1
            self._apply_to_active(lambda img: img.filter(ImageFilter.Kernel((v,v), k, scale=v)))

    def sharpen(self): self._apply_to_active(lambda img: img.filter(ImageFilter.SHARPEN))

    def unsharp_mask(self):
        dlg = QDialog(self); dlg.setWindowTitle("Unsharp Mask"); form = QFormLayout(dlg)
        r = QDoubleSpinBox(); r.setRange(0.1,100); r.setValue(2.0)
        pct = QSpinBox(); pct.setRange(1,500); pct.setValue(150)
        th = QSpinBox(); th.setRange(0,255); th.setValue(3)
        form.addRow("Radius:", r); form.addRow("Amount %:", pct); form.addRow("Threshold:", th)
        btns = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject); form.addRow(btns)
        if dlg.exec_() == QDialog.Accepted:
            self._apply_to_active(lambda img: img.filter(ImageFilter.UnsharpMask(r.value(), pct.value(), th.value())))

    def edge_detect(self): self._apply_to_active(lambda img: img.filter(ImageFilter.FIND_EDGES))
    def emboss(self): self._apply_to_active(lambda img: img.filter(ImageFilter.EMBOSS))
    def contour(self): self._apply_to_active(lambda img: img.filter(ImageFilter.CONTOUR))

    def posterize(self):
        v, ok = QInputDialog.getInt(self, "Posterize", "Levels (2-8):", 4, 2, 8)
        if ok:
            def ap(img):
                r,g,b,a = img.split(); rgb = ImageOps.posterize(Image.merge("RGB",(r,g,b)),v)
                rr,gg,bb = rgb.split(); return Image.merge("RGBA",(rr,gg,bb,a))
            self._apply_to_active(ap)

    def solarize(self):
        v, ok = QInputDialog.getInt(self, "Solarize", "Threshold:", 128, 0, 255)
        if ok:
            def ap(img):
                r,g,b,a = img.split(); rgb = ImageOps.solarize(Image.merge("RGB",(r,g,b)),v)
                rr,gg,bb = rgb.split(); return Image.merge("RGBA",(rr,gg,bb,a))
            self._apply_to_active(ap)

    def pixelate(self):
        v, ok = QInputDialog.getInt(self, "Pixelate", "Block size:", 8, 2, 100)
        if ok:
            def ap(img):
                w,h = img.size
                return img.resize((w//v, h//v), Image.NEAREST).resize((w,h), Image.NEAREST)
            self._apply_to_active(ap)

    # Zoom
    def _zoom(self, f):
        self.canvas.zoom *= f
        self.canvas.update()
        self.refresh_analysis_panels()

    def _set_zoom(self, v):
        self.canvas.zoom = v
        self.canvas.update()
        self.refresh_analysis_panels()

    def set_show_grid(self, checked):
        self.show_grid = checked
        self.record_macro_step("set_show_grid", checked)
        self.canvas.update()

    def set_show_guides(self, checked):
        self.show_guides = checked
        self.record_macro_step("set_show_guides", checked)
        self.canvas.update()

    def set_show_rulers(self, checked):
        self.show_rulers = checked
        self.record_macro_step("set_show_rulers", checked)
        self.canvas.update()

    def set_snap_enabled(self, checked):
        self.snap_enabled = checked
        self.record_macro_step("set_snap_enabled", checked)

    def set_grid_size(self):
        value, ok = QInputDialog.getInt(self, "Grid Size", "Pixels:", self.grid_size, 1, 2000, 1)
        if ok:
            self.grid_size = value
            self.canvas.update()

    def add_guide(self, orientation):
        if not self.layers:
            return
        width, height = self.layers[0].image.size
        maximum = width if orientation == "vertical" else height
        label = "X:" if orientation == "vertical" else "Y:"
        value, ok = QInputDialog.getInt(self, "Add Guide", label, maximum // 2, 0, maximum, 1)
        if ok:
            self.guides.append((orientation, value))
            self.canvas.update()

    def clear_guides(self):
        self.guides.clear()
        self.canvas.update()

# ---- Main -----------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app_icon = QIcon(str(app_icon_path()))
    app.setWindowIcon(app_icon)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
