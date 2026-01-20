"""Sci-Fi theme constants and styles for Sombra Desktop.

Cyberpunk-inspired palette with glassmorphism effects.
Colors: Cyan (#00d4ff) + Magenta (#e94560)
"""


class SciFiTheme:
    """Centralized theme constants for Sci-Fi UI."""

    # Primary colors
    CYAN = "#00d4ff"
    CYAN_RGB = "0, 212, 255"
    MAGENTA = "#e94560"
    MAGENTA_RGB = "233, 69, 96"

    # Secondary colors
    DARK_CYAN = "#0096b3"
    DARK_MAGENTA = "#c83050"
    PURPLE = "#9d4edd"

    # Background colors
    BG_DARK = "#0a0a12"
    BG_PANEL = "#12121a"
    BG_CARD = "#1a1a24"

    # Text colors
    TEXT_PRIMARY = "#eaeaea"
    TEXT_SECONDARY = "#888899"
    TEXT_MUTED = "#555566"

    # Opacity levels for glassmorphism
    GLASS_OPACITY = 0.08
    GLASS_OPACITY_HOVER = 0.12
    BORDER_OPACITY = 0.3
    BORDER_OPACITY_HOVER = 0.5

    # Sombra bubble style (cyan accent)
    SOMBRA_BUBBLE = f"""
        ChatBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({CYAN_RGB}, 0.08),
                stop:1 rgba({CYAN_RGB}, 0.03));
            border: 1px solid rgba({CYAN_RGB}, 0.25);
            border-radius: 12px;
        }}
        ChatBubble:hover {{
            border: 1px solid rgba({CYAN_RGB}, 0.4);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({CYAN_RGB}, 0.12),
                stop:1 rgba({CYAN_RGB}, 0.05));
        }}
    """

    # User bubble style (magenta accent)
    USER_BUBBLE = f"""
        ChatBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({MAGENTA_RGB}, 0.10),
                stop:1 rgba({MAGENTA_RGB}, 0.04));
            border: 1px solid rgba({MAGENTA_RGB}, 0.30);
            border-radius: 12px;
        }}
        ChatBubble:hover {{
            border: 1px solid rgba({MAGENTA_RGB}, 0.45);
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({MAGENTA_RGB}, 0.14),
                stop:1 rgba({MAGENTA_RGB}, 0.06));
        }}
    """

    # Thinking bubble style (neutral)
    THINKING_BUBBLE = """
        ThinkingBubble {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(100, 100, 120, 0.08),
                stop:1 rgba(80, 80, 100, 0.04));
            border: 1px solid rgba(100, 100, 120, 0.2);
            border-radius: 12px;
        }
    """

    # Streaming bubble style (cyan, animated feel)
    STREAMING_BUBBLE = f"""
        StreamingBubble {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba({CYAN_RGB}, 0.06),
                stop:1 rgba({CYAN_RGB}, 0.02));
            border: 1px solid rgba({CYAN_RGB}, 0.20);
            border-radius: 12px;
        }}
    """

    # Text browser inside bubbles
    TEXT_BROWSER = """
        QTextBrowser {
            background-color: transparent;
            border: none;
            padding: 0;
            selection-background-color: rgba(0, 212, 255, 0.3);
        }
    """

    # Chat container background
    CHAT_CONTAINER = f"""
        QWidget#chatContainer {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {BG_DARK},
                stop:0.5 {BG_PANEL},
                stop:1 {BG_DARK});
        }}
    """

    # Input field style
    INPUT_FIELD = f"""
        QLineEdit {{
            background-color: rgba(20, 20, 30, 0.8);
            border: 1px solid rgba({CYAN_RGB}, 0.2);
            border-radius: 8px;
            padding: 10px 14px;
            color: {TEXT_PRIMARY};
            font-size: 14px;
        }}
        QLineEdit:focus {{
            border: 1px solid rgba({CYAN_RGB}, 0.5);
            background-color: rgba(25, 25, 35, 0.9);
        }}
        QLineEdit:hover {{
            border: 1px solid rgba({CYAN_RGB}, 0.35);
        }}
    """

    # Status card styles
    STATUS_CONNECTED = f"""
        CardWidget {{
            background: rgba(78, 204, 163, 0.08);
            border: 1px solid rgba(78, 204, 163, 0.25);
            border-radius: 8px;
        }}
    """

    STATUS_DISCONNECTED = f"""
        CardWidget {{
            background: rgba({MAGENTA_RGB}, 0.08);
            border: 1px solid rgba({MAGENTA_RGB}, 0.25);
            border-radius: 8px;
        }}
    """

    @classmethod
    def get_glow_shadow(cls, color_rgb: str, blur: int = 20, spread: int = 0) -> str:
        """Generate CSS for glow effect (Qt doesn't support box-shadow, use border trick)."""
        return f"border: 2px solid rgba({color_rgb}, 0.4);"

    @classmethod
    def get_text_color(cls, is_dark: bool = True) -> str:
        """Get appropriate text color for theme."""
        return cls.TEXT_PRIMARY if is_dark else "#212121"
