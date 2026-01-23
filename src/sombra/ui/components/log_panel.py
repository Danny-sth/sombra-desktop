"""Server log panel for dashboard - real-time SSE streaming with expand/collapse."""

import json
from datetime import datetime

import httpx
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from qfluentwidgets import (
    FluentIcon,
    TextEdit,
    ToolTipFilter,
    ToolTipPosition,
    TransparentToolButton,
)

from ...config.settings import get_settings


class SSELogWorker(QThread):
    """Worker thread for SSE log streaming with auto-reconnect."""

    log_received = Signal(dict)
    status_changed = Signal(str)  # "connected", "disconnected", "error"

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self._url = url
        self._running = False

    def run(self):
        """Stream SSE logs with auto-reconnect."""
        self._running = True

        while self._running:
            try:
                self.status_changed.emit("connected")

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

            except Exception:
                if self._running:
                    self.status_changed.emit("error")
                    # Wait before reconnect
                    for _ in range(50):  # 5 seconds in 100ms chunks
                        if not self._running:
                            break
                        self.msleep(100)

        self.status_changed.emit("disconnected")

    def stop(self):
        """Stop streaming."""
        self._running = False


class LogPanel(QFrame):
    """Server log panel for dashboard with SSE streaming and expand/collapse."""

    MAX_LOGS = 500  # Max logs to keep in display

    # Height settings
    COLLAPSED_MIN = 150
    COLLAPSED_MAX = 200
    EXPANDED_MIN = 400
    EXPANDED_MAX = 600

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logPanel")

        self._worker: SSELogWorker | None = None
        self._autoscroll = True
        self._log_count = 0
        self._expanded = False

        # Server URL from settings
        settings = get_settings()
        self._server_url = settings.sombra_api_url

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the log panel interface."""
        self.setStyleSheet("""
            QFrame#logPanel {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # Header with controls
        header = self._create_header()
        layout.addLayout(header)

        # Log display
        self._log_display = TextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setPlaceholderText("Server logs will appear here...")
        self._log_display.setMinimumHeight(self.COLLAPSED_MIN)
        self._log_display.setMaximumHeight(self.COLLAPSED_MAX)

        # Monospace font
        self._log_display.setStyleSheet("""
            TextEdit {
                font-family: 'Cascadia Code', 'JetBrains Mono', 'Consolas', monospace;
                font-size: 11px;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                padding: 8px;
            }
        """)

        layout.addWidget(self._log_display)

    def _create_header(self) -> QHBoxLayout:
        """Create header with status and controls."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Status indicator
        self._status_dot = QLabel()
        self._status_dot.setFixedSize(10, 10)
        self._update_status_dot("disconnected")
        layout.addWidget(self._status_dot)

        # Title
        title = QLabel("Server Logs")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        layout.addStretch()

        # Auto-scroll toggle
        self._autoscroll_btn = TransparentToolButton(FluentIcon.SCROLL)
        self._autoscroll_btn.setToolTip("Auto-scroll: On")
        self._autoscroll_btn.installEventFilter(
            ToolTipFilter(self._autoscroll_btn, 500, ToolTipPosition.BOTTOM)
        )
        self._autoscroll_btn.clicked.connect(self._toggle_autoscroll)
        layout.addWidget(self._autoscroll_btn)

        # Clear button
        clear_btn = TransparentToolButton(FluentIcon.DELETE)
        clear_btn.setToolTip("Clear logs")
        clear_btn.installEventFilter(
            ToolTipFilter(clear_btn, 500, ToolTipPosition.BOTTOM)
        )
        clear_btn.clicked.connect(self._clear_logs)
        layout.addWidget(clear_btn)

        # Expand/Collapse button
        self._expand_btn = TransparentToolButton(FluentIcon.FULL_SCREEN)
        self._expand_btn.setToolTip("Expand")
        self._expand_btn.installEventFilter(
            ToolTipFilter(self._expand_btn, 500, ToolTipPosition.BOTTOM)
        )
        self._expand_btn.clicked.connect(self._toggle_expand)
        layout.addWidget(self._expand_btn)

        # Connect/Disconnect button
        self._connect_btn = TransparentToolButton(FluentIcon.PLAY)
        self._connect_btn.setToolTip("Connect")
        self._connect_btn.installEventFilter(
            ToolTipFilter(self._connect_btn, 500, ToolTipPosition.BOTTOM)
        )
        self._connect_btn.clicked.connect(self._toggle_stream)
        layout.addWidget(self._connect_btn)

        return layout

    def _update_status_dot(self, status: str) -> None:
        """Update status indicator color."""
        colors = {
            "connected": "#4CAF50",  # Green
            "disconnected": "#9E9E9E",  # Gray
            "error": "#FF5722",  # Orange
        }
        color = colors.get(status, "#9E9E9E")
        self._status_dot.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    @Slot()
    def _toggle_expand(self) -> None:
        """Toggle expanded/collapsed state."""
        self._expanded = not self._expanded

        if self._expanded:
            self._log_display.setMinimumHeight(self.EXPANDED_MIN)
            self._log_display.setMaximumHeight(self.EXPANDED_MAX)
            self._expand_btn.setIcon(FluentIcon.BACK_TO_WINDOW)
            self._expand_btn.setToolTip("Collapse")
        else:
            self._log_display.setMinimumHeight(self.COLLAPSED_MIN)
            self._log_display.setMaximumHeight(self.COLLAPSED_MAX)
            self._expand_btn.setIcon(FluentIcon.FULL_SCREEN)
            self._expand_btn.setToolTip("Expand")

        # Scroll to bottom if autoscroll enabled
        if self._autoscroll:
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def _toggle_stream(self) -> None:
        """Toggle log streaming."""
        if self._worker and self._worker.isRunning():
            self.stop_streaming()
        else:
            self.start_streaming()

    def start_streaming(self) -> None:
        """Start log streaming via SSE."""
        if self._worker and self._worker.isRunning():
            return

        self._connect_btn.setIcon(FluentIcon.PAUSE)
        self._connect_btn.setToolTip("Disconnect")

        # Start SSE worker
        sse_url = f"{self._server_url}/api/logs/watch/sse"
        self._worker = SSELogWorker(sse_url, self)
        self._worker.log_received.connect(self._on_log_received)
        self._worker.status_changed.connect(self._on_status_changed)
        self._worker.start()

    def stop_streaming(self) -> None:
        """Stop log streaming."""
        if self._worker:
            self._worker.stop()
            self._worker.wait(2000)
            self._worker = None

        self._connect_btn.setIcon(FluentIcon.PLAY)
        self._connect_btn.setToolTip("Connect")
        self._update_status_dot("disconnected")

    @Slot(str)
    def _on_status_changed(self, status: str) -> None:
        """Handle connection status change."""
        self._update_status_dot(status)

        if status == "connected":
            self._append_system_log("Connected to server")
        elif status == "error":
            self._append_system_log("Connection error, reconnecting...")

    @Slot(dict)
    def _on_log_received(self, log: dict) -> None:
        """Handle received log entry."""
        level = log.get("level", "INFO")
        message = log.get("message", "")
        logger = log.get("logger", "")
        client_id = log.get("client_id", "")
        timestamp = log.get("timestamp", "")

        # Parse timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M:%S")
            except Exception:
                time_str = datetime.now().strftime("%H:%M:%S")
        else:
            time_str = datetime.now().strftime("%H:%M:%S")

        # Shorten client_id and determine if server log
        is_server = client_id == "server"
        if is_server:
            short_client = "SRV"
            client_color = "#E91E63"  # Pink for server
        else:
            short_client = client_id.split("-")[0] if "-" in client_id else client_id[:6]
            client_color = "#888888"  # Gray for desktop clients

        # Shorten logger name
        short_logger = logger.split(".")[-1] if "." in logger else logger

        # Color by level
        level_colors = {
            "DEBUG": "#888888",
            "INFO": "#FFFFFF",
            "WARNING": "#FFA726",
            "ERROR": "#EF5350",
            "CRITICAL": "#D32F2F",
        }
        color = level_colors.get(level.upper(), "#FFFFFF")

        # Format with HTML color
        formatted = (
            f'<span style="color: #666666;">[{time_str}]</span> '
            f'<span style="color: {client_color};">[{short_client}]</span> '
            f'<span style="color: {color};">[{level}]</span> '
            f'<span style="color: #AAAAAA;">{short_logger}:</span> '
            f'{message}'
        )

        self._log_display.append(formatted)
        self._log_count += 1

        # Trim old logs if too many
        if self._log_count > self.MAX_LOGS:
            self._trim_logs()

        # Auto-scroll
        if self._autoscroll:
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _append_system_log(self, message: str) -> None:
        """Append a system message."""
        time_str = datetime.now().strftime("%H:%M:%S")
        formatted = (
            f'<span style="color: #666666;">[{time_str}]</span> '
            f'<span style="color: #4CAF50;">[SYSTEM]</span> '
            f'{message}'
        )
        self._log_display.append(formatted)
        self._log_count += 1

        if self._autoscroll:
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _trim_logs(self) -> None:
        """Remove oldest logs to stay under MAX_LOGS."""
        # Get current HTML, remove first N lines
        html = self._log_display.toHtml()
        lines = html.split("<p")

        # Keep header and last MAX_LOGS-100 lines
        if len(lines) > self.MAX_LOGS - 100:
            # Find the header part (before first <p)
            header_end = html.find("<p")
            if header_end > 0:
                header = html[:header_end]
                kept_lines = lines[-(self.MAX_LOGS - 100):]
                new_html = header + "<p" + "<p".join(kept_lines)
                self._log_display.setHtml(new_html)
                self._log_count = len(kept_lines)

    @Slot()
    def _clear_logs(self) -> None:
        """Clear log display."""
        self._log_display.clear()
        self._log_count = 0

    @Slot()
    def _toggle_autoscroll(self) -> None:
        """Toggle auto-scroll."""
        self._autoscroll = not self._autoscroll
        if self._autoscroll:
            self._autoscroll_btn.setToolTip("Auto-scroll: On")
            # Scroll to bottom immediately
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            self._autoscroll_btn.setToolTip("Auto-scroll: Off")

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_streaming()
