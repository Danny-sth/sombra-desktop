"""UI utilities."""

import platform
import sys
from pathlib import Path
from typing import Dict

from PySide6.QtGui import QIcon

from sombra import __app_name__, __version__


def get_app_icon() -> QIcon:
    """Get the application icon (cross-platform)."""
    # Determine base path for resources
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running from source
        base_path = Path(__file__).parent.parent.parent.parent / "resources"

    icons_path = base_path / "icons"

    # Try PNG first (works everywhere), then ICO (Windows)
    icon = QIcon()

    # Add multiple sizes for best quality
    for size in [16, 32, 48, 64, 128, 256, 512]:
        png_file = icons_path / f"sombra-{size}.png"
        if png_file.exists():
            icon.addFile(str(png_file))

    # Fallback to ICO if no PNGs found
    if icon.isNull():
        ico_file = icons_path / "sombra.ico"
        if ico_file.exists():
            icon = QIcon(str(ico_file))

    return icon


def health_check() -> Dict[str, str]:
    """Return version and system info for health checks.

    Returns:
        Dictionary containing version, app_name, python_version, and platform.
    """
    return {
        "version": __version__,
        "app_name": __app_name__,
        "python_version": platform.python_version(),
        "platform": platform.system(),
    }
