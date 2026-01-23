"""Data layer for Sombra Desktop - SQLite persistence."""

from .chat_repository import ChatRepository
from .database import get_db_path, init_db
from .models import Conversation, Message

__all__ = [
    "init_db",
    "get_db_path",
    "Conversation",
    "Message",
    "ChatRepository",
]
