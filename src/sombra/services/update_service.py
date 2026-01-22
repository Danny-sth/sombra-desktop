"""Auto-update service using GitHub Releases API."""

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

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
                # Find correct asset for platform
                download_url = None
                is_linux = sys.platform != "win32"

                for asset in data.get("assets", []):
                    name = asset.get("name", "")
                    logger.debug(f"Asset: {name}")

                    if is_linux:
                        # Linux: prefer Linux-Source zip, or use git pull
                        if "Linux" in name and name.endswith(".zip"):
                            download_url = asset.get("browser_download_url")
                            logger.info(f"Found Linux update: {name}")
                            break
                    else:
                        # Windows: prefer Portable zip
                        if "Portable" in name and name.endswith(".zip"):
                            download_url = asset.get("browser_download_url")
                            logger.info(f"Found Windows update: {name}")
                            break

                # Fallback: On Linux with git, we don't need download URL
                if is_linux and not download_url:
                    project_dir = Path(__file__).parent.parent.parent.parent
                    if (project_dir / ".git").exists():
                        logger.info("Linux git repo - will use git pull for update")
                        # Use dummy URL to signal update available
                        download_url = "git-pull"

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

    def __init__(self, url: str, dest_path: str):
        super().__init__()
        self.url = url
        self.dest_path = dest_path
        self._cancelled = False

    def cancel(self):
        """Cancel the download."""
        self._cancelled = True

    def run(self):
        """Download the update file."""
        try:
            with httpx.Client(timeout=300, follow_redirects=True) as client:
                with client.stream("GET", self.url) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    downloaded = 0

                    with open(self.dest_path, "wb") as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            if self._cancelled:
                                Path(self.dest_path).unlink(missing_ok=True)
                                return

                            f.write(chunk)
                            downloaded += len(chunk)
                            self.progress.emit(downloaded, total)

            self.download_complete.emit(self.dest_path)

        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            Path(self.dest_path).unlink(missing_ok=True)
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
        # Cache directory for downloaded updates
        self._cache_dir = Path(tempfile.gettempdir()) / "sombra_updates"
        self._cache_dir.mkdir(exist_ok=True)

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

    def _get_cached_path(self, version: str) -> Path:
        """Get path for cached update file."""
        return self._cache_dir / f"sombra_update_{version}.zip"

    def download_update(self):
        """Download the latest update (or use cached version)."""
        if not self._download_url or not self._latest_version:
            self.error.emit("No update URL available")
            return

        if self._downloader and self._downloader.isRunning():
            return

        # Git-based update doesn't need download
        if self._download_url == "git-pull":
            logger.info("Git-based update - no download needed")
            self._update_path = "git-pull"
            self.update_ready.emit("git-pull")
            return

        # Check if already downloaded
        cached_path = self._get_cached_path(self._latest_version)
        if cached_path.exists():
            logger.info(f"Using cached update: {cached_path}")
            self._on_download_complete(str(cached_path))
            return

        logger.info(f"Starting download: {self._download_url}")
        self._downloader = UpdateDownloader(self._download_url, str(cached_path))
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

        if not self._update_path:
            logger.error("Update path not set")
            self.error.emit("Update file not found")
            return False

        try:
            if sys.platform == "win32":
                # Windows requires frozen executable
                if not getattr(sys, 'frozen', False):
                    logger.warning("Cannot apply update in development mode")
                    self.error.emit("Обновление недоступно в режиме разработки")
                    return False

                if not os.path.exists(self._update_path):
                    self.error.emit("Update file not found")
                    return False

                exe_path = Path(sys.executable)
                app_dir = exe_path.parent
                return self._apply_update_windows(app_dir)
            else:
                # Linux - source-based update (git pull or zip)
                return self._apply_update_linux_source()

        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            self.error.emit(f"Ошибка при установке обновления: {e}")
            return False

    def _apply_update_windows(self, app_dir: Path) -> bool:
        """Apply update on Windows."""
        import os as _os

        # Get actual paths from running executable
        current_exe = Path(sys.executable)
        exe_dir = current_exe.parent

        # Find the actual app directory (where _internal folder is)
        # This handles both correct installs (Program Files/Sombra/)
        # and broken installs (directly in Program Files/)
        if (exe_dir / "_internal").exists():
            # _internal is next to exe - this is the app dir
            app_install_dir = exe_dir
        elif (exe_dir.parent / "_internal").exists():
            # Weird case - shouldn't happen but handle it
            app_install_dir = exe_dir.parent
        else:
            # Fallback to exe directory
            app_install_dir = exe_dir

        zip_path = str(self._update_path).replace('/', '\\')
        dest_path = str(app_install_dir).replace('/', '\\')
        exe_path = str(app_install_dir / 'Sombra.exe').replace('/', '\\')

        logger.info(f"Update: exe={current_exe}, app_dir={app_install_dir}, dest={dest_path}")

        # Check if needs admin rights
        needs_admin = "program files" in dest_path.lower()

        # Temp extraction folder
        temp_extract = str(Path(tempfile.gettempdir()) / "sombra_update_extract").replace('/', '\\')

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

