"""Status indicator card components with Sombra branding."""

from PySide6.QtCore import Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    FluentIcon,
    IconWidget,
    SimpleCardWidget,
)

from sombra.themes.colors import (
    BORDER_RADIUS,
    DARK_PALETTE,
    SOMBRA_PRIMARY,
    TRANSPARENCY,
)

# Sombra brand RGB values
_PRIMARY_RGB = "233, 69, 96"
_SUCCESS_RGB = "78, 204, 163"
_WARNING_RGB = "249, 168, 37"
_ERROR_RGB = "255, 107, 107"


class StatusCard(SimpleCardWidget):
    """Generic status card with icon, title, and value.

    Uses Sombra branding with glassmorphism effects.
    """

    def __init__(
        self,
        title: str,
        value: str = "",
        icon: FluentIcon = FluentIcon.INFO,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._title = title
        self._value = value

        self._setup_ui(icon)
        self._apply_style()

    def _setup_ui(self, icon: FluentIcon) -> None:
        """Build the card UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon with Sombra accent
        self._icon_widget = IconWidget(icon)
        self._icon_widget.setFixedSize(32, 32)
        layout.addWidget(self._icon_widget)

        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self._title_label = BodyLabel(self._title)
        self._title_label.setStyleSheet(f"color: {DARK_PALETTE['text_primary']};")
        text_layout.addWidget(self._title_label)

        self._value_label = CaptionLabel(self._value)
        self._value_label.setStyleSheet(f"color: {DARK_PALETTE['text_secondary']};")
        text_layout.addWidget(self._value_label)

        layout.addLayout(text_layout)
        layout.addStretch()

    def _apply_style(self) -> None:
        """Apply Sombra card styling."""
        self.setStyleSheet(f"""
            SimpleCardWidget {{
                background-color: {TRANSPARENCY["card_bg"]};
                border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
                border-radius: {BORDER_RADIUS["lg"]};
            }}
            SimpleCardWidget:hover {{
                background-color: {TRANSPARENCY["card_bg_hover"]};
                border-color: rgba({_PRIMARY_RGB}, 0.22);
            }}
        """)

    def set_value(self, value: str) -> None:
        """Update the status value."""
        self._value = value
        self._value_label.setText(value)

    def set_icon(self, icon: FluentIcon) -> None:
        """Update the icon."""
        self._icon_widget.setIcon(icon)


class ConnectionStatusCard(SimpleCardWidget):
    """Compact connection status indicator card with Sombra branding."""

    # Status colors - using Sombra palette
    COLOR_CONNECTED = QColor(DARK_PALETTE["success"])      # #4ecca3
    COLOR_DISCONNECTED = QColor(SOMBRA_PRIMARY)            # #e94560
    COLOR_CONNECTING = QColor(DARK_PALETTE["warning"])     # #f9a825

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._status = "Connecting..."

        self._setup_ui()
        self._apply_base_style()

    def _setup_ui(self) -> None:
        """Build the card UI."""
        self.setFixedHeight(48)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Status dot
        self._dot_label = BodyLabel("")
        self._dot_label.setFixedWidth(20)
        layout.addWidget(self._dot_label)

        # Status text
        self._status_label = BodyLabel("Connecting...")
        self._status_label.setStyleSheet(f"color: {DARK_PALETTE['text_primary']};")
        layout.addWidget(self._status_label)
        layout.addStretch()

        # Update initial state
        self._update_visual("connecting")

    def _apply_base_style(self) -> None:
        """Apply base card styling."""
        self.setStyleSheet(f"""
            SimpleCardWidget {{
                background-color: {TRANSPARENCY["card_bg"]};
                border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
                border-radius: {BORDER_RADIUS["md"]};
            }}
        """)

    @Slot(str)
    def set_status(self, status: str) -> None:
        """Update connection status.

        Args:
            status: Status text (Connected, Disconnected, Error, Connecting...)
        """
        self._status = status
        self._status_label.setText(status)

        status_lower = status.lower()
        if "connected" in status_lower and "dis" not in status_lower:
            self._update_visual("connected")
        elif "error" in status_lower or "disconnect" in status_lower:
            self._update_visual("error")
        else:
            self._update_visual("connecting")

    def _update_visual(self, state: str) -> None:
        """Update visual appearance based on state."""
        if state == "connected":
            color = self.COLOR_CONNECTED
            dot = ""
            border_rgb = _SUCCESS_RGB
        elif state == "error":
            color = self.COLOR_DISCONNECTED
            dot = ""
            border_rgb = _PRIMARY_RGB
        else:
            color = self.COLOR_CONNECTING
            dot = ""
            border_rgb = _WARNING_RGB

        self._dot_label.setText(dot)
        self._dot_label.setStyleSheet(f"color: {color.name()}; font-size: 16px;")

        # Update card border to match status
        self.setStyleSheet(f"""
            SimpleCardWidget {{
                background-color: {TRANSPARENCY["card_bg"]};
                border: 1px solid rgba({border_rgb}, 0.25);
                border-radius: {BORDER_RADIUS["md"]};
            }}
            SimpleCardWidget:hover {{
                background-color: {TRANSPARENCY["card_bg_hover"]};
                border-color: rgba({border_rgb}, 0.40);
            }}
        """)


class RecordingStatusCard(SimpleCardWidget):
    """Recording status indicator card with Sombra branding."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_recording = False

        self._setup_ui()
        self._apply_base_style()

    def _setup_ui(self) -> None:
        """Build the card UI."""
        self.setFixedHeight(48)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Recording dot
        self._dot_label = BodyLabel("")
        self._dot_label.setFixedWidth(20)
        layout.addWidget(self._dot_label)

        # Status text
        self._status_label = BodyLabel("Idle")
        self._status_label.setStyleSheet(f"color: {DARK_PALETTE['text_primary']};")
        layout.addWidget(self._status_label)
        layout.addStretch()

        self._update_visual(False)

    def _apply_base_style(self) -> None:
        """Apply base card styling."""
        self.setStyleSheet(f"""
            SimpleCardWidget {{
                background-color: {TRANSPARENCY["card_bg"]};
                border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
                border-radius: {BORDER_RADIUS["md"]};
            }}
        """)

    @Slot(bool)
    def set_recording(self, is_recording: bool) -> None:
        """Update recording status."""
        self._is_recording = is_recording
        self._update_visual(is_recording)

    def _update_visual(self, is_recording: bool) -> None:
        """Update visual appearance."""
        if is_recording:
            self._dot_label.setText("")
            self._dot_label.setStyleSheet(f"color: {SOMBRA_PRIMARY}; font-size: 16px;")
            self._status_label.setText("Recording...")
            self._status_label.setStyleSheet(f"color: {SOMBRA_PRIMARY};")

            # Recording state - highlight with Sombra pink border
            self.setStyleSheet(f"""
                SimpleCardWidget {{
                    background-color: rgba({_PRIMARY_RGB}, 0.08);
                    border: 1px solid rgba({_PRIMARY_RGB}, 0.35);
                    border-radius: {BORDER_RADIUS["md"]};
                }}
            """)
        else:
            self._dot_label.setText("")
            text_disabled = DARK_PALETTE['text_disabled']
            self._dot_label.setStyleSheet(f"color: {text_disabled}; font-size: 16px;")
            self._status_label.setText("Idle")
            text_secondary = DARK_PALETTE['text_secondary']
            self._status_label.setStyleSheet(f"color: {text_secondary};")

            # Idle state - normal styling
            self._apply_base_style()


class WakeWordStatusCard(SimpleCardWidget):
    """Wake word detection status card with Sombra branding."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_listening = False

        self._setup_ui()
        self._apply_base_style()

    def _setup_ui(self) -> None:
        """Build the card UI."""
        self.setFixedHeight(48)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Icon
        self._icon = IconWidget(FluentIcon.MICROPHONE)
        self._icon.setFixedSize(20, 20)
        layout.addWidget(self._icon)

        # Status text
        self._status_label = BodyLabel("Wake Word: Off")
        self._status_label.setStyleSheet(f"color: {DARK_PALETTE['text_secondary']};")
        layout.addWidget(self._status_label)
        layout.addStretch()

    def _apply_base_style(self) -> None:
        """Apply base card styling."""
        self.setStyleSheet(f"""
            SimpleCardWidget {{
                background-color: {TRANSPARENCY["card_bg"]};
                border: 1px solid rgba({_PRIMARY_RGB}, 0.12);
                border-radius: {BORDER_RADIUS["md"]};
            }}
        """)

    @Slot(bool)
    def set_listening(self, is_listening: bool) -> None:
        """Update listening status."""
        self._is_listening = is_listening

        if is_listening:
            self._status_label.setText("Wake Word: Listening")
            self._status_label.setStyleSheet(f"color: {DARK_PALETTE['success']};")

            # Listening state - highlight with success border
            self.setStyleSheet(f"""
                SimpleCardWidget {{
                    background-color: rgba({_SUCCESS_RGB}, 0.08);
                    border: 1px solid rgba({_SUCCESS_RGB}, 0.30);
                    border-radius: {BORDER_RADIUS["md"]};
                }}
                SimpleCardWidget:hover {{
                    background-color: rgba({_SUCCESS_RGB}, 0.12);
                    border-color: rgba({_SUCCESS_RGB}, 0.40);
                }}
            """)
        else:
            self._status_label.setText("Wake Word: Off")
            self._status_label.setStyleSheet(f"color: {DARK_PALETTE['text_secondary']};")

            # Off state - normal styling
            self._apply_base_style()
