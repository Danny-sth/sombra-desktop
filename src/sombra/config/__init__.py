"""Configuration module."""

from .settings import Settings, get_settings, init_settings

# Global config instance for convenient imports
config = get_settings()

__all__ = ["Settings", "config", "get_settings", "init_settings"]
