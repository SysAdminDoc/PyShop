from pathlib import Path

from pyshop.windows_shell import PROG_ID, format_open_command, shell_registry_entries


def test_format_open_command_quotes_paths_and_file_placeholder():
    command = format_open_command([Path(r"C:\Program Files\PyShop\PyShop.exe")])

    assert command.startswith('"C:\\Program Files\\PyShop\\PyShop.exe"')
    assert command.endswith('"%1"')


def test_shell_registry_entries_include_project_association_and_image_context_menu():
    command = '"PyShop.exe" "%1"'
    entries = shell_registry_entries(command, r"C:\PyShop\icon.ico")

    assert any(entry.key == r"Software\Classes\.pyshop" and entry.value == PROG_ID for entry in entries)
    assert any(
        entry.key == r"Software\Classes\PyShop.Project\shell\open\command" and entry.value == command
        for entry in entries
    )
    assert any(
        entry.key == r"Software\Classes\SystemFileAssociations\image\shell\PyShop.Edit\command"
        and entry.value == command
        for entry in entries
    )
