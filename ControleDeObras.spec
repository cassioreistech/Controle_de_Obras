# -*- mode: python ; coding: utf-8 -*-
"""Spec do PyInstaller para empacotar o Controle de Obras em executavel."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.win32.versioninfo import VSVersionInfo  # noqa: F401

project_root = Path(SPECPATH).resolve()
src_dir = project_root / "src"

block_cipher = None

a = Analysis(
    [str(src_dir / "controle_obras" / "main.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        (str(project_root / "assets" / "icon.png"), "assets"),
        (str(project_root / "assets" / "icon.ico"), "assets"),
    ],
    hiddenimports=[
        "controle_obras.application.reportlab_pdf_service",
        "controle_obras.application.docx_report_service",
        "controle_obras.infrastructure.backup",
        "controle_obras.infrastructure.backup_history",
        "controle_obras.infrastructure.database",
        "controle_obras.infrastructure.repositories",
        "controle_obras.infrastructure.storage",
        "controle_obras.ui.app_container",
        "controle_obras.ui.anexos_screen",
        "controle_obras.ui.dashboard_screen",
        "controle_obras.ui.empresa_screen",
        "controle_obras.ui.lancamentos_screen",
        "controle_obras.ui.obra_form_screen",
        "controle_obras.ui.obras_list_screen",
        "controle_obras.ui.styles",
        "controle_obras.ui.welcome_screen",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pandas", "numpy", "pytest", "playwright"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ControleDeObras",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "icon.ico"),
    version=str(project_root / "version_info.txt"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ControleDeObras",
)