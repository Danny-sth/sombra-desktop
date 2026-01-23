"""UI utilities."""

import platform
import sys
from pathlib import Path

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


def health_check() -> dict[str, str]:
    """Return health check information about the application.

    Returns:
        dict: A dictionary containing:
            - version: The application version
            - app_name: The application name
            - python_version: The Python version
            - platform: The operating system platform
    """
    return {
        "version": __version__,
        "app_name": __app_name__,
        "python_version": platform.python_version(),
        "platform": platform.system(),
    }
