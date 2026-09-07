#!/usr/bin/env python3
"""Capture PyShop's public product states on an isolated Windows desktop."""

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "windows")
os.environ.setdefault("QT_SCALE_FACTOR", "1")

from PIL import Image, ImageDraw
from PyQt5.QtCore import QSettings, QStandardPaths
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

REPO_ROOT = Path(__file__).resolve().parents[1]
PHOTO_PATH = REPO_ROOT / "assets" / "demo" / "coastal-cabin.png"
OUTPUT_DIR = REPO_ROOT / "assets" / "screenshots"

sys.path.insert(0, str(REPO_ROOT))

from pyshop.app_info import APP_DISPLAY_NAME, app_icon_path
from pyshop.core import Layer
from pyshop_image_editor import DARK_STYLE, ImageEditor


def settle(app: QApplication, delay_ms: int = 300) -> None:
    for _ in range(3):
        app.processEvents()
        QTest.qWait(delay_ms // 3)


def capture(editor: ImageEditor, app: QApplication, name: str) -> None:
    settle(app)
    target = OUTPUT_DIR / name
    pixmap = editor.grab()
    if pixmap.isNull() or not pixmap.save(str(target), "PNG"):
        raise RuntimeError(f"Could not save {target}")
    if target.stat().st_size < 10_000:
        raise RuntimeError(f"Unexpectedly small screenshot: {target}")


def wait_for_open(editor: ImageEditor, app: QApplication) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        app.processEvents()
        if editor.layers and editor.current_job is None:
            return
        QTest.qWait(50)
    raise RuntimeError("PyShop did not finish opening the demo image")


def main() -> int:
    if not PHOTO_PATH.is_file():
        raise FileNotFoundError(PHOTO_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    QStandardPaths.setTestModeEnabled(True)

    app = QApplication([])
    app.setApplicationName("PyShop Marketing Capture")
    app.setWindowIcon(QIcon(str(app_icon_path())))
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    QSettings("SysAdminDoc", "PyShop").clear()

    editor = ImageEditor()
    editor.showNormal()
    editor.resize(1600, 1000)
    editor.move(0, 0)
    for name, dock in editor.docks.items():
        dock.setVisible(name in {"Layers", "Navigator", "Histogram"})
    settle(app, 450)

    capture(editor, app, "01-welcome.png")

    if not editor.open_path(str(PHOTO_PATH)):
        raise RuntimeError("PyShop rejected the demo image")
    wait_for_open(editor, app)

    width, height = editor.layers[0].image.size
    contrast = Layer("Contrast and depth", width, height)
    contrast.adjustment = {"type": "brightness_contrast", "brightness": 2, "contrast": 13}
    color = Layer("Ocean color grade", width, height)
    color.adjustment = {"type": "hue_saturation", "hue": 0, "saturation": 8, "lightness": -2}
    retouch = Layer("Window glow retouch", width, height)
    editor.layers = [editor.layers[0], contrast, color, retouch]
    editor.set_active_layer_index(2)
    editor.guides = [("vertical", width // 3), ("horizontal", height * 2 // 3)]
    editor.history_list.clear()
    editor.history_list.addItems(
        [
            "Open coastal-cabin.png",
            "Add contrast adjustment",
            "Add ocean color grade",
            "Create retouch layer",
        ]
    )
    editor.setWindowTitle(f"{APP_DISPLAY_NAME} | Coastal Cabin Editorial")
    editor.update_layer_panel()
    editor.set_tool("brush")
    editor.canvas.fit_in_view()
    editor.refresh_analysis_panels()
    editor.statusBar().showMessage("Coastal Cabin Editorial | 1536 x 1024 | 4 layers")
    capture(editor, app, "02-layered-edit.png")

    for name, dock in editor.docks.items():
        dock.setVisible(name in {"Histogram", "Info", "Channels"})
    editor.refresh_analysis_panels()
    editor.statusBar().showMessage("Inspecting tonal range and channel balance")
    capture(editor, app, "03-analysis.png")

    for name, dock in editor.docks.items():
        dock.setVisible(name in {"Layers", "Navigator"})
    selection = Image.new("L", (width, height), 0)
    ImageDraw.Draw(selection).rounded_rectangle((120, 150, 760, 720), radius=48, fill=255)
    editor.canvas.set_selection_mask(selection)
    editor.set_tool("select_rect")
    editor.statusBar().showMessage("Selection ready | 640 x 570 px")
    capture(editor, app, "04-selection.png")

    editor.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
