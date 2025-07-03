# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Define data files to include
datas = [
    # Language files
    (str(current_dir / 'src' / 'locales' / 'en.yaml'), 'src/locales/'),
    (str(current_dir / 'src' / 'locales' / 'ja.yaml'), 'src/locales/'),
    # Assets (icons)
    (str(current_dir / 'assets' / 'app_icon.ico'), 'assets/'),
]

# Define hidden imports
hiddenimports = [
    'yaml',
    'psutil',
    'win32gui',
    'win32process',
    'win32con',
    'src.components',
    'src.core',
    'src.locales',
    'src.helper',
]

a = Analysis(
    ['app.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='App Sticky Memo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(current_dir / 'assets' / 'app_icon.ico'),
    version_file=None,
)
