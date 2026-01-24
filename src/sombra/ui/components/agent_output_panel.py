"""Agent output panel - Real-time streaming agent logs."""

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QVBoxLayout, QWidget

from qfluentwidgets import (
    BodyLabel,
    PlainTextEdit,
    SimpleCardWidget,
    StrongBodyLabel,
)


class AgentOutputPanel(SimpleCardWidget):
    """Panel showing real-time agent output logs."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header
        header = StrongBodyLabel("Agent Output (Real-time)")
        layout.addWidget(header)

        # Log viewer
        self._log_viewer = PlainTextEdit()
        self._log_viewer.setReadOnly(True)
        self._log_viewer.setMaximumBlockCount(500)  # Limit to last 500 lines
        self._log_viewer.setPlaceholderText("Agent output will appear here when tasks are running...")
        self._log_viewer.setMinimumHeight(200)
        
        # Dark background for logs
        self._log_viewer.setStyleSheet("""
            PlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self._log_viewer)

    @Slot(str, str)
    def append_output(self, agent: str, message: str) -> None:
        """Append agent output to log viewer.
        
        Args:
            agent: Agent name (coder, deploy, qa)
            message: Output message
        """
        # Format: [AGENT] message
        emoji = {
            "coder": "💻",
            "deploy": "🚀",
            "qa": "🧪",
        }.get(agent.lower(), "🤖")
        
        formatted = f"{emoji} [{agent.upper()}] {message}"
        self._log_viewer.appendPlainText(formatted)
        
        # Auto-scroll to bottom
        cursor = self._log_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log_viewer.setTextCursor(cursor)

    def clear(self) -> None:
        """Clear all logs."""
        self._log_viewer.clear()
