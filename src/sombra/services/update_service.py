"""Auto-update service using GitHub Releases API."""

import logging
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import httpx
from packaging import version
from PySide6.QtCore import QObject, QThread, Signal

from .. import __version__

logger = logging.getLogger(__name__)

GITHUB_REPO = "Danny-sth/sombra-desktop"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


class UpdateChecker(QThread):
    """Background thread for checking updates."""

    update_available = Signal(str, str, str)  # version, download_url, release_notes
    check_complete = Signal(bool)  # has_update
    error = Signal(str)

    def __init__(self, current_version: str):
        super().__init__()
        self.current_version = current_version

    def run(self):
        """Check GitHub for latest release."""
        try:
            logger.info(f"Checking for updates... current={self.current_version}")
            with httpx.Client(timeout=10) as client:
                response = client.get(GITHUB_API, headers={
                    "Accept": "application/vnd.github.v3+json"
                })
                response.raise_for_status()
                data = response.json()

            tag = data.get("tag_name", "").lstrip("v")
            logger.info(f"Latest version on GitHub: {tag}")
            if not tag:
                self.check_complete.emit(False)
                return

            # Compare versions
            current = version.parse(self.current_version)
            latest = version.parse(tag)

            if latest > current:
                logger.info(f"Update available: {current} -> {latest}")
                # Find zip asset (portable or any zip)
                download_url = None
                for asset in data.get("assets", []):
                    name = asset.get("name", "")
                    logger.debug(f"Asset: {name}")
                    # Prefer Portable, but accept any zip
                    if name.endswith(".zip"):
                        download_url = asset.get("browser_download_url")
                        logger.info(f"Found update zip: {name}")
                        if "Portable" in name:
                            break  # Prefer portable, stop searching

                if download_url:
                    release_notes = data.get("body", "")
                    self.update_available.emit(tag, download_url, release_notes)
                    self.check_complete.emit(True)
                else:
                    logger.warning("No portable zip found in release assets")
                    self.check_complete.emit(False)
            else:
                logger.info(f"Already on latest version: {self.current_version} >= {tag}")
                self.check_complete.emit(False)

        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            self.error.emit(str(e))
            self.check_complete.emit(False)


