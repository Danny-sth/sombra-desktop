"""Toggle voice button widget - click to start/stop recording."""

from PySide6.QtCore import Property, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QPushButton, QWidget


class VoiceButton(QPushButton):
    """Toggle recording button with visual feedback.

    Click once to start recording, click again to stop and send.
    Features:
    - Visual recording state indication
    - Audio level visualization (pulsing effect)
    - Smooth animations
    """

    # Signals
    recording_started = Signal()
    recording_stopped = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_recording = False
        self._audio_level = 0.0

        # Setup widget
        self.setObjectName("voiceButton")
        self.setText("🎤")
        self.setToolTip("Click to start/stop recording")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Setup pulse animation for recording state
        self._pulse_animation = QPropertyAnimation(self, b"audioLevel")
        self._pulse_animation.setDuration(500)
        self._pulse_animation.setLoopCount(-1)  # Infinite loop

        # Connect clicked signal for toggle behavior
        self.clicked.connect(self._on_clicked)

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    def _get_audio_level(self) -> float:
        """Get current audio level."""
        return self._audio_level

    def _set_audio_level(self, level: float) -> None:
        """Set audio level and update visual feedback."""
        self._audio_level = max(0.0, min(1.0, level))
        self._update_style()

    # Qt property for animation
    audioLevel = Property(float, _get_audio_level, _set_audio_level)

    def _on_clicked(self) -> None:
        """Handle button click - toggle recording state."""
        if self._is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def set_recording_state(self, is_recording: bool) -> None:
        """Update recording state and visual appearance.

        Args:
            is_recording: Whether recording is active.
        """
        self._is_recording = is_recording
        self.setProperty("recording", is_recording)

        if is_recording:
            self.setText("⏹️")
            self.setToolTip("Click to stop and send")
            self._start_pulse()
        else:
            self.setText("🎤")
            self.setToolTip("Click to start recording")
            self._stop_pulse()

        # Force style recalculation
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_audio_level(self, level: float) -> None:
        """Update audio level for visual feedback.

        Args:
            level: Audio level from 0.0 to 1.0.
        """
        if self._is_recording:
            self._audio_level = level
            self._update_style()

    def _update_style(self) -> None:
        """Update visual style based on audio level."""
        if not self._is_recording:
            return

        # Adjust border width based on audio level
        # This creates a "breathing" effect
        border_width = 3 + int(self._audio_level * 4)  # 3-7px
        self.setStyleSheet(
            f"""
            QPushButton#voiceButton {{
                border-width: {border_width}px;
            }}
            """
        )

    def _start_pulse(self) -> None:
        """Start the pulse animation."""
        self._pulse_animation.setStartValue(0.3)
        self._pulse_animation.setEndValue(1.0)
        self._pulse_animation.start()

    def _stop_pulse(self) -> None:
        """Stop the pulse animation."""
        self._pulse_animation.stop()
        self._audio_level = 0.0
        self.setStyleSheet("")  # Reset to default style

    def start_recording(self) -> None:
        """Start recording."""
        if not self._is_recording:
            self.set_recording_state(True)
            self.recording_started.emit()

    def stop_recording(self) -> None:
        """Stop recording."""
        if self._is_recording:
            self.set_recording_state(False)
            self.recording_stopped.emit()

    def toggle_recording(self) -> None:
        """Toggle recording state (for hotkey support)."""
        if self._is_recording:
            self.stop_recording()
        else:
            self.start_recording()
