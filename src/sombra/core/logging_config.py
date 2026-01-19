"""Centralized logging configuration with remote streaming."""

import asyncio
import json
import logging
import os
import platform
import queue
import sys
import threading
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from pathlib import Path
from typing import Optional

import websockets
from websockets.exceptions import WebSocketException

from .. import __version__

# Generate unique client ID
CLIENT_ID = f"desktop-{platform.node()}-{uuid.uuid4().hex[:8]}"


def get_log_dir() -> Path:
    """Get platform-specific log directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
        log_dir = base / "Sombra" / "logs"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")))
        log_dir = base / "sombra" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


class WebSocketLogHandler(logging.Handler):
    """Async handler that sends logs to server via WebSocket."""

    def __init__(self, url: str, level: int = logging.INFO):
        super().__init__(level)
        self.url = url
        self._queue: queue.Queue = queue.Queue(maxsize=1000)
        self._connected = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start the background sender thread."""
        if self._thread is not None:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_sender, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background sender thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def emit(self, record: logging.LogRecord):
        """Queue log record for sending."""
        if self._stop_event.is_set():
            return

        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "client_id": CLIENT_ID,
                "version": __version__,
                "func": record.funcName,
                "line": record.lineno,
            }
            # Non-blocking put
            self._queue.put_nowait(log_entry)
        except queue.Full:
            pass  # Drop if queue is full

    def _run_sender(self):
        """Background thread running async sender."""
        asyncio.run(self._async_sender())

    async def _async_sender(self):
        """Async loop that sends queued logs."""
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(
                    self.url,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5,
                ) as ws:
                    self._connected = True

                    while not self._stop_event.is_set():
                        try:
                            # Get with timeout to check stop event periodically
                            log_entry = self._queue.get(timeout=0.5)
                            await ws.send(json.dumps(log_entry))
                        except queue.Empty:
                            continue
                        except WebSocketException:
                            break

            except Exception:
                self._connected = False
                # Wait before reconnect
                for _ in range(50):  # 5 seconds total
                    if self._stop_event.is_set():
                        return
                    await asyncio.sleep(0.1)


# Global handler reference for cleanup
_ws_handler: Optional[WebSocketLogHandler] = None


def setup_logging(level: int = logging.INFO, remote_url: Optional[str] = None) -> None:
    """Configure application logging.

    Args:
        level: Minimum log level (default INFO)
        remote_url: WebSocket URL for remote logging (optional)
    """
    global _ws_handler
    log_dir = get_log_dir()

    # Log formats
    console_format = "%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s"
    file_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    date_format = "%H:%M:%S"
    file_date_format = "%Y-%m-%d %H:%M:%S"

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
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
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(file_format, datefmt=file_date_format))
    root_logger.addHandler(file_handler)

    # Error log file
    error_log = log_dir / "sombra-error.log"
    error_handler = RotatingFileHandler(
        error_log,
        maxBytes=2 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(file_format, datefmt=file_date_format))
    root_logger.addHandler(error_handler)

    # WebSocket remote handler
    if remote_url is None:
        # Default to production server
        remote_url = "ws://90.156.230.49:8080/api/logs/stream"

    _ws_handler = WebSocketLogHandler(remote_url, level=level)
    _ws_handler.setFormatter(logging.Formatter("%(message)s"))
    _ws_handler.start()
    root_logger.addHandler(_ws_handler)

    # Reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PySide6").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - client_id: {CLIENT_ID}, logs: {log_dir}")


def cleanup_logging():
    """Cleanup logging resources."""
    global _ws_handler
    if _ws_handler:
        _ws_handler.stop()
        _ws_handler = None


def get_log_file_path() -> Path:
    """Get path to main log file."""
    return get_log_dir() / "sombra.log"
