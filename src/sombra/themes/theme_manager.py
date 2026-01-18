"""Theme manager using qt-material for Material Design styling."""

from typing import Optional

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet, list_themes

from ..config.settings import get_settings
from .colors import DARK_PALETTE, LIGHT_PALETTE


class ThemeManager:
    """Manages application themes using qt-material.

    Provides Material Design styling with dark and light theme support.
    """

    # Map simple theme names to qt-material theme files
    THEME_MAP = {
        "dark": "dark_teal.xml",
        "light": "light_teal.xml",
    }

    # Custom CSS to append for app-specific widgets
    CUSTOM_CSS = """
    /* Voice button - circular style */
    QPushButton#voiceButton {
        min-width: 80px;
        max-width: 80px;
        min-height: 80px;
        max-height: 80px;
        border-radius: 40px;
        font-size: 24px;
    }

    QPushButton#voiceButton:pressed,
    QPushButton#voiceButton[recording="true"] {
        background-color: #e94560;
        border-color: #ff6b8a;
    }

    /* Title styling */
    QLabel#titleLabel {
        font-size: 20px;
        font-weight: bold;
    }

    QLabel#subtitleLabel {
        font-size: 12px;
        opacity: 0.7;
    }

    /* Output display */
    QTextBrowser#outputDisplay {
        border-radius: 8px;
        padding: 12px;
    }

    /* Status bar buttons */
    QPushButton#themeButton,
    QPushButton#settingsButton {
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        border-radius: 18px;
        font-size: 16px;
    }
    """

    def __init__(self, app: QApplication):
        """Initialize theme manager.

        Args:
            app: The QApplication instance.
        """
        self._app = app
        self._current_theme: str = "dark"

        # Load initial theme from settings
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
        """Apply a Material Design theme.

        Args:
            theme_name: Name of the theme ('dark' or 'light').
        """
        if theme_name not in self.THEME_MAP:
            theme_name = "dark"

        # Apply qt-material base theme
        material_theme = self.THEME_MAP[theme_name]
        apply_stylesheet(self._app, theme=material_theme, extra={'density_scale': '-1'})

        # Append custom CSS for app-specific widgets
        current_style = self._app.styleSheet()
        self._app.setStyleSheet(current_style + self.CUSTOM_CSS)

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
        """List all available qt-material themes.

        Returns:
            List of theme names.
        """
        return list_themes()


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
