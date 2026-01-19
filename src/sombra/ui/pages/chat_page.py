"""Chat page - main voice and text chat interface."""

import time

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    BodyLabel,
    CaptionLabel,
    PrimaryPushButton,
    LineEdit,
    TransparentToolButton,
    FluentIcon,
    isDarkTheme,
)

from ..components.voice_button import FluentVoiceButton
from ..components.chat_bubble import ChatBubble, ThinkingBubble, StreamingBubble
from ..components.status_card import ConnectionStatusCard

from ...services.audio_service import AudioService
from ...services.whisper_service import WhisperService
from ...services.sombra_service import SombraService
from ...services.hotkey_service import HotkeyService
from ...services.sound_service import SoundService
from ...services.wakeword_service import WakeWordService


class ChatPage(ScrollArea):
    """Main chat interface with voice input.

    Combines:
    - Voice button for recording
    - Text input for typing
    - Chat bubbles for messages
    - Connection status indicator
    """

    def __init__(self, services: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("chatPage")

        # Store services
        self._audio: AudioService = services["audio"]
        self._whisper: WhisperService = services["whisper"]
        self._sombra: SombraService = services["sombra"]
        self._hotkey: HotkeyService = services["hotkey"]
        self._wakeword: WakeWordService | None = services.get("wakeword")

        # Wake word cooldown
        self._last_recording_end_time: float = 0
        self._wake_word_cooldown = 3.0

        # Chat history
        self._messages: list[QWidget] = []

        self._setup_ui()
        self._connect_signals()

        # Check connection
        self._sombra.check_connection_async()

    def _setup_ui(self) -> None:
        """Build the chat interface."""
        # Container widget
        self.container = QWidget()
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(36, 20, 36, 20)
        layout.setSpacing(20)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Connection status
        self._status_card = ConnectionStatusCard()
        layout.addWidget(self._status_card)

        # Chat area
        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setSpacing(12)
        self._chat_layout.setContentsMargins(0, 0, 0, 0)
        self._chat_layout.addStretch()
        layout.addWidget(self._chat_container, 1)

        # Current streaming bubble (hidden until streaming)
        self._streaming_bubble = StreamingBubble()
        self._streaming_bubble.hide()
        self._chat_layout.addWidget(self._streaming_bubble)

        # Voice section
        voice_section = self._create_voice_section()
        layout.addWidget(voice_section)

        # Text input section
        input_section = self._create_input_section()
        layout.addWidget(input_section)

    def _create_header(self) -> QWidget:
        """Create header with title and actions."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = TitleLabel("Sombra Chat")
        layout.addWidget(title)

        # Subtitle
        subtitle = CaptionLabel("Voice-enabled AI Assistant")
        subtitle.setStyleSheet("color: #888888;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Clear button
        clear_btn = TransparentToolButton(FluentIcon.DELETE)
        clear_btn.setToolTip("Clear chat")
        clear_btn.clicked.connect(self._clear_chat)
        layout.addWidget(clear_btn)

        # New session button
        new_btn = TransparentToolButton(FluentIcon.ADD)
        new_btn.setToolTip("New session")
        new_btn.clicked.connect(self._new_session)
        layout.addWidget(new_btn)

        return widget

    def _create_voice_section(self) -> QWidget:
        """Create centered voice button section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Voice button
        self._voice_button = FluentVoiceButton()
        layout.addWidget(self._voice_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status label
        self._status_label = CaptionLabel("Click to record, click again to send")
        self._status_label.setStyleSheet("color: #888888;")
        layout.addWidget(self._status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Hotkey hint
        hotkey_label = CaptionLabel("Hotkey: Ctrl+Shift+S")
        hotkey_label.setStyleSheet("color: #666666;")
        layout.addWidget(hotkey_label, alignment=Qt.AlignmentFlag.AlignCenter)

        return widget

    def _create_input_section(self) -> QWidget:
        """Create text input with send button."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Text input
        self._text_input = LineEdit()
        self._text_input.setPlaceholderText("Type a message...")
        self._text_input.setClearButtonEnabled(True)
        self._text_input.returnPressed.connect(self._on_text_submitted)
        layout.addWidget(self._text_input, 1)

        # Send button
        self._send_btn = PrimaryPushButton("Send")
        self._send_btn.setFixedWidth(80)
        self._send_btn.clicked.connect(self._on_text_submitted)
        layout.addWidget(self._send_btn)

        return widget

    def _connect_signals(self) -> None:
        """Connect service signals to UI."""
        # Voice button
        self._voice_button.recording_started.connect(self._on_recording_started)
        self._voice_button.recording_stopped.connect(self._on_recording_stopped)

        # Audio service
        self._audio.audio_level.connect(self._voice_button.set_audio_level)
        self._audio.recording_stopped.connect(self._on_audio_ready)
        self._audio.error.connect(self._on_error)

        # Whisper service
        self._whisper.transcription_started.connect(self._on_transcription_started)
        self._whisper.transcription_completed.connect(self._on_transcription_completed)
        self._whisper.transcription_error.connect(self._on_error)

        # Sombra service
        self._sombra.query_sent.connect(self._on_query_sent)
        self._sombra.thinking_update.connect(self._on_thinking_update)
        self._sombra.response_received.connect(self._on_response_received)
        self._sombra.stream_completed.connect(self._on_stream_completed)
        self._sombra.stream_error.connect(self._on_error)
        self._sombra.connection_status.connect(self._status_card.set_status)

        # Hotkey service
        self._hotkey.hotkey_pressed.connect(self._on_hotkey_pressed)

        # Wake word service
        if self._wakeword:
            self._wakeword.wake_word_detected.connect(self._on_wake_word_detected)
            self._wakeword.error.connect(self._on_error)

    # ===== Event Handlers =====

    @Slot()
    def _on_recording_started(self) -> None:
        """Handle recording start."""
        SoundService.play_start_sound()
        self._audio.start_recording()
        self._status_label.setText("Listening...")
        self._status_label.setStyleSheet("color: #e94560;")

    @Slot()
    def _on_recording_stopped(self) -> None:
        """Handle recording stop."""
        self._audio.stop_recording()
        self._status_label.setText("Processing...")
        self._status_label.setStyleSheet("color: #f9a825;")

    @Slot(bytes)
    def _on_audio_ready(self, audio_data: bytes) -> None:
        """Handle audio data ready for transcription."""
        import logging
        logger = logging.getLogger(__name__)

        SoundService.play_stop_sound()

        # Update UI
        self._voice_button.set_recording_state(False)
        self._status_label.setText("Transcribing...")

        # Set cooldown
        self._last_recording_end_time = time.time()
        logger.info(f"Recording ended. Cooldown set for {self._wake_word_cooldown}s")

        if audio_data:
            self._whisper.transcribe_async(audio_data)

    @Slot()
    def _on_transcription_started(self) -> None:
        """Handle transcription start."""
        self._status_label.setText("Transcribing...")

    @Slot(str)
    def _on_transcription_completed(self, text: str) -> None:
        """Handle transcription completed."""
        self._status_label.setText(f'"{text}"')
        self._status_label.setStyleSheet("color: #888888;")
        self._text_input.setText(text)

        # Auto-send
        if text.strip():
            self._send_query(text)

    @Slot()
    def _on_text_submitted(self) -> None:
        """Handle text input submission."""
        text = self._text_input.text().strip()
        if text:
            self._send_query(text)

    def _send_query(self, text: str) -> None:
        """Send query to Sombra."""
        # Add user bubble
        user_bubble = ChatBubble(text, is_user=True)
        self._add_message(user_bubble)

        # Clear input
        self._text_input.clear()

        # Start streaming
        self._streaming_bubble.start_streaming()
        self._streaming_bubble.show()

        # Send to Sombra
        self._sombra.send_chat_async(text)

    @Slot(str)
    def _on_query_sent(self, query: str) -> None:
        """Handle query sent."""
        self._status_label.setText("Waiting for response...")
        self._status_label.setStyleSheet("color: #888888;")

    @Slot(str)
    def _on_thinking_update(self, thinking: str) -> None:
        """Handle thinking update."""
        # Could show thinking indicator
        pass

    @Slot(str)
    def _on_response_received(self, response: str) -> None:
        """Handle response chunk received."""
        self._streaming_bubble.set_content(response)

    @Slot()
    def _on_stream_completed(self) -> None:
        """Handle stream completed."""
        # Convert streaming bubble to permanent bubble
        content = self._streaming_bubble.get_content()
        if content:
            sombra_bubble = ChatBubble(content, is_user=False)
            self._add_message(sombra_bubble)

        self._streaming_bubble.hide()
        self._streaming_bubble.clear()

        self._status_label.setText("Click to record, click again to send")
        self._status_label.setStyleSheet("color: #888888;")

    @Slot(str)
    def _on_error(self, error: str) -> None:
        """Handle errors."""
        self._status_label.setText(f"Error: {error}")
        self._status_label.setStyleSheet("color: #e94560;")
        self._streaming_bubble.hide()

    @Slot(str)
    def _on_hotkey_pressed(self, name: str) -> None:
        """Handle global hotkey press."""
        if name == "push_to_talk":
            self._voice_button.toggle_recording()

    @Slot()
    def _on_wake_word_detected(self) -> None:
        """Handle wake word detection."""
        import logging
        logger = logging.getLogger(__name__)

        # Check cooldown
        elapsed = time.time() - self._last_recording_end_time
        if elapsed < self._wake_word_cooldown:
            logger.info(f"Wake word IGNORED (cooldown)")
            return

        if self._voice_button.is_recording:
            logger.info("Wake word IGNORED (already recording)")
            return

        logger.info("Wake word ACCEPTED - starting recording")
        SoundService.play_start_sound()
        self._status_label.setText("Wake word detected! Listening...")
        self._status_label.setStyleSheet("color: #4ecca3;")
        self._audio.start_recording(auto_stop=True)
        self._voice_button.set_recording_state(True)

    def _add_message(self, bubble: QWidget) -> None:
        """Add a message bubble to the chat."""
        self._messages.append(bubble)

        # Insert before the stretch
        index = self._chat_layout.count() - 2  # Before stretch and streaming bubble
        self._chat_layout.insertWidget(index, bubble)

        # Scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    @Slot()
    def _clear_chat(self) -> None:
        """Clear all chat messages."""
        for msg in self._messages:
            msg.deleteLater()
        self._messages.clear()

        self._streaming_bubble.clear()
        self._streaming_bubble.hide()

        self._status_label.setText("Chat cleared")
        self._status_label.setStyleSheet("color: #888888;")

    @Slot()
    def _new_session(self) -> None:
        """Start a new session."""
        from ...core.session import get_session_manager

        session = get_session_manager()
        session.regenerate()
        self._clear_chat()
        self._status_label.setText("New session started")
