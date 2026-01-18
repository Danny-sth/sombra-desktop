"""Main application window."""

import time

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QVBoxLayout,
    QWidget,
)

from ..core.async_bridge import get_async_bridge
from ..core.events import get_event_hub
from ..services.audio_service import AudioService
from ..services.hotkey_service import HotkeyService
from ..services.sombra_service import SombraService
from ..services.sound_service import SoundService
from ..services.wakeword_service import WakeWordService
from ..services.whisper_service import WhisperService
from ..themes.theme_manager import get_theme_manager
from .widgets.output_display import OutputDisplay
from .widgets.status_bar import StatusBar
from .widgets.text_input import TextInput
from .widgets.voice_button import VoiceButton


class MainWindow(QMainWindow):
    """Main application window.

    Assembles all UI components and wires up event handling.
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

        # Store service references
        self._audio_service = audio_service
        self._whisper_service = whisper_service
        self._sombra_service = sombra_service
        self._hotkey_service = hotkey_service
        self._wakeword_service = wakeword_service

        # Get event hub
        self._event_hub = get_event_hub()

        # Wake word cooldown (prevent immediate re-trigger after recording)
        self._last_recording_end_time: float = 0
        self._wake_word_cooldown = 3.0  # seconds

        # Setup window
        self._setup_window()
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()

        # Check connection on startup
        self._sombra_service.check_connection_async()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Sombra Desktop")
        self.setMinimumSize(500, 600)
        self.resize(600, 700)

        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _setup_ui(self) -> None:
        """Initialize UI components and layout."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # ===== Header =====
        header = self._create_header()
        main_layout.addWidget(header)

        # ===== Output Display =====
        self._output_display = OutputDisplay()
        main_layout.addWidget(self._output_display, 1)  # stretch=1

        # ===== Recognized Text Label =====
        self._recognized_label = QLabel("Press and hold the microphone button to speak...")
        self._recognized_label.setObjectName("subtitleLabel")
        self._recognized_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recognized_label.setWordWrap(True)
        main_layout.addWidget(self._recognized_label)

        # ===== Voice Input Section =====
        voice_section = self._create_voice_section()
        main_layout.addWidget(voice_section)

        # ===== Text Input =====
        self._text_input = TextInput()
        main_layout.addWidget(self._text_input)

        # ===== Separator =====
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)

        # ===== Status Bar =====
        self._status_bar = StatusBar()
        main_layout.addWidget(self._status_bar)

    def _create_header(self) -> QWidget:
        """Create header section."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Sombra Desktop")
        title.setObjectName("titleLabel")

        subtitle = QLabel("Voice-enabled AI Assistant")
        subtitle.setObjectName("subtitleLabel")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        return header

    def _create_voice_section(self) -> QWidget:
        """Create voice input section with button."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Voice button
        self._voice_button = VoiceButton()
        layout.addWidget(self._voice_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Hotkey hint
        hotkey_label = QLabel("Click to record, click again to send (Ctrl+Shift+S)")
        hotkey_label.setObjectName("subtitleLabel")
        hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hotkey_label)

        return section

    def _setup_menu(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_session_action = QAction("New Session", self)
        new_session_action.setShortcut(QKeySequence("Ctrl+N"))
        new_session_action.triggered.connect(self._on_new_session)
        file_menu.addAction(new_session_action)

        file_menu.addSeparator()

        clear_action = QAction("Clear Output", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self._output_display.clear)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self._apply_theme("dark"))
        view_menu.addAction(dark_theme_action)

        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self._apply_theme("light"))
        view_menu.addAction(light_theme_action)

        view_menu.addSeparator()

        always_on_top_action = QAction("Always on Top", self)
        always_on_top_action.setCheckable(True)
        always_on_top_action.triggered.connect(self._toggle_always_on_top)
        view_menu.addAction(always_on_top_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self) -> None:
        """Wire up event hub signals to UI updates."""
        # Voice button signals
        self._voice_button.recording_started.connect(self._on_recording_started)
        self._voice_button.recording_stopped.connect(self._on_recording_stopped)

        # Audio service signals
        self._audio_service.audio_level.connect(self._voice_button.set_audio_level)
        self._audio_service.recording_stopped.connect(self._on_audio_ready)
        self._audio_service.error.connect(self._on_error)

        # Whisper service signals
        self._whisper_service.transcription_started.connect(self._on_transcription_started)
        self._whisper_service.transcription_completed.connect(self._on_transcription_completed)
        self._whisper_service.transcription_error.connect(self._on_error)

        # Sombra service signals
        self._sombra_service.query_sent.connect(self._on_query_sent)
        self._sombra_service.thinking_update.connect(self._output_display.append_thinking)
        self._sombra_service.response_received.connect(self._on_response_received)
        self._sombra_service.stream_completed.connect(self._output_display.end_streaming)
        self._sombra_service.stream_error.connect(self._on_error)
        self._sombra_service.connection_status.connect(self._status_bar.set_connection_status)

        # Hotkey service signals
        self._hotkey_service.hotkey_pressed.connect(self._on_hotkey_pressed)
        self._hotkey_service.hotkey_released.connect(self._on_hotkey_released)

        # Text input signals
        self._text_input.text_submitted.connect(self._on_text_submitted)

        # Status bar signals
        self._status_bar.theme_toggle_clicked.connect(self._on_theme_toggle)
        self._status_bar.settings_clicked.connect(self._on_settings_clicked)

        # Wake word service signals
        if self._wakeword_service:
            self._wakeword_service.wake_word_detected.connect(self._on_wake_word_detected)
            self._wakeword_service.error.connect(self._on_error)

    # ===== Event Handlers =====

    @Slot()
    def _on_recording_started(self) -> None:
        """Handle recording start."""
        SoundService.play_start_sound()
        self._audio_service.start_recording()
        self._status_bar.set_recording_status(True)
        self._recognized_label.setText("Listening...")

    @Slot()
    def _on_recording_stopped(self) -> None:
        """Handle recording stop."""
        self._audio_service.stop_recording()
        self._status_bar.set_recording_status(False)
        self._recognized_label.setText("Processing...")

    @Slot(bytes)
    def _on_audio_ready(self, audio_data: bytes) -> None:
        """Handle audio data ready for transcription (from auto-stop or manual stop)."""
        import logging
        logger = logging.getLogger(__name__)

        # Play stop sound
        SoundService.play_stop_sound()

        # Update UI state (important for auto-stop case)
        self._voice_button.set_recording_state(False)
        self._status_bar.set_recording_status(False)
        self._recognized_label.setText("Processing...")

        # Set cooldown timestamp to prevent wake word re-trigger
        self._last_recording_end_time = time.time()
        logger.info(f"Recording ended. Cooldown set for {self._wake_word_cooldown}s")

        if audio_data:
            self._whisper_service.transcribe_async(audio_data)

    @Slot()
    def _on_transcription_started(self) -> None:
        """Handle transcription start."""
        self._recognized_label.setText("Transcribing...")

    @Slot(str)
    def _on_transcription_completed(self, text: str) -> None:
        """Handle transcription completed."""
        self._recognized_label.setText(f'"{text}"')
        self._text_input.set_text(text)

        # Auto-send if text is valid
        if text.strip():
            self._send_query(text)

    @Slot(str)
    def _on_text_submitted(self, text: str) -> None:
        """Handle text submission from input field."""
        self._send_query(text)

    def _send_query(self, text: str) -> None:
        """Send a query to Sombra."""
        self._output_display.start_streaming()
        self._sombra_service.send_chat_async(text)

    @Slot(str)
    def _on_query_sent(self, query: str) -> None:
        """Handle query sent."""
        self._text_input.clear()
        self._status_bar.show_message("Sending query...")

    @Slot(str)
    def _on_response_received(self, response: str) -> None:
        """Handle response received."""
        self._output_display.set_content(response)

    @Slot(str)
    def _on_error(self, error: str) -> None:
        """Handle errors."""
        self._recognized_label.setText(f"Error: {error}")
        self._status_bar.show_message(f"Error: {error}", 5000)

    @Slot(str)
    def _on_hotkey_pressed(self, name: str) -> None:
        """Handle global hotkey press - toggle recording."""
        if name == "push_to_talk":
            self._voice_button.toggle_recording()

    @Slot(str)
    def _on_hotkey_released(self, name: str) -> None:
        """Handle global hotkey release - unused in toggle mode."""
        pass

    @Slot()
    def _on_wake_word_detected(self) -> None:
        """Handle wake word detection - start recording with auto-stop."""
        import logging
        logger = logging.getLogger(__name__)

        # Check cooldown to prevent immediate re-trigger
        elapsed = time.time() - self._last_recording_end_time
        if elapsed < self._wake_word_cooldown:
            logger.info(f"Wake word IGNORED (cooldown: {elapsed:.1f}s < {self._wake_word_cooldown}s)")
            return

        if self._voice_button.is_recording:
            logger.info("Wake word IGNORED (already recording)")
            return

        logger.info("Wake word ACCEPTED - starting recording")
        SoundService.play_start_sound()
        self._recognized_label.setText("Wake word detected! Listening...")
        self._audio_service.start_recording(auto_stop=True)
        self._voice_button.set_recording_state(True)
        self._status_bar.set_recording_status(True)

    @Slot()
    def _on_new_session(self) -> None:
        """Create a new session."""
        from ..core.session import get_session_manager

        session = get_session_manager()
        session.regenerate()
        self._output_display.clear()
        self._recognized_label.setText("New session started")
        self._status_bar.show_message("New session started")

    @Slot()
    def _on_theme_toggle(self) -> None:
        """Toggle theme."""
        theme_manager = get_theme_manager()
        new_theme = theme_manager.toggle_theme()
        self._status_bar.set_theme(new_theme)

    def _apply_theme(self, theme: str) -> None:
        """Apply a specific theme."""
        theme_manager = get_theme_manager()
        theme_manager.apply_theme(theme)
        self._status_bar.set_theme(theme)

    @Slot()
    def _on_settings_clicked(self) -> None:
        """Show settings dialog."""
        # TODO: Implement settings dialog
        self._status_bar.show_message("Settings coming soon...")

    @Slot(bool)
    def _toggle_always_on_top(self, checked: bool) -> None:
        """Toggle always on top."""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def _show_about(self) -> None:
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About Sombra Desktop",
            "<h2>Sombra Desktop</h2>"
            "<p>Voice-enabled AI Assistant</p>"
            "<p>Version 0.1.0</p>"
            "<br>"
            "<p>A desktop client for interacting with Sombra AI using voice.</p>",
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close."""
        # Clean up services
        if self._wakeword_service:
            self._wakeword_service.cleanup()
        self._audio_service.cleanup()
        self._whisper_service.cleanup()
        self._sombra_service.cleanup()
        self._hotkey_service.cleanup()

        # Stop async bridge
        bridge = get_async_bridge()
        bridge.stop()

        event.accept()
