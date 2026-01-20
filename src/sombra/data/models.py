"""Data models for chat history."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """A single chat message."""

    conversation_id: str
    role: str  # 'user' | 'assistant'
    content: str
    id: int | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Conversation:
    """A chat conversation containing multiple messages."""

    id: str
    session_id: str
    title: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    messages: list[Message] = field(default_factory=list)

    def __post_init__(self):
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
