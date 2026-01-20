"""System tray icon and menu."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon, QWidget

from .utils import get_app_icon


class SystemTray(QSystemTrayIcon):
    """System tray integration.

    Provides:
    - Tray icon
    - Context menu (show/hide, settings, quit)
    - System notifications
    """

    # Signals
    show_requested = Signal()
    hide_requested = Signal()
    quit_requested = Signal()
    settings_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._setup_icon()
        self._setup_menu()
        self._connect_signals()

    def _setup_icon(self) -> None:
        """Setup tray icon."""
        icon = get_app_icon()
        if icon.isNull():
            # Fallback to system icon
            icon = QIcon.fromTheme("audio-input-microphone")
        self.setIcon(icon)
        self.setToolTip("Sombra Desktop")

    def _setup_menu(self) -> None:
        """Create tray context menu."""
        menu = QMenu()

        # Show/Hide action
        self._show_action = QAction("Show", self)
        self._show_action.triggered.connect(self.show_requested.emit)
        menu.addAction(self._show_action)

        self._hide_action = QAction("Hide", self)
        self._hide_action.triggered.connect(self.hide_requested.emit)
        menu.addAction(self._hide_action)

        menu.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle visibility
            self.show_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.show_requested.emit()

    def show_notification(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
        duration_ms: int = 3000,
    ) -> None:
        """Display a system notification.

        Args:
            title: Notification title.
            message: Notification message.
            icon: Icon type.
            duration_ms: Display duration in milliseconds.
        """
        self.showMessage(title, message, icon, duration_ms)

    def update_visibility_actions(self, is_visible: bool) -> None:
        """Update show/hide actions based on window visibility.

        Args:
            is_visible: Whether the main window is visible.
        """
        self._show_action.setVisible(not is_visible)
        self._hide_action.setVisible(is_visible)
