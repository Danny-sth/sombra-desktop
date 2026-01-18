"""Status bar widget showing connection status and controls."""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class StatusBar(QWidget):
    """Status bar with connection indicator, theme toggle, and settings.

    Shows:
    - Connection status (Connected/Disconnected)
    - Recording status
    - Theme toggle button
    - Settings button
    """

    # Signals
    theme_toggle_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_connected = False
        self._is_recording = False
        self._current_theme = "dark"

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(16)

        # Connection status indicator
        self._connection_indicator = QLabel("●")
        self._connection_indicator.setObjectName("statusLabel")
        self._connection_indicator.setStyleSheet("color: #666666;")  # Gray = unknown

        self._connection_label = QLabel("Connecting...")
        self._connection_label.setObjectName("statusLabel")

        # Recording status (hidden by default)
        self._recording_label = QLabel("🔴 Recording")
        self._recording_label.setObjectName("statusLabel")
        self._recording_label.setStyleSheet("color: #ff6b6b;")
        self._recording_label.hide()

        # Hotkey hint
        self._hotkey_label = QLabel("Ctrl+Shift+S")
        self._hotkey_label.setObjectName("subtitleLabel")
        self._hotkey_label.setToolTip("Global hotkey for push-to-talk")

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().horizontalPolicy().Expanding,
            spacer.sizePolicy().verticalPolicy().Preferred,
        )

        # Theme toggle button
        self._theme_button = QPushButton("🌙")
        self._theme_button.setToolTip("Toggle dark/light theme")
        self._theme_button.setFixedSize(32, 32)
        self._theme_button.setFlat(True)

        # Settings button
        self._settings_button = QPushButton("⚙️")
        self._settings_button.setToolTip("Settings")
        self._settings_button.setFixedSize(32, 32)
        self._settings_button.setFlat(True)

        # Add widgets to layout
        layout.addWidget(self._connection_indicator)
        layout.addWidget(self._connection_label)
        layout.addWidget(self._recording_label)
        layout.addWidget(self._hotkey_label)
        layout.addWidget(spacer)
        layout.addWidget(self._theme_button)
        layout.addWidget(self._settings_button)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._theme_button.clicked.connect(self.theme_toggle_clicked.emit)
        self._settings_button.clicked.connect(self.settings_clicked.emit)

    @Slot(str)
    def set_connection_status(self, status: str) -> None:
        """Update connection status display.

        Args:
            status: Status string ('Connected', 'Disconnected', 'Connecting...', 'Error')
        """
        self._connection_label.setText(status)

        status_lower = status.lower()
        if "connect" in status_lower and "dis" not in status_lower:
            # Connected
            self._connection_indicator.setStyleSheet("color: #4ecca3;")  # Green
            self._is_connected = True
        elif "disconnect" in status_lower or "error" in status_lower:
            # Disconnected or Error
            self._connection_indicator.setStyleSheet("color: #ff6b6b;")  # Red
            self._is_connected = False
        else:
            # Connecting or unknown
            self._connection_indicator.setStyleSheet("color: #ffc107;")  # Yellow
            self._is_connected = False

    @Slot(bool)
    def set_recording_status(self, is_recording: bool) -> None:
        """Update recording status display.

        Args:
            is_recording: Whether currently recording.
        """
        self._is_recording = is_recording
        self._recording_label.setVisible(is_recording)

    @Slot(str)
    def set_theme(self, theme: str) -> None:
        """Update theme button icon.

        Args:
            theme: Current theme ('dark' or 'light').
        """
        self._current_theme = theme
        if theme == "dark":
            self._theme_button.setText("🌙")
            self._theme_button.setToolTip("Switch to light theme")
        else:
            self._theme_button.setText("☀️")
            self._theme_button.setToolTip("Switch to dark theme")

    @Slot(str)
    def set_hotkey_hint(self, hotkey: str) -> None:
        """Update hotkey hint display.

        Args:
            hotkey: Hotkey combination string.
        """
        self._hotkey_label.setText(hotkey)

    @Slot(str)
    def show_message(self, message: str, duration_ms: int = 3000) -> None:
        """Temporarily show a status message.

        Args:
            message: Message to show.
            duration_ms: Duration in milliseconds.
        """
        original_text = self._connection_label.text()
        self._connection_label.setText(message)

        # Reset after duration
        from PySide6.QtCore import QTimer

        QTimer.singleShot(duration_ms, lambda: self._connection_label.setText(original_text))

    @property
    def is_connected(self) -> bool:
        """Get connection status."""
        return self._is_connected

    @property
    def is_recording(self) -> bool:
        """Get recording status."""
        return self._is_recording
