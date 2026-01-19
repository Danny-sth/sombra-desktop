"""Status indicator card components."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from qfluentwidgets import (
    SimpleCardWidget,
    BodyLabel,
    CaptionLabel,
    IconWidget,
    FluentIcon,
    isDarkTheme,
)


class StatusCard(SimpleCardWidget):
    """Generic status card with icon, title, and value."""

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

    def _setup_ui(self, icon: FluentIcon) -> None:
        """Build the card UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon
        self._icon_widget = IconWidget(icon)
        self._icon_widget.setFixedSize(32, 32)
        layout.addWidget(self._icon_widget)

        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        self._title_label = BodyLabel(self._title)
        text_layout.addWidget(self._title_label)

        self._value_label = CaptionLabel(self._value)
        self._value_label.setStyleSheet("color: #888888;")
        text_layout.addWidget(self._value_label)

        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, value: str) -> None:
        """Update the status value."""
        self._value = value
        self._value_label.setText(value)

    def set_icon(self, icon: FluentIcon) -> None:
        """Update the icon."""
        self._icon_widget.setIcon(icon)


class ConnectionStatusCard(SimpleCardWidget):
    """Compact connection status indicator card."""

    # Status colors
    COLOR_CONNECTED = QColor("#4ecca3")  # Green
    COLOR_DISCONNECTED = QColor("#e94560")  # Red
    COLOR_CONNECTING = QColor("#f9a825")  # Yellow/Orange

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._status = "Connecting..."

        self._setup_ui()

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
        layout.addWidget(self._status_label)
        layout.addStretch()

        # Update initial state
        self._update_visual("connecting")

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
        elif state == "error":
            color = self.COLOR_DISCONNECTED
            dot = ""
        else:
            color = self.COLOR_CONNECTING
            dot = ""

        self._dot_label.setText(dot)
        self._dot_label.setStyleSheet(f"color: {color.name()}; font-size: 16px;")


class RecordingStatusCard(SimpleCardWidget):
    """Recording status indicator card."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_recording = False

        self._setup_ui()

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
        layout.addWidget(self._status_label)
        layout.addStretch()

        self._update_visual(False)

    @Slot(bool)
    def set_recording(self, is_recording: bool) -> None:
        """Update recording status."""
        self._is_recording = is_recording
        self._update_visual(is_recording)

    def _update_visual(self, is_recording: bool) -> None:
        """Update visual appearance."""
        if is_recording:
            self._dot_label.setText("")
            self._dot_label.setStyleSheet("color: #e94560; font-size: 16px;")
            self._status_label.setText("Recording...")
        else:
            self._dot_label.setText("")
            self._dot_label.setStyleSheet("color: #888888; font-size: 16px;")
            self._status_label.setText("Idle")


class WakeWordStatusCard(SimpleCardWidget):
    """Wake word detection status card."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_listening = False

        self._setup_ui()

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
        layout.addWidget(self._status_label)
        layout.addStretch()

    @Slot(bool)
    def set_listening(self, is_listening: bool) -> None:
        """Update listening status."""
        self._is_listening = is_listening

        if is_listening:
            self._status_label.setText("Wake Word: Listening")
            self._status_label.setStyleSheet("color: #4ecca3;")
        else:
            self._status_label.setText("Wake Word: Off")
            self._status_label.setStyleSheet("color: #888888;")