:: Step 1: Rename running exe (Windows allows this!)
echo [1/6] Renaming old executable...
del "{dest_path}\\Sombra_old.exe" 2>nul
if exist "{exe_path}" ren "{exe_path}" Sombra_old.exe

:: Step 2: Kill process
echo [2/6] Stopping Sombra...
taskkill /f /im Sombra.exe >nul 2>&1
taskkill /f /im Sombra_old.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Step 3: Extract to temp folder first
echo [3/6] Extracting to temp...
rd /s /q "{temp_extract}" 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '{zip_path}' -DestinationPath '{temp_extract}' -Force"

if not exist "{temp_extract}\\Sombra.exe" (
    echo ERROR: Extraction failed!
    pause
    exit /b 1
)

:: Step 4: Use robocopy to mirror (handles read-only, retries)
:: /XF excludes .env and .env.example from being deleted
echo [4/6] Installing files...
robocopy "{temp_extract}" "{dest_path}" /MIR /R:3 /W:1 /NP /NFL /NDL /NJH /NJS /XF .env .env.example >nul

:: Step 5: Cleanup
echo [5/6] Cleaning up...
del "{dest_path}\\Sombra_old.exe" 2>nul
rd /s /q "{temp_extract}" 2>nul

:: Step 6: Launch
echo [6/6] Starting Sombra...
start "" "{exe_path}"

del "{zip_path}" 2>nul
timeout /t 2 /nobreak >nul
del "%~f0"
'''
        else:
            # Simple script without elevation (same logic)
            script = f'''@echo off
chcp 65001 >nul
echo Sombra Update Script
echo ====================
echo.

echo [1/6] Renaming old executable...
del "{dest_path}\\Sombra_old.exe" 2>nul
if exist "{exe_path}" ren "{exe_path}" Sombra_old.exe

echo [2/6] Stopping Sombra...
taskkill /f /im Sombra.exe >nul 2>&1
taskkill /f /im Sombra_old.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [3/6] Extracting to temp...
rd /s /q "{temp_extract}" 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '{zip_path}' -DestinationPath '{temp_extract}' -Force"

if not exist "{temp_extract}\\Sombra.exe" (
    echo ERROR: Extraction failed!
    pause
    exit /b 1
)

echo [4/6] Installing files...
robocopy "{temp_extract}" "{dest_path}" /MIR /R:3 /W:1 /NP /NFL /NDL /NJH /NJS /XF .env .env.example >nul

echo [5/6] Cleaning up...
del "{dest_path}\\Sombra_old.exe" 2>nul
rd /s /q "{temp_extract}" 2>nul

