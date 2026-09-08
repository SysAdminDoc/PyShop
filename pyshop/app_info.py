import os
import sys
from pathlib import Path

APP_NAME = "PyShop"
APP_VERSION = "0.1.43"
APP_DISPLAY_NAME = f"{APP_NAME} v{APP_VERSION}"


def app_settings():
    from PyQt5.QtCore import QSettings

    profile = os.environ.get("PYSHOP_TEST_PROFILE", "")
    if not profile:
        return QSettings("SysAdminDoc", "PyShop")
    root = Path(profile)
    if not root.is_absolute():
        raise ValueError("PYSHOP_TEST_PROFILE must be an absolute directory")
    root.mkdir(parents=True, exist_ok=True)
    return QSettings(str(root / "settings.ini"), QSettings.IniFormat)


def app_icon_path() -> Path:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "icon.png")
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "icon.png")

    package_dir = Path(__file__).resolve().parent
    repo_root = package_dir.parent
    candidates.extend(
        [
            repo_root / "icon.png",
            package_dir / "resources" / "icon.png",
            Path.cwd() / "icon.png",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path("icon.png")
