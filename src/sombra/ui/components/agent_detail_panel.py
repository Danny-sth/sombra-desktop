"""Agent detail panel - Detailed view for individual agent."""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    PlainTextEdit,
    PrimaryPushButton,
    PushButton,
    StrongBodyLabel,
    SubtitleLabel,
    TextEdit,
    TitleLabel,
)


class AgentDetailPanel(CardWidget):
    """Panel showing detailed information about a specific agent.
    
    Displays:
    - Agent thinking/reasoning logs
    - Execution logs
    - Additional context input
    - Agent parameters
    """

    # Signals
    context_submitted = Signal(str, str)  # agent_id, context
    closed = Signal()

    def __init__(self, agent_id: str, agent_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        
        self._agent_id = agent_id
        self._agent_name = agent_name
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header with agent name and close button
        header_layout = QHBoxLayout()
        
        self._title = TitleLabel(f"{self._agent_name} Agent Details")
        header_layout.addWidget(self._title)
        
        header_layout.addStretch()
        
        self._close_btn = PushButton("Close")
        self._close_btn.clicked.connect(self._on_close)
        header_layout.addWidget(self._close_btn)
        
        layout.addLayout(header_layout)

        # Agent status info
        self._create_status_section(layout)

        # Thinking logs section
        self._create_thinking_section(layout)

        # Execution logs section
        self._create_logs_section(layout)

        # Additional context section
        self._create_context_section(layout)

    def _create_status_section(self, parent_layout: QVBoxLayout) -> None:
        """Create agent status info section."""
        status_label = SubtitleLabel("Status")
        parent_layout.addWidget(status_label)

        status_row = QHBoxLayout()
        status_row.setSpacing(20)

        self._status_text = BodyLabel("Idle")
        status_row.addWidget(BodyLabel("Current status:"))
        status_row.addWidget(self._status_text)
        
        status_row.addStretch()
        
        self._iterations_text = BodyLabel("0")
        status_row.addWidget(BodyLabel("Iterations:"))
        status_row.addWidget(self._iterations_text)
        
        status_row.addStretch()
        
        self._cost_text = BodyLabel("$0.00")
        status_row.addWidget(BodyLabel("Cost:"))
        status_row.addWidget(self._cost_text)

        parent_layout.addLayout(status_row)

    def _create_thinking_section(self, parent_layout: QVBoxLayout) -> None:
        """Create thinking/reasoning logs section."""
        thinking_label = SubtitleLabel("Agent Reasoning")
        parent_layout.addWidget(thinking_label)

        self._thinking_viewer = PlainTextEdit()
        self._thinking_viewer.setReadOnly(True)
        self._thinking_viewer.setPlaceholderText("Agent thinking will appear here...")
        self._thinking_viewer.setMinimumHeight(200)
        
        # Styling for thinking viewer
        self._thinking_viewer.setStyleSheet("""
            PlainTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        parent_layout.addWidget(self._thinking_viewer)

    def _create_logs_section(self, parent_layout: QVBoxLayout) -> None:
        """Create execution logs section."""
        logs_label = SubtitleLabel("Execution Logs")
        parent_layout.addWidget(logs_label)

        self._logs_viewer = PlainTextEdit()
        self._logs_viewer.setReadOnly(True)
        self._logs_viewer.setPlaceholderText("Agent execution logs will appear here...")
        self._logs_viewer.setMinimumHeight(200)
        
        # Styling for logs viewer
        self._logs_viewer.setStyleSheet("""
            PlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        parent_layout.addWidget(self._logs_viewer)

    def _create_context_section(self, parent_layout: QVBoxLayout) -> None:
        """Create additional context input section."""
        context_label = SubtitleLabel("Additional Context")
        parent_layout.addWidget(context_label)

        help_text = BodyLabel("Provide additional context or instructions for this agent:")
        help_text.setStyleSheet("color: #888888;")
        parent_layout.addWidget(help_text)

        self._context_input = TextEdit()
        self._context_input.setPlaceholderText(
            "Enter additional context, requirements, or specific instructions for this agent...\n\n"
            "Examples:\n"
            "- Use TypeScript instead of JavaScript\n"
            "- Follow specific coding style guidelines\n"
            "- Focus on performance optimization\n"
            "- Add detailed documentation"
        )
        self._context_input.setMinimumHeight(120)
        parent_layout.addWidget(self._context_input)

        # Submit button
        submit_layout = QHBoxLayout()
        submit_layout.addStretch()
        
        self._submit_btn = PrimaryPushButton("Submit Context")
        self._submit_btn.clicked.connect(self._on_submit_context)
        submit_layout.addWidget(self._submit_btn)
        
        parent_layout.addLayout(submit_layout)

    @Slot()
    def _on_close(self) -> None:
        """Handle close button click."""
        self.closed.emit()

    @Slot()
    def _on_submit_context(self) -> None:
        """Handle context submission."""
        context = self._context_input.toPlainText().strip()
        if context:
            self.context_submitted.emit(self._agent_id, context)
            self._context_input.clear()

    # ===== Public API =====

    def update_status(self, status: str, iterations: int = 0, cost_usd: float = 0.0) -> None:
        """Update agent status information.
        
        Args:
            status: Current agent status
            iterations: Number of iterations
            cost_usd: Cost in USD
        """
        self._status_text.setText(status)
        self._iterations_text.setText(str(iterations))
        self._cost_text.setText(f"${cost_usd:.2f}")

    def append_thinking(self, message: str) -> None:
        """Append thinking/reasoning message.
        
        Args:
            message: Thinking message to append
        """
        self._thinking_viewer.appendPlainText(message)
        
        # Auto-scroll to bottom
        cursor = self._thinking_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._thinking_viewer.setTextCursor(cursor)

    def append_log(self, message: str) -> None:
        """Append execution log message.
        
        Args:
            message: Log message to append
        """
        self._logs_viewer.appendPlainText(message)
        
        # Auto-scroll to bottom
        cursor = self._logs_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._logs_viewer.setTextCursor(cursor)

    def clear_thinking(self) -> None:
        """Clear thinking viewer."""
        self._thinking_viewer.clear()

    def clear_logs(self) -> None:
        """Clear logs viewer."""
        self._logs_viewer.clear()

    def clear_all(self) -> None:
        """Clear all content."""
        self.clear_thinking()
        self.clear_logs()
        self._context_input.clear()
