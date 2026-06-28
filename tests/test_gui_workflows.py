import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QToolButton

from pyshop.core import Layer, create_document_layers, named_background_rgba
from pyshop.tools import CanvasToolEvent
from pyshop_image_editor import ImageEditor


def make_editor(qtbot):
    editor = ImageEditor()
    editor.settings.clear()
    qtbot.addWidget(editor)
    return editor


def install_small_document(editor):
    editor.layers = create_document_layers(4, 4, named_background_rgba("Transparent"))
    editor.set_active_layer_index(0)
    editor.update_layer_panel()


def test_actions_register_no_keyboard_shortcuts(qtbot):
    editor = make_editor(qtbot)

    actions = [action for action in editor.findChildren(type(editor.menuBar().actions()[0])) if not action.isSeparator()]

    assert actions
    assert all(action.shortcut().isEmpty() for action in actions)


def test_icon_only_tool_buttons_have_accessible_labels(qtbot):
    editor = make_editor(qtbot)

    icon_buttons = [button for button in editor.tool_bar.findChildren(QToolButton) if button.defaultAction()]

    assert icon_buttons
    for button in icon_buttons:
        default_action = button.defaultAction()
        label = button.accessibleName() or button.toolTip() or (default_action.text() if default_action else "")
        assert label


def test_layer_panel_duplicate_and_remove_workflows(qtbot):
    editor = make_editor(qtbot)
    install_small_document(editor)

    editor.layer_panel.duplicate_layer()

    assert len(editor.layers) == 2
    assert editor.active_layer().name == "Background copy"

    editor.layer_panel.remove_layer()

    assert len(editor.layers) == 1


def test_macro_replay_reports_invalid_commands(qtbot):
    editor = make_editor(qtbot)
    editor.macro_steps = [("unsupported_command", ())]

    editor.replay_macro()

    assert "macro replay failed" in editor.statusBar().currentMessage().lower()


def test_workspace_preset_persists_dock_state(qtbot):
    editor = make_editor(qtbot)
    dock = editor.docks["Histogram"]

    dock.hide()
    editor.save_workspace_preset()
    dock.show()
    editor.restore_workspace_preset()

    assert dock.isHidden()


def test_finish_open_document_imports_raster_layers_without_file_path(qtbot, tmp_path):
    editor = make_editor(qtbot)
    layer = Layer("Imported", image=Image.new("RGBA", (2, 2), (1, 2, 3, 255)))
    path = tmp_path / "import.png"

    editor.finish_open_document({"kind": "raster", "path": str(path), "layers": [layer]})

    assert editor.file_path is None
    assert editor.layers[0].name == "Imported"
    assert "Imported Image" in editor.windowTitle()


def test_save_filter_adds_expected_extensions(qtbot):
    editor = make_editor(qtbot)

    assert editor.path_for_selected_save_filter("work", "PyShop Project (*.pyshop)").endswith(".pyshop")
    assert editor.path_for_selected_save_filter("flat", "PNG (*.png)").endswith(".png")
    assert editor.path_for_selected_save_filter("photo", "JPEG (*.jpg *.jpeg)").endswith(".jpg")


def test_open_filter_advertises_project_raw_and_raster_inputs(qtbot):
    editor = make_editor(qtbot)
    file_filter = editor.open_file_filter()

    assert "*.pyshop" in file_filter
    assert "*.dng" in file_filter
    assert "*.cr3" in file_filter
    assert "*.png" in file_filter


def test_brush_tool_flow_paints_active_layer(qtbot):
    editor = make_editor(qtbot)
    install_small_document(editor)
    editor.fg_color = QColor(255, 0, 0)
    canvas = editor.canvas
    event = CanvasToolEvent(QPointF(1, 1), QPointF(1, 1), buttons=Qt.LeftButton, modifiers=Qt.NoModifier)

    assert canvas.tool_handlers["brush"].press(canvas, event) is True

    assert editor.active_layer().image.getpixel((1, 1))[0] == 255
