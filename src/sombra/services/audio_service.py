"""Audio capture service with Silero VAD for end-of-speech detection."""

import io
import logging
import wave

import numpy as np
from PySide6.QtCore import QObject, Qt, Signal, Slot

from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# Import sounddevice
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except OSError as e:
    sd = None
    SOUNDDEVICE_AVAILABLE = False
    logger.warning(f"sounddevice not available: {e}")

# Import Silero VAD
try:
    import torch
    from silero_vad import load_silero_vad
    SILERO_VAD_AVAILABLE = True
except ImportError:
    load_silero_vad = None
    torch = None
    SILERO_VAD_AVAILABLE = False
    logger.warning("silero-vad not available")


class AudioService(QObject):
    """Audio recording with Silero VAD for end-of-speech detection."""

    SAMPLE_RATE = 16000
    CHANNELS = 1
    DTYPE = "int16"
    BLOCKSIZE = 512

    # VAD settings
    SPEECH_PROB_THRESHOLD = 0.5
    SILENCE_FRAMES_THRESHOLD = 47  # ~1.5 sec at 512 samples/frame (32ms)
    MAX_RECORDING_FRAMES = 940  # ~30 sec
    NO_SPEECH_TIMEOUT_FRAMES = 310  # ~10 sec - stop if no speech detected at all

    # Signals
    recording_started = Signal()
    recording_stopped = Signal(bytes)
    audio_level = Signal(float)
    error = Signal(str)
    _request_stop = Signal()  # Internal signal for thread-safe stop

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._stream = None
        self._buffer: io.BytesIO = io.BytesIO()
        self._is_recording = False
        self._device_id = None
        self._stop_requested = False  # Prevent multiple stop requests

        # VAD state
        self._vad_model = None
        self._auto_stop = False
        self._speech_detected = False
        self._silence_frames = 0
        self._total_frames = 0

        # Settings
        settings = get_settings()
        self._device_id = settings.audio_device_id
        self._sample_rate = settings.audio_sample_rate or self.SAMPLE_RATE

        # Load VAD
        if SILERO_VAD_AVAILABLE:
            try:
                self._vad_model = load_silero_vad()
                logger.info("Silero VAD loaded")
            except Exception as e:
                logger.error(f"Failed to load VAD: {e}")

        # Connect internal signal for thread-safe stop from callback
        self._request_stop.connect(self._do_stop, type=Qt.ConnectionType.QueuedConnection)

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    def start_recording(self, auto_stop: bool = False) -> None:
        if not SOUNDDEVICE_AVAILABLE:
            self.error.emit("Audio not available")
            return
        if self._is_recording:
            return

        self._buffer = io.BytesIO()
        self._is_recording = True
        self._stop_requested = False
        self._auto_stop = auto_stop and self._vad_model is not None
        self._speech_detected = False
        self._silence_frames = 0
        self._total_frames = 0

        if self._vad_model:
            self._vad_model.reset_states()

        mode = "auto-stop" if self._auto_stop else "manual"
        logger.info(f"Recording started ({mode})")

        try:
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self.CHANNELS,
                dtype=self.DTYPE,
                blocksize=self.BLOCKSIZE,
                device=self._device_id,
                callback=self._callback,
            )
            self._stream.start()
            self.recording_started.emit()
        except Exception as e:
            self._is_recording = False
            self.error.emit(f"Recording failed: {e}")

    def stop_recording(self) -> bytes:
        if not self._is_recording:
            return b""

        # Mark as stopping first to prevent callback from processing more data
        self._is_recording = False
        self._auto_stop = False
        self._stop_requested = True

        if self._stream:
            try:
                # Stop the stream - this blocks until callback finishes
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.warning(f"Error stopping stream: {e}")
            finally:
                self._stream = None

        data = self._buffer.getvalue()
        wav = self._to_wav(data)
        logger.info(f"Recording stopped ({len(data)} bytes, {self._total_frames} frames)")
        self.recording_stopped.emit(wav)
        return wav

    @Slot()
    def _do_stop(self) -> None:
        """Thread-safe stop handler called from main Qt thread."""
        logger.info(">>> _do_stop called from main thread")
        self.stop_recording()

    def _callback(self, indata, frames, time_info, status):
        if not self._is_recording or self._stop_requested:
            return

        self._buffer.write(indata.tobytes())
        self._total_frames += 1

        # Audio level (emit less frequently to reduce overhead)
        if self._total_frames % 3 == 0:
            rms = np.sqrt(np.mean(indata.astype(np.float32) ** 2))
            self.audio_level.emit(min(1.0, rms / 32767.0))

        # VAD
        if self._auto_stop and self._vad_model:
            audio = indata.flatten().astype(np.float32) / 32768.0
            tensor = torch.from_numpy(audio)

            with torch.no_grad():
                prob = self._vad_model(tensor, self.SAMPLE_RATE).item()

            is_speech = prob > self.SPEECH_PROB_THRESHOLD

            if is_speech:
                self._speech_detected = True
                self._silence_frames = 0
            elif self._speech_detected:
                self._silence_frames += 1

            # Log every ~1 sec
            if self._total_frames % 31 == 0:
                sil = f"{self._silence_frames}/{self.SILENCE_FRAMES_THRESHOLD}"
                logger.info(
                    f"VAD: prob={prob:.2f} speech={self._speech_detected} "
                    f"silence={sil} frames={self._total_frames}"
                )

            # Auto-stop conditions
            should_stop = False
            stop_reason = ""

            # 1. Speech ended (silence after speech)
            if self._speech_detected and self._silence_frames >= self.SILENCE_FRAMES_THRESHOLD:
                stop_reason = "silence after speech"
                should_stop = True

            # 2. Max duration
            elif self._total_frames >= self.MAX_RECORDING_FRAMES:
                stop_reason = "max duration"
                should_stop = True

            # 3. No speech timeout (nothing detected for too long)
            elif not self._speech_detected and self._total_frames >= self.NO_SPEECH_TIMEOUT_FRAMES:
                stop_reason = "no speech timeout"
                should_stop = True

            if should_stop and not self._stop_requested:
                self._stop_requested = True
                logger.info(f">>> AUTO-STOP TRIGGERED: {stop_reason}")
                self._request_stop.emit()

    def _to_wav(self, data: bytes) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(self.CHANNELS)
            w.setsampwidth(2)
            w.setframerate(self._sample_rate)
            w.writeframes(data)
        return buf.getvalue()

    @staticmethod
    def get_audio_devices():
        if not SOUNDDEVICE_AVAILABLE:
            return []
        return [
            {"id": i, "name": d["name"]}
            for i, d in enumerate(sd.query_devices())
            if d["max_input_channels"] > 0
        ]

    def set_device(self, device_id):
        self._device_id = device_id

    def cleanup(self):
        if self._is_recording:
            self.stop_recording()
