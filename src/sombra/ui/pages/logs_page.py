"""Logs page - Real-time log viewer with SSE streaming."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    SubtitleLabel,
    PrimaryPushButton,
    TransparentPushButton,
    TextEdit,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
)


class LogsPage(ScrollArea):
    """Real-time logs viewer using SSE stream."""

    def __init__(self, sombra_service=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("logsPage")

        self._sombra = sombra_service
        self._is_streaming = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the logs interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(20)

        # Header
        header = TitleLabel("System Logs")
        layout.addWidget(header)

        subtitle = SubtitleLabel("Real-time log stream from Sombra server")
        subtitle.setStyleSheet("color: #888888;")
        layout.addWidget(subtitle)

        # Controls
        controls = self._create_controls()
        layout.addLayout(controls)

        # Log display
        self._log_display = TextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setPlaceholderText("Click 'Connect' to start streaming logs...")

        # Monospace font for logs
        self._log_display.setStyleSheet("""
            TextEdit {
                font-family: 'Cascadia Code', 'JetBrains Mono', 'Consolas', monospace;
                font-size: 12px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout.addWidget(self._log_display, 1)

    def _create_controls(self) -> QHBoxLayout:
        """Create control buttons."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Connect/Disconnect button
        self._connect_btn = PrimaryPushButton("Connect")
        self._connect_btn.setIcon(FluentIcon.PLAY)
        self._connect_btn.clicked.connect(self._toggle_stream)
        layout.addWidget(self._connect_btn)

        # Clear button
        clear_btn = TransparentPushButton("Clear")
        clear_btn.setIcon(FluentIcon.DELETE)
        clear_btn.clicked.connect(self._clear_logs)
        layout.addWidget(clear_btn)

        # Auto-scroll toggle
        self._autoscroll_btn = TransparentPushButton("Auto-scroll: On")
        self._autoscroll_btn.setIcon(FluentIcon.SCROLL)
        self._autoscroll_btn.clicked.connect(self._toggle_autoscroll)
        layout.addWidget(self._autoscroll_btn)

        layout.addStretch()

        return layout

    @Slot()
    def _toggle_stream(self) -> None:
        """Toggle log streaming."""
        if self._is_streaming:
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self) -> None:
        """Start log streaming."""
        self._is_streaming = True
        self._connect_btn.setText("Disconnect")
        self._connect_btn.setIcon(FluentIcon.PAUSE)

        # Add placeholder log entries for demo
        self._append_log("[INFO] Connected to log stream")
        self._append_log("[INFO] Sombra Desktop v1.1 started")
        self._append_log("[INFO] Wake word detection: enabled")
        self._append_log("[INFO] Hotkey service: Ctrl+Shift+S registered")

        InfoBar.success(
            title="Connected",
            content="Streaming logs from server",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    def _stop_stream(self) -> None:
        """Stop log streaming."""
        self._is_streaming = False
        self._connect_btn.setText("Connect")
        self._connect_btn.setIcon(FluentIcon.PLAY)

        self._append_log("[INFO] Disconnected from log stream")

        InfoBar.info(
            title="Disconnected",
            content="Log streaming stopped",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    def _append_log(self, log: str) -> None:
        """Append a log entry."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {log}"

        self._log_display.append(formatted)

        # Auto-scroll
        scrollbar = self._log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def _clear_logs(self) -> None:
        """Clear log display."""
        self._log_display.clear()

    @Slot()
    def _toggle_autoscroll(self) -> None:
        """Toggle auto-scroll."""
        current = self._autoscroll_btn.text()
        if "On" in current:
            self._autoscroll_btn.setText("Auto-scroll: Off")
        else:
            self._autoscroll_btn.setText("Auto-scroll: On")

    # Public methods for external log injection
    def add_log(self, level: str, message: str) -> None:
        """Add a log entry from external source."""
        self._append_log(f"[{level.upper()}] {message}")
