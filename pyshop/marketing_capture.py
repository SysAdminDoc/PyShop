#!/usr/bin/env python3
"""Exercise a sample project in the real editor and capture its public surfaces."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from PIL import Image, ImageDraw
from PyQt5.QtCore import QSettings
from PyQt5.QtTest import QTest

from pyshop.app_info import APP_DISPLAY_NAME, APP_VERSION
from pyshop.core import Layer


def settle(app, delay_ms=300):
    for _ in range(3):
        app.processEvents()
        QTest.qWait(delay_ms // 3)


def file_record(path):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"file": path.name, "sha256": digest.hexdigest(), "sizeBytes": path.stat().st_size}


def select_tool(editor, tool_id):
    action = next(action for action in editor.tool_group.actions() if action.data() == tool_id)
    action.trigger()
    if not action.isChecked() or editor.current_tool != tool_id:
        raise RuntimeError(f"Tool selection did not update both controls: {tool_id}")


def capture_session(editor, app, photo_path, output_dir):
    photo_path, output_dir = Path(photo_path), Path(output_dir)
    profile = Path(os.environ["PYSHOP_TEST_PROFILE"]).resolve()
    if editor.settings.format() != QSettings.IniFormat or Path(editor.settings.fileName()).resolve().parent != profile:
        raise RuntimeError("Capture settings are not isolated")
    if not photo_path.is_file():
        raise FileNotFoundError(photo_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    captures = []

    def capture(name):
        settle(app)
        path = output_dir / name
        pixmap = editor.grab()
        if pixmap.isNull() or not pixmap.save(str(path), "PNG") or path.stat().st_size < 10_000:
            raise RuntimeError(f"Invalid screenshot: {path}")
        captures.append({**file_record(path), "width": pixmap.width(), "height": pixmap.height()})

    editor.showNormal()
    editor.resize(1600, 1000)
    editor.move(0, 0)
    for name, dock in editor.docks.items():
        dock.setVisible(name in {"Layers", "Navigator", "Histogram"})
    settle(app, 450)
    capture("01-welcome.png")

    if not editor.open_path(str(photo_path)):
        raise RuntimeError("PyShop rejected the demo image")
    deadline = time.monotonic() + 20
    while not editor.layers or editor.current_job is not None:
        if time.monotonic() >= deadline:
            raise RuntimeError("PyShop did not finish opening the demo image")
        app.processEvents()
        QTest.qWait(50)

    width, height = editor.layers[0].image.size
    contrast = Layer("Contrast and depth", width, height)
    contrast.adjustment = {"type": "brightness_contrast", "brightness": 2, "contrast": 13}
    color = Layer("Ocean color grade", width, height)
    color.adjustment = {"type": "hue_saturation", "hue": 0, "saturation": 8, "lightness": -2}
    retouch = Layer("Retouch workspace", width, height)
    editor.layers = [editor.layers[0], contrast, color, retouch]
    editor.set_active_layer_index(2)
    editor.guides = [("vertical", width // 3), ("horizontal", height * 2 // 3)]
    editor.history_list.clear()
    editor.history_list.addItems(["Open coastal-cabin.png", "Add contrast adjustment", "Add ocean color grade", "Create retouch layer"])
    editor.setWindowTitle(f"{APP_DISPLAY_NAME} | Coastal Cabin Editorial")
    editor.update_layer_panel()
    select_tool(editor, "brush")
    editor.canvas.fit_in_view()
    editor.refresh_analysis_panels()
    editor.statusBar().showMessage(f"Sample project | {width} x {height} | {len(editor.layers)} layers")
    capture("02-layered-edit.png")

    for name, dock in editor.docks.items():
        dock.setVisible(name in {"Histogram", "Info", "Channels"})
    editor.refresh_analysis_panels()
    editor.statusBar().showMessage("Inspecting tonal range and channel balance")
    capture("03-analysis.png")

    for name, dock in editor.docks.items():
        dock.setVisible(name in {"Layers", "Navigator"})
    selection = Image.new("L", (width, height), 0)
    ImageDraw.Draw(selection).rounded_rectangle((120, 150, 760, 720), radius=48, fill=255)
    editor.canvas.set_selection_mask(selection)
    select_tool(editor, "select_rect")
    editor.statusBar().showMessage("Selection ready | 640 x 570 px")
    capture("04-selection.png")

    frozen = bool(getattr(sys, "frozen", False))
    report = {
        "schemaVersion": 1,
        "version": APP_VERSION,
        "source": {"kind": "Windows executable", **file_record(sys.executable)} if frozen else {"kind": "source checkout"},
        "environment": {"surface": "isolated Windows desktop", "temporaryProfile": True, "sampleProject": True},
        "demoImage": file_record(photo_path),
        "captures": captures,
    }
    (output_dir / "capture-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
