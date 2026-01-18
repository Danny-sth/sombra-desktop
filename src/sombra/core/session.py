"""Session management for Sombra API authentication."""

import uuid
from datetime import datetime
from typing import Optional

from ..config.settings import get_settings


class SessionManager:
    """Manages session state for API authentication.

    Maintains a persistent session ID for communication with Sombra backend.
    The session ID is used for:
    - API authentication via X-Session-Id header
    - SSE stream identification
    - Rate limiting
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize session manager.

        Args:
            session_id: Optional session ID. If not provided, uses settings
                       or generates a new UUID.
        """
        settings = get_settings()

        if session_id:
            self._session_id = session_id
        elif settings.sombra_session_id:
            self._session_id = settings.sombra_session_id
        else:
            self._session_id = self._generate_session_id()

        self._created_at = datetime.now()

    @property
    def session_id(self) -> str:
        """Get the current session ID."""
        return self._session_id

    @property
    def created_at(self) -> datetime:
        """Get session creation timestamp."""
        return self._created_at

    def regenerate(self) -> str:
        """Generate a new session ID.

        Returns:
            The new session ID.
        """
        self._session_id = self._generate_session_id()
        self._created_at = datetime.now()
        return self._session_id

    def get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests.

        Returns:
            Dictionary with authentication headers.
        """
        return {
            "X-Session-Id": self._session_id,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID."""
        return f"sombra-desktop-{uuid.uuid4().hex[:8]}"

    def __repr__(self) -> str:
        return f"SessionManager(session_id={self._session_id!r}, created_at={self._created_at})"


# Global session manager instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get the global SessionManager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def init_session_manager(session_id: Optional[str] = None) -> SessionManager:
    """Initialize or reinitialize the SessionManager."""
    global _session_manager
    _session_manager = SessionManager(session_id)
    return _session_manager
