"""Data layer for Sombra Desktop - SQLite persistence."""

from .database import init_db, get_db_path
from .models import Conversation, Message
from .chat_repository import ChatRepository

__all__ = [
    "init_db",
    "get_db_path",
    "Conversation",
    "Message",
    "ChatRepository",
]
