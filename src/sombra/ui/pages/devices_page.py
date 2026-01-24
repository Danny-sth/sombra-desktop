"""Devices page - Connected clients with real-time log viewer."""

import json
import logging
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, Slot, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QFrame,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    SubtitleLabel,
    BodyLabel,
    StrongBodyLabel,
    PrimaryPushButton,
    TransparentPushButton,
    TextEdit,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    CardWidget,
    IconWidget,
)

from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class LogStreamWorker(QThread):
    """Worker thread for SSE log streaming."""

    log_received = Signal(dict)  # Single log entry
    connection_status = Signal(str)  # "connected", "disconnected", "error"

    def __init__(self, api_url: str, parent=None):
        super().__init__(parent)
        self._api_url = api_url
        self._running = False

    def run(self):
        """Stream logs via SSE."""
        import httpx

        self._running = True
        url = f"{self._api_url}/api/logs/watch/sse"

        try:
            self.connection_status.emit("connected")

            with httpx.Client(timeout=None) as client:
                with client.stream("GET", url) as response:
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
            logger.error(f"Log stream error: {e}")
            self.connection_status.emit(f"error: {e}")
        finally:
            self.connection_status.emit("disconnected")

    def stop(self):
        """Stop streaming."""
        self._running = False


class DeviceCard(CardWidget):
    """Card representing a connected device."""

    selected = Signal(str)  # client_id

    def __init__(self, client_id: str, parent=None):
        super().__init__(parent)
        self._client_id = client_id
        self._is_selected = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Device icon based on client_id
        icon = self._get_icon()
        icon_widget = IconWidget(icon)
        icon_widget.setFixedSize(32, 32)
        layout.addWidget(icon_widget)

        # Device info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = StrongBodyLabel(self._get_display_name())
        info_layout.addWidget(name_label)

        id_label = BodyLabel(self._client_id)
        id_label.setStyleSheet("color: #888888; font-size: 11px;")
        info_layout.addWidget(id_label)

        layout.addLayout(info_layout, 1)

        # Online indicator
        self._status_dot = QFrame()
        self._status_dot.setFixedSize(10, 10)
        self._status_dot.setStyleSheet("""
            QFrame {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self._status_dot)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _get_icon(self) -> FluentIcon:
        """Get icon based on client_id hints."""
        client_lower = self._client_id.lower()
        if "windows" in client_lower or "win" in client_lower:
            return FluentIcon.LAPTOP
        elif "android" in client_lower:
            return FluentIcon.PHONE
        elif "linux" in client_lower:
            return FluentIcon.CODE
        elif "mac" in client_lower or "darwin" in client_lower:
            return FluentIcon.DEVELOPER_TOOLS
        return FluentIcon.IOT

    def _get_display_name(self) -> str:
        """Get friendly display name."""
        client_lower = self._client_id.lower()
        if "windows" in client_lower:
            return "Windows Desktop"
        elif "android" in client_lower:
            return "Android Phone"
        elif "linux" in client_lower:
            return "Linux Desktop"
        elif "mac" in client_lower or "darwin" in client_lower:
            return "macOS"
        return self._client_id.split("-")[0].title()

    def mousePressEvent(self, event):
        """Handle click to select."""
        super().mousePressEvent(event)
        self.selected.emit(self._client_id)

    def set_selected(self, selected: bool):
        """Update selected state."""
        self._is_selected = selected
        if selected:
            self.setStyleSheet("CardWidget { border: 2px solid #e94560; }")
        else:
            self.setStyleSheet("")


class DevicesPage(ScrollArea):
    """Connected devices viewer with real-time logs."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("devicesPage")

        self._settings = get_settings()
        self._stream_worker: Optional[LogStreamWorker] = None
        self._device_cards: dict[str, DeviceCard] = {}
        self._selected_client: Optional[str] = None
        self._autoscroll = True
        self._all_logs: list[dict] = []  # All received logs
        self._connection_warned = False  # Track if we already warned

        self._setup_ui()
        self._setup_refresh_timer()

    def _setup_ui(self) -> None:
        """Build the devices interface."""
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(20)

        # Header
        header = TitleLabel("Connected Devices")
        layout.addWidget(header)

        subtitle = SubtitleLabel("View real-time logs from connected clients")
        subtitle.setStyleSheet("color: #888888;")
        layout.addWidget(subtitle)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # Left panel - Device list
        left_panel = self._create_device_panel()
        splitter.addWidget(left_panel)

        # Right panel - Log viewer
        right_panel = self._create_log_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (30% / 70%)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter, 1)

    def _create_device_panel(self) -> QWidget:
        """Create device list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        # Header with refresh
        header_layout = QHBoxLayout()
        header_label = StrongBodyLabel("Devices")
        header_layout.addWidget(header_label)

        refresh_btn = TransparentPushButton()
        refresh_btn.setIcon(FluentIcon.SYNC)
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.clicked.connect(self._refresh_devices)
        refresh_btn.setToolTip("Refresh device list")
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Device list container
        self._devices_container = QWidget()
        self._devices_layout = QVBoxLayout(self._devices_container)
        self._devices_layout.setContentsMargins(0, 0, 0, 0)
        self._devices_layout.setSpacing(8)
        self._devices_layout.addStretch()

        # Scroll area for devices
        devices_scroll = ScrollArea()
        devices_scroll.setWidget(self._devices_container)
        devices_scroll.setWidgetResizable(True)
        devices_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        devices_scroll.setStyleSheet("background: transparent; border: none;")

        layout.addWidget(devices_scroll, 1)

        # Placeholder when no devices
        self._no_devices_label = BodyLabel("No devices connected")
        self._no_devices_label.setStyleSheet("color: #666666; padding: 20px;")
        self._no_devices_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._no_devices_label)

        return panel

    def _create_log_panel(self) -> QWidget:
        """Create log viewer panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(12)

        # Controls
        controls = self._create_log_controls()
        layout.addLayout(controls)

        # Log display
        self._log_display = TextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setPlaceholderText("Select a device to view logs...")
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

        return panel

    def _create_log_controls(self) -> QHBoxLayout:
        """Create log control buttons."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Selected device label
        self._selected_label = BodyLabel("No device selected")
        self._selected_label.setStyleSheet("color: #888888;")
        layout.addWidget(self._selected_label)

        layout.addStretch()

        # Stream toggle
        self._stream_btn = PrimaryPushButton("Start Stream")
        self._stream_btn.setIcon(FluentIcon.PLAY)
        self._stream_btn.clicked.connect(self._toggle_stream)
        self._stream_btn.setEnabled(False)
        layout.addWidget(self._stream_btn)

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

        return layout

    def _setup_refresh_timer(self):
        """Setup timer to refresh device list periodically."""
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_devices)
        self._refresh_timer.start(10000)  # Every 10 seconds

        # Initial refresh
        QTimer.singleShot(500, self._refresh_devices)

    @Slot()
    def _refresh_devices(self):
        """Refresh connected devices list."""
        import httpx

        try:
            url = f"{self._settings.sombra_api_url}/api/logs/clients"
            response = httpx.get(url, timeout=5.0)
            data = response.json()

            clients = data.get("clients", [])
            self._update_device_list(clients)
            self._connection_warned = False  # Reset on success

        except Exception as e:
            if not self._connection_warned:
                logger.warning(f"Devices API not available")
                self._connection_warned = True

    def _update_device_list(self, clients: list[str]):
        """Update device cards based on client list."""
        # Remove devices no longer connected
        for client_id in list(self._device_cards.keys()):
            if client_id not in clients:
                card = self._device_cards.pop(client_id)
                self._devices_layout.removeWidget(card)
                card.deleteLater()

        # Add new devices
        for client_id in clients:
            if client_id not in self._device_cards:
                card = DeviceCard(client_id, self)
                card.selected.connect(self._on_device_selected)
                self._device_cards[client_id] = card
                # Insert before stretch
                self._devices_layout.insertWidget(
                    self._devices_layout.count() - 1, card
                )

        # Update visibility
        has_devices = len(self._device_cards) > 0
        self._no_devices_label.setVisible(not has_devices)
        self._devices_container.setVisible(has_devices)

    @Slot(str)
    def _on_device_selected(self, client_id: str):
        """Handle device selection."""
        self._selected_client = client_id

        # Update card selection states
        for cid, card in self._device_cards.items():
            card.set_selected(cid == client_id)

        # Update UI
        self._selected_label.setText(f"Selected: {client_id}")
        self._stream_btn.setEnabled(True)

        # Filter logs for this device
        self._filter_logs_for_device(client_id)

    def _filter_logs_for_device(self, client_id: str):
        """Show only logs from selected device."""
        self._log_display.clear()

        for log in self._all_logs:
            if log.get("client_id") == client_id:
                self._display_log_entry(log)

    @Slot()
    def _toggle_stream(self):
        """Toggle log streaming."""
        if self._stream_worker and self._stream_worker.isRunning():
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self):
        """Start streaming logs."""
        self._stream_worker = LogStreamWorker(self._settings.sombra_api_url, self)
        self._stream_worker.log_received.connect(self._on_log_received)
        self._stream_worker.connection_status.connect(self._on_stream_status)
        self._stream_worker.start()

        self._stream_btn.setText("Stop Stream")
        self._stream_btn.setIcon(FluentIcon.PAUSE)

    def _stop_stream(self):
        """Stop streaming logs."""
        if self._stream_worker:
            self._stream_worker.stop()
            self._stream_worker.wait(1000)
            self._stream_worker = None

        self._stream_btn.setText("Start Stream")
        self._stream_btn.setIcon(FluentIcon.PLAY)

    @Slot(dict)
    def _on_log_received(self, log: dict):
        """Handle received log entry."""
        self._all_logs.append(log)

        # Keep buffer limited
        if len(self._all_logs) > 5000:
            self._all_logs = self._all_logs[-4000:]

        # Only display if matches selected device
        if self._selected_client and log.get("client_id") == self._selected_client:
            self._display_log_entry(log)

    def _display_log_entry(self, log: dict):
        """Display a single log entry."""
        timestamp = log.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                timestamp = dt.strftime("%H:%M:%S")
            except ValueError:
                timestamp = timestamp[:8] if len(timestamp) > 8 else timestamp

        level = log.get("level", "INFO").upper()
        message = log.get("message", str(log))
        logger_name = log.get("logger", "")

        # Color based on level
        color = {
            "DEBUG": "#888888",
            "INFO": "#FFFFFF",
            "WARNING": "#FFA726",
            "ERROR": "#EF5350",
            "CRITICAL": "#D32F2F",
        }.get(level, "#FFFFFF")

        # Format log line
        if logger_name:
            formatted = f'<span style="color: #666666">[{timestamp}]</span> ' \
                       f'<span style="color: {color}">[{level}]</span> ' \
                       f'<span style="color: #888888">[{logger_name}]</span> ' \
                       f'{message}'
        else:
            formatted = f'<span style="color: #666666">[{timestamp}]</span> ' \
                       f'<span style="color: {color}">[{level}]</span> ' \
                       f'{message}'

        self._log_display.append(formatted)

        # Auto-scroll
        if self._autoscroll:
            scrollbar = self._log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    @Slot(str)
    def _on_stream_status(self, status: str):
        """Handle stream connection status."""
        if status == "connected":
            InfoBar.success(
                title="Connected",
                content="Streaming logs from server",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=2000
            )
        elif status == "disconnected":
            InfoBar.info(
                title="Disconnected",
                content="Log stream stopped",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=2000
            )
            self._stream_btn.setText("Start Stream")
            self._stream_btn.setIcon(FluentIcon.PLAY)
        elif status.startswith("error"):
            InfoBar.error(
                title="Stream Error",
                content=status,
                parent=self,
                position=InfoBarPosition.TOP,
                duration=3000
            )

    @Slot()
    def _clear_logs(self):
        """Clear log display."""
        self._log_display.clear()
        if self._selected_client:
            # Clear logs for selected device only
            self._all_logs = [
                log for log in self._all_logs
                if log.get("client_id") != self._selected_client
            ]

    @Slot()
    def _toggle_autoscroll(self):
        """Toggle auto-scroll."""
        self._autoscroll = not self._autoscroll
        if self._autoscroll:
            self._autoscroll_btn.setText("Auto-scroll: On")
        else:
            self._autoscroll_btn.setText("Auto-scroll: Off")

    def showEvent(self, event):
        """Refresh devices when page becomes visible."""
        super().showEvent(event)
        self._refresh_devices()

    def hideEvent(self, event):
        """Stop stream when leaving page."""
        super().hideEvent(event)
        # Don't stop stream - let it run in background

    def cleanup(self):
        """Cleanup resources."""
        self._refresh_timer.stop()
        self._stop_stream()
