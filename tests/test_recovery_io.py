from PIL import Image

from pyshop.core import clear_recovery_project, recovery_project_path, save_image_atomic, write_error_log


def test_save_image_atomic_writes_target_and_cleans_temp(tmp_path):
    path = tmp_path / "image.png"

    saved_path = save_image_atomic(path, Image.new("RGBA", (1, 1), (1, 2, 3, 255)))

    assert saved_path == path
    assert Image.open(path).getpixel((0, 0)) == (1, 2, 3, 255)
    assert not list(tmp_path.glob(".image.png.*.png"))


def test_error_log_and_recovery_paths_use_configurable_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSHOP_DATA_DIR", str(tmp_path))

    try:
        raise RuntimeError("boom")
    except RuntimeError as exc:
        log_path = write_error_log("Open Image", exc)

    assert log_path.exists()
    assert "Open Image" in log_path.read_text(encoding="utf-8")
    assert "RuntimeError: boom" in log_path.read_text(encoding="utf-8")
    assert recovery_project_path() == tmp_path / "recovery" / "autosave.pyshop"


def test_clear_recovery_project_removes_existing_autosave(tmp_path, monkeypatch):
    monkeypatch.setenv("PYSHOP_DATA_DIR", str(tmp_path))
    path = recovery_project_path()
    path.parent.mkdir(parents=True)
    path.write_text("placeholder", encoding="utf-8")

    clear_recovery_project()

    assert not path.exists()
