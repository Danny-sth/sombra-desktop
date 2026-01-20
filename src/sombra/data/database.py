"""SQLite database connection and migrations."""

import sqlite3
import sys
from pathlib import Path

_connection: sqlite3.Connection | None = None


def get_db_path() -> Path:
    """Get platform-specific database path."""
    if sys.platform == "win32":
        # Windows: %LOCALAPPDATA%/Sombra/chat.db
        base = Path.home() / "AppData" / "Local" / "Sombra"
    else:
        # Linux/macOS: ~/.local/share/sombra/chat.db
        base = Path.home() / ".local" / "share" / "sombra"

    base.mkdir(parents=True, exist_ok=True)
    return base / "chat.db"


def get_connection() -> sqlite3.Connection:
    """Get or create database connection."""
    global _connection

    if _connection is None:
        db_path = get_db_path()
        _connection = sqlite3.connect(str(db_path), check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        # Enable foreign keys
        _connection.execute("PRAGMA foreign_keys = ON")

    return _connection


def init_db() -> None:
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            session_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_conversation
        ON messages(conversation_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_updated
        ON conversations(updated_at DESC)
    """)

    conn.commit()


def close_db() -> None:
    """Close database connection."""
    global _connection

    if _connection is not None:
        _connection.close()
        _connection = None
