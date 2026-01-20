"""Repository for chat history CRUD operations."""

import uuid
from datetime import datetime

from .database import get_connection
from .models import Conversation, Message


class ChatRepository:
    """Repository for managing conversations and messages."""

    # =========================================================================
    # Conversations
    # =========================================================================

    def create_conversation(self, session_id: str, title: str | None = None) -> Conversation:
        """Create a new conversation."""
        conn = get_connection()
        cursor = conn.cursor()

        conversation_id = str(uuid.uuid4())
        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO conversations (id, title, session_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, title, session_id, now, now),
        )
        conn.commit()

        return Conversation(
            id=conversation_id,
            title=title,
            session_id=session_id,
            created_at=now,
            updated_at=now,
        )

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get a conversation by ID with all its messages."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        conversation = Conversation(
            id=row["id"],
            title=row["title"],
            session_id=row["session_id"],
            created_at=_parse_datetime(row["created_at"]),
            updated_at=_parse_datetime(row["updated_at"]),
        )

        # Load messages
        conversation.messages = self.get_messages(conversation_id)

        return conversation

    def list_conversations(self, limit: int = 50) -> list[Conversation]:
        """List recent conversations (without messages)."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        )

        conversations = []
        for row in cursor.fetchall():
            conversations.append(
                Conversation(
                    id=row["id"],
                    title=row["title"],
                    session_id=row["session_id"],
                    created_at=_parse_datetime(row["created_at"]),
                    updated_at=_parse_datetime(row["updated_at"]),
                )
            )

        return conversations

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update conversation title."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, datetime.now(), conversation_id),
        )
        conn.commit()

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation and all its messages."""
        conn = get_connection()
        cursor = conn.cursor()

        # Messages are deleted by CASCADE
        cursor.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        conn.commit()

    def touch_conversation(self, conversation_id: str) -> None:
        """Update conversation's updated_at timestamp."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (datetime.now(), conversation_id),
        )
        conn.commit()

    # =========================================================================
    # Messages
    # =========================================================================

    def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> Message:
        """Add a message to a conversation."""
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, now),
        )

        # Update conversation's updated_at
        cursor.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, conversation_id),
        )

        conn.commit()

        return Message(
            id=cursor.lastrowid,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=now,
        )

    def get_messages(self, conversation_id: str) -> list[Message]:
        """Get all messages for a conversation."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        )

        messages = []
        for row in cursor.fetchall():
            messages.append(
                Message(
                    id=row["id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    content=row["content"],
                    created_at=_parse_datetime(row["created_at"]),
                )
            )

        return messages


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    """Parse datetime from SQLite string or return as-is."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