class UpdateDownloader(QThread):
    """Background thread for downloading updates."""

    progress = Signal(int, int)  # downloaded, total
    download_complete = Signal(str)  # file path
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._cancelled = False

    def cancel(self):
        """Cancel the download."""
        self._cancelled = True

    def run(self):
        """Download the update file."""
        try:
            # Create temp file for download
            fd, temp_path = tempfile.mkstemp(suffix=".zip", prefix="sombra_update_")
            os.close(fd)

            with httpx.Client(timeout=300, follow_redirects=True) as client:
                with client.stream("GET", self.url) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    with open(temp_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            if self._cancelled:
                                os.unlink(temp_path)
                                return

                            f.write(chunk)
                            downloaded += len(chunk)
                            self.progress.emit(downloaded, total)

            self.download_complete.emit(temp_path)

        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            self.error.emit(str(e))


class UpdateService(QObject):
    """Service for checking and applying updates."""

    update_available = Signal(str, str)  # version, release_notes
    download_progress = Signal(int, int)  # downloaded, total
    update_ready = Signal(str)  # path to update
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checker: Optional[UpdateChecker] = None
        self._downloader: Optional[UpdateDownloader] = None
        self._latest_version: Optional[str] = None
        self._download_url: Optional[str] = None
        self._update_path: Optional[str] = None

    @property
    def current_version(self) -> str:
        """Get current application version."""
        return __version__

    def check_for_updates(self):
        """Start checking for updates in background."""
        if self._checker and self._checker.isRunning():
            return

        self._checker = UpdateChecker(self.current_version)
        self._checker.update_available.connect(self._on_update_found)
        self._checker.error.connect(lambda e: self.error.emit(e))
        self._checker.start()

    def _on_update_found(self, ver: str, url: str, notes: str):
        """Handle update found."""
        self._latest_version = ver
        self._download_url = url
        logger.info(f"Update available: {ver}")
        self.update_available.emit(ver, notes)

    def download_update(self):
        """Download the latest update."""
        if not self._download_url:
            self.error.emit("No update URL available")
            return

        if self._downloader and self._downloader.isRunning():
            return

        logger.info(f"Starting download: {self._download_url}")
        self._downloader = UpdateDownloader(self._download_url)
        self._downloader.progress.connect(self.download_progress.emit)
        self._downloader.download_complete.connect(self._on_download_complete)
        self._downloader.error.connect(lambda e: self.error.emit(e))
        self._downloader.start()

    def _on_download_complete(self, path: str):
        """Handle download complete."""
        self._update_path = path
        logger.info(f"Update downloaded to: {path}")
        self.update_ready.emit(path)

    def apply_update(self) -> bool:
        """Apply the downloaded update and restart.

        Returns:
            True if update process started, False otherwise.
        """
        logger.info(f"Applying update from: {self._update_path}")

        if not self._update_path or not os.path.exists(self._update_path):
            logger.error("Update file not found")
            self.error.emit("Update file not found")
            return False

        if not getattr(sys, 'frozen', False):
            logger.warning("Cannot apply update in development mode")
            self.error.emit("Обновление недоступно в режиме разработки")
            return False

        try:
            # Get current executable directory
            exe_path = Path(sys.executable)
            app_dir = exe_path.parent

            # Create update script
            if sys.platform == "win32":
                return self._apply_update_windows(app_dir)
            else:
                return self._apply_update_linux(app_dir)

        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            self.error.emit(f"Ошибка при установке обновления: {e}")
            return False

    def _apply_update_windows(self, app_dir: Path) -> bool:
        """Apply update on Windows."""
        import os as _os

        # Convert paths to proper Windows format
        zip_path = str(self._update_path).replace('/', '\\')
        # Extract directly to app_dir (where Sombra.exe lives)
        dest_path = str(app_dir).replace('/', '\\')
        exe_path = str(app_dir / 'Sombra.exe').replace('/', '\\')

        logger.info(f"Update paths - zip: {zip_path}, dest: {dest_path}, exe: {exe_path}")

        # Check if needs admin rights
        needs_admin = "program files" in str(app_dir).lower()

        if needs_admin:
            # Script with self-elevation for Program Files
            script = f'''@echo off
chcp 65001 >nul

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo Sombra Update Script (Admin)
echo ============================
echo.
echo Waiting for Sombra to close...
timeout /t 3 /nobreak >nul

echo.
echo Extracting update to: {dest_path}
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '{zip_path}' -DestinationPath '{dest_path}' -Force"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Extraction failed!
    pause
    exit /b 1
)

echo.
echo Update installed! Starting Sombra...
timeout /t 1 /nobreak >nul
start "" "{exe_path}"

del "{zip_path}" 2>nul
timeout /t 2 /nobreak >nul
del "%~f0"
'''
        else:
            # Simple script without elevation
            script = f'''@echo off
chcp 65001 >nul
echo Sombra Update Script
echo ====================
echo.
echo Waiting for Sombra to close...
timeout /t 3 /nobreak >nul

echo.
echo Extracting update to: {dest_path}
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '{zip_path}' -DestinationPath '{dest_path}' -Force"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Extraction failed!
    pause
    exit /b 1
)

echo.
echo Update installed! Starting Sombra...
timeout /t 1 /nobreak >nul
start "" "{exe_path}"

del "{zip_path}" 2>nul
timeout /t 2 /nobreak >nul
del "%~f0"
'''
        script_path = Path(tempfile.gettempdir()) / "sombra_update.bat"
        script_path.write_text(script, encoding="utf-8")

        logger.info(f"Update script created: {script_path}, needs_admin={needs_admin}")

        # Run script
        subprocess.Popen(
            ["cmd", "/c", str(script_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
        )

        logger.info("Update script launched, exiting application...")

        # Force exit after short delay
        import threading
        def force_exit():
            import time
            time.sleep(1)
            _os._exit(0)

        threading.Thread(target=force_exit, daemon=True).start()
        return True

    def _apply_update_linux(self, app_dir: Path) -> bool:
        """Apply update on Linux."""
        # Create shell script
        script = f'''#!/bin/bash
sleep 2

echo "Extracting update..."
unzip -o "{self._update_path}" -d "{app_dir.parent}"

echo "Starting Sombra..."
"{app_dir / 'Sombra'}" &

echo "Cleaning up..."
rm "{self._update_path}"
rm "$0"
'''
        script_path = Path(tempfile.gettempdir()) / "sombra_update.sh"
        script_path.write_text(script)
        os.chmod(script_path, 0o755)

        # Run script detached
        subprocess.Popen(
            [str(script_path)],
            start_new_session=True,
            close_fds=True
        )

        # Exit application
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
        return True

    def cancel_download(self):
        """Cancel ongoing download."""
        if self._downloader:
            self._downloader.cancel()

    def cleanup(self):
        """Cleanup resources."""
        if self._checker and self._checker.isRunning():
            self._checker.quit()
            self._checker.wait(1000)

        if self._downloader and self._downloader.isRunning():
            self._downloader.cancel()
            self._downloader.quit()
            self._downloader.wait(1000)

        # DON'T clean up temp file - update script needs it!
        # The batch/shell script will delete it after extraction
