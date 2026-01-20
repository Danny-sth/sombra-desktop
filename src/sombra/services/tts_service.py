"""TTS service - communicates with Sombra server for text-to-speech."""

import logging
from typing import Optional

import httpx
from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings
from ..core.async_bridge import get_async_bridge

logger = logging.getLogger(__name__)


class TtsService(QObject):
    """Text-to-Speech API client.

    Sends text to Sombra server which proxies to ElevenLabs.
    Returns MP3 audio data.
    """

    # Signals
    synthesis_started = Signal()
    audio_ready = Signal(bytes)  # MP3 audio data
    synthesis_error = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        settings = get_settings()
        self._base_url = settings.sombra_api_url
        self._endpoint = f"{self._base_url}/api/tts"
        self._client: Optional[httpx.AsyncClient] = None
        self._enabled = getattr(settings, 'tts_enabled', True)

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @is_enabled.setter
    def is_enabled(self, value: bool) -> None:
        self._enabled = value

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def synthesize(self, text: str) -> bytes:
        """Send text to TTS server and return audio.

        Args:
            text: Text to synthesize.

        Returns:
            MP3 audio bytes.

        Raises:
            httpx.HTTPError: On network or server errors.
        """
        if not self._enabled:
            raise ValueError("TTS is disabled")

        client = await self._ensure_client()

        response = await client.post(
            self._endpoint,
            json={"text": text},
        )
        response.raise_for_status()

        return response.content

    def synthesize_async(self, text: str) -> None:
        """Non-blocking synthesis (emits signals).

        Args:
            text: Text to synthesize.
        """
        if not self._enabled:
            return

        # Skip empty text
        if not text or not text.strip():
            return

        self.synthesis_started.emit()
        logger.info(f"TTS synthesis started, text length: {len(text)}")

        async def do_synthesize() -> None:
            try:
                audio = await self.synthesize(text)
                logger.info(f"TTS synthesis completed, audio size: {len(audio)}")
                self.audio_ready.emit(audio)
            except httpx.HTTPError as e:
                error_msg = f"TTS failed: {e}"
                logger.error(error_msg)
                self.synthesis_error.emit(error_msg)
            except Exception as e:
                error_msg = f"TTS unexpected error: {e}"
                logger.error(error_msg)
                self.synthesis_error.emit(error_msg)

        bridge = get_async_bridge()
        bridge.run_coroutine(do_synthesize())

    async def check_status(self) -> dict:
        """Check TTS service status on server.

        Returns:
            Status dict with 'available', 'model', 'voice_id'.
        """
        client = await self._ensure_client()
        response = await client.get(f"{self._endpoint}/status")
        response.raise_for_status()
        return response.json()

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
