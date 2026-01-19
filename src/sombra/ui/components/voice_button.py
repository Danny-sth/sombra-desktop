"""Fluent Design voice button with animations."""

from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget


class FluentVoiceButton(QWidget):
    """Circular voice recording button with Fluent Design animations.

    Features:
    - Pulsing glow animation when recording
    - Audio level visualization
    - Smooth state transitions
    - Click to toggle recording
    """

    # Signals
    recording_started = Signal()
    recording_stopped = Signal()

    # Constants
    BUTTON_SIZE = 80
    WIDGET_SIZE = 120  # Extra space for glow effect

    # Colors (Sombra theme)
    COLOR_IDLE = QColor("#4ecca3")  # Green
    COLOR_RECORDING = QColor("#e94560")  # Pink/Red
    COLOR_HOVER = QColor("#5fd9b0")  # Lighter green

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_recording = False
        self._is_hovered = False
        self._audio_level = 0.0
        self._pulse_value = 0.0
        self._glow_opacity = 0.0

        # Setup widget
        self.setFixedSize(self.WIDGET_SIZE, self.WIDGET_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to start/stop recording")

        # Pulse animation (for recording state)
        self._pulse_anim = QPropertyAnimation(self, b"pulseValue")
        self._pulse_anim.setDuration(1000)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Glow fade animation
        self._glow_anim = QPropertyAnimation(self, b"glowOpacity")
        self._glow_anim.setDuration(200)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # Qt Properties for animations
    def _get_pulse_value(self) -> float:
        return self._pulse_value

    def _set_pulse_value(self, value: float) -> None:
        self._pulse_value = value
        self.update()

    pulseValue = Property(float, _get_pulse_value, _set_pulse_value)

    def _get_glow_opacity(self) -> float:
        return self._glow_opacity

    def _set_glow_opacity(self, value: float) -> None:
        self._glow_opacity = value
        self.update()

    glowOpacity = Property(float, _get_glow_opacity, _set_glow_opacity)

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    def paintEvent(self, event) -> None:
        """Custom paint for the button."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        base_radius = self.BUTTON_SIZE // 2

        # Draw glow effect when recording
        if self._is_recording:
            self._draw_recording_glow(painter, center, base_radius)
        elif self._glow_opacity > 0:
            self._draw_idle_glow(painter, center, base_radius)

        # Draw main button
        self._draw_button(painter, center, base_radius)

        # Draw icon
        self._draw_icon(painter, center)

    def _draw_recording_glow(self, painter: QPainter, center, radius: int) -> None:
        """Draw animated glow when recording."""
        # Pulsing outer glow
        glow_radius = radius + 10 + self._pulse_value * 15
        glow_color = QColor(self.COLOR_RECORDING)
        glow_color.setAlpha(int(80 - self._pulse_value * 40))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(center, int(glow_radius), int(glow_radius))

        # Inner glow (audio level based)
        if self._audio_level > 0:
            inner_radius = radius + 5 + self._audio_level * 10
            inner_color = QColor(self.COLOR_RECORDING)
            inner_color.setAlpha(int(100 * self._audio_level))
            painter.setBrush(QBrush(inner_color))
            painter.drawEllipse(center, int(inner_radius), int(inner_radius))

    def _draw_idle_glow(self, painter: QPainter, center, radius: int) -> None:
        """Draw subtle glow on hover."""
        glow_radius = radius + 8
        glow_color = QColor(self.COLOR_IDLE)
        glow_color.setAlpha(int(50 * self._glow_opacity))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(center, glow_radius, glow_radius)

    def _draw_button(self, painter: QPainter, center, radius: int) -> None:
        """Draw the main button circle."""
        # Button color
        if self._is_recording:
            color = self.COLOR_RECORDING
        elif self._is_hovered:
            color = self.COLOR_HOVER
        else:
            color = self.COLOR_IDLE

        # Shadow (subtle)
        shadow_color = QColor(0, 0, 0, 40)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.drawEllipse(center.x() + 2, center.y() + 2, radius * 2 - 4, radius * 2 - 4)

        # Main circle
        painter.setBrush(QBrush(color))
        painter.drawEllipse(center, radius, radius)

        # Border
        border_color = QColor(255, 255, 255, 30)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius - 1, radius - 1)

    def _draw_icon(self, painter: QPainter, center) -> None:
        """Draw microphone or stop icon."""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255)))

        if self._is_recording:
            # Stop icon (square)
            size = 22
            painter.drawRoundedRect(
                center.x() - size // 2,
                center.y() - size // 2,
                size, size, 4, 4
            )
        else:
            # Microphone icon (simplified)
            # Mic body
            mic_width = 14
            mic_height = 24
            mic_x = center.x() - mic_width // 2
            mic_y = center.y() - mic_height // 2 - 4
            painter.drawRoundedRect(mic_x, mic_y, mic_width, mic_height, 7, 7)

            # Mic stand arc
            painter.setPen(QPen(QColor(255, 255, 255), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            arc_y = center.y() + 6
            painter.drawArc(center.x() - 12, arc_y - 8, 24, 16, 0, -180 * 16)

            # Mic stand line
            painter.drawLine(center.x(), arc_y, center.x(), arc_y + 10)

    def enterEvent(self, event) -> None:
        """Handle mouse enter."""
        self._is_hovered = True
        if not self._is_recording:
            self._glow_anim.setStartValue(self._glow_opacity)
            self._glow_anim.setEndValue(1.0)
            self._glow_anim.start()
        self.update()

    def leaveEvent(self, event) -> None:
        """Handle mouse leave."""
        self._is_hovered = False
        if not self._is_recording:
            self._glow_anim.setStartValue(self._glow_opacity)
            self._glow_anim.setEndValue(0.0)
            self._glow_anim.start()
        self.update()

    def mousePressEvent(self, event) -> None:
        """Handle mouse click - toggle recording."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_recording()

    def set_recording_state(self, is_recording: bool) -> None:
        """Update recording state and visual appearance.

        Args:
            is_recording: Whether recording is active.
        """
        self._is_recording = is_recording

        if is_recording:
            self._pulse_anim.start()
            self.setToolTip("Click to stop and send")
        else:
            self._pulse_anim.stop()
            self._pulse_value = 0.0
            self._audio_level = 0.0
            self.setToolTip("Click to start recording")

        self.update()

    def set_audio_level(self, level: float) -> None:
        """Update audio level for visual feedback.

        Args:
            level: Audio level from 0.0 to 1.0.
        """
        if self._is_recording:
            self._audio_level = max(0.0, min(1.0, level))
            self.update()

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
