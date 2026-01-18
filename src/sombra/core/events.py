"""EventHub - Centralized Qt signal hub for decoupled component communication."""

from PySide6.QtCore import QObject, Signal


class EventHub(QObject):
    """Centralized event bus using Qt signals.

    All components communicate through this hub, enabling loose coupling
    and making it easy to add/remove functionality.

    Usage:
        hub = EventHub()
        hub.recording_started.connect(on_recording_started)
        hub.recording_started.emit()
    """

    # ============== Audio Events ==============
    # Emitted when audio recording begins
    recording_started = Signal()

    # Emitted when recording stops, carries raw audio bytes
    recording_stopped = Signal(bytes)

    # Emitted periodically during recording with audio level (0.0 - 1.0)
    audio_level_changed = Signal(float)

    # Emitted on audio capture error
    audio_error = Signal(str)

    # ============== Transcription Events ==============
    # Emitted when transcription request is sent to Whisper
    transcription_started = Signal()

    # Emitted when transcription completes successfully
    transcription_completed = Signal(str)

    # Emitted on transcription error
    transcription_error = Signal(str)

    # ============== Sombra API Events ==============
    # Emitted when query is sent to Sombra
    query_sent = Signal(str)

    # Emitted for each streaming chunk received
    stream_chunk_received = Signal(str)

    # Emitted when thinking update is received from SSE
    thinking_update = Signal(str)

    # Emitted when streaming response is complete
    stream_completed = Signal()

    # Emitted on API error
    api_error = Signal(str)

    # Emitted with full response after stream completes
    response_received = Signal(str)

    # ============== Connection Events ==============
    # Emitted when connection to backend is established
    connected = Signal()

    # Emitted when connection to backend is lost
    disconnected = Signal()

    # Emitted with connection status message
    connection_status_changed = Signal(str)

    # ============== UI Events ==============
    # Emitted when theme changes ('dark' or 'light')
    theme_changed = Signal(str)

    # Emitted with status bar message
    status_update = Signal(str)

    # Emitted when settings are changed
    settings_changed = Signal()

    # Emitted to request app quit
    quit_requested = Signal()

    # Emitted to show/hide main window
    show_window_requested = Signal()
    hide_window_requested = Signal()

    # ============== Hotkey Events ==============
    # Emitted when global hotkey is pressed
    hotkey_pressed = Signal(str)

    # Emitted when global hotkey is released
    hotkey_released = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)


# Global event hub instance
_event_hub: EventHub | None = None


def get_event_hub() -> EventHub:
    """Get the global EventHub instance."""
    global _event_hub
    if _event_hub is None:
        _event_hub = EventHub()
    return _event_hub


def init_event_hub(parent: QObject | None = None) -> EventHub:
    """Initialize or reinitialize the EventHub."""
    global _event_hub
    _event_hub = EventHub(parent)
    return _event_hub
