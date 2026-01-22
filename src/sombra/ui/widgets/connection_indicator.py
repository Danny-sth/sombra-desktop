"""Connection status indicator widget."""

from enum import Enum

from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve, Qt, Signal, Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ...themes.colors import DARK_PALETTE, LIGHT_PALETTE


class ConnectionState(Enum):
    """Connection states with associated colors and labels."""

    CONNECTED = ("connected", "Connected")
    CONNECTING = ("connecting", "Connecting...")
    DISCONNECTED = ("disconnected", "Disconnected")
    ERROR = ("error", "Error")

    def __init__(self, state_id: str, label: str):
        self.state_id = state_id
        self.label = label


class ConnectionIndicator(QWidget):
    """Compact connection status indicator with colored dot and text.

    Shows connection state via:
    - Green dot: Connected
    - Yellow dot (pulsing): Connecting
    - Red dot: Disconnected/Error

    Designed to be placed in navigation sidebar or status bar.
    """

    # Signals
    state_changed = Signal(ConnectionState)
    clicked = Signal()

    # Color mappings per theme
    _COLORS = {
        "dark": {
            ConnectionState.CONNECTED: DARK_PALETTE["success"],      # Green
            ConnectionState.CONNECTING: DARK_PALETTE["warning"],     # Yellow
            ConnectionState.DISCONNECTED: DARK_PALETTE["error"],     # Red
            ConnectionState.ERROR: DARK_PALETTE["error"],            # Red
        },
        "light": {
            ConnectionState.CONNECTED: LIGHT_PALETTE["success"],
            ConnectionState.CONNECTING: LIGHT_PALETTE["warning"],
            ConnectionState.DISCONNECTED: LIGHT_PALETTE["error"],
            ConnectionState.ERROR: LIGHT_PALETTE["error"],
        },
    }

    def __init__(self, parent: QWidget | None = None, compact: bool = False):
        """Initialize connection indicator.

        Args:
            parent: Parent widget.
            compact: If True, show only dot without text label.
        """
        super().__init__(parent)

        self._state = ConnectionState.DISCONNECTED
        self._theme = "dark"
        self._compact = compact
        self._opacity = 1.0

        self._setup_ui()
        self._setup_animation()
        self._update_display()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Status dot indicator
        self._dot = QLabel("●")
        self._dot.setObjectName("connectionDot")
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dot.setFixedSize(16, 16)
        layout.addWidget(self._dot)

        # Status text label (hidden in compact mode)
        self._label = QLabel()
        self._label.setObjectName("connectionLabel")
        if self._compact:
            self._label.hide()
        layout.addWidget(self._label)

        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to check connection")

    def _setup_animation(self) -> None:
        """Setup pulse animation for connecting state."""
        self._pulse_animation = QPropertyAnimation(self, b"dotOpacity")
        self._pulse_animation.setDuration(800)
        self._pulse_animation.setLoopCount(-1)  # Infinite
        self._pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

    def _get_dot_opacity(self) -> float:
        """Get current dot opacity."""
        return self._opacity

    def _set_dot_opacity(self, value: float) -> None:
        """Set dot opacity and update style."""
        self._opacity = max(0.3, min(1.0, value))
        self._apply_dot_style()

    # Qt property for animation
    dotOpacity = Property(float, _get_dot_opacity, _set_dot_opacity)

    def _apply_dot_style(self) -> None:
        """Apply current color and opacity to dot."""
        color = self._COLORS[self._theme][self._state]
        self._dot.setStyleSheet(
            f"color: {color}; opacity: {self._opacity}; font-size: 14px;"
        )

    def _update_display(self) -> None:
        """Update the visual display based on current state."""
        color = self._COLORS[self._theme][self._state]

        # Update dot color
        self._apply_dot_style()

        # Update label text and color
        self._label.setText(self._state.label)
        self._label.setStyleSheet(f"color: {color}; font-size: 12px;")

        # Update tooltip
        self.setToolTip(f"Status: {self._state.label}\nClick to refresh")

        # Handle animation for connecting state
        if self._state == ConnectionState.CONNECTING:
            self._start_pulse()
        else:
            self._stop_pulse()

    def _start_pulse(self) -> None:
        """Start pulse animation."""
        self._pulse_animation.setStartValue(1.0)
        self._pulse_animation.setEndValue(0.3)
        self._pulse_animation.start()

    def _stop_pulse(self) -> None:
        """Stop pulse animation."""
        self._pulse_animation.stop()
        self._opacity = 1.0
        self._apply_dot_style()

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for click signal."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    # ===== Public API =====

    @property
    def state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state

    @Slot(ConnectionState)
    def set_state(self, state: ConnectionState) -> None:
        """Set connection state.

        Args:
            state: New connection state.
        """
        if self._state != state:
            self._state = state
            self._update_display()
            self.state_changed.emit(state)

    @Slot(str)
    def set_status(self, status: str) -> None:
        """Set connection state from status string.

        Compatible with SombraService.connection_status signal.

        Args:
            status: Status string ('Connected', 'Disconnected', 'Connecting...', 'Error', etc.)
        """
        status_lower = status.lower()

        if "error" in status_lower:
            self.set_state(ConnectionState.ERROR)
        elif "disconnect" in status_lower:
            self.set_state(ConnectionState.DISCONNECTED)
        elif "connect" in status_lower and "ing" in status_lower:
            self.set_state(ConnectionState.CONNECTING)
        elif "connect" in status_lower:
            self.set_state(ConnectionState.CONNECTED)
        else:
            # Unknown status - treat as connecting
            self.set_state(ConnectionState.CONNECTING)
            self._label.setText(status)  # Show original text

    @Slot(str)
    def set_theme(self, theme: str) -> None:
        """Update colors for theme.

        Args:
            theme: Theme name ('dark' or 'light').
        """
        self._theme = theme if theme in ("dark", "light") else "dark"
        self._update_display()

    def set_compact(self, compact: bool) -> None:
        """Toggle compact mode.

        Args:
            compact: If True, hide text label.
        """
        self._compact = compact
        self._label.setVisible(not compact)

    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._state == ConnectionState.CONNECTED
