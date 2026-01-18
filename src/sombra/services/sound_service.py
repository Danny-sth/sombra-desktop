"""Sound notification service."""

import logging
import numpy as np
import threading

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
    SOUND_AVAILABLE = True
except ImportError:
    sd = None
    SOUND_AVAILABLE = False


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
