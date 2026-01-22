"""Text input widget for manual text entry."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget


class TextInput(QWidget):
    """Text input area with send button.

    Features:
    - Single-line input with Enter to send
    - Send button
    - Displays transcribed text from voice input
    """

    # Emitted when user submits text (Enter or click Send)
    text_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Text input field
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("Type a message or use voice input...")
        self._input_field.setClearButtonEnabled(True)

        # Send button
        self._send_button = QPushButton("Send")
        self._send_button.setProperty("primary", True)
        self._send_button.setFixedWidth(80)

        layout.addWidget(self._input_field, 1)
        layout.addWidget(self._send_button)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._send_button.clicked.connect(self._on_send_clicked)
        self._input_field.returnPressed.connect(self._on_send_clicked)
        self._input_field.textChanged.connect(self._on_text_changed)

    def _on_send_clicked(self) -> None:
        """Handle send button click or Enter press."""
        text = self._input_field.text().strip()
        if text:
            self.text_submitted.emit(text)
            self._input_field.clear()

    def _on_text_changed(self, text: str) -> None:
        """Handle text changes."""
        # Enable/disable send button based on content
        self._send_button.setEnabled(bool(text.strip()))

    def set_text(self, text: str) -> None:
        """Set the input text (e.g., from voice transcription).

        Args:
            text: Text to set.
        """
        self._input_field.setText(text)
        self._input_field.setFocus()
        # Move cursor to end
        self._input_field.setCursorPosition(len(text))

    def get_text(self) -> str:
        """Get current input text.

        Returns:
            Current text.
        """
        return self._input_field.text()

    def clear(self) -> None:
        """Clear the input field."""
        self._input_field.clear()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the input.

        Args:
            enabled: Whether to enable.
        """
        self._input_field.setEnabled(enabled)
        self._send_button.setEnabled(enabled and bool(self._input_field.text().strip()))

    def set_placeholder(self, text: str) -> None:
        """Set placeholder text.

        Args:
            text: Placeholder text.
        """
        self._input_field.setPlaceholderText(text)

    def focus(self) -> None:
        """Set focus to the input field."""
        self._input_field.setFocus()
