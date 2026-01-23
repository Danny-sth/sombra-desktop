"""Theme manager using qt-material for Material Design styling.

Enhanced with Sombra branding, glassmorphism effects, and unified design system.
"""

from typing import Optional

from PySide6.QtWidgets import QApplication, QGraphicsBlurEffect, QWidget
from qt_material import apply_stylesheet, list_themes

from ..config.settings import get_settings
from .colors import (
    BORDER_RADIUS,
    DARK_PALETTE,
    LIGHT_PALETTE,
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_MUTED,
    TRANSPARENCY,
    get_blur,
    get_radius,
    get_shadow,
    get_transparency,
    hex_to_rgba,
)


class ThemeManager:
    """Manages application themes with Sombra branding.

    Provides Material Design base with custom Sombra styling,
    glassmorphism effects, and unified design tokens.
    """

    # Map simple theme names to qt-material theme files
    THEME_MAP = {
        "dark": "dark_teal.xml",
        "light": "light_teal.xml",
    }

    # Sombra brand colors for CSS
    _PRIMARY = SOMBRA_PRIMARY           # #e94560
    _PRIMARY_LIGHT = SOMBRA_PRIMARY_LIGHT   # #ff6b8a
    _PRIMARY_DARK = SOMBRA_PRIMARY_DARK     # #c73e54
    _PRIMARY_MUTED = SOMBRA_PRIMARY_MUTED   # #a63346
    _PRIMARY_RGB = "233, 69, 96"
    _PRIMARY_LIGHT_RGB = "255, 107, 138"

    # Custom CSS with Sombra branding
    CUSTOM_CSS = f"""
    /* ==========================================================================
       SOMBRA GLOBAL STYLES
       ========================================================================== */

    /* Global text selection */
    *::selection {{
        background-color: rgba({_PRIMARY_RGB}, 0.35);
        color: #f0f0f0;
    }}

    /* ==========================================================================
       BUTTONS - Sombra Branded
       ========================================================================== */

    /* Primary button */
    PrimaryPushButton {{
        background-color: {_PRIMARY};
        border: none;
        border-radius: {BORDER_RADIUS["md"]};
        padding: 8px 20px;
        color: white;
        font-weight: 500;
    }}
    PrimaryPushButton:hover {{
        background-color: {_PRIMARY_LIGHT};
    }}
    PrimaryPushButton:pressed {{
        background-color: {_PRIMARY_DARK};
    }}
    PrimaryPushButton:disabled {{
        background-color: rgba({_PRIMARY_RGB}, 0.35);
        color: rgba(255, 255, 255, 0.50);
    }}

    /* Secondary/outline button */
    PushButton {{
        background-color: transparent;
        border: 1px solid rgba({_PRIMARY_RGB}, 0.30);
        border-radius: {BORDER_RADIUS["md"]};
        padding: 8px 20px;
        color: #f0f0f0;
    }}
    PushButton:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.10);
        border-color: rgba({_PRIMARY_RGB}, 0.50);
    }}
    PushButton:pressed {{
        background-color: rgba({_PRIMARY_RGB}, 0.18);
    }}

    /* Ghost/transparent button */
    TransparentPushButton {{
        background-color: transparent;
        border: none;
        border-radius: {BORDER_RADIUS["md"]};
        padding: 8px 16px;
        color: #a8a8b3;
    }}
    TransparentPushButton:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.08);
        color: #f0f0f0;
    }}
    TransparentPushButton:pressed {{
        background-color: rgba({_PRIMARY_RGB}, 0.14);
    }}

    /* Tool button */
    ToolButton {{
        background-color: transparent;
        border: none;
        border-radius: {BORDER_RADIUS["md"]};
        padding: 6px;
    }}
    ToolButton:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.10);
    }}
    ToolButton:pressed {{
        background-color: rgba({_PRIMARY_RGB}, 0.18);
    }}

    /* ==========================================================================
       VOICE BUTTON - Special Circular Style
       ========================================================================== */

    QPushButton#voiceButton {{
        min-width: 80px;
        max-width: 80px;
        min-height: 80px;
        max-height: 80px;
        border-radius: 40px;
        font-size: 24px;
        background-color: rgba({_PRIMARY_RGB}, 0.15);
        border: 2px solid rgba({_PRIMARY_RGB}, 0.30);
    }}
    QPushButton#voiceButton:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.25);
        border-color: rgba({_PRIMARY_RGB}, 0.50);
    }}
    QPushButton#voiceButton:pressed,
    QPushButton#voiceButton[recording="true"] {{
        background-color: {_PRIMARY};
        border-color: {_PRIMARY_LIGHT};
    }}

    /* ==========================================================================
       INPUT FIELDS - Sombra Styled
       ========================================================================== */

    /* Line edit */
    QLineEdit, LineEdit {{
        background-color: {TRANSPARENCY["input_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
        border-radius: {BORDER_RADIUS["md"]};
        padding: 10px 14px;
        color: #f0f0f0;
        selection-background-color: rgba({_PRIMARY_RGB}, 0.35);
    }}
    QLineEdit:hover, LineEdit:hover {{
        border-color: rgba({_PRIMARY_RGB}, 0.35);
        background-color: rgba(13, 27, 42, 0.90);
    }}
    QLineEdit:focus, LineEdit:focus {{
        border-color: rgba({_PRIMARY_RGB}, 0.55);
        background-color: {TRANSPARENCY["input_bg_focus"]};
    }}

    /* Text edit / multi-line */
    QTextEdit, TextEdit, PlainTextEdit {{
        background-color: {TRANSPARENCY["input_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
        border-radius: {BORDER_RADIUS["md"]};
        padding: 10px 14px;
        color: #f0f0f0;
        selection-background-color: rgba({_PRIMARY_RGB}, 0.35);
    }}
    QTextEdit:hover, TextEdit:hover {{
        border-color: rgba({_PRIMARY_RGB}, 0.35);
    }}
    QTextEdit:focus, TextEdit:focus {{
        border-color: rgba({_PRIMARY_RGB}, 0.55);
        background-color: {TRANSPARENCY["input_bg_focus"]};
    }}

    /* Search box */
    SearchLineEdit {{
        background-color: {TRANSPARENCY["input_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.15);
        border-radius: {BORDER_RADIUS["md"]};
        padding: 8px 12px;
    }}
    SearchLineEdit:focus {{
        border-color: rgba({_PRIMARY_RGB}, 0.45);
    }}

    /* Spin box */
    SpinBox, DoubleSpinBox {{
        background-color: {TRANSPARENCY["input_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
        border-radius: {BORDER_RADIUS["md"]};
        padding: 6px 10px;
    }}

    /* ==========================================================================
       CARDS & PANELS - Glassmorphism
       ========================================================================== */

    /* Simple card */
    SimpleCardWidget {{
        background-color: {TRANSPARENCY["card_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
        border-radius: {BORDER_RADIUS["lg"]};
    }}
    SimpleCardWidget:hover {{
        background-color: {TRANSPARENCY["card_bg_hover"]};
        border-color: rgba({_PRIMARY_RGB}, 0.22);
    }}

    /* Card widget */
    CardWidget {{
        background-color: {TRANSPARENCY["card_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
        border-radius: {BORDER_RADIUS["lg"]};
    }}
    CardWidget:hover {{
        background-color: {TRANSPARENCY["card_bg_hover"]};
        border-color: rgba({_PRIMARY_RGB}, 0.22);
    }}

    /* Elevated card */
    ElevatedCardWidget {{
        background-color: {TRANSPARENCY["card_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.15);
        border-radius: {BORDER_RADIUS["lg"]};
    }}

    /* Info bar / banner */
    InfoBar {{
        background-color: {TRANSPARENCY["panel_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
        border-radius: {BORDER_RADIUS["md"]};
    }}

    /* ==========================================================================
       DIALOGS & POPUPS - Glassmorphism
       ========================================================================== */

    /* Message box / dialog */
    MessageBox, Dialog {{
        background-color: {TRANSPARENCY["dialog_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
        border-radius: {BORDER_RADIUS["xl"]};
    }}

    /* Flyout */
    FlyoutViewBase {{
        background-color: {TRANSPARENCY["dialog_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.18);
        border-radius: {BORDER_RADIUS["lg"]};
    }}

    /* Menu */
    RoundMenu {{
        background-color: {TRANSPARENCY["panel_bg_heavy"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.15);
        border-radius: {BORDER_RADIUS["md"]};
    }}

    /* Tooltip */
    QToolTip, ToolTip {{
        background-color: {TRANSPARENCY["tooltip_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.25);
        border-radius: {BORDER_RADIUS["sm"]};
        padding: 6px 10px;
        color: #f0f0f0;
    }}

    /* ==========================================================================
       NAVIGATION - Sidebar & Tabs
       ========================================================================== */

    /* Navigation panel */
    NavigationPanel {{
        background-color: {TRANSPARENCY["panel_bg"]};
        border-right: 1px solid rgba({_PRIMARY_RGB}, 0.10);
    }}

    /* Navigation item */
    NavigationPushButton {{
        border-radius: {BORDER_RADIUS["md"]};
    }}
    NavigationPushButton:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.08);
    }}
    NavigationPushButton:pressed {{
        background-color: rgba({_PRIMARY_RGB}, 0.14);
    }}
    NavigationPushButton:checked {{
        background-color: rgba({_PRIMARY_RGB}, 0.12);
    }}

    /* Tab widget */
    TabBar {{
        background-color: transparent;
    }}
    TabBar::tab {{
        border-radius: {BORDER_RADIUS["sm"]};
        padding: 8px 16px;
    }}
    TabBar::tab:selected {{
        background-color: rgba({_PRIMARY_RGB}, 0.15);
    }}
    TabBar::tab:hover:!selected {{
        background-color: rgba({_PRIMARY_RGB}, 0.08);
    }}

    /* Pivot (top tabs) */
    PivotItem {{
        border-radius: {BORDER_RADIUS["sm"]};
    }}
    PivotItem:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.06);
    }}
    PivotItem:pressed {{
        background-color: rgba({_PRIMARY_RGB}, 0.10);
    }}

    /* ==========================================================================
       SCROLLBARS - Sombra Pink
       ========================================================================== */

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: rgba({_PRIMARY_RGB}, 0.30);
        border-radius: 4px;
        min-height: 40px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba({_PRIMARY_RGB}, 0.50);
    }}
    QScrollBar::handle:vertical:pressed {{
        background: rgba({_PRIMARY_RGB}, 0.60);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
        background: none;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 2px 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba({_PRIMARY_RGB}, 0.30);
        border-radius: 4px;
        min-width: 40px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: rgba({_PRIMARY_RGB}, 0.50);
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
        background: none;
    }}

    /* Smooth scroll area */
    SmoothScrollArea {{
        background-color: transparent;
        border: none;
    }}

    /* ==========================================================================
       LIST & TREE VIEWS
       ========================================================================== */

    QListView, ListView {{
        background-color: transparent;
        border: none;
        border-radius: {BORDER_RADIUS["md"]};
    }}
    QListView::item, ListView::item {{
        border-radius: {BORDER_RADIUS["sm"]};
        padding: 6px 10px;
    }}
    QListView::item:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.08);
    }}
    QListView::item:selected {{
        background-color: rgba({_PRIMARY_RGB}, 0.15);
    }}

    QTreeView, TreeView {{
        background-color: transparent;
        border: none;
    }}
    QTreeView::item {{
        border-radius: {BORDER_RADIUS["sm"]};
        padding: 4px 8px;
    }}
    QTreeView::item:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.08);
    }}
    QTreeView::item:selected {{
        background-color: rgba({_PRIMARY_RGB}, 0.15);
    }}

    /* ==========================================================================
       COMBO BOX & DROPDOWN
       ========================================================================== */

    ComboBox {{
        background-color: {TRANSPARENCY["input_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
        border-radius: {BORDER_RADIUS["md"]};
        padding: 6px 12px;
    }}
    ComboBox:hover {{
        border-color: rgba({_PRIMARY_RGB}, 0.35);
    }}
    ComboBox:focus {{
        border-color: rgba({_PRIMARY_RGB}, 0.55);
    }}

    /* ==========================================================================
       TOGGLE & CHECKBOX
       ========================================================================== */

    SwitchButton {{
        border-radius: {BORDER_RADIUS["full"]};
    }}
    SwitchButton:checked {{
        background-color: {_PRIMARY};
    }}

    CheckBox::indicator {{
        border-radius: {BORDER_RADIUS["sm"]};
    }}
    CheckBox::indicator:checked {{
        background-color: {_PRIMARY};
        border-color: {_PRIMARY};
    }}

    RadioButton::indicator {{
        border-radius: {BORDER_RADIUS["full"]};
    }}
    RadioButton::indicator:checked {{
        background-color: {_PRIMARY};
        border-color: {_PRIMARY};
    }}

    /* ==========================================================================
       SLIDER & PROGRESS
       ========================================================================== */

    Slider::groove {{
        background-color: rgba({_PRIMARY_RGB}, 0.20);
        border-radius: 3px;
    }}
    Slider::handle {{
        background-color: {_PRIMARY};
        border-radius: {BORDER_RADIUS["full"]};
    }}
    Slider::handle:hover {{
        background-color: {_PRIMARY_LIGHT};
    }}
    Slider::sub-page {{
        background-color: {_PRIMARY};
        border-radius: 3px;
    }}

    ProgressBar {{
        background-color: rgba({_PRIMARY_RGB}, 0.15);
        border-radius: {BORDER_RADIUS["sm"]};
    }}
    ProgressBar::chunk {{
        background-color: {_PRIMARY};
        border-radius: {BORDER_RADIUS["sm"]};
    }}

    IndeterminateProgressBar {{
        background-color: rgba({_PRIMARY_RGB}, 0.15);
        border-radius: {BORDER_RADIUS["sm"]};
    }}

    /* ==========================================================================
       LABELS & TYPOGRAPHY
       ========================================================================== */

    QLabel#titleLabel, TitleLabel {{
        font-size: 20px;
        font-weight: bold;
        color: #f0f0f0;
    }}

    QLabel#subtitleLabel, SubtitleLabel {{
        font-size: 14px;
        color: #a8a8b3;
    }}

    CaptionLabel {{
        color: #888899;
    }}

    StrongBodyLabel {{
        font-weight: 600;
    }}

    /* Hyperlink */
    HyperlinkLabel {{
        color: {_PRIMARY};
    }}
    HyperlinkLabel:hover {{
        color: {_PRIMARY_LIGHT};
    }}

    /* ==========================================================================
       OUTPUT DISPLAY & TEXT BROWSER
       ========================================================================== */

    QTextBrowser#outputDisplay {{
        background-color: {TRANSPARENCY["card_bg"]};
        border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
        border-radius: {BORDER_RADIUS["lg"]};
        padding: 12px;
        selection-background-color: rgba({_PRIMARY_RGB}, 0.35);
    }}

    QTextBrowser {{
        background-color: transparent;
        border: none;
        selection-background-color: rgba({_PRIMARY_RGB}, 0.35);
    }}

    /* ==========================================================================
       STATUS BAR BUTTONS
       ========================================================================== */

    QPushButton#themeButton,
    QPushButton#settingsButton {{
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        border-radius: 18px;
        font-size: 16px;
        background-color: transparent;
        border: 1px solid rgba({_PRIMARY_RGB}, 0.20);
    }}
    QPushButton#themeButton:hover,
    QPushButton#settingsButton:hover {{
        background-color: rgba({_PRIMARY_RGB}, 0.10);
        border-color: rgba({_PRIMARY_RGB}, 0.35);
    }}

    /* ==========================================================================
       SPECIAL STATES
       ========================================================================== */

    /* Focus ring */
    *:focus {{
        outline: none;
    }}

    /* Disabled state */
    *:disabled {{
        opacity: 0.5;
    }}
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

    @property
    def is_dark(self) -> bool:
        """Check if current theme is dark."""
        return self._current_theme == "dark"

    def apply_theme(self, theme_name: str) -> None:
        """Apply a Material Design theme with Sombra customizations.

        Args:
            theme_name: Name of the theme ('dark' or 'light').
        """
        if theme_name not in self.THEME_MAP:
            theme_name = "dark"

        # Apply qt-material base theme
        material_theme = self.THEME_MAP[theme_name]
        apply_stylesheet(self._app, theme=material_theme, extra={'density_scale': '-1'})

        # Append custom Sombra CSS
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

    # ==========================================================================
    # TRANSPARENCY & GLASSMORPHISM HELPERS
    # ==========================================================================

    @staticmethod
    def get_transparency(key: str) -> str:
        """Get transparency value for glassmorphism effects.

        Args:
            key: Transparency key ('panel_bg', 'card_bg', 'dialog_bg', etc.)

        Returns:
            RGBA color string.

        Example:
            >>> ThemeManager.get_transparency('panel_bg')
            'rgba(26, 26, 46, 0.85)'
        """
        return get_transparency(key)

    @staticmethod
    def get_blur_value(size: str = "md") -> str:
        """Get blur value for backdrop effects.

        Args:
            size: Blur size ('sm', 'md', 'lg', 'xl', '2xl').

        Returns:
            CSS blur value string.

        Example:
            >>> ThemeManager.get_blur_value('lg')
            '12px'
        """
        return get_blur(size)

    @staticmethod
    def create_blur_effect(radius: float = 10.0) -> QGraphicsBlurEffect:
        """Create a QGraphicsBlurEffect for widget transparency.

        Args:
            radius: Blur radius in pixels.

        Returns:
            Configured QGraphicsBlurEffect.

        Example:
            >>> effect = ThemeManager.create_blur_effect(8.0)
            >>> widget.setGraphicsEffect(effect)
        """
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(radius)
        return effect

    @staticmethod
    def apply_glassmorphism(
        widget: QWidget,
        blur_radius: float = 10.0,
        bg_key: str = "panel_bg"
    ) -> None:
        """Apply glassmorphism effect to a widget.

        Applies background transparency and optional blur effect.

        Args:
            widget: The widget to style.
            blur_radius: Blur radius for the effect.
            bg_key: Transparency key for background.

        Note:
            Qt's blur effect applies to widget content, not background.
            For true backdrop blur, use platform-specific solutions.
        """
        bg_color = get_transparency(bg_key)
        border_radius = get_radius("lg")

        widget.setStyleSheet(f"""
            background-color: {bg_color};
            border: 1px solid rgba(233, 69, 96, 0.15);
            border-radius: {border_radius};
        """)

    # ==========================================================================
    # SHADOW HELPERS
    # ==========================================================================

    @staticmethod
    def get_shadow(key: str = "md") -> str:
        """Get shadow value for elevation effects.

        Args:
            key: Shadow key ('sm', 'md', 'lg', 'card', 'button', 'glow_sm', etc.)

        Returns:
            CSS box-shadow string.

        Example:
            >>> ThemeManager.get_shadow('card')
            '0 4px 12px rgba(0, 0, 0, 0.25), 0 0 1px rgba(233, 69, 96, 0.10)'
        """
        return get_shadow(key)

    # ==========================================================================
    # BORDER RADIUS HELPERS
    # ==========================================================================

    @staticmethod
    def get_radius(size: str = "md") -> str:
        """Get border radius value.

        Args:
            size: Size key ('sm', 'md', 'lg', 'xl', '2xl', 'full').

        Returns:
            CSS border-radius value.

        Example:
            >>> ThemeManager.get_radius('lg')
            '12px'
        """
        return get_radius(size)

    # ==========================================================================
    # COLOR UTILITIES
    # ==========================================================================

    @staticmethod
    def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
        """Convert hex color to rgba string.

        Args:
            hex_color: Hex color string like '#e94560'.
            alpha: Alpha value (0.0 to 1.0).

        Returns:
            RGBA color string.

        Example:
            >>> ThemeManager.hex_to_rgba('#e94560', 0.5)
            'rgba(233, 69, 96, 0.5)'
        """
        return hex_to_rgba(hex_color, alpha)

    @staticmethod
    def get_primary_color(variant: str = "default") -> str:
        """Get Sombra primary color variant.

        Args:
            variant: Color variant ('default', 'light', 'dark', 'muted').

        Returns:
            Hex color string.

        Example:
            >>> ThemeManager.get_primary_color('light')
            '#ff6b8a'
        """
        variants = {
            "default": SOMBRA_PRIMARY,
            "light": SOMBRA_PRIMARY_LIGHT,
            "dark": SOMBRA_PRIMARY_DARK,
            "muted": SOMBRA_PRIMARY_MUTED,
        }
        return variants.get(variant, SOMBRA_PRIMARY)

    # ==========================================================================
    # STYLE GENERATION HELPERS
    # ==========================================================================

    @classmethod
    def generate_card_style(
        cls,
        accent_rgb: str = None,
        radius: str = "lg",
        include_hover: bool = True
    ) -> str:
        """Generate custom card stylesheet.

        Args:
            accent_rgb: RGB values string (e.g., "233, 69, 96").
            radius: Border radius size key.
            include_hover: Whether to include hover state.

        Returns:
            CSS stylesheet string.
        """
        rgb = accent_rgb or cls._PRIMARY_RGB
        border_radius = get_radius(radius)
        card_bg = get_transparency("card_bg")
        card_hover = get_transparency("card_bg_hover")

        style = f"""
            background-color: {card_bg};
            border: 1px solid rgba({rgb}, 0.12);
            border-radius: {border_radius};
        """

        if include_hover:
            style = f"""
                SimpleCardWidget {{
                    background-color: {card_bg};
                    border: 1px solid rgba({rgb}, 0.12);
                    border-radius: {border_radius};
                }}
                SimpleCardWidget:hover {{
                    background-color: {card_hover};
                    border-color: rgba({rgb}, 0.25);
                }}
            """

        return style

    @classmethod
    def generate_button_style(
        cls,
        variant: str = "primary",
        radius: str = "md"
    ) -> str:
        """Generate custom button stylesheet.

        Args:
            variant: Button variant ('primary', 'secondary', 'ghost').
            radius: Border radius size key.

        Returns:
            CSS stylesheet string.
        """
        border_radius = get_radius(radius)

        if variant == "primary":
            return f"""
                background-color: {cls._PRIMARY};
                border: none;
                border-radius: {border_radius};
                color: white;
                padding: 8px 20px;
            """
        elif variant == "secondary":
            return f"""
                background-color: transparent;
                border: 1px solid rgba({cls._PRIMARY_RGB}, 0.30);
                border-radius: {border_radius};
                color: #f0f0f0;
                padding: 8px 20px;
            """
        else:  # ghost
            return f"""
                background-color: transparent;
                border: none;
                border-radius: {border_radius};
                color: #a8a8b3;
                padding: 8px 16px;
            """

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
