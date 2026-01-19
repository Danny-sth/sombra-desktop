"""Logs page - Real-time log viewer with SSE streaming."""

import json
from datetime import datetime

from PySide6.QtCore import Qt, Slot, QThread, Signal
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

import httpx


class SSEWorker(QThread):
    """Worker thread for SSE streaming."""

    log_received = Signal(dict)
    error = Signal(str)
    connected = Signal()
    disconnected = Signal()

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self._url = url
        self._running = False

    def run(self):
        """Stream SSE logs."""
        self._running = True
        self.connected.emit()

        try:
            with httpx.Client(timeout=None) as client:
                with client.stream("GET", self._url) as response:
                    for line in response.iter_lines():
                        if not self._running:
                            break

                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                self.log_received.emit(data)
                            except json.JSONDecodeError:
                                pass

        except Exception as e:
            if self._running:
                self.error.emit(str(e))
        finally:
            self._running = False
            self.disconnected.emit()

    def stop(self):
        """Stop streaming."""
        self._running = False


class LogsPage(ScrollArea):
    """Real-time logs viewer using SSE stream."""

    def __init__(self, sombra_service=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("logsPage")

        self._sombra = sombra_service
        self._is_streaming = False
        self._autoscroll = True
        self._worker: SSEWorker | None = None

        # Get server URL from service or use default
        self._server_url = "http://90.156.230.49:8080"

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

        subtitle = SubtitleLabel("Real-time log stream from all Sombra clients")
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
        """Start log streaming via SSE."""
        self._is_streaming = True
        self._connect_btn.setText("Disconnect")
        self._connect_btn.setIcon(FluentIcon.PAUSE)

        # Start SSE worker
        sse_url = f"{self._server_url}/api/logs/watch/sse"
        self._worker = SSEWorker(sse_url, self)
        self._worker.log_received.connect(self._on_log_received)
        self._worker.error.connect(self._on_stream_error)
        self._worker.connected.connect(self._on_connected)
        self._worker.disconnected.connect(self._on_disconnected)
        self._worker.start()

    def _stop_stream(self) -> None:
        """Stop log streaming."""
        if self._worker:
            self._worker.stop()
            self._worker.wait(2000)  # Wait up to 2 seconds
            self._worker = None

        self._is_streaming = False
        self._connect_btn.setText("Connect")
        self._connect_btn.setIcon(FluentIcon.PLAY)

    @Slot()
    def _on_connected(self) -> None:
        """Handle stream connected."""
        self._append_log("INFO", "Connected to log stream", "system")
        InfoBar.success(
            title="Connected",
            content="Streaming logs from server",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=2000
        )

    @Slot()
    def _on_disconnected(self) -> None:
        """Handle stream disconnected."""
        self._append_log("INFO", "Disconnected from log stream", "system")

    @Slot(dict)
    def _on_log_received(self, log: dict) -> None:
        """Handle received log entry."""
        level = log.get("level", "INFO")
        message = log.get("message", "")
        logger = log.get("logger", "unknown")
        client_id = log.get("client_id", "unknown")
        timestamp = log.get("timestamp", "")

        # Format: [HH:MM:SS] [CLIENT] [LEVEL] logger: message
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M:%S")
            except Exception:
                time_str = datetime.now().strftime("%H:%M:%S")
        else:
            time_str = datetime.now().strftime("%H:%M:%S")

        # Shorten client_id for display
        short_client = client_id.split("-")[0] if "-" in client_id else client_id[:8]

        formatted = f"[{time_str}] [{short_client}] [{level}] {logger}: {message}"
        self._log_display.append(formatted)

        # Auto-scroll
        if self._autoscroll:
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    @Slot(str)
    def _on_stream_error(self, error: str) -> None:
        """Handle stream error."""
        self._append_log("ERROR", f"Stream error: {error}", "system")
        InfoBar.error(
            title="Connection Error",
            content=error[:50],
            parent=self,
            position=InfoBarPosition.TOP,
            duration=3000
        )

    def _append_log(self, level: str, message: str, source: str = "local") -> None:
        """Append a log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{source}] [{level}] {message}"
        self._log_display.append(formatted)

        if self._autoscroll:
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def _clear_logs(self) -> None:
        """Clear log display."""
        self._log_display.clear()

    @Slot()
    def _toggle_autoscroll(self) -> None:
        """Toggle auto-scroll."""
        self._autoscroll = not self._autoscroll
        if self._autoscroll:
            self._autoscroll_btn.setText("Auto-scroll: On")
        else:
            self._autoscroll_btn.setText("Auto-scroll: Off")

    # Public methods for external log injection
    def add_log(self, level: str, message: str) -> None:
        """Add a log entry from external source."""
        self._append_log(level.upper(), message, "local")

    def closeEvent(self, event):
        """Clean up on close."""
        self._stop_stream()
        super().closeEvent(event)
