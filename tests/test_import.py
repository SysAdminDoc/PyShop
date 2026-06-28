import importlib
import os

from PyQt5.QtWidgets import QApplication


def test_app_module_imports_without_starting_qapplication():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing_app = QApplication.instance()

    package = importlib.import_module("pyshop")
    module = importlib.import_module("pyshop_image_editor")

    assert package.APP_DISPLAY_NAME == "PyShop v0.1.35"
    assert module.APP_DISPLAY_NAME == package.APP_DISPLAY_NAME
    assert module.__version__ == package.__version__
    assert callable(module.main)
    assert module.QApplication.instance() is existing_app
