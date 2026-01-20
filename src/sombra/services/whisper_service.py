"""ElevenLabs Scribe STT service - Speech-to-Text via ElevenLabs API."""

import logging
from typing import Optional

import httpx
from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings
from ..core.async_bridge import get_async_bridge

logger = logging.getLogger(__name__)


class WhisperService(QObject):
    """ElevenLabs Scribe Speech-to-Text API client.

    Uses ElevenLabs Scribe v1 model for transcription.
    Fallback to local Whisper server if ElevenLabs key not configured.
    """

    ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

    # Signals
    transcription_started = Signal()
    transcription_completed = Signal(str)
    transcription_error = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        settings = get_settings()
        self._elevenlabs_key = settings.elevenlabs_api_key
        self._fallback_url = settings.stt_url  # Local Whisper fallback
        self._client: Optional[httpx.AsyncClient] = None

        # Log which STT backend we're using
        if self._elevenlabs_key:
            logger.info("STT: Using ElevenLabs Scribe API")
        else:
            logger.info(f"STT: Using local Whisper at {self._fallback_url}")

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def transcribe(self, audio_data: bytes) -> str:
        """Send audio to STT service and return transcription.

        Args:
            audio_data: WAV-formatted audio bytes.

        Returns:
            Transcribed text.

        Raises:
            httpx.HTTPError: On network or server errors.
        """
        if self._elevenlabs_key:
            return await self._transcribe_elevenlabs(audio_data)
        else:
            return await self._transcribe_local(audio_data)

    async def _transcribe_elevenlabs(self, audio_data: bytes) -> str:
        """Transcribe using ElevenLabs Scribe API."""
        client = await self._ensure_client()

        headers = {
            "xi-api-key": self._elevenlabs_key,
        }

        # Send as multipart form data
        files = {
            "file": ("audio.wav", audio_data, "audio/wav"),
        }
        data = {
            "model_id": "scribe_v1",
            "language_code": "ru",  # Russian, can be made configurable
        }

        logger.info("STT: Sending to ElevenLabs Scribe...")

        response = await client.post(
            self.ELEVENLABS_STT_URL,
            headers=headers,
            files=files,
            data=data,
        )
        response.raise_for_status()

        result = response.json()
        text = result.get("text", "")

        logger.info(f"STT: Transcribed {len(text)} chars")
        return text

    async def _transcribe_local(self, audio_data: bytes) -> str:
        """Transcribe using local Whisper server (fallback)."""
        client = await self._ensure_client()

        files = {"file": ("audio.wav", audio_data, "audio/wav")}

        logger.info(f"STT: Sending to local Whisper at {self._fallback_url}")

        response = await client.post(self._fallback_url, files=files)
        response.raise_for_status()

        result = response.json()

        # Handle different response formats
        if isinstance(result, dict):
            return result.get("text", result.get("transcription", ""))
        elif isinstance(result, str):
            return result
        else:
            return str(result)

    def transcribe_async(self, audio_data: bytes) -> None:
        """Non-blocking transcription (emits signals).

        Args:
            audio_data: WAV-formatted audio bytes.
        """
        self.transcription_started.emit()

        async def do_transcribe() -> None:
            try:
                text = await self.transcribe(audio_data)
                self.transcription_completed.emit(text)
            except httpx.HTTPError as e:
                error_msg = f"Transcription failed: {e}"
                logger.error(error_msg)
                self.transcription_error.emit(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.error(error_msg)
                self.transcription_error.emit(error_msg)

        bridge = get_async_bridge()
        bridge.run_coroutine(do_transcribe())

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def cleanup(self) -> None:
        """Clean up resources (sync wrapper)."""
        bridge = get_async_bridge()
        if bridge.is_running:
            bridge.run_coroutine(self.close())
