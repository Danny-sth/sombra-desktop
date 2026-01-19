"""Configuration management using dotenv."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self, env_path: Optional[Path] = None):
        """Initialize settings from .env file or environment variables.

        Args:
            env_path: Optional path to .env file. If not provided, searches in
                     current directory and parent directories.
        """
        # For PyInstaller builds, look for .env next to the executable
        if env_path:
            load_dotenv(env_path)
        else:
            # Try multiple locations
            import sys
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_dir = Path(sys.executable).parent
                env_file = exe_dir / '.env'
                if env_file.exists():
                    load_dotenv(env_file)
                else:
                    load_dotenv()
            else:
                load_dotenv()

        # Sombra Backend (default to production server)
        self.sombra_api_url: str = os.getenv("SOMBRA_API_URL", "http://90.156.230.49:8080")
        self.sombra_session_id: str = os.getenv("SOMBRA_SESSION_ID", "owner")

        # Whisper STT Service
        self.stt_url: str = os.getenv("STT_URL", "http://100.87.46.63:5000/transcribe")

        # UI Settings
        self.theme: str = os.getenv("THEME", "dark")
        self.global_hotkey: str = os.getenv("GLOBAL_HOTKEY", "ctrl+shift+s")

        # Audio Settings
        self.audio_device_id: Optional[int] = self._get_int("AUDIO_DEVICE_ID")
        self.audio_sample_rate: int = self._get_int("AUDIO_SAMPLE_RATE", 16000)

        # Wake Word Settings
        self.wake_word_enabled: bool = os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
        self.wake_word: str = os.getenv("WAKE_WORD", "jarvis")
        self.porcupine_access_key: Optional[str] = os.getenv("PORCUPINE_ACCESS_KEY")

    def _get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get integer from environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def __repr__(self) -> str:
        return (
            f"Settings(sombra_api_url={self.sombra_api_url!r}, "
            f"stt_url={self.stt_url!r}, theme={self.theme!r})"
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def init_settings(env_path: Optional[Path] = None) -> Settings:
    """Initialize or reinitialize settings."""
    global _settings
    _settings = Settings(env_path)
    return _settings
