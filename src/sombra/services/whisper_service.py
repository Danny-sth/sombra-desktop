"""Whisper STT service - communicates with local Whisper server."""

from typing import Optional

import httpx
from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings
from ..core.async_bridge import get_async_bridge


class WhisperService(QObject):
    """Whisper Speech-to-Text API client.

    Sends audio to a local Whisper server for transcription.
    Expected endpoint: POST /transcribe with audio file.
    """

    # Signals
    transcription_started = Signal()
    transcription_completed = Signal(str)
    transcription_error = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        settings = get_settings()
        self._endpoint = settings.stt_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def transcribe(self, audio_data: bytes) -> str:
        """Send audio to Whisper and return transcription.

        Args:
            audio_data: WAV-formatted audio bytes.

        Returns:
            Transcribed text.

        Raises:
            httpx.HTTPError: On network or server errors.
        """
        client = await self._ensure_client()

        # Send as multipart form data with audio file
        files = {"file": ("audio.wav", audio_data, "audio/wav")}

        response = await client.post(self._endpoint, files=files)
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
                self.transcription_error.emit(f"Transcription failed: {e}")
            except Exception as e:
                self.transcription_error.emit(f"Unexpected error: {e}")

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
