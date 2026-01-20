"""Home page - Dashboard with status cards and quick actions."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    CaptionLabel,
    PrimaryPushButton,
    TransparentPushButton,
    SimpleCardWidget,
    IconWidget,
    FluentIcon,
    isDarkTheme,
)

from sombra import __version__
from ..components.log_panel import LogPanel


class HomePage(ScrollArea):
    """Dashboard with status overview and quick actions."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("homePage")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the dashboard interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(24)

        # Welcome header
        self._create_header(layout)

        # Status cards grid
        self._create_status_grid(layout)

        # Quick actions
        self._create_quick_actions(layout)

        # Info section
        self._create_info_section(layout)

        # Server logs panel
        self._create_log_panel(layout)

        layout.addStretch()

    def _create_header(self, parent_layout: QVBoxLayout) -> None:
        """Create welcome header."""
        header = TitleLabel("Welcome to Sombra")
        parent_layout.addWidget(header)

        subtitle = BodyLabel("Your AI orchestrator is ready to assist")
        subtitle.setStyleSheet("color: #888888;")
        parent_layout.addWidget(subtitle)

    def _create_status_grid(self, parent_layout: QVBoxLayout) -> None:
        """Create status cards grid."""
        section_title = SubtitleLabel("System Status")
        parent_layout.addWidget(section_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        # Connection card
        self._connection_card = self._create_status_card(
            "Connection",
            "Checking...",
            FluentIcon.WIFI
        )
        grid.addWidget(self._connection_card, 0, 0)

        # Recording card
        self._recording_card = self._create_status_card(
            "Voice Input",
            "Idle",
            FluentIcon.MICROPHONE
        )
        grid.addWidget(self._recording_card, 0, 1)

        # Wake Word card
        self._wakeword_card = self._create_status_card(
            "Wake Word",
            "Listening",
            FluentIcon.VOLUME
        )
        grid.addWidget(self._wakeword_card, 1, 0)

        # Session card
        self._session_card = self._create_status_card(
            "Session",
            "Active",
            FluentIcon.PEOPLE
        )
        grid.addWidget(self._session_card, 1, 1)

        parent_layout.addLayout(grid)

    def _create_status_card(
        self,
        title: str,
        status: str,
        icon: FluentIcon
    ) -> SimpleCardWidget:
        """Create a status card widget."""
        card = SimpleCardWidget()

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon
        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(32, 32)
        layout.addWidget(icon_widget)

        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = BodyLabel(title)
        text_layout.addWidget(title_label)

        status_label = CaptionLabel(status)
        status_label.setObjectName(f"{title.lower().replace(' ', '_')}_status")
        status_label.setStyleSheet("color: #888888;")
        text_layout.addWidget(status_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        return card

    def _create_quick_actions(self, parent_layout: QVBoxLayout) -> None:
        """Create quick actions section."""
        section_title = SubtitleLabel("Quick Actions")
        parent_layout.addWidget(section_title)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        # Start Chat button
        chat_btn = PrimaryPushButton("Start Chat")
        chat_btn.setIcon(FluentIcon.CHAT)
        chat_btn.clicked.connect(self._on_start_chat)
        actions_layout.addWidget(chat_btn)

        # New Session button
        new_session_btn = TransparentPushButton("New Session")
        new_session_btn.setIcon(FluentIcon.ADD)
        new_session_btn.clicked.connect(self._on_new_session)
        actions_layout.addWidget(new_session_btn)

        # View Logs button
        logs_btn = TransparentPushButton("View Logs")
        logs_btn.setIcon(FluentIcon.DOCUMENT)
        logs_btn.clicked.connect(self._on_view_logs)
        actions_layout.addWidget(logs_btn)

        actions_layout.addStretch()
        parent_layout.addLayout(actions_layout)

    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Create information section."""
        section_title = SubtitleLabel("About Sombra Desktop")
        parent_layout.addWidget(section_title)

        info_card = SimpleCardWidget()
        layout = QVBoxLayout(info_card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        self._version_label = BodyLabel(f"Version {__version__}")
        layout.addWidget(self._version_label)

        desc_label = CaptionLabel(
            "Sombra Desktop is your gateway to the Sombra AI orchestrator. "
            "Use voice commands or text to interact with your AI assistant. "
            "Say 'Jarvis' to activate voice input, or press Ctrl+Shift+S."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888888;")
        layout.addWidget(desc_label)

        parent_layout.addWidget(info_card)

    def _create_log_panel(self, parent_layout: QVBoxLayout) -> None:
        """Create server logs panel."""
        section_title = SubtitleLabel("Server Logs")
        parent_layout.addWidget(section_title)

        self._log_panel = LogPanel(self)
        parent_layout.addWidget(self._log_panel)

        # Start streaming automatically
        self._log_panel.start_streaming()

    # ===== Slot Handlers =====

    @Slot()
    def _on_start_chat(self) -> None:
        """Navigate to chat page."""
        # Find parent window and switch to chat page
        window = self.window()
        if hasattr(window, "switchTo"):
            window.switchTo(window.chat_page)

    @Slot()
    def _on_new_session(self) -> None:
        """Create new session."""
        from ...core.session import get_session_manager

        session = get_session_manager()
        session.regenerate()

        # Update session card
        status_label = self._session_card.findChild(CaptionLabel, "session_status")
        if status_label:
            status_label.setText("New session started")

    @Slot()
    def _on_view_logs(self) -> None:
        """Navigate to logs page."""
        window = self.window()
        if hasattr(window, "switchTo"):
            window.switchTo(window.logs_page)

    # ===== Public Methods =====

    def set_connection_status(self, status: str) -> None:
        """Update connection status display."""
        status_label = self._connection_card.findChild(CaptionLabel, "connection_status")
        if status_label:
            status_label.setText(status)
            if "connected" in status.lower() and "dis" not in status.lower():
                status_label.setStyleSheet("color: #4ecca3;")
            elif "error" in status.lower() or "disconnect" in status.lower():
                status_label.setStyleSheet("color: #e94560;")
            else:
                status_label.setStyleSheet("color: #f9a825;")

    def set_recording_status(self, is_recording: bool) -> None:
        """Update recording status display."""
        status_label = self._recording_card.findChild(CaptionLabel, "voice_input_status")
        if status_label:
            if is_recording:
                status_label.setText("Recording...")
                status_label.setStyleSheet("color: #e94560;")
            else:
                status_label.setText("Idle")
                status_label.setStyleSheet("color: #888888;")

    def set_wakeword_status(self, is_listening: bool) -> None:
        """Update wake word status display."""
        status_label = self._wakeword_card.findChild(CaptionLabel, "wake_word_status")
        if status_label:
            if is_listening:
                status_label.setText("Listening")
                status_label.setStyleSheet("color: #4ecca3;")
            else:
                status_label.setText("Disabled")
                status_label.setStyleSheet("color: #888888;")

    def cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, "_log_panel"):
            self._log_panel.cleanup()
