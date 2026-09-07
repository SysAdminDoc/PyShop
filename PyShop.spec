# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


ROOT = Path(SPEC).resolve().parent
qta_datas, qta_binaries, qta_hiddenimports = collect_all("qtawesome")

a = Analysis(
    [str(ROOT / "pyshop_image_editor.py")],
    pathex=[str(ROOT)],
    binaries=qta_binaries,
    datas=[(str(ROOT / "icon.png"), "."), *qta_datas],
    hiddenimports=qta_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "tools" / "runtime_hook_mp.py")],
    excludes=["matplotlib", "PyQt6", "PySide6", "tkinter"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PyShop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "icon.ico"),
    version=str(ROOT / "tools" / "version_info.txt"),
    uac_admin=False,
)
