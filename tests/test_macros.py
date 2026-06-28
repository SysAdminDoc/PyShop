import json

import pytest

from pyshop.core import MacroFormatError, load_macro_file, macro_steps_from_records, save_macro_file


def test_macro_file_round_trip_preserves_command_args(tmp_path):
    path = tmp_path / "paint.pyshopmacro"
    steps = [("set_tool", ("brush",)), ("set_show_grid", (True,))]

    saved_path = save_macro_file(path, steps)
    loaded = load_macro_file(saved_path)

    assert saved_path == path
    assert loaded == steps


def test_macro_file_adds_default_extension(tmp_path):
    saved_path = save_macro_file(tmp_path / "paint", [("set_snap_enabled", (False,))])

    assert saved_path.name == "paint.pyshopmacro"


def test_macro_loader_rejects_unknown_commands(tmp_path):
    path = tmp_path / "bad.pyshopmacro"
    path.write_text(json.dumps([{"command": "delete_everything", "args": []}]), encoding="utf-8")

    with pytest.raises(MacroFormatError, match="Unsupported macro command"):
        load_macro_file(path)


def test_macro_records_require_list_args():
    with pytest.raises(MacroFormatError, match="args must be a list"):
        macro_steps_from_records([{"command": "set_tool", "args": "brush"}])
