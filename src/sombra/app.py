"""Main application setup and initialization."""

import sys
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .config.settings import init_settings
from .core.async_bridge import init_async_bridge
from .core.events import init_event_hub
from .core.session import init_session_manager
from .config.settings import get_settings
from .services.audio_service import AudioService
from .services.hotkey_service import HotkeyService
from .services.sombra_service import SombraService
from .services.wakeword_service import WakeWordService
from .services.whisper_service import WhisperService
from .themes.theme_manager import init_theme_manager
from .ui.main_window import MainWindow


class SombraApp:
    """Main application controller.

    Initializes all components and manages the application lifecycle.
    """

    def __init__(self):
        """Initialize the application."""
        self._app: Optional[QApplication] = None
        self._main_window: Optional[MainWindow] = None

        # Services
        self._audio_service: Optional[AudioService] = None
        self._whisper_service: Optional[WhisperService] = None
        self._sombra_service: Optional[SombraService] = None
        self._hotkey_service: Optional[HotkeyService] = None
        self._wakeword_service: Optional[WakeWordService] = None

    def run(self) -> int:
        """Initialize and start the application.

        Returns:
            Exit code.
        """
        # Enable high DPI scaling (must be called before QApplication creation)
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Initialize Qt application
        self._app = QApplication(sys.argv)
        self._app.setApplicationName("Sombra Desktop")
        self._app.setOrganizationName("Sombra")
        self._app.setApplicationVersion("0.1.0")

        # Initialize settings
        init_settings()

        # Initialize core components
        init_event_hub()
        init_session_manager()
        async_bridge = init_async_bridge()
        async_bridge.start()

        # Initialize theme manager and apply initial theme
        theme_manager = init_theme_manager(self._app)
        theme_manager.apply_theme(theme_manager.current_theme)

        # Initialize services
        self._audio_service = AudioService()
        self._whisper_service = WhisperService()
        self._sombra_service = SombraService()
        self._hotkey_service = HotkeyService()
        self._wakeword_service = WakeWordService()

        # Start hotkey listener
        self._hotkey_service.start()

        # Start wake word listener if enabled
        settings = get_settings()
        if settings.wake_word_enabled and self._wakeword_service.is_available:
            self._wakeword_service.start_listening()

        # Create and show main window
        self._main_window = MainWindow(
            audio_service=self._audio_service,
            whisper_service=self._whisper_service,
            sombra_service=self._sombra_service,
            hotkey_service=self._hotkey_service,
            wakeword_service=self._wakeword_service,
        )
        self._main_window.show()

        # Run event loop
        return self._app.exec()

    def shutdown(self) -> None:
        """Graceful shutdown of all services."""
        if self._wakeword_service:
            self._wakeword_service.cleanup()

        if self._hotkey_service:
            self._hotkey_service.cleanup()

        if self._audio_service:
            self._audio_service.cleanup()

        if self._whisper_service:
            self._whisper_service.cleanup()

        if self._sombra_service:
            self._sombra_service.cleanup()


def main() -> int:
    """Application entry point.

    Returns:
        Exit code.
    """
    app = SombraApp()
    try:
        return app.run()
    except KeyboardInterrupt:
        app.shutdown()
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        app.shutdown()
        return 1
