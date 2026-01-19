# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Sombra Desktop
Cross-platform build configuration (Windows/Linux/macOS)
"""

import sys
import os
from pathlib import Path

# Detect platform
is_windows = sys.platform == 'win32'
is_macos = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# Paths
ROOT_DIR = Path(SPECPATH)
SRC_DIR = ROOT_DIR / 'src'
RESOURCES_DIR = ROOT_DIR / 'resources'
MODELS_DIR = ROOT_DIR / 'models'

# Icon based on platform
if is_windows:
    icon_file = str(RESOURCES_DIR / 'icons' / 'sombra.ico')
elif is_macos:
    icon_file = str(RESOURCES_DIR / 'icons' / 'sombra-512.png')  # Will need .icns for proper macOS
else:
    icon_file = str(RESOURCES_DIR / 'icons' / 'sombra-256.png')

# Collect data files
datas = [
    (str(RESOURCES_DIR), 'resources'),
]

# Add models if they exist
if MODELS_DIR.exists():
    datas.append((str(MODELS_DIR), 'models'))

# Add .env.example as template
env_example = ROOT_DIR / '.env.example'
if env_example.exists():
    datas.append((str(env_example), '.'))

# Hidden imports for dynamic loading
hiddenimports = [
    # PySide6
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',

    # Fluent Widgets
    'qfluentwidgets',
    'qfluentwidgets.components',
    'qfluentwidgets.common',
    'qfluentwidgets.window',

    # HTTP/SSE
    'httpx',
    'httpx_sse',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',

    # Audio
    'sounddevice',
    'pyaudio',
    'numpy',

    # Wake word
    'pvporcupine',

    # VAD
    'silero_vad',
    'torch',

    # Hotkeys
    'pynput',
    'pynput.keyboard',
    'pynput.keyboard._win32' if is_windows else 'pynput.keyboard._xorg',

    # Utils
    'markdown',
    'pygments',
    'dotenv',
]

# Platform-specific hidden imports
if is_windows:
    hiddenimports.extend([
        'win32api',
        'win32con',
        'pywintypes',
    ])

# Excluded modules to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    'PIL',
    'scipy',
    'pandas',
    'notebook',
    'jupyter',
    'IPython',
]

# Analysis
a = Analysis(
    [str(SRC_DIR / 'sombra' / '__main__.py')],
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# Remove unnecessary torch files to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith('torch/lib/libtorch_cuda')]
a.binaries = [x for x in a.binaries if 'cudnn' not in x[0].lower()]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Sombra',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version='version_info.txt' if is_windows and Path('version_info.txt').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Sombra',
)

# macOS app bundle (optional)
if is_macos:
    app = BUNDLE(
        coll,
        name='Sombra.app',
        icon=icon_file,
        bundle_identifier='dev.sombra.desktop',
        info_plist={
            'CFBundleName': 'Sombra',
            'CFBundleDisplayName': 'Sombra',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.0',
            'NSMicrophoneUsageDescription': 'Sombra needs microphone access for voice commands.',
            'NSHighResolutionCapable': True,
        },
    )
