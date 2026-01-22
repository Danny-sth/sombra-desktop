"""Remote command handlers for server-to-client control.

This module implements all command handlers that allow Sombra AI
to have FULL control over the desktop client remotely.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ..core.logging_config import register_command_handler, get_ws_handler

logger = logging.getLogger(__name__)


class RemoteCommandService:
    """Service for handling all remote commands from server."""

    def __init__(self, update_service=None):
        self._update_service = update_service
        self._response_callback: Optional[Callable] = None

    def register_all_handlers(self):
        """Register all command handlers."""
        handlers = {
            # Core commands
            "force_update": self._handle_force_update,
            "restart": self._handle_restart,

            # Shell/System commands
            "execute_shell": self._handle_execute_shell,
            "get_system_info": self._handle_get_system_info,

            # Config commands
            "get_config": self._handle_get_config,
            "set_config": self._handle_set_config,

            # File commands
            "read_file": self._handle_read_file,
            "write_file": self._handle_write_file,
            "list_dir": self._handle_list_dir,

            # Logs
            "get_local_logs": self._handle_get_local_logs,

            # App info
            "get_app_info": self._handle_get_app_info,
            "ping": self._handle_ping,
        }

        for command, handler in handlers.items():
            register_command_handler(command, handler)
            logger.debug(f"Registered handler: {command}")

        logger.info(f"Remote command service initialized with {len(handlers)} handlers")

    def _send_response(self, command: str, success: bool, data: Any = None, error: str = None):
        """Send response back to server via WebSocket."""
        response = {
            "type": "command_response",
            "command": command,
            "success": success,
            "data": data,
            "error": error,
        }

        # Log the response
        ws_handler = get_ws_handler()
        if ws_handler:
            # Send as a log entry with special type
            logger.info(f"Command response: {command} -> success={success}, data_size={len(str(data)) if data else 0}")

            # Also emit as special log for server to catch
            response_logger = logging.getLogger("sombra.command_response")
            response_logger.info(json.dumps(response))

    # ===== Core Commands =====

    def _handle_force_update(self, data: dict):
        """Force update check."""
        logger.info("Executing: force_update")
        if self._update_service:
            QTimer.singleShot(0, self._update_service.check_for_updates)
            self._send_response("force_update", True, {"message": "Update check triggered"})
        else:
            self._send_response("force_update", False, error="Update service not available")

    def _handle_restart(self, data: dict):
        """Restart the application."""
        logger.info("Executing: restart")
        self._send_response("restart", True, {"message": "Restarting..."})
        QTimer.singleShot(500, QApplication.quit)

    # ===== Shell Commands =====

    def _handle_execute_shell(self, data: dict):
        """Execute shell command and return output."""
        command = data.get("command", "")
        if not command:
            self._send_response("execute_shell", False, error="No command provided")
            return

        logger.info(f"Executing shell: {command[:100]}...")

        try:
            # Run command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=data.get("cwd"),
            )

            self._send_response("execute_shell", True, {
                "stdout": result.stdout[-5000:] if result.stdout else "",  # Limit output
                "stderr": result.stderr[-2000:] if result.stderr else "",
                "returncode": result.returncode,
            })

        except subprocess.TimeoutExpired:
            self._send_response("execute_shell", False, error="Command timed out (30s)")
        except Exception as e:
            self._send_response("execute_shell", False, error=str(e))

    def _handle_get_system_info(self, data: dict):
        """Get system information."""
        import platform

        try:
            info = {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "executable": sys.executable,
                "frozen": getattr(sys, 'frozen', False),
                "cwd": os.getcwd(),
            }

            # Add memory info if psutil available
            try:
                import psutil
                mem = psutil.virtual_memory()
                info["memory_total_gb"] = round(mem.total / (1024**3), 2)
                info["memory_available_gb"] = round(mem.available / (1024**3), 2)
                info["memory_percent"] = mem.percent
                info["cpu_count"] = psutil.cpu_count()
            except ImportError:
                pass

            self._send_response("get_system_info", True, info)

        except Exception as e:
            self._send_response("get_system_info", False, error=str(e))

    # ===== Config Commands =====

    def _handle_get_config(self, data: dict):
        """Get current .env configuration."""
        try:
            if getattr(sys, 'frozen', False):
                env_path = Path(sys.executable).parent / '.env'
            else:
                env_path = Path.cwd() / '.env'

            if env_path.exists():
                content = env_path.read_text(encoding='utf-8')
                self._send_response("get_config", True, {
                    "path": str(env_path),
                    "content": content,
                    "exists": True,
                })
            else:
                self._send_response("get_config", True, {
                    "path": str(env_path),
                    "content": None,
                    "exists": False,
                })

        except Exception as e:
            self._send_response("get_config", False, error=str(e))

    def _handle_set_config(self, data: dict):
        """Update .env configuration."""
        content = data.get("content")
        if content is None:
            self._send_response("set_config", False, error="No content provided")
            return

        try:
            if getattr(sys, 'frozen', False):
                env_path = Path(sys.executable).parent / '.env'
            else:
                env_path = Path.cwd() / '.env'

            # Backup old config
            if env_path.exists():
                backup_path = env_path.with_suffix('.env.backup')
                backup_path.write_text(env_path.read_text(encoding='utf-8'), encoding='utf-8')

            # Write new config
            env_path.write_text(content, encoding='utf-8')

            self._send_response("set_config", True, {
                "path": str(env_path),
                "message": "Config updated. Restart required for changes to take effect.",
            })

        except Exception as e:
            self._send_response("set_config", False, error=str(e))

    # ===== File Commands =====

    def _handle_read_file(self, data: dict):
        """Read file contents."""
        path = data.get("path")
        if not path:
            self._send_response("read_file", False, error="No path provided")
            return

        try:
            file_path = Path(path)
            if not file_path.exists():
                self._send_response("read_file", False, error=f"File not found: {path}")
                return

            if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
                self._send_response("read_file", False, error="File too large (>1MB)")
                return

            content = file_path.read_text(encoding='utf-8', errors='replace')
            self._send_response("read_file", True, {
                "path": str(file_path.absolute()),
                "content": content,
                "size": file_path.stat().st_size,
            })

        except Exception as e:
            self._send_response("read_file", False, error=str(e))

    def _handle_write_file(self, data: dict):
        """Write file contents."""
        path = data.get("path")
        content = data.get("content")

        if not path:
            self._send_response("write_file", False, error="No path provided")
            return
        if content is None:
            self._send_response("write_file", False, error="No content provided")
            return

        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')

            self._send_response("write_file", True, {
                "path": str(file_path.absolute()),
                "size": len(content),
            })

        except Exception as e:
            self._send_response("write_file", False, error=str(e))

    def _handle_list_dir(self, data: dict):
        """List directory contents."""
        path = data.get("path", ".")

        try:
            dir_path = Path(path)
            if not dir_path.exists():
                self._send_response("list_dir", False, error=f"Directory not found: {path}")
                return

            entries = []
            for entry in dir_path.iterdir():
                try:
                    stat = entry.stat()
                    entries.append({
                        "name": entry.name,
                        "is_dir": entry.is_dir(),
                        "size": stat.st_size if entry.is_file() else None,
                    })
                except OSError:
                    entries.append({"name": entry.name, "error": "stat failed"})

            self._send_response("list_dir", True, {
                "path": str(dir_path.absolute()),
                "entries": entries[:500],  # Limit entries
            })

        except Exception as e:
            self._send_response("list_dir", False, error=str(e))

    # ===== Log Commands =====

    def _handle_get_local_logs(self, data: dict):
        """Get local log file contents."""
        lines = data.get("lines", 200)

        try:
            # Find log directory
            if sys.platform == "win32":
                log_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Sombra" / "logs"
            else:
                log_dir = Path.home() / ".local" / "share" / "sombra" / "logs"

            if not log_dir.exists():
                self._send_response("get_local_logs", True, {
                    "path": str(log_dir),
                    "exists": False,
                    "content": None,
                })
                return

            # Find latest log file
            log_files = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
            if not log_files:
                self._send_response("get_local_logs", True, {
                    "path": str(log_dir),
                    "exists": True,
                    "files": [],
                    "content": None,
                })
                return

            latest_log = log_files[0]
            content = latest_log.read_text(encoding='utf-8', errors='replace')

            # Get last N lines
            log_lines = content.splitlines()[-lines:]

            self._send_response("get_local_logs", True, {
                "path": str(latest_log),
                "files": [f.name for f in log_files[:10]],
                "content": "\n".join(log_lines),
                "total_lines": len(content.splitlines()),
            })

        except Exception as e:
            self._send_response("get_local_logs", False, error=str(e))

    # ===== App Info Commands =====

    def _handle_get_app_info(self, data: dict):
        """Get application info and paths."""
        from .. import __version__

        try:
            if getattr(sys, 'frozen', False):
                app_dir = Path(sys.executable).parent
            else:
                app_dir = Path.cwd()

            info = {
                "version": __version__,
                "frozen": getattr(sys, 'frozen', False),
                "executable": sys.executable,
                "app_dir": str(app_dir),
                "env_file": str(app_dir / '.env'),
                "env_exists": (app_dir / '.env').exists(),
            }

            # Check _internal folder
            internal_dir = app_dir / '_internal'
            info["internal_exists"] = internal_dir.exists()

            self._send_response("get_app_info", True, info)

        except Exception as e:
            self._send_response("get_app_info", False, error=str(e))

    def _handle_ping(self, data: dict):
        """Simple ping to check if client is responsive."""
        from .. import __version__
        self._send_response("ping", True, {
            "pong": True,
            "version": __version__,
        })


# Global instance
_remote_service: Optional[RemoteCommandService] = None


def init_remote_commands(update_service=None) -> RemoteCommandService:
    """Initialize remote command service."""
    global _remote_service
    _remote_service = RemoteCommandService(update_service)
    _remote_service.register_all_handlers()
    return _remote_service


def get_remote_service() -> Optional[RemoteCommandService]:
    """Get global remote service instance."""
    return _remote_service
