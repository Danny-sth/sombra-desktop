"""Wake word detection service using Picovoice Porcupine."""

import logging
import threading
import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# Try to import dependencies
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    pvporcupine = None
    PORCUPINE_AVAILABLE = False

try:
    import pyaudio
    import numpy as np
    PYAUDIO_AVAILABLE = True
except (ImportError, OSError):
    pyaudio = None
    np = None
    PYAUDIO_AVAILABLE = False


class WakeWordService(QObject):
    """Wake word detection using Picovoice Porcupine.

    Listens continuously for "Sombra" wake word and emits signal when detected.
    """

    # Signals
    wake_word_detected = Signal()
    listening_started = Signal()
    listening_stopped = Signal()
    error = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._porcupine = None
        self._is_listening = False
        self._listen_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pa: Optional[pyaudio.PyAudio] = None
        self._stream = None

        # Get settings
        settings = get_settings()
        self._access_key = getattr(settings, 'porcupine_access_key', None) or os.getenv('PORCUPINE_ACCESS_KEY', '')

        # Model paths
        self._model_path = self._find_model_path("sombra.ppn")
        self._language_model_path = self._find_model_path("porcupine_params_pt.pv")

    def _find_model_path(self, filename: str) -> Optional[str]:
        """Find a model file by name."""
        # __file__ = src/sombra/services/wakeword_service.py
        project_root = Path(__file__).parent.parent.parent.parent  # -> sombra-desktop/
        possible_paths = [
            project_root / "models" / filename,
            Path.home() / ".local" / "share" / "sombra" / "models" / filename,
            Path("/usr/share/sombra/models") / filename,
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Found model at: {path}")
                return str(path)

        logger.warning(f"Model not found: {filename}")
        return None

    @property
    def is_available(self) -> bool:
        """Check if wake word detection is available."""
        if not PORCUPINE_AVAILABLE or not PYAUDIO_AVAILABLE:
            return False
        if not self._access_key:
            logger.warning("Porcupine access key not configured")
            return False
        if not self._model_path:
            return False
        return True

    @property
    def is_listening(self) -> bool:
        """Check if currently listening for wake word."""
        return self._is_listening

    def start_listening(self) -> bool:
        """Start listening for wake word.

        Returns:
            True if started successfully, False otherwise.
        """
        if not self.is_available:
            if not self._access_key:
                self.error.emit("Porcupine access key not configured. Set PORCUPINE_ACCESS_KEY in .env")
            elif not self._model_path:
                self.error.emit("Wake word model not found")
            else:
                self.error.emit("Wake word detection not available (missing dependencies)")
            return False

        if self._is_listening:
            return True

        try:
            # Initialize Porcupine with Portuguese model
            logger.info("Loading Porcupine wake word model...")
            self._porcupine = pvporcupine.create(
                access_key=self._access_key,
                keyword_paths=[self._model_path],
                model_path=self._language_model_path
            )
            logger.info(f"Porcupine initialized. Frame length: {self._porcupine.frame_length}")
        except Exception as e:
            logger.error(f"Failed to initialize Porcupine: {e}")
            self.error.emit(f"Failed to initialize wake word: {e}")
            return False

        # Initialize PyAudio
        try:
            self._pa = pyaudio.PyAudio()
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            self.error.emit(f"Failed to initialize audio: {e}")
            self._cleanup_porcupine()
            return False

        # Start listening thread
        self._stop_event.clear()
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()

        self._is_listening = True
        self.listening_started.emit()
        logger.info("Wake word detection started (Sombra)")
        return True

    def stop_listening(self) -> None:
        """Stop listening for wake word."""
        if not self._is_listening:
            return

        self._stop_event.set()

        if self._listen_thread:
            self._listen_thread.join(timeout=2.0)
            self._listen_thread = None

        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        if self._pa:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None

        self._cleanup_porcupine()
        self._is_listening = False
        self.listening_stopped.emit()
        logger.info("Wake word detection stopped")

    def _cleanup_porcupine(self) -> None:
        """Clean up Porcupine resources."""
        if self._porcupine:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None

    def _listen_loop(self) -> None:
        """Main listening loop (runs in separate thread)."""
        if not self._porcupine or not self._pa:
            return

        try:
            # Open audio stream
            self._stream = self._pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self._porcupine.sample_rate,
                input=True,
                frames_per_buffer=self._porcupine.frame_length
            )

            logger.info(f"Audio stream opened at {self._porcupine.sample_rate}Hz, listening...")

            while not self._stop_event.is_set():
                try:
                    # Read audio chunk
                    audio_data = self._stream.read(self._porcupine.frame_length, exception_on_overflow=False)
                    audio = np.frombuffer(audio_data, dtype=np.int16)

                    # Process with Porcupine
                    result = self._porcupine.process(audio)

                    if result >= 0:
                        logger.info("Wake word 'Sombra' detected!")
                        self.wake_word_detected.emit()

                except Exception as e:
                    if not self._stop_event.is_set():
                        logger.error(f"Error reading audio: {e}")

        except Exception as e:
            logger.error(f"Wake word listening error: {e}")
            if not self._stop_event.is_set():
                self.error.emit(f"Wake word listening error: {e}")

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_listening()
