"""Sombra theme constants and styles for Sombra Desktop.

Unified Sombra branding with pink/red accent (#e94560),
glassmorphism effects, and consistent design system.
"""

from sombra.themes.colors import (
    SOMBRA_PRIMARY,
    SOMBRA_PRIMARY_LIGHT,
    SOMBRA_PRIMARY_DARK,
    SOMBRA_PRIMARY_MUTED,
    SOMBRA_PURPLE,
    SOMBRA_CYAN,
    TRANSPARENCY,
    BORDER_RADIUS,
    SHADOWS,
    BLUR,
    DARK_PALETTE,
)


class SciFiTheme:
    """Centralized theme constants for Sombra UI.

    Unified branding with Sombra pink (#e94560) as primary accent.
    """

    # ==========================================================================
    # PRIMARY SOMBRA COLORS
    # ==========================================================================

    # Primary accent - Sombra Pink/Red
    PRIMARY = SOMBRA_PRIMARY           # #e94560
    PRIMARY_RGB = "233, 69, 96"
    PRIMARY_LIGHT = SOMBRA_PRIMARY_LIGHT   # #ff6b8a
    PRIMARY_LIGHT_RGB = "255, 107, 138"
    PRIMARY_DARK = SOMBRA_PRIMARY_DARK     # #c73e54
    PRIMARY_DARK_RGB = "199, 62, 84"
    PRIMARY_MUTED = SOMBRA_PRIMARY_MUTED   # #a63346
    PRIMARY_MUTED_RGB = "166, 51, 70"

    # Secondary colors
    SECONDARY = SOMBRA_PURPLE          # #533483
    SECONDARY_RGB = "83, 52, 131"
    ACCENT_CYAN = SOMBRA_CYAN          # #00d9ff (for info/links)
    ACCENT_CYAN_RGB = "0, 217, 255"

    # Legacy aliases (for backward compatibility)
    CYAN = SOMBRA_CYAN
    CYAN_RGB = ACCENT_CYAN_RGB
    MAGENTA = PRIMARY
    MAGENTA_RGB = PRIMARY_RGB
    DARK_CYAN = "#0096b3"
    DARK_MAGENTA = PRIMARY_DARK
    PURPLE = SOMBRA_PURPLE

    # ==========================================================================
    # BACKGROUND COLORS
    # ==========================================================================

    BG_DARK = DARK_PALETTE["bg_sunken"]      # #12121f
    BG_PANEL = DARK_PALETTE["bg_primary"]    # #1a1a2e
    BG_CARD = DARK_PALETTE["bg_secondary"]   # #16213e
    BG_ELEVATED = DARK_PALETTE["bg_elevated"]  # #1e2746
    BG_INPUT = DARK_PALETTE["bg_input"]      # #0d1b2a

    # ==========================================================================
    # TEXT COLORS
    # ==========================================================================

    TEXT_PRIMARY = DARK_PALETTE["text_primary"]      # #f0f0f0
    TEXT_SECONDARY = DARK_PALETTE["text_secondary"]  # #a8a8b3
    TEXT_MUTED = DARK_PALETTE["text_disabled"]       # #5a5a6e
    TEXT_PLACEHOLDER = DARK_PALETTE["text_placeholder"]  # #4a4a5e

    # ==========================================================================
    # GLASSMORPHISM CONSTANTS
    # ==========================================================================

    # Opacity levels
    GLASS_OPACITY = 0.10
    GLASS_OPACITY_HOVER = 0.15
    GLASS_OPACITY_ACTIVE = 0.20
    BORDER_OPACITY = 0.25
    BORDER_OPACITY_HOVER = 0.40
    BORDER_OPACITY_FOCUS = 0.55

    # Transparency values (from colors.py)
    PANEL_BG = TRANSPARENCY["panel_bg"]           # rgba(26, 26, 46, 0.85)
    PANEL_BG_LIGHT = TRANSPARENCY["panel_bg_light"]  # rgba(26, 26, 46, 0.70)
    CARD_BG = TRANSPARENCY["card_bg"]             # rgba(22, 33, 62, 0.80)
    CARD_BG_HOVER = TRANSPARENCY["card_bg_hover"] # rgba(22, 33, 62, 0.90)
    DIALOG_BG = TRANSPARENCY["dialog_bg"]         # rgba(22, 33, 62, 0.92)
    INPUT_BG = TRANSPARENCY["input_bg"]           # rgba(13, 27, 42, 0.85)
    INPUT_BG_FOCUS = TRANSPARENCY["input_bg_focus"]  # rgba(13, 27, 42, 0.95)

    # Blur values
    BLUR_SM = BLUR["sm"]    # 4px
    BLUR_MD = BLUR["md"]    # 8px
    BLUR_LG = BLUR["lg"]    # 12px
    BLUR_XL = BLUR["xl"]    # 16px

    # ==========================================================================
    # BORDER RADIUS
    # ==========================================================================

    RADIUS_SM = BORDER_RADIUS["sm"]    # 4px
    RADIUS_MD = BORDER_RADIUS["md"]    # 8px
    RADIUS_LG = BORDER_RADIUS["lg"]    # 12px
    RADIUS_XL = BORDER_RADIUS["xl"]    # 16px
    RADIUS_2XL = BORDER_RADIUS["2xl"]  # 20px
    RADIUS_FULL = BORDER_RADIUS["full"]  # 9999px

    # ==========================================================================
    # SHADOWS
    # ==========================================================================

    SHADOW_SM = SHADOWS["sm"]
    SHADOW_MD = SHADOWS["md"]
    SHADOW_LG = SHADOWS["lg"]
    SHADOW_CARD = SHADOWS["card"]
    SHADOW_CARD_HOVER = SHADOWS["card_hover"]
    SHADOW_BUTTON = SHADOWS["button"]
    SHADOW_BUTTON_HOVER = SHADOWS["button_hover"]
    SHADOW_GLOW_SM = SHADOWS["glow_sm"]
    SHADOW_GLOW_MD = SHADOWS["glow_md"]
    SHADOW_DIALOG = SHADOWS["dialog"]
    SHADOW_INSET = SHADOWS["inset"]
    SHADOW_INSET_FOCUS = SHADOWS["inset_focus"]

    # ==========================================================================
    # STATUS COLORS
    # ==========================================================================

    SUCCESS = DARK_PALETTE["success"]          # #4ecca3
    SUCCESS_RGB = "78, 204, 163"
    WARNING = DARK_PALETTE["warning"]          # #f9a825
    WARNING_RGB = "249, 168, 37"
    ERROR = DARK_PALETTE["error"]              # #ff6b6b
    ERROR_RGB = "255, 107, 107"
    INFO = SOMBRA_CYAN                         # #00d9ff
    INFO_RGB = ACCENT_CYAN_RGB

    # ==========================================================================
    # CHAT BUBBLE STYLES - Sombra Branded
    # ==========================================================================

    # Sombra/AI bubble style (primary pink accent)
    SOMBRA_BUBBLE = f"""
        ChatBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({PRIMARY_RGB}, 0.10),
                stop:1 rgba({PRIMARY_RGB}, 0.04));
            border: 1px solid rgba({PRIMARY_RGB}, 0.25);
            border-radius: {RADIUS_LG};
        }}
        ChatBubble:hover {{
            border: 1px solid rgba({PRIMARY_RGB}, 0.40);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({PRIMARY_RGB}, 0.14),
                stop:1 rgba({PRIMARY_RGB}, 0.06));
        }}
    """

    # User bubble style (lighter pink, slightly different gradient)
    USER_BUBBLE = f"""
        ChatBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({PRIMARY_LIGHT_RGB}, 0.08),
                stop:1 rgba({PRIMARY_RGB}, 0.03));
            border: 1px solid rgba({PRIMARY_LIGHT_RGB}, 0.20);
            border-radius: {RADIUS_LG};
        }}
        ChatBubble:hover {{
            border: 1px solid rgba({PRIMARY_LIGHT_RGB}, 0.35);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({PRIMARY_LIGHT_RGB}, 0.12),
                stop:1 rgba({PRIMARY_RGB}, 0.05));
        }}
    """

    # Thinking bubble style (muted, subtle animation feel)
    THINKING_BUBBLE = f"""
        ThinkingBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({SECONDARY_RGB}, 0.08),
                stop:1 rgba({SECONDARY_RGB}, 0.03));
            border: 1px solid rgba({SECONDARY_RGB}, 0.20);
            border-radius: {RADIUS_LG};
        }}
    """

    # Streaming bubble style (active, pulsing feel)
    STREAMING_BUBBLE = f"""
        StreamingBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({PRIMARY_RGB}, 0.08),
                stop:1 rgba({PRIMARY_RGB}, 0.03));
            border: 1px solid rgba({PRIMARY_RGB}, 0.30);
            border-radius: {RADIUS_LG};
        }}
    """

    # ==========================================================================
    # TEXT BROWSER STYLES
    # ==========================================================================

    TEXT_BROWSER = f"""
        QTextBrowser {{
            background-color: transparent;
            border: none;
            padding: 0;
            selection-background-color: rgba({PRIMARY_RGB}, 0.35);
            selection-color: {TEXT_PRIMARY};
        }}
    """

    # ==========================================================================
    # CONTAINER STYLES
    # ==========================================================================

    CHAT_CONTAINER = f"""
        QWidget#chatContainer {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {BG_DARK},
                stop:0.5 {BG_PANEL},
                stop:1 {BG_DARK});
        }}
    """

    # ==========================================================================
    # INPUT FIELD STYLES
    # ==========================================================================

    INPUT_FIELD = f"""
        QLineEdit {{
            background-color: {INPUT_BG};
            border: 1px solid rgba({PRIMARY_RGB}, 0.20);
            border-radius: {RADIUS_MD};
            padding: 10px 14px;
            color: {TEXT_PRIMARY};
            font-size: 14px;
        }}
        QLineEdit:hover {{
            border: 1px solid rgba({PRIMARY_RGB}, 0.35);
            background-color: rgba(13, 27, 42, 0.90);
        }}
        QLineEdit:focus {{
            border: 1px solid rgba({PRIMARY_RGB}, 0.55);
            background-color: {INPUT_BG_FOCUS};
        }}
        QLineEdit::placeholder {{
            color: {TEXT_PLACEHOLDER};
        }}
    """

    TEXT_EDIT = f"""
        QTextEdit {{
            background-color: {INPUT_BG};
            border: 1px solid rgba({PRIMARY_RGB}, 0.20);
            border-radius: {RADIUS_MD};
            padding: 10px 14px;
            color: {TEXT_PRIMARY};
            font-size: 14px;
        }}
        QTextEdit:hover {{
            border: 1px solid rgba({PRIMARY_RGB}, 0.35);
        }}
        QTextEdit:focus {{
            border: 1px solid rgba({PRIMARY_RGB}, 0.55);
            background-color: {INPUT_BG_FOCUS};
        }}
    """

    # ==========================================================================
    # CARD STYLES
    # ==========================================================================

    CARD_BASE = f"""
        SimpleCardWidget, CardWidget {{
            background-color: {CARD_BG};
            border: 1px solid rgba({PRIMARY_MUTED_RGB}, 0.15);
            border-radius: {RADIUS_LG};
        }}
        SimpleCardWidget:hover, CardWidget:hover {{
            background-color: {CARD_BG_HOVER};
            border: 1px solid rgba({PRIMARY_RGB}, 0.25);
        }}
    """

    STATUS_CONNECTED = f"""
        CardWidget {{
            background: rgba({SUCCESS_RGB}, 0.10);
            border: 1px solid rgba({SUCCESS_RGB}, 0.30);
            border-radius: {RADIUS_MD};
        }}
        CardWidget:hover {{
            background: rgba({SUCCESS_RGB}, 0.14);
            border: 1px solid rgba({SUCCESS_RGB}, 0.40);
        }}
    """

    STATUS_DISCONNECTED = f"""
        CardWidget {{
            background: rgba({ERROR_RGB}, 0.10);
            border: 1px solid rgba({ERROR_RGB}, 0.30);
            border-radius: {RADIUS_MD};
        }}
        CardWidget:hover {{
            background: rgba({ERROR_RGB}, 0.14);
            border: 1px solid rgba({ERROR_RGB}, 0.40);
        }}
    """

    STATUS_WARNING = f"""
        CardWidget {{
            background: rgba({WARNING_RGB}, 0.10);
            border: 1px solid rgba({WARNING_RGB}, 0.30);
            border-radius: {RADIUS_MD};
        }}
        CardWidget:hover {{
            background: rgba({WARNING_RGB}, 0.14);
            border: 1px solid rgba({WARNING_RGB}, 0.40);
        }}
    """

    # ==========================================================================
    # BUTTON STYLES
    # ==========================================================================

    BUTTON_PRIMARY = f"""
        PrimaryPushButton {{
            background-color: {PRIMARY};
            border: none;
            border-radius: {RADIUS_MD};
            padding: 8px 16px;
            color: white;
            font-weight: 500;
        }}
        PrimaryPushButton:hover {{
            background-color: {PRIMARY_LIGHT};
        }}
        PrimaryPushButton:pressed {{
            background-color: {PRIMARY_DARK};
        }}
        PrimaryPushButton:disabled {{
            background-color: rgba({PRIMARY_RGB}, 0.40);
            color: rgba(255, 255, 255, 0.60);
        }}
    """

    BUTTON_SECONDARY = f"""
        PushButton {{
            background-color: transparent;
            border: 1px solid rgba({PRIMARY_RGB}, 0.30);
            border-radius: {RADIUS_MD};
            padding: 8px 16px;
            color: {TEXT_PRIMARY};
        }}
        PushButton:hover {{
            background-color: rgba({PRIMARY_RGB}, 0.10);
            border: 1px solid rgba({PRIMARY_RGB}, 0.45);
        }}
        PushButton:pressed {{
            background-color: rgba({PRIMARY_RGB}, 0.15);
        }}
    """

    BUTTON_GHOST = f"""
        TransparentPushButton {{
            background-color: transparent;
            border: none;
            border-radius: {RADIUS_MD};
            padding: 8px 16px;
            color: {TEXT_SECONDARY};
        }}
        TransparentPushButton:hover {{
            background-color: rgba({PRIMARY_RGB}, 0.08);
            color: {TEXT_PRIMARY};
        }}
        TransparentPushButton:pressed {{
            background-color: rgba({PRIMARY_RGB}, 0.12);
        }}
    """

    # ==========================================================================
    # PANEL / DIALOG STYLES (Glassmorphism)
    # ==========================================================================

    PANEL_GLASS = f"""
        QWidget#glassPanel {{
            background-color: {PANEL_BG};
            border: 1px solid rgba({PRIMARY_RGB}, 0.15);
            border-radius: {RADIUS_XL};
        }}
    """

    DIALOG_GLASS = f"""
        QDialog {{
            background-color: {DIALOG_BG};
            border: 1px solid rgba({PRIMARY_RGB}, 0.20);
            border-radius: {RADIUS_XL};
        }}
    """

    SIDEBAR = f"""
        QWidget#sidebar {{
            background-color: {PANEL_BG};
            border-right: 1px solid rgba({PRIMARY_RGB}, 0.12);
        }}
    """

    # ==========================================================================
    # SCROLLBAR STYLES
    # ==========================================================================

    SCROLLBAR = f"""
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba({PRIMARY_RGB}, 0.30);
            border-radius: 4px;
            min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: rgba({PRIMARY_RGB}, 0.50);
        }}
        QScrollBar::handle:vertical:pressed {{
            background: rgba({PRIMARY_RGB}, 0.60);
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
            background: rgba({PRIMARY_RGB}, 0.30);
            border-radius: 4px;
            min-width: 40px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: rgba({PRIMARY_RGB}, 0.50);
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
            background: none;
        }}
    """

    # ==========================================================================
    # TOOLTIP STYLES
    # ==========================================================================

    TOOLTIP = f"""
        QToolTip {{
            background-color: {TRANSPARENCY["tooltip_bg"]};
            border: 1px solid rgba({PRIMARY_RGB}, 0.25);
            border-radius: {RADIUS_SM};
            padding: 6px 10px;
            color: {TEXT_PRIMARY};
            font-size: 12px;
        }}
    """

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================

    @classmethod
    def get_glow_shadow(cls, color_rgb: str = None, intensity: float = 0.4) -> str:
        """Generate CSS for glow effect border.

        Args:
            color_rgb: RGB values as string (e.g., "233, 69, 96").
                       Defaults to PRIMARY_RGB.
            intensity: Opacity of the glow (0.0 to 1.0).

        Returns:
            CSS border property string.
        """
        rgb = color_rgb or cls.PRIMARY_RGB
        return f"border: 2px solid rgba({rgb}, {intensity});"

    @classmethod
    def get_text_color(cls, is_dark: bool = True) -> str:
        """Get appropriate text color for theme."""
        return cls.TEXT_PRIMARY if is_dark else "#1a1a2e"

    @classmethod
    def get_accent_gradient(cls, opacity_start: float = 0.10, opacity_end: float = 0.04) -> str:
        """Generate a gradient using the primary accent color.

        Args:
            opacity_start: Starting opacity.
            opacity_end: Ending opacity.

        Returns:
            CSS gradient string.
        """
        return f"""qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba({cls.PRIMARY_RGB}, {opacity_start}),
            stop:1 rgba({cls.PRIMARY_RGB}, {opacity_end}))"""

    @classmethod
    def get_card_style(cls, accent_rgb: str = None, hover: bool = True) -> str:
        """Generate card style with optional custom accent.

        Args:
            accent_rgb: Custom RGB color string. Defaults to PRIMARY_RGB.
            hover: Whether to include hover state.

        Returns:
            CSS style string for cards.
        """
        rgb = accent_rgb or cls.PRIMARY_RGB
        style = f"""
            SimpleCardWidget {{
                background-color: {cls.CARD_BG};
                border: 1px solid rgba({rgb}, 0.15);
                border-radius: {cls.RADIUS_LG};
            }}
        """
        if hover:
            style += f"""
            SimpleCardWidget:hover {{
                background-color: {cls.CARD_BG_HOVER};
                border: 1px solid rgba({rgb}, 0.30);
            }}
            """
        return style

    @classmethod
    def get_button_style(cls, variant: str = "primary") -> str:
        """Get button style by variant name.

        Args:
            variant: Button variant ('primary', 'secondary', 'ghost').

        Returns:
            CSS style string for button.
        """
        styles = {
            "primary": cls.BUTTON_PRIMARY,
            "secondary": cls.BUTTON_SECONDARY,
            "ghost": cls.BUTTON_GHOST,
        }
        return styles.get(variant, cls.BUTTON_PRIMARY)
