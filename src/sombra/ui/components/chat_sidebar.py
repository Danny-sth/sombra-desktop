"""Collapsible sidebar for chat history."""

from datetime import datetime, timedelta

from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMenu,
    QInputDialog,
)

from qfluentwidgets import (
    BodyLabel,
    CaptionLabel,
    TransparentToolButton,
    PrimaryPushButton,
    FluentIcon,
    isDarkTheme,
    ScrollArea,
)

from ...data.models import Conversation


class ConversationItem(QFrame):
    """Single conversation item in the sidebar."""

    clicked = Signal(str)  # conversation_id
    rename_requested = Signal(str)  # conversation_id
    delete_requested = Signal(str)  # conversation_id

    def __init__(
        self,
        conversation: Conversation,
        is_active: bool = False,
        parent: QWidget | None = None
    ):
        super().__init__(parent)

        self._conversation = conversation
        self._is_active = is_active

        self._setup_ui()
        self._update_style()

    def _setup_ui(self) -> None:
        """Build the item UI."""
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Chat icon
        icon_label = BodyLabel("")
        icon_label.setFixedWidth(20)
        layout.addWidget(icon_label)

        # Title
        title = self._conversation.title or "New Chat"
        self._title_label = BodyLabel(title)
        self._title_label.setWordWrap(False)
        layout.addWidget(self._title_label, 1)

        # Context menu on right-click
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _update_style(self) -> None:
        """Update visual style based on state."""
        if self._is_active:
            bg_color = "rgba(233, 69, 96, 0.15)" if isDarkTheme() else "rgba(233, 69, 96, 0.1)"
            border = "2px solid #e94560"
        else:
            bg_color = "rgba(255, 255, 255, 0.03)" if isDarkTheme() else "rgba(0, 0, 0, 0.02)"
            border = "1px solid transparent"

        self.setStyleSheet(f"""
            ConversationItem {{
                background-color: {bg_color};
                border: {border};
                border-radius: 8px;
            }}
            ConversationItem:hover {{
                background-color: {'rgba(255, 255, 255, 0.08)' if isDarkTheme() else 'rgba(0, 0, 0, 0.05)'};
            }}
        """)

    def set_active(self, is_active: bool) -> None:
        """Set active state."""
        self._is_active = is_active
        self._update_style()

    def mousePressEvent(self, event) -> None:
        """Handle click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._conversation.id)
        super().mousePressEvent(event)

    def _show_context_menu(self, pos) -> None:
        """Show context menu."""
        menu = QMenu(self)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_requested.emit(self._conversation.id))
        menu.addAction(rename_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self._conversation.id))
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(pos))

    @property
    def conversation_id(self) -> str:
        return self._conversation.id


class ChatSidebar(QFrame):
    """Collapsible sidebar showing chat history.

    Signals:
        conversation_selected(str): Emitted when user clicks a conversation
        new_conversation_requested(): Emitted when user clicks "New Chat"
        conversation_renamed(str, str): Emitted when user renames (id, new_title)
        conversation_deleted(str): Emitted when user deletes
        toggle_requested(): Emitted when collapse/expand button clicked
    """

    conversation_selected = Signal(str)
    new_conversation_requested = Signal()
    conversation_renamed = Signal(str, str)
    conversation_deleted = Signal(str)
    toggle_requested = Signal()

    # Width constants
    EXPANDED_WIDTH = 280
    COLLAPSED_WIDTH = 0

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._is_expanded = False
        self._conversations: list[Conversation] = []
        self._items: dict[str, ConversationItem] = {}
        self._active_id: str | None = None

        self._setup_ui()
        self._setup_animation()

        # Start collapsed
        self.setFixedWidth(self.COLLAPSED_WIDTH)

    def _setup_ui(self) -> None:
        """Build the sidebar UI."""
        self.setObjectName("chatSidebar")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Content widget (slides in/out)
        self._content = QWidget()
        self._content.setFixedWidth(self.EXPANDED_WIDTH)
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # Header
        header = self._create_header()
        content_layout.addWidget(header)

        # New Chat button
        self._new_btn = PrimaryPushButton("New Chat")
        self._new_btn.setIcon(FluentIcon.ADD)
        self._new_btn.clicked.connect(self.new_conversation_requested.emit)
        content_layout.addWidget(self._new_btn)

        # Conversations list
        self._scroll_area = ScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()

        self._scroll_area.setWidget(self._list_widget)
        content_layout.addWidget(self._scroll_area, 1)

        layout.addWidget(self._content)

        # Styling
        self._update_style()

    def _create_header(self) -> QWidget:
        """Create sidebar header."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        title = BodyLabel("History")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        layout.addStretch()

        # Collapse button
        collapse_btn = TransparentToolButton(FluentIcon.LEFT_ARROW)
        collapse_btn.setToolTip("Collapse sidebar")
        collapse_btn.clicked.connect(self.toggle_requested.emit)
        layout.addWidget(collapse_btn)

        return widget

    def _setup_animation(self) -> None:
        """Setup slide animation."""
        self._animation = QPropertyAnimation(self, b"minimumWidth")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _update_style(self) -> None:
        """Update sidebar styling."""
        border_color = "rgba(255, 255, 255, 0.1)" if isDarkTheme() else "rgba(0, 0, 0, 0.1)"
        bg_color = "rgba(30, 30, 30, 0.95)" if isDarkTheme() else "rgba(250, 250, 250, 0.95)"

        self.setStyleSheet(f"""
            #chatSidebar {{
                background-color: {bg_color};
                border-right: 1px solid {border_color};
            }}
        """)

    def toggle(self) -> None:
        """Toggle expanded/collapsed state."""
        self._is_expanded = not self._is_expanded

        target_width = self.EXPANDED_WIDTH if self._is_expanded else self.COLLAPSED_WIDTH

        self._animation.stop()
        self._animation.setStartValue(self.width())
        self._animation.setEndValue(target_width)
        self._animation.start()

    def expand(self) -> None:
        """Expand the sidebar."""
        if not self._is_expanded:
            self.toggle()

    def collapse(self) -> None:
        """Collapse the sidebar."""
        if self._is_expanded:
            self.toggle()

    @property
    def is_expanded(self) -> bool:
        return self._is_expanded

    def set_conversations(self, conversations: list[Conversation]) -> None:
        """Update the list of conversations."""
        self._conversations = conversations
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        """Rebuild the conversation list UI."""
        # Clear existing items
        for item in self._items.values():
            item.deleteLater()
        self._items.clear()

        # Remove all widgets from layout except stretch
        while self._list_layout.count() > 1:
            child = self._list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Group conversations by date
        groups = self._group_by_date(self._conversations)

        # Add grouped items
        insert_index = 0
        for group_name, convs in groups.items():
            # Group header
            header = CaptionLabel(group_name)
            header.setStyleSheet("color: #888888; padding: 8px 0 4px 0;")
            self._list_layout.insertWidget(insert_index, header)
            insert_index += 1

            # Items
            for conv in convs:
                item = ConversationItem(
                    conv,
                    is_active=(conv.id == self._active_id)
                )
                item.clicked.connect(self._on_item_clicked)
                item.rename_requested.connect(self._on_rename_requested)
                item.delete_requested.connect(self._on_delete_requested)

                self._items[conv.id] = item
                self._list_layout.insertWidget(insert_index, item)
                insert_index += 1

    def _group_by_date(self, conversations: list[Conversation]) -> dict[str, list[Conversation]]:
        """Group conversations by date."""
        groups: dict[str, list[Conversation]] = {}

        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        for conv in conversations:
            if conv.updated_at is None:
                group = "Earlier"
            else:
                conv_date = conv.updated_at.date()
                if conv_date == today:
                    group = "Today"
                elif conv_date == yesterday:
                    group = "Yesterday"
                elif conv_date > week_ago:
                    group = "This Week"
                else:
                    group = "Earlier"

            if group not in groups:
                groups[group] = []
            groups[group].append(conv)

        # Order groups
        ordered = {}
        for key in ["Today", "Yesterday", "This Week", "Earlier"]:
            if key in groups:
                ordered[key] = groups[key]

        return ordered

    def set_active_conversation(self, conversation_id: str | None) -> None:
        """Set the active conversation."""
        # Deactivate old
        if self._active_id and self._active_id in self._items:
            self._items[self._active_id].set_active(False)

        # Activate new
        self._active_id = conversation_id
        if conversation_id and conversation_id in self._items:
            self._items[conversation_id].set_active(True)

    def refresh(self) -> None:
        """Request a refresh from parent."""
        # Parent should call set_conversations with updated data
        pass

    @Slot(str)
    def _on_item_clicked(self, conversation_id: str) -> None:
        """Handle conversation item click."""
        self.set_active_conversation(conversation_id)
        self.conversation_selected.emit(conversation_id)

    @Slot(str)
    def _on_rename_requested(self, conversation_id: str) -> None:
        """Handle rename request."""
        conv = next((c for c in self._conversations if c.id == conversation_id), None)
        if not conv:
            return

        title, ok = QInputDialog.getText(
            self,
            "Rename Chat",
            "New title:",
            text=conv.title or ""
        )

        if ok and title.strip():
            self.conversation_renamed.emit(conversation_id, title.strip())

    @Slot(str)
    def _on_delete_requested(self, conversation_id: str) -> None:
        """Handle delete request."""
        self.conversation_deleted.emit(conversation_id)
