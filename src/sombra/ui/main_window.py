"""Main application window with Fluent Design navigation."""

import logging
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QColor, QCloseEvent

from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    FluentIcon,
    setTheme,
    setThemeColor,
    Theme,
    InfoBar,
    InfoBarPosition,
    StateToolTip,
)

from .system_tray import SystemTray
from .utils import get_app_icon
from .widgets.connection_indicator import ConnectionIndicator
from .widgets.footer import Footer
from .pages.home_page import HomePage
from .pages.chat_page import ChatPage
from .pages.agents_page import AgentsPage
from .pages.tasks_page import TasksPage
from .pages.devices_page import DevicesPage
from .pages.settings_page import SettingsPage

from ..core.async_bridge import get_async_bridge
from ..services.audio_service import AudioService
from ..services.whisper_service import WhisperService
from ..services.sombra_service import SombraService
from ..services.hotkey_service import HotkeyService
from ..services.wakeword_service import WakeWordService
from ..services.update_service import UpdateService
from ..services.remote_commands import init_remote_commands
from ..config.settings import get_settings

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
        self._update_tooltip: StateToolTip | None = None
        self._update_version: str | None = None

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
        self._setup_system_tray()
        self._setup_auto_update()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Sombra Desktop")
        self.setMinimumSize(800, 600)

        # Set window icon
        icon = get_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)

        # Enable window transparency (requires compositor on Linux)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)

        # Start maximized
        self.showMaximized()

    def _setup_theme(self) -> None:
        """Configure theme and colors."""
        # Sombra accent color (pink/red)
        setThemeColor(QColor("#e94560"))

        # Dark theme by default
        setTheme(Theme.DARK)

    def _setup_system_tray(self) -> None:
        """Initialize system tray icon and menu."""
        self._tray = SystemTray(self)
        self._force_quit = False

        # Connect tray signals
        self._tray.show_requested.connect(self._show_from_tray)
        self._tray.hide_requested.connect(self._hide_to_tray)
        self._tray.quit_requested.connect(self._quit_app)
        self._tray.settings_requested.connect(self._show_settings)

        # Show tray icon
        self._tray.show()
        self._tray.update_visibility_actions(True)

    def _show_from_tray(self) -> None:
        """Show and activate window from tray."""
        self.show()
        self.raise_()
        self.activateWindow()
        if self.isMinimized():
            self.showNormal()
        self._tray.update_visibility_actions(True)

    def _hide_to_tray(self) -> None:
        """Hide window to tray."""
        self.hide()
        self._tray.update_visibility_actions(False)

    def _show_settings(self) -> None:
        """Show settings page."""
        self._show_from_tray()
        self.switchTo(self.settings_page)

    def _quit_app(self) -> None:
        """Actually quit the application."""
        self._force_quit = True
        self.close()

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

        # Devices
        self.devices_page = DevicesPage(self)
        self.devices_page.setObjectName("devicesPage")

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

        # Devices
        self.addSubInterface(
            self.devices_page,
            FluentIcon.IOT,
            "Devices",
            NavigationItemPosition.SCROLL
        )

        # Settings - bottom position
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM
        )

        # Connection status indicator at the very bottom of sidebar
        self._connection_indicator = ConnectionIndicator(self)
        self._connection_indicator.setObjectName("connectionIndicator")

        # Footer with version info
        self._footer = Footer(self)
        self._footer.setObjectName("footer")

        # Add to navigation panel's bottom layout (below Settings)
        nav_panel = self.navigationInterface.panel
        nav_panel.bottomLayout.addWidget(self._connection_indicator)
        nav_panel.bottomLayout.addWidget(self._footer)

        # Navigate to chat by default
        self.switchTo(self.chat_page)

    def _connect_signals(self) -> None:
        """Connect service signals to UI updates."""
        # Connection status to dashboard and sidebar indicator
        self._sombra_service.connection_status.connect(self._on_connection_status)
        self._sombra_service.connection_status.connect(self._connection_indicator.set_status)

        # Connection indicator click triggers connection check
        self._connection_indicator.clicked.connect(
            self._sombra_service.check_connection_async
        )

        # Recording status to dashboard
        self._audio_service.recording_started.connect(
            lambda: self.home_page.set_recording_status(True)
        )
        self._audio_service.recording_stopped.connect(
            lambda _: self.home_page.set_recording_status(False)
        )

        # Settings theme change
        self.settings_page.theme_changed.connect(self._on_theme_changed)

        # Initial connection check on startup (after 1 second to let UI settle)
        QTimer.singleShot(1000, self._sombra_service.check_connection_async)

        # Update signals
        self._update_service.update_available.connect(self._on_update_available)
        self._update_service.download_progress.connect(self._on_download_progress)
        self._update_service.update_ready.connect(self._on_update_ready)
        self._update_service.error.connect(self._on_update_error)

    def _setup_auto_update(self) -> None:
        """Setup auto-update check on startup and periodic checks."""
        # Check for updates 3 seconds after startup
        QTimer.singleShot(3000, self._update_service.check_for_updates)

        # Periodic check every 5 minutes
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_service.check_for_updates)
        self._update_timer.start(5 * 60 * 1000)  # 5 minutes

        # Register remote command handlers
        self._setup_remote_commands()

    def _setup_remote_commands(self) -> None:
        """Register handlers for server commands."""
        # Initialize remote command service with all handlers
        self._remote_service = init_remote_commands(self._update_service)
        logger.info("Remote command service initialized")

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
        # Update connection indicator theme
        self._connection_indicator.set_theme(theme)
        # Update footer theme
        self._footer.set_theme(theme)

    # ===== Update Handlers =====

    @Slot(str, str)
    def _on_update_available(self, version: str, release_notes: str) -> None:
        """Auto-download update with progress indicator."""
        logger.info(f"Update available: v{version}, downloading automatically...")
        self._update_version = version

        # Show progress tooltip
        self._update_tooltip = StateToolTip(
            "Обновление",
            f"Загружаю v{version}... 0%",
            self
        )
        self._update_tooltip.move(self.width() - 300, 50)
        self._update_tooltip.show()

        self._update_service.download_update()

    @Slot(int, int)
    def _on_download_progress(self, downloaded: int, total: int) -> None:
        """Update progress indicator."""
        if self._update_tooltip and total > 0:
            percent = int(downloaded * 100 / total)
            mb_down = downloaded / (1024 * 1024)
            mb_total = total / (1024 * 1024)
            self._update_tooltip.setContent(
                f"Загружаю v{self._update_version}... {percent}% ({mb_down:.1f}/{mb_total:.1f} MB)"
            )

    @Slot(str)
    def _on_update_ready(self, path: str) -> None:
        """Auto-apply update and restart."""
        logger.info("Update downloaded, applying and restarting...")

        if self._update_tooltip:
            self._update_tooltip.setContent("Установка... Перезапуск через 2 сек")
            self._update_tooltip.setState(True)  # Success state

        # Small delay to show the message, then apply
        QTimer.singleShot(2000, self._update_service.apply_update)

    @Slot(str)
    def _on_update_error(self, error: str) -> None:
        """Show error in tooltip."""
        logger.error(f"Update failed: {error}")

        if self._update_tooltip:
            self._update_tooltip.setContent(f"Ошибка: {error[:50]}")
            self._update_tooltip.setState(True)
            # Hide after 5 seconds
            QTimer.singleShot(5000, self._update_tooltip.close)

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
        """Minimize to tray instead of closing, unless force quit."""
        settings = get_settings()

        if self._force_quit or not settings.minimize_to_tray:
            # Real quit - cleanup and exit
            self._cleanup_services()
            event.accept()
        else:
            # Minimize to tray
            event.ignore()
            self.hide()
            self._tray.update_visibility_actions(False)
            self._tray.show_notification(
                "Sombra Desktop",
                "Приложение свёрнуто в трей",
                duration_ms=2000
            )

    def _cleanup_services(self) -> None:
        """Cleanup all services before quit."""
        # Clean up services
        if self._wakeword_service:
            self._wakeword_service.cleanup()
        self._audio_service.cleanup()
        self._whisper_service.cleanup()
        self._sombra_service.cleanup()
        self._hotkey_service.cleanup()
        self._update_service.cleanup()
        self.devices_page.cleanup()
        self.home_page.cleanup()

        # Hide tray icon
        if hasattr(self, '_tray'):
            self._tray.hide()

        # Stop async bridge
        bridge = get_async_bridge()
        bridge.stop()
