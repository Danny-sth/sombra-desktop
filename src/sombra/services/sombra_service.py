"""Sombra API service with SSE streaming support."""

import json
from typing import Optional

import httpx
from httpx_sse import aconnect_sse
from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings
from ..core.async_bridge import get_async_bridge
from ..core.session import get_session_manager


class SombraService(QObject):
    """Sombra backend API client with SSE streaming support.

    Handles communication with Sombra backend:
    - POST /api/chat - Send messages
    - GET /api/thinking/stream/{sessionId} - Real-time thinking updates (SSE)
    """

    # Signals
    query_sent = Signal(str)
    chunk_received = Signal(str)
    thinking_update = Signal(str)
    stream_completed = Signal()
    stream_error = Signal(str)
    response_received = Signal(str)
    connection_status = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        settings = get_settings()
        self._base_url = settings.sombra_api_url
        self._client: Optional[httpx.AsyncClient] = None
        self._cancel_requested = False

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def send_chat(self, query: str) -> str:
        """Send chat query and process response.

        Args:
            query: The message to send.

        Returns:
            The response text.
        """
        client = await self._ensure_client()
        session = get_session_manager()

        payload = {
            "query": query,
            "sessionId": session.session_id,
        }

        self.query_sent.emit(query)
        self.connection_status.emit("Sending query...")

        try:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json=payload,
                headers=session.get_headers(),
            )
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "")

            self.response_received.emit(response_text)
            self.stream_completed.emit()
            self.connection_status.emit("Connected")

            return response_text

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                error_msg = "Rate limited - please wait a moment and try again"
            elif e.response.status_code == 503:
                error_msg = "Server is busy - please try again later"
            else:
                error_msg = f"API error ({e.response.status_code}): {e.response.text[:100]}"
            self.stream_error.emit(error_msg)
            self.connection_status.emit("Error")
            raise
        except httpx.HTTPError as e:
            error_msg = f"Connection error: {e}"
            self.stream_error.emit(error_msg)
            self.connection_status.emit("Error")
            raise

    async def send_chat_with_thinking(self, query: str) -> str:
        """Send chat and listen to thinking stream in parallel.

        This method:
        1. Starts listening to the thinking SSE stream
        2. Sends the chat request
        3. Emits thinking updates as they arrive
        4. Returns the final response

        Args:
            query: The message to send.

        Returns:
            The response text.
        """
        import asyncio

        client = await self._ensure_client()
        session = get_session_manager()

        self._cancel_requested = False
        self.query_sent.emit(query)
        self.connection_status.emit("Connecting...")

        thinking_task = None
        final_response = ""

        async def listen_thinking() -> None:
            """Listen to SSE thinking stream."""
            try:
                async with aconnect_sse(
                    client,
                    "GET",
                    f"{self._base_url}/api/thinking/stream/{session.session_id}",
                    headers=session.get_headers(),
                ) as sse:
                    async for event in sse.aiter_sse():
                        if self._cancel_requested:
                            break

                        if event.data:
                            try:
                                data = json.loads(event.data)
                                msg_type = data.get("type", "")
                                message = data.get("message", "")

                                if msg_type == "thinking":
                                    self.thinking_update.emit(message)
                                elif msg_type == "complete":
                                    break
                                elif msg_type == "connected":
                                    self.connection_status.emit("Connected")
                            except json.JSONDecodeError:
                                # Raw text message
                                self.chunk_received.emit(event.data)

            except httpx.HTTPError:
                # SSE stream ended or errored - this is expected
                pass

        async def send_chat_request() -> str:
            """Send the chat request."""
            payload = {
                "query": query,
                "sessionId": session.session_id,
            }

            response = await client.post(
                f"{self._base_url}/api/chat",
                json=payload,
                headers=session.get_headers(),
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        try:
            # Start thinking listener
            thinking_task = asyncio.create_task(listen_thinking())

            # Small delay to ensure SSE connection is established
            await asyncio.sleep(0.1)

            # Send chat request
            final_response = await send_chat_request()

            # Cancel thinking task
            self._cancel_requested = True
            if thinking_task and not thinking_task.done():
                thinking_task.cancel()
                try:
                    await thinking_task
                except asyncio.CancelledError:
                    pass

            self.response_received.emit(final_response)
            self.stream_completed.emit()
            self.connection_status.emit("Connected")

            return final_response

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                error_msg = "Rate limited - please wait a moment and try again"
            elif e.response.status_code == 503:
                error_msg = "Server is busy - please try again later"
            else:
                error_msg = f"API error ({e.response.status_code}): {e.response.text[:100]}"
            self.stream_error.emit(error_msg)
            self.connection_status.emit("Error")

            if thinking_task and not thinking_task.done():
                thinking_task.cancel()

            raise
        except httpx.HTTPError as e:
            error_msg = f"Connection error: {e}"
            self.stream_error.emit(error_msg)
            self.connection_status.emit("Error")

            if thinking_task and not thinking_task.done():
                thinking_task.cancel()

            raise

    def send_chat_async(self, query: str, with_thinking: bool = True, max_retries: int = 3) -> None:
        """Non-blocking chat (emits signals) with automatic retry on rate limit.

        Args:
            query: The message to send.
            with_thinking: Whether to listen to thinking stream.
            max_retries: Maximum retry attempts for rate limiting.
        """
        import asyncio

        async def do_chat() -> None:
            retries = 0
            while retries <= max_retries:
                try:
                    if with_thinking:
                        await self.send_chat_with_thinking(query)
                    else:
                        await self.send_chat(query)
                    return
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and retries < max_retries:
                        retries += 1
                        wait_time = 2 ** retries  # Exponential backoff: 2, 4, 8 seconds
                        self.connection_status.emit(f"Rate limited, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
                except Exception:
                    raise

        bridge = get_async_bridge()
        bridge.run_coroutine(do_chat())

    def cancel_stream(self) -> None:
        """Cancel ongoing stream."""
        self._cancel_requested = True

    async def check_connection(self) -> bool:
        """Check if backend is reachable.

        Returns:
            True if connected, False otherwise.
        """
        try:
            client = await self._ensure_client()
            response = await client.get(
                f"{self._base_url}/api/system/version",
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False

    def check_connection_async(self) -> None:
        """Non-blocking connection check."""

        async def do_check() -> None:
            connected = await self.check_connection()
            if connected:
                self.connection_status.emit("Connected")
            else:
                self.connection_status.emit("Disconnected")

        bridge = get_async_bridge()
        bridge.run_coroutine(do_check())

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def cleanup(self) -> None:
        """Clean up resources (sync wrapper)."""
        self._cancel_requested = True
        bridge = get_async_bridge()
        if bridge.is_running:
            bridge.run_coroutine(self.close())
