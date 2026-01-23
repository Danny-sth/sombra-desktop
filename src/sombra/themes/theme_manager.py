"""Simplified theme manager - default qfluentwidgets styling."""

from typing import Optional

from PySide6.QtWidgets import QApplication

from ..config.settings import get_settings
from .colors import DARK_PALETTE, LIGHT_PALETTE


class ThemeManager:
    """Minimal theme manager - tracks theme preference only.

    All styling delegated to qfluentwidgets defaults.
    """

    THEME_MAP = {
        "dark": "dark",
        "light": "light",
    }

    def __init__(self, app: QApplication):
        """Initialize theme manager."""
        self._app = app
        self._current_theme: str = "dark"

        settings = get_settings()
        if settings.theme in self.THEME_MAP:
            self._current_theme = settings.theme

    @property
    def current_theme(self) -> str:
        """Get current theme name."""
        return self._current_theme

    @property
    def current_palette(self) -> dict[str, str]:
        """Get current color palette."""
        return LIGHT_PALETTE if self._current_theme == "light" else DARK_PALETTE

    def apply_theme(self, theme_name: str) -> None:
        """Apply theme (stores preference, qfluentwidgets handles styling)."""
        if theme_name not in self.THEME_MAP:
            theme_name = "dark"
        self._current_theme = theme_name

    def toggle_theme(self) -> str:
        """Switch between dark and light themes.

        Returns:
            The new theme name.
        """
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme

    def get_color(self, name: str) -> str:
        """Get a color from the current palette.

        Args:
            name: Color name (e.g., 'bg_primary', 'accent_primary').

        Returns:
            Color value.
        """
        return self.current_palette.get(name, "#000000")

    @staticmethod
    def available_themes() -> list[str]:
        """List available themes."""
        return ["dark", "light"]


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global ThemeManager instance.

    Raises:
        RuntimeError: If theme manager has not been initialized.
    """
    global _theme_manager
    if _theme_manager is None:
        raise RuntimeError("ThemeManager has not been initialized. Call init_theme_manager first.")
    return _theme_manager


def init_theme_manager(app: QApplication) -> ThemeManager:
    """Initialize the global ThemeManager.

    Args:
        app: The QApplication instance.

    Returns:
        The ThemeManager instance.
    """
    global _theme_manager
    _theme_manager = ThemeManager(app)
    return _theme_manager
