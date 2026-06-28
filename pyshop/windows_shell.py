import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .app_info import APP_DISPLAY_NAME, APP_NAME, app_icon_path


PROG_ID = "PyShop.Project"
IMAGE_CONTEXT_KEY = r"Software\Classes\SystemFileAssociations\image\shell\PyShop.Edit"
PROJECT_CONTEXT_KEY = r"Software\Classes\PyShop.Project\shell\open"


@dataclass(frozen=True)
class RegistryEntry:
    key: str
    name: str | None
    value: str


def default_launch_command() -> str:
    if getattr(sys, "frozen", False):
        return format_open_command([Path(sys.executable)])
    script_path = Path(__file__).resolve().parent.parent / "pyshop_image_editor.py"
    if script_path.exists():
        return format_open_command([Path(sys.executable), script_path])
    return format_open_command([Path(sys.executable), "-m", "pyshop_image_editor"])


def format_open_command(parts) -> str:
    quoted = [subprocess.list2cmdline([str(part)]) for part in parts]
    quoted.append('"%1"')
    return " ".join(quoted)


def shell_registry_entries(command: str | None = None, icon_path: str | None = None) -> list[RegistryEntry]:
    command = command or default_launch_command()
    icon = str(icon_path or default_shell_icon_path())
    return [
        RegistryEntry(r"Software\Classes\.pyshop", None, PROG_ID),
        RegistryEntry(r"Software\Classes\.pyshop\OpenWithProgids", PROG_ID, ""),
        RegistryEntry(r"Software\Classes\PyShop.Project", None, "PyShop Project"),
        RegistryEntry(r"Software\Classes\PyShop.Project\DefaultIcon", None, icon),
        RegistryEntry(r"Software\Classes\PyShop.Project\shell", None, "open"),
        RegistryEntry(PROJECT_CONTEXT_KEY, None, f"Open with {APP_NAME}"),
        RegistryEntry(PROJECT_CONTEXT_KEY, "Icon", icon),
        RegistryEntry(PROJECT_CONTEXT_KEY + r"\command", None, command),
        RegistryEntry(IMAGE_CONTEXT_KEY, None, f"Edit with {APP_NAME}"),
        RegistryEntry(IMAGE_CONTEXT_KEY, "Icon", icon),
        RegistryEntry(IMAGE_CONTEXT_KEY + r"\command", None, command),
        RegistryEntry(r"Software\Classes\Applications\PyShop.exe", None, APP_DISPLAY_NAME),
        RegistryEntry(r"Software\Classes\Applications\PyShop.exe\DefaultIcon", None, icon),
        RegistryEntry(r"Software\Classes\Applications\PyShop.exe\shell\open\command", None, command),
    ]


def default_shell_icon_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    icon = repo_root / "icon.ico"
    if icon.exists():
        return icon
    return app_icon_path()


def install_windows_shell(command: str | None = None, icon_path: str | None = None) -> int:
    winreg = _winreg()
    for entry in shell_registry_entries(command, icon_path):
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, entry.key, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, entry.name, 0, winreg.REG_SZ, entry.value)
    _notify_shell()
    return len(shell_registry_entries(command, icon_path))


def remove_windows_shell() -> int:
    keys = [
        r"Software\Classes\Applications\PyShop.exe\shell\open\command",
        r"Software\Classes\Applications\PyShop.exe\shell\open",
        r"Software\Classes\Applications\PyShop.exe\shell",
        r"Software\Classes\Applications\PyShop.exe\DefaultIcon",
        r"Software\Classes\Applications\PyShop.exe",
        IMAGE_CONTEXT_KEY + r"\command",
        IMAGE_CONTEXT_KEY,
        PROJECT_CONTEXT_KEY + r"\command",
        PROJECT_CONTEXT_KEY,
        r"Software\Classes\PyShop.Project\shell",
        r"Software\Classes\PyShop.Project\DefaultIcon",
        r"Software\Classes\PyShop.Project",
        r"Software\Classes\.pyshop\OpenWithProgids",
        r"Software\Classes\.pyshop",
    ]
    winreg = _winreg()
    removed = 0
    for key in keys:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key)
            removed += 1
        except FileNotFoundError:
            pass
        except OSError:
            pass
    _notify_shell()
    return removed


def _winreg():
    if os.name != "nt":
        raise RuntimeError("Windows shell integration is only available on Windows.")
    import winreg

    return winreg


def _notify_shell():
    if os.name != "nt":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
    except Exception:
        pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install or remove PyShop Windows shell integration.")
    parser.add_argument("action", choices=("install", "remove", "print"))
    parser.add_argument("--command", help="Custom registry open command. Defaults to the current PyShop launch command.")
    parser.add_argument("--icon", help="Custom icon path. Defaults to PyShop's icon.")
    args = parser.parse_args(argv)

    if args.action == "print":
        for entry in shell_registry_entries(args.command, args.icon):
            name = "(Default)" if entry.name is None else entry.name
            print(f"{entry.key} [{name}] = {entry.value}")
        return 0
    if args.action == "install":
        count = install_windows_shell(args.command, args.icon)
        print(f"Installed {count} PyShop shell registry values.")
        return 0
    count = remove_windows_shell()
    print(f"Removed {count} PyShop shell registry keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
