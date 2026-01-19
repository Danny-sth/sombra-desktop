"""Centralized logging configuration."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_dir() -> Path:
    """Get platform-specific log directory."""
    if sys.platform == "win32":
        # Windows: %LOCALAPPDATA%/Sombra/logs
        base = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
        log_dir = base / "Sombra" / "logs"
    else:
        # Linux/Mac: ~/.local/share/sombra/logs
        base = Path(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")))
        log_dir = base / "sombra" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application logging.

    - Console output with colors
    - File output with rotation (5MB max, 3 backups)
    - Separate error log file

    Args:
        level: Minimum log level (default INFO)
    """
    log_dir = get_log_dir()

    # Log format
    console_format = "%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s"
    file_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    date_format = "%H:%M:%S"
    file_date_format = "%Y-%m-%d %H:%M:%S"

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(console_format, datefmt=date_format))
    root_logger.addHandler(console_handler)

    # Main log file (rotating)
    main_log = log_dir / "sombra.log"
    file_handler = RotatingFileHandler(
        main_log,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(file_format, datefmt=file_date_format))
    root_logger.addHandler(file_handler)

    # Error log file (errors only)
    error_log = log_dir / "sombra-error.log"
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=2,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(file_format, datefmt=file_date_format))
    root_logger.addHandler(error_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PySide6").setLevel(logging.WARNING)

    # Log startup info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - logs dir: {log_dir}")


def get_log_file_path() -> Path:
    """Get path to main log file."""
    return get_log_dir() / "sombra.log"