echo [6/6] Starting Sombra...
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

    def _apply_update_linux_source(self) -> bool:
        """Apply source-based update on Linux (git pull or zip extraction)."""
        # Determine project directory
        project_dir = Path(__file__).parent.parent.parent.parent
        logger.info(f"Linux update - project dir: {project_dir}")

        # If git repo exists, use git pull
        if (project_dir / ".git").exists():
            return self._git_pull_update(project_dir)

        # Otherwise, extract zip
        if self._update_path and self._update_path != "git-pull":
            return self._zip_extract_update(project_dir)

        self.error.emit("No update method available")
        return False

    def _git_pull_update(self, project_dir: Path) -> bool:
        """Update via git pull."""
        logger.info(f"Git pull update in: {project_dir}")

        # Find venv activate path
        venv_activate = project_dir / ".venv" / "bin" / "activate"

        script = f'''#!/bin/bash
echo ""
echo "=============================="
echo "  Sombra Linux Auto-Update"
echo "=============================="
echo ""

# Wait for app to close
sleep 2

cd "{project_dir}"

echo "[1/3] Pulling updates from GitHub..."
git fetch origin
git reset --hard origin/master
echo "Done."

echo ""
echo "[2/3] Updating dependencies..."
if [ -f "{venv_activate}" ]; then
    source "{venv_activate}"
fi
pip install -e . -q 2>/dev/null || pip install -e .
echo "Done."

echo ""
echo "[3/3] Restarting Sombra..."
cd "{project_dir}"
if [ -f "{venv_activate}" ]; then
    source "{venv_activate}"
fi
nohup python -m sombra > /dev/null 2>&1 &
echo "Started."

echo ""
echo "Update complete!"
sleep 2

# Cleanup
rm "$0"
'''
        return self._run_linux_script(script)

    def _zip_extract_update(self, project_dir: Path) -> bool:
        """Update via zip extraction."""
        logger.info(f"Zip extract update to: {project_dir}")

        venv_activate = project_dir / ".venv" / "bin" / "activate"

        script = f'''#!/bin/bash
echo ""
echo "=============================="
echo "  Sombra Linux Auto-Update"
echo "=============================="
echo ""

sleep 2

echo "[1/3] Extracting update..."
unzip -o "{self._update_path}" -d "{project_dir}"
echo "Done."

echo ""
echo "[2/3] Updating dependencies..."
cd "{project_dir}"
if [ -f "{venv_activate}" ]; then
    source "{venv_activate}"
fi
pip install -e . -q 2>/dev/null || pip install -e .
echo "Done."

echo ""
echo "[3/3] Restarting Sombra..."
if [ -f "{venv_activate}" ]; then
    source "{venv_activate}"
fi
nohup python -m sombra > /dev/null 2>&1 &
echo "Started."

echo ""
echo "Update complete!"
sleep 2

# Cleanup
rm "{self._update_path}"
rm "$0"
'''
        return self._run_linux_script(script)

    def _run_linux_script(self, script: str) -> bool:
        """Run update script in new terminal and exit app."""
        script_path = Path(tempfile.gettempdir()) / "sombra_update.sh"
        script_path.write_text(script)
        os.chmod(script_path, 0o755)

        logger.info(f"Running update script: {script_path}")

        # Try to run in a visible terminal
        terminals = [
            ["gnome-terminal", "--", "bash", str(script_path)],
            ["konsole", "-e", "bash", str(script_path)],
            ["xfce4-terminal", "-e", f"bash {script_path}"],
            ["xterm", "-e", f"bash {script_path}"],
        ]

        launched = False
        for term_cmd in terminals:
            try:
                subprocess.Popen(
                    term_cmd,
                    start_new_session=True,
                    close_fds=True
                )
                logger.info(f"Launched update in terminal: {term_cmd[0]}")
                launched = True
                break
            except FileNotFoundError:
                continue

        # Fallback: run in background without terminal
        if not launched:
            logger.info("No terminal found, running in background")
            subprocess.Popen(
                ["bash", str(script_path)],
                start_new_session=True,
                close_fds=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Exit application
        logger.info("Exiting application for update...")
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
