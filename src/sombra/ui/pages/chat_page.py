"""Chat page - main voice and text chat interface with history."""

import logging
import time

from PySide6.QtCore import Qt, Slot, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    CaptionLabel,
    PrimaryPushButton,
    LineEdit,
    TransparentToolButton,
    FluentIcon,
)

from ..components.voice_button import FluentVoiceButton
from ..components.chat_bubble import ChatBubble, StreamingBubble
from ..components.status_card import ConnectionStatusCard

from ...data.models import Conversation
from ...data.chat_repository import ChatRepository

from ...services.audio_service import AudioService
from ...services.whisper_service import WhisperService
from ...services.sombra_service import SombraService
from ...services.hotkey_service import HotkeyService
from ...services.sound_service import SoundService
from ...services.wakeword_service import WakeWordService
from ...services.tts_service import TtsService

logger = logging.getLogger(__name__)


class ChatPage(QWidget):
    """Main chat interface with voice input and history.

    Combines:
    - Collapsible sidebar with chat history
    - Voice button for recording
    - Text input for typing
    - Chat bubbles for messages
    - Connection status indicator
    - SQLite persistence
    """

    # Signals for thread-safe UI updates from async code
    _sessions_loaded = Signal(list)  # sessions data
    _session_messages_loaded = Signal(str, list)  # session_id, messages

    def __init__(self, services: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("chatPage")

        # Store services
        self._audio: AudioService = services["audio"]
        self._whisper: WhisperService = services["whisper"]
        self._sombra: SombraService = services["sombra"]
        self._hotkey: HotkeyService = services["hotkey"]
        self._wakeword: WakeWordService | None = services.get("wakeword")

        # TTS service
        self._tts = TtsService()
        self._tts.audio_ready.connect(self._on_tts_audio_ready)
        self._tts.synthesis_error.connect(self._on_tts_error)
        self._current_tts_bubble: ChatBubble | None = None  # Track bubble for caching

        # Wake word cooldown
        self._last_recording_end_time: float = 0
        self._wake_word_cooldown = 3.0

        # Chat history (UI widgets)
        self._messages: list[QWidget] = []

        # Database
        self._repository = ChatRepository()
        self._current_conversation: Conversation | None = None
        self._pending_user_message: str | None = None

        self._setup_ui()
        self._connect_signals()

        # Load conversations and check connection
        self._load_conversations()
        self._sombra.check_connection_async()

    def _setup_ui(self) -> None:
        """Build the chat interface with sidebar."""
        # Main horizontal layout: sidebar + chat area
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (session list from API)
        from ..components.session_list_widget import SessionListWidget
        self._session_list = SessionListWidget()
        self._session_list.setMaximumWidth(300)
        main_layout.addWidget(self._session_list)

        # Chat area
        chat_widget = self._create_chat_area()
        main_layout.addWidget(chat_widget, 1)

    def _create_chat_area(self) -> QWidget:
        """Create the main chat area (scrollable)."""
        # Scroll area wrapper
        scroll_area = ScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container widget
        container = QWidget()
        container.setObjectName("chatContainer")
        scroll_area.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(8)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Connection status
        self._status_card = ConnectionStatusCard()
        layout.addWidget(self._status_card)

        # Chat area
        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setSpacing(6)
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

        # Store scroll area reference for scrolling
        self._scroll_area = scroll_area

        return scroll_area

    def _create_header(self) -> QWidget:
        """Create header with title and actions."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # History toggle button
        self._history_btn = TransparentToolButton(FluentIcon.MENU)
        self._history_btn.setToolTip("Show history")
        self._history_btn.clicked.connect(self._toggle_sidebar)
        layout.addWidget(self._history_btn)

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
        clear_btn.clicked.connect(self._clear_current_chat)
        layout.addWidget(clear_btn)

        # New chat button
        new_btn = TransparentToolButton(FluentIcon.ADD)
        new_btn.setToolTip("New chat")
        new_btn.clicked.connect(self._new_conversation)
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
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)

        # Text input
        self._text_input = LineEdit()
        self._text_input.setPlaceholderText("Type a message...")
        self._text_input.setClearButtonEnabled(True)
        self._text_input.returnPressed.connect(self._on_text_submitted)
        layout.addWidget(self._text_input, 1)

        # Send button
        self._send_btn = PrimaryPushButton("Send")
        self._send_btn.setFixedWidth(90)
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

        # Session list signals
        self._session_list.session_selected.connect(self._on_session_selected)
        self._session_list.new_session_requested.connect(self._new_conversation)
        self._session_list.session_deleted.connect(self._on_session_deleted)

        # Internal signals for thread-safe UI updates
        self._sessions_loaded.connect(self._on_sessions_loaded)
        self._session_messages_loaded.connect(self._on_session_messages_loaded)

    # ===== History / Persistence =====

    def _load_conversations(self) -> None:
        """Load sessions from API."""
        async def load_sessions() -> None:
            try:
                sessions = await self._sombra.get_sessions(limit=50)
                # Emit signal to update UI in main thread
                self._sessions_loaded.emit(sessions)
            except Exception as e:
                print(f"Failed to load sessions: {e}")

        from ...core.async_bridge import get_async_bridge
        bridge = get_async_bridge()
        bridge.run_coroutine(load_sessions())

    @Slot(list)
    def _on_sessions_loaded(self, sessions: list[dict]) -> None:
        """Handle sessions loaded from API (runs in main thread)."""
        self._session_list.set_sessions(sessions)

        # Load most recent session if exists
        if sessions:
            session_id = sessions[0].get("id", "")
            if session_id:
                self._on_session_selected(session_id)

    async def _load_session(self, session_id: str) -> None:
        """Load a session from API and display its messages."""
        try:
            # Get session messages from API
            messages = await self._sombra.get_session_messages(session_id, limit=100)

            # Update current session ID
            from ...core.session import get_session_manager
            session = get_session_manager()
            session.set_session_id(session_id)

            # Emit signal to update UI in main thread
            self._session_messages_loaded.emit(session_id, messages)

        except Exception as e:
            print(f"Failed to load session {session_id}: {e}")

    @Slot(str, list)
    def _on_session_messages_loaded(self, session_id: str, messages: list[dict]) -> None:
        """Handle session messages loaded from API (runs in main thread)."""
        # Clear current UI
        self._clear_chat_ui()

        # Display messages
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            bubble = ChatBubble(content, is_user=(role == "user"))
            # Connect play/stop buttons for Sombra messages
            if role == "assistant":
                bubble.play_requested.connect(self._on_replay_requested)
                bubble.play_audio.connect(self._on_play_cached_audio)
                bubble.stop_requested.connect(self._on_stop_requested)
            self._add_message_widget(bubble)

    def _load_conversation(self, conversation_id: str) -> None:
        """Load a conversation and display its messages."""
        conv = self._repository.get_conversation(conversation_id)
        if not conv:
            return

        self._current_conversation = conv

        # Clear current UI
        self._clear_chat_ui()

        # Display messages
        for msg in conv.messages:
            bubble = ChatBubble(msg.content, is_user=(msg.role == "user"))
            # Connect play/stop buttons for Sombra messages
            if msg.role == "assistant":
                bubble.play_requested.connect(self._on_replay_requested)
                bubble.play_audio.connect(self._on_play_cached_audio)
                bubble.stop_requested.connect(self._on_stop_requested)
            self._add_message_widget(bubble)

    def _ensure_conversation(self) -> Conversation:
        """Ensure a conversation exists, create if needed."""
        if self._current_conversation is None:
            from ...core.session import get_session_manager
            session = get_session_manager()

            self._current_conversation = self._repository.create_conversation(
                session_id=session.session_id
            )
            self._load_conversations()
            self._sidebar.set_active_conversation(self._current_conversation.id)

        return self._current_conversation

    def _generate_title(self, first_message: str) -> str:
        """Generate title from first message."""
        # First 50 chars or until newline
        title = first_message[:50].split('\n')[0].strip()
        if len(first_message) > 50:
            title += "..."
        return title

    @Slot()
    def _new_conversation(self) -> None:
        """Start a new conversation."""
        async def create_new() -> None:
            try:
                from ...core.session import get_session_manager
                session = get_session_manager()
                session.regenerate()

                # Create new session via API
                await self._sombra.create_session(session.session_id)

                # Clear UI and reload sessions
                self._clear_chat_ui()
                self._load_conversations()

                self._status_label.setText("New chat started")
                self._status_label.setStyleSheet("color: #888888;")
            except Exception as e:
                print(f"Failed to create new session: {e}")

        from ...core.async_bridge import get_async_bridge
        bridge = get_async_bridge()
        bridge.run_coroutine(create_new())

    @Slot(str)
    def _on_session_selected(self, session_id: str) -> None:
        """Handle session selection from sidebar."""
        async def load() -> None:
            await self._load_session(session_id)

        from ...core.async_bridge import get_async_bridge
        bridge = get_async_bridge()
        bridge.run_coroutine(load())

    @Slot(str)
    def _on_conversation_selected(self, conversation_id: str) -> None:
        """Handle conversation selection from sidebar."""
        if self._current_conversation and self._current_conversation.id == conversation_id:
            return

        self._load_conversation(conversation_id)

        # Update session to match conversation's session_id
        if self._current_conversation:
            from ...core.session import get_session_manager
            session = get_session_manager()
            session.set_session_id(self._current_conversation.session_id)

    @Slot(str, str)
    def _on_conversation_renamed(self, conversation_id: str, new_title: str) -> None:
        """Handle conversation rename."""
        self._repository.update_conversation_title(conversation_id, new_title)
        self._load_conversations()

    @Slot(str)
    def _on_session_deleted(self, session_id: str) -> None:
        """Handle session deletion."""
        async def delete() -> None:
            try:
                await self._sombra.delete_session(session_id)
                self._session_list.remove_session(session_id)

                # Clear chat if deleted session was active
                from ...core.session import get_session_manager
                session = get_session_manager()
                if session.session_id == session_id:
                    self._clear_chat_ui()
                    # Create new session
                    session.regenerate()
            except Exception as e:
                print(f"Failed to delete session {session_id}: {e}")

        from ...core.async_bridge import get_async_bridge
        bridge = get_async_bridge()
        bridge.run_coroutine(delete())

    @Slot(str)
    def _on_conversation_deleted(self, conversation_id: str) -> None:
        """Handle conversation deletion."""
        self._repository.delete_conversation(conversation_id)

        # If deleted current, clear and load another
        if self._current_conversation and self._current_conversation.id == conversation_id:
            self._current_conversation = None
            self._clear_chat_ui()

        self._load_conversations()

    @Slot()
    def _toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self._session_list.setVisible(not self._session_list.isVisible())

    @Slot()
    def _clear_current_chat(self) -> None:
        """Clear current chat (UI only, keeps history)."""
        self._clear_chat_ui()
        self._status_label.setText("Chat cleared")
        self._status_label.setStyleSheet("color: #888888;")

    def _clear_chat_ui(self) -> None:
        """Clear chat UI widgets."""
        for msg in self._messages:
            msg.deleteLater()
        self._messages.clear()

        self._streaming_bubble.clear()
        self._streaming_bubble.hide()

    def _add_message_widget(self, bubble: QWidget) -> None:
        """Add a message bubble widget to the chat."""
        self._messages.append(bubble)

        # Insert before the stretch
        index = self._chat_layout.count() - 2  # Before stretch and streaming bubble
        self._chat_layout.insertWidget(index, bubble)

        # Scroll to bottom (delayed to ensure layout is updated)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        """Scroll chat to bottom."""
        scrollbar = self._scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ===== Voice / Text Handlers =====

    @Slot()
    def _on_recording_started(self) -> None:
        """Handle recording start."""
        # Stop any TTS playback (barge-in)
        SoundService.stop_playback()

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
        # Add user bubble to UI
        user_bubble = ChatBubble(text, is_user=True)
        self._add_message_widget(user_bubble)

        # Clear input
        self._text_input.clear()

        # Start streaming
        self._streaming_bubble.start_streaming()
        self._streaming_bubble.show()

        # Send to Sombra (backend saves messages)
        self._sombra.send_chat_async(text)

    @Slot(str)
    def _on_query_sent(self, query: str) -> None:
        """Handle query sent."""
        self._status_label.setText("Waiting for response...")
        self._status_label.setStyleSheet("color: #888888;")

    @Slot(str)
    def _on_thinking_update(self, thinking: str) -> None:
        """Handle thinking update - show in status and streaming bubble."""
        # Update status label with thinking
        self._status_label.setText(f"💭 {thinking[:80]}..." if len(thinking) > 80 else f"💭 {thinking}")
        self._status_label.setStyleSheet("color: #888888; font-style: italic;")

    @Slot(str)
    def _on_response_received(self, response: str) -> None:
        """Handle response chunk received."""
        self._streaming_bubble.set_content(response)

    @Slot()
    def _on_stream_completed(self) -> None:
        """Handle stream completed."""
        # Get response content
        content = self._streaming_bubble.get_content()

        if content:
            # Convert streaming bubble to permanent bubble
            sombra_bubble = ChatBubble(content, is_user=False)
            sombra_bubble.play_requested.connect(self._on_replay_requested)
            sombra_bubble.play_audio.connect(self._on_play_cached_audio)
            sombra_bubble.stop_requested.connect(self._on_stop_requested)
            self._add_message_widget(sombra_bubble)

            # Synthesize and play response (track bubble for caching)
            if self._tts.is_enabled:
                self._current_tts_bubble = sombra_bubble
                self._tts.synthesize_async(content)

        self._streaming_bubble.hide()
        self._streaming_bubble.clear()
        self._pending_user_message = None

        self._status_label.setText("Click to record, click again to send")
        self._status_label.setStyleSheet("color: #888888;")

    @Slot(bytes)
    def _on_tts_audio_ready(self, audio: bytes) -> None:
        """Handle TTS audio ready - play and cache it."""
        logger.info(f"TTS audio ready: {len(audio)} bytes")
        # Cache audio in the bubble
        if self._current_tts_bubble is not None:
            self._current_tts_bubble.set_audio(audio)
            self._current_tts_bubble = None
        SoundService.play_audio(audio)

    @Slot(str)
    def _on_tts_error(self, error: str) -> None:
        """Handle TTS error."""
        logger.error(f"TTS error: {error}")

    @Slot(str)
    def _on_replay_requested(self, text: str) -> None:
        """Handle replay button click - synthesize TTS and cache."""
        if self._tts.is_enabled:
            # Track which bubble requested TTS for caching
            bubble = self.sender()
            if isinstance(bubble, ChatBubble):
                self._current_tts_bubble = bubble
            self._tts.synthesize_async(text)

    @Slot(bytes)
    def _on_play_cached_audio(self, audio: bytes) -> None:
        """Handle play cached audio directly."""
        SoundService.play_audio(audio)

    @Slot()
    def _on_stop_requested(self) -> None:
        """Handle stop button click - stop TTS playback."""
        SoundService.stop_playback()

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
        # Check cooldown
        elapsed = time.time() - self._last_recording_end_time
        if elapsed < self._wake_word_cooldown:
            logger.info("Wake word IGNORED (cooldown)")
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
