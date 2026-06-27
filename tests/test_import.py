import importlib
import os


def test_app_module_imports_without_starting_qapplication():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    module = importlib.import_module("pyshop_image_editor")

    assert module.APP_DISPLAY_NAME == "PyShop v0.1.0"
    assert callable(module.main)
    assert module.QApplication.instance() is None
