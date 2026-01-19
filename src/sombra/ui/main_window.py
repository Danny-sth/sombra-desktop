"""Main application window with Fluent Design navigation."""

import logging
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QIcon, QColor, QCloseEvent
from PySide6.QtWidgets import QApplication

from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    FluentIcon,
    setTheme,
    setThemeColor,
    Theme,
    InfoBar,
    InfoBarPosition,
    isDarkTheme,
)

from .pages.home_page import HomePage
from .pages.chat_page import ChatPage
from .pages.agents_page import AgentsPage
from .pages.tasks_page import TasksPage
from .pages.logs_page import LogsPage
from .pages.settings_page import SettingsPage

from ..core.async_bridge import get_async_bridge
from ..services.audio_service import AudioService
from ..services.whisper_service import WhisperService
from ..services.sombra_service import SombraService
from ..services.hotkey_service import HotkeyService
from ..services.wakeword_service import WakeWordService
from ..services.update_service import UpdateService

logger = logging.getLogger(__name__)


class MainWindow(FluentWindow):
    """Sombra Desktop main window with Fluent Design.

    Features:
    - Sidebar navigation with 6 pages
    - Dark/Light theme support
    - Voice and text chat integration
    - Extensible for future orchestrator features
    """

    def __init__(
        self,
        audio_service: AudioService,
        whisper_service: WhisperService,
        sombra_service: SombraService,
        hotkey_service: HotkeyService,
        wakeword_service: WakeWordService | None = None,
    ):
        super().__init__()

        # Store services
        self._audio_service = audio_service
        self._whisper_service = whisper_service
        self._sombra_service = sombra_service
        self._hotkey_service = hotkey_service
        self._wakeword_service = wakeword_service

        # Update service
        self._update_service = UpdateService(self)

        # Services dict for pages
        self._services = {
            "audio": audio_service,
            "whisper": whisper_service,
            "sombra": sombra_service,
            "hotkey": hotkey_service,
            "wakeword": wakeword_service,
        }

        # Setup window
        self._setup_window()
        self._setup_theme()
        self._init_pages()
        self._init_navigation()
        self._connect_signals()
        self._setup_auto_update()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Sombra Desktop")
        self.setMinimumSize(800, 600)

        # Start maximized
        self.showMaximized()

    def _setup_theme(self) -> None:
        """Configure theme and colors."""
        # Sombra accent color (pink/red)
        setThemeColor(QColor("#e94560"))

        # Dark theme by default
        setTheme(Theme.DARK)

    def _init_pages(self) -> None:
        """Create all page instances."""
        # Home/Dashboard
        self.home_page = HomePage(self)
        self.home_page.setObjectName("homePage")

        # Chat (main functionality)
        self.chat_page = ChatPage(self._services, self)
        self.chat_page.setObjectName("chatPage")

        # Agents (placeholder)
        self.agents_page = AgentsPage(self)
        self.agents_page.setObjectName("agentsPage")

        # Tasks (placeholder)
        self.tasks_page = TasksPage(self)
        self.tasks_page.setObjectName("tasksPage")

        # Logs
        self.logs_page = LogsPage(self._sombra_service, self)
        self.logs_page.setObjectName("logsPage")

        # Settings
        self.settings_page = SettingsPage(self)
        self.settings_page.setObjectName("settingsPage")

    def _init_navigation(self) -> None:
        """Setup sidebar navigation."""
        # Dashboard - top position
        self.addSubInterface(
            self.home_page,
            FluentIcon.HOME,
            "Dashboard",
            NavigationItemPosition.TOP
        )

        # Chat - scroll area (main)
        self.addSubInterface(
            self.chat_page,
            FluentIcon.CHAT,
            "Chat",
            NavigationItemPosition.SCROLL
        )

        # Agents
        self.addSubInterface(
            self.agents_page,
            FluentIcon.ROBOT,
            "Agents",
            NavigationItemPosition.SCROLL
        )

        # Tasks
        self.addSubInterface(
            self.tasks_page,
            FluentIcon.CHECKBOX,
            "Tasks",
            NavigationItemPosition.SCROLL
        )

        # Logs
        self.addSubInterface(
            self.logs_page,
            FluentIcon.DOCUMENT,
            "Logs",
            NavigationItemPosition.SCROLL
        )

        # Settings - bottom position
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM
        )

        # Navigate to chat by default
        self.switchTo(self.chat_page)

    def _connect_signals(self) -> None:
        """Connect service signals to UI updates."""
        # Connection status to dashboard
        self._sombra_service.connection_status.connect(self._on_connection_status)

        # Recording status to dashboard
        self._audio_service.recording_started.connect(
            lambda: self.home_page.set_recording_status(True)
        )
        self._audio_service.recording_stopped.connect(
            lambda _: self.home_page.set_recording_status(False)
        )

        # Settings theme change
        self.settings_page.theme_changed.connect(self._on_theme_changed)

        # Update signals
        self._update_service.update_available.connect(self._on_update_available)
        self._update_service.download_progress.connect(self._on_download_progress)
        self._update_service.update_ready.connect(self._on_update_ready)
        self._update_service.error.connect(self._on_update_error)

    def _setup_auto_update(self) -> None:
        """Setup auto-update check on startup."""
        # Check for updates 3 seconds after startup
        QTimer.singleShot(3000, self._update_service.check_for_updates)

    # ===== Signal Handlers =====

    @Slot(str)
    def _on_connection_status(self, status: str) -> None:
        """Handle connection status updates."""
        self.home_page.set_connection_status(status)

        # Show notification for connection changes
        if "connected" in status.lower() and "dis" not in status.lower():
            InfoBar.success(
                title="Connected",
                content="Successfully connected to Sombra server",
                parent=self,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000
            )
        elif "error" in status.lower() or "disconnect" in status.lower():
            InfoBar.error(
                title="Connection Error",
                content=status,
                parent=self,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000
            )

    @Slot(str)
    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme change from settings."""
        # Theme is already applied by settings page
        pass

    # ===== Update Handlers =====

    @Slot(str, str)
    def _on_update_available(self, version: str, release_notes: str) -> None:
        """Auto-download update without asking."""
        logger.info(f"Update available: v{version}, downloading automatically...")
        InfoBar.info(
            title="Обновление",
            content=f"Загружаю v{version}...",
            parent=self,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000
        )
        self._update_service.download_update()

    @Slot(int, int)
    def _on_download_progress(self, downloaded: int, total: int) -> None:
        """Silent progress tracking."""
        pass  # No UI feedback needed

    @Slot(str)
    def _on_update_ready(self, path: str) -> None:
        """Auto-apply update and restart."""
        logger.info("Update downloaded, applying and restarting...")
        InfoBar.success(
            title="Обновление",
            content="Перезапускаюсь...",
            parent=self,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000
        )
        # Small delay to show the message, then apply
        QTimer.singleShot(1500, self._update_service.apply_update)

    @Slot(str)
    def _on_update_error(self, error: str) -> None:
        """Log error silently."""
        logger.error(f"Update failed: {error}")

    # ===== Public Methods =====

    def show_notification(
        self,
        title: str,
        content: str,
        notification_type: str = "info"
    ) -> None:
        """Show a notification banner.

        Args:
            title: Notification title
            content: Notification content
            notification_type: One of "success", "error", "warning", "info"
        """
        if notification_type == "success":
            InfoBar.success(title, content, parent=self, position=InfoBarPosition.TOP_RIGHT)
        elif notification_type == "error":
            InfoBar.error(title, content, parent=self, position=InfoBarPosition.TOP_RIGHT)
        elif notification_type == "warning":
            InfoBar.warning(title, content, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.info(title, content, parent=self, position=InfoBarPosition.TOP_RIGHT)

    # ===== Window Events =====

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close - cleanup services."""
        # Clean up services
        if self._wakeword_service:
            self._wakeword_service.cleanup()
        self._audio_service.cleanup()
        self._whisper_service.cleanup()
        self._sombra_service.cleanup()
        self._hotkey_service.cleanup()
        self._update_service.cleanup()

        # Stop async bridge
        bridge = get_async_bridge()
        bridge.stop()

        event.accept()
