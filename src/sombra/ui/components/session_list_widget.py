"""Session list widget - displays list of chat sessions."""

from datetime import datetime

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    PrimaryPushButton,
    PushButton,
    StrongBodyLabel,
)


class SessionItemWidget(CardWidget):
    """Custom widget for a single session item in the list."""

    clicked = Signal(str)  # session_id
    deleted = Signal(str)  # session_id

    def __init__(
        self,
        session_id: str,
        last_message: str | None,
        message_count: int,
        last_active: datetime,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._session_id = session_id

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Top row: Session ID and delete button
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        # Session ID (truncated if too long)
        display_id = session_id if len(session_id) <= 30 else session_id[:27] + "..."
        self.session_label = StrongBodyLabel(display_id)
        self.session_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        top_layout.addWidget(self.session_label)

        top_layout.addStretch()

        # Delete button
        self.delete_btn = PushButton("🗑")
        self.delete_btn.setFixedSize(32, 24)
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self._session_id))
        top_layout.addWidget(self.delete_btn)

        layout.addLayout(top_layout)

        # Middle row: Last message (truncated)
        if last_message:
            preview = last_message if len(last_message) <= 100 else last_message[:97] + "..."
            self.message_label = BodyLabel(preview)
            self.message_label.setWordWrap(True)
            self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(self.message_label)

        # Bottom row: Message count and last active time
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        # Message count
        count_label = CaptionLabel(f"💬 {message_count} messages")
        count_label.setStyleSheet("color: gray;")
        bottom_layout.addWidget(count_label)

        bottom_layout.addStretch()

        # Last active time
        time_str = self._format_time(last_active)
        time_label = CaptionLabel(time_str)
        time_label.setStyleSheet("color: gray;")
        bottom_layout.addWidget(time_label)

        layout.addLayout(bottom_layout)

        # Make card clickable
        self.setCursor(Qt.PointingHandCursor)

    def _format_time(self, dt: datetime) -> str:
        """Format datetime to human-readable string."""
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = now - dt

        if delta.days == 0:
            # Today
            if delta.seconds < 60:
                return "just now"
            elif delta.seconds < 3600:
                mins = delta.seconds // 60
                return f"{mins}m ago"
            else:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
        elif delta.days == 1:
            return "yesterday"
        elif delta.days < 7:
            return f"{delta.days}d ago"
        else:
            return dt.strftime("%b %d")

    def mousePressEvent(self, event):
        """Handle mouse click - emit clicked signal."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._session_id)
        super().mousePressEvent(event)


class SessionListWidget(QWidget):
    """Widget displaying list of chat sessions."""

    session_selected = Signal(str)  # session_id
    session_deleted = Signal(str)  # session_id
    new_session_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._sessions: list[dict] = []
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header with title and new chat button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = StrongBodyLabel("Chats")
        title_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # New chat button
        self.new_chat_btn = PrimaryPushButton("+ New Chat")
        self.new_chat_btn.clicked.connect(self.new_session_requested.emit)
        header_layout.addWidget(self.new_chat_btn)

        layout.addLayout(header_layout)

        # Sessions list (using QListWidget for scrolling)
        self.sessions_list = QListWidget()
        self.sessions_list.setSpacing(4)
        self.sessions_list.setStyleSheet("QListWidget { border: none; background: transparent; }")
        layout.addWidget(self.sessions_list)

    def set_sessions(self, sessions: list[dict]):
        """Set the list of sessions to display.

        Args:
            sessions: List of session dictionaries from API
        """
        self._sessions = sessions
        self._refresh_list()

    def _refresh_list(self):
        """Refresh the sessions list display."""
        self.sessions_list.clear()

        for session in self._sessions:
            session_id = session.get("id", "")
            last_message = session.get("last_message")
            message_count = session.get("message_count", 0)
            last_active_str = session.get("last_active_at", "")

            # Parse datetime
            try:
                last_active = datetime.fromisoformat(last_active_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                last_active = datetime.now()

            # Create session item widget
            item_widget = SessionItemWidget(
                session_id=session_id,
                last_message=last_message,
                message_count=message_count,
                last_active=last_active,
            )
            item_widget.clicked.connect(self.session_selected.emit)
            item_widget.deleted.connect(self._on_delete_requested)

            # Add to list
            list_item = QListWidgetItem(self.sessions_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.sessions_list.addItem(list_item)
            self.sessions_list.setItemWidget(list_item, item_widget)

    @Slot(str)
    def _on_delete_requested(self, session_id: str):
        """Handle delete button click."""
        self.session_deleted.emit(session_id)

    def remove_session(self, session_id: str):
        """Remove a session from the list.

        Args:
            session_id: Session ID to remove
        """
        self._sessions = [s for s in self._sessions if s.get("id") != session_id]
        self._refresh_list()
