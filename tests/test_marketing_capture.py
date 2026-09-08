import hashlib
import os
from pathlib import Path

import pytest
from PyQt5.QtCore import QSettings

from pyshop.app_info import app_settings
from pyshop.marketing_capture import file_record, select_tool
import pyshop_image_editor as application


def test_profile_uses_explicit_ini_file():
    settings = app_settings()
    assert settings.format() == QSettings.IniFormat
    assert Path(settings.fileName()).resolve() == Path(os.environ['PYSHOP_TEST_PROFILE'], 'settings.ini').resolve()
    settings.setValue('workspace/test', 'isolated')
    settings.sync()
    assert app_settings().value('workspace/test') == 'isolated'


def test_relative_profile_is_rejected(monkeypatch):
    monkeypatch.setenv('PYSHOP_TEST_PROFILE', 'relative-profile')
    with pytest.raises(ValueError, match='absolute'):
        app_settings()


@pytest.mark.parametrize('mode', ['PYSHOP_CAPTURE_DIR', 'PYSHOP_SMOKE_EXIT_MS'])
@pytest.mark.parametrize('required', ['PYSHOP_TEST_PROFILE', 'PYSHOP_DATA_DIR'])
def test_verification_requires_isolation_before_creating_a_window(monkeypatch, mode, required):
    monkeypatch.setenv(mode, '1000')
    monkeypatch.delenv(required)
    monkeypatch.setattr(application, 'QApplication', lambda *args: pytest.fail('Window created before safety check'))
    with pytest.raises(RuntimeError, match='isolated'):
        application.main()


def test_selection_capture_uses_the_selected_toolbar_action(qtbot):
    editor = application.ImageEditor()
    qtbot.addWidget(editor)
    select_tool(editor, 'select_rect')
    assert editor.current_tool == 'select_rect'
    assert [a.data() for a in editor.tool_group.actions() if a.isChecked()] == ['select_rect']


def test_file_record_hashes_all_bytes(tmp_path):
    target = tmp_path / 'sample.bin'
    content = b'sample' * 200_000
    target.write_bytes(content)
    assert file_record(target) == {'file': target.name, 'sha256': hashlib.sha256(content).hexdigest(), 'sizeBytes': len(content)}
