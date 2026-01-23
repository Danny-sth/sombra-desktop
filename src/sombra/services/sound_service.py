"""Sound notification service."""

import io
import logging
import threading
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    SOUND_AVAILABLE = True
except ImportError:
    sd = None
    SOUND_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    AudioSegment = None
    PYDUB_AVAILABLE = False


class SoundService:
    """Simple sound notification service."""

    SAMPLE_RATE = 44100

    @staticmethod
    def _generate_tone(frequency: float, duration: float, volume: float = 0.3) -> np.ndarray:
        """Generate a sine wave tone."""
        t = np.linspace(0, duration, int(SoundService.SAMPLE_RATE * duration), False)
        tone = np.sin(2 * np.pi * frequency * t) * volume
        # Apply fade in/out to avoid clicks
        fade_samples = int(0.01 * SoundService.SAMPLE_RATE)
        tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
        tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        return tone.astype(np.float32)

    @staticmethod
    def play_start_sound():
        """Play sound when recording starts (ascending tone)."""
        if not SOUND_AVAILABLE:
            return

        def _play():
            try:
                # Two quick ascending tones
                tone1 = SoundService._generate_tone(600, 0.1, 0.25)
                tone2 = SoundService._generate_tone(900, 0.15, 0.25)
                silence = np.zeros(int(0.05 * SoundService.SAMPLE_RATE), dtype=np.float32)
                sound = np.concatenate([tone1, silence, tone2])
                sd.play(sound, SoundService.SAMPLE_RATE)
                sd.wait()
            except Exception as e:
                logger.debug(f"Sound play error: {e}")

        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def play_stop_sound():
        """Play sound when recording stops (descending tone)."""
        if not SOUND_AVAILABLE:
            return

        def _play():
            try:
                # Single descending tone
                tone = SoundService._generate_tone(500, 0.2, 0.2)
                sd.play(tone, SoundService.SAMPLE_RATE)
                sd.wait()
            except Exception as e:
                logger.debug(f"Sound play error: {e}")

        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def play_wake_sound():
        """Play sound when wake word detected."""
        if not SOUND_AVAILABLE:
            return

        def _play():
            try:
                # Quick chirp
                tone = SoundService._generate_tone(800, 0.1, 0.3)
                sd.play(tone, SoundService.SAMPLE_RATE)
                sd.wait()
            except Exception as e:
                logger.debug(f"Sound play error: {e}")

        threading.Thread(target=_play, daemon=True).start()

    # Track current playback for interruption
    _current_playback: Optional[threading.Event] = None
    _playback_lock = threading.Lock()

    @classmethod
    def play_audio(cls, audio_data: bytes, format: str = "mp3") -> None:
        """Play audio data (MP3 or WAV).

        Args:
            audio_data: Audio bytes.
            format: Audio format ('mp3' or 'wav').
        """
        if not SOUND_AVAILABLE:
            logger.warning("sounddevice not available")
            return

        if not PYDUB_AVAILABLE:
            logger.warning("pydub not available - cannot decode MP3")
            return

        def _play():
            try:
                # Stop any current playback
                with cls._playback_lock:
                    if cls._current_playback:
                        cls._current_playback.set()

                    stop_event = threading.Event()
                    cls._current_playback = stop_event

                # Decode audio
                audio_io = io.BytesIO(audio_data)
                audio = AudioSegment.from_file(audio_io, format=format)

                # Convert to numpy array
                samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
                samples = samples / (2 ** 15)  # Normalize to [-1, 1]

                # Handle stereo
                if audio.channels == 2:
                    samples = samples.reshape((-1, 2))

                logger.info(
                    f"Playing audio: {len(samples)} samples, "
                    f"{audio.frame_rate}Hz, {audio.channels}ch"
                )

                # Play with interruption support
                sd.play(samples, audio.frame_rate)

                # Wait for playback or interruption
                while sd.get_stream().active:
                    if stop_event.is_set():
                        sd.stop()
                        logger.info("Audio playback interrupted")
                        break
                    stop_event.wait(0.1)

                with cls._playback_lock:
                    if cls._current_playback is stop_event:
                        cls._current_playback = None

            except Exception as e:
                logger.error(f"Audio playback error: {e}")

        threading.Thread(target=_play, daemon=True).start()

    @classmethod
    def stop_playback(cls) -> None:
        """Stop current audio playback."""
        with cls._playback_lock:
            if cls._current_playback:
                cls._current_playback.set()
                logger.info("Stopping audio playback")
