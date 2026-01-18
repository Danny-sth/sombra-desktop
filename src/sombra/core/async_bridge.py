"""AsyncBridge - Bridge between asyncio event loop and Qt main thread."""

import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Callable, Coroutine, Optional

from PySide6.QtCore import QObject, Signal, Slot


class AsyncBridge(QObject):
    """Bridges asyncio coroutines with Qt event loop.

    Runs an asyncio event loop in a separate thread and provides methods
    to schedule coroutines from the Qt main thread. Results are delivered
    back to the main thread via Qt signals.

    Usage:
        bridge = AsyncBridge()
        bridge.start()

        # Run a coroutine
        bridge.run_coroutine(some_async_function())

        # Run and get result via callback
        bridge.run_with_callback(some_async_function(), on_complete)

        # Clean shutdown
        bridge.stop()
    """

    # Signal emitted when a coroutine completes (result, error)
    task_completed = Signal(object, object)

    # Signal emitted when an error occurs in the async loop
    error_occurred = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if the async bridge is running."""
        return self._running and self._thread is not None and self._thread.is_alive()

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """Get the asyncio event loop."""
        return self._loop

    def start(self) -> None:
        """Start the async event loop thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # Wait for loop to be ready
        while self._loop is None and self._running:
            threading.Event().wait(0.01)

    def stop(self) -> None:
        """Stop the async event loop thread."""
        if not self._running:
            return

        self._running = False

        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

        self._loop = None

    def _run_loop(self) -> None:
        """Run the asyncio event loop (called in thread)."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_forever()
        finally:
            # Cancel all pending tasks
            pending = asyncio.all_tasks(self._loop)
            for task in pending:
                task.cancel()

            # Run until all tasks are cancelled
            if pending:
                self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            self._loop.close()

    def run_coroutine(self, coro: Coroutine[Any, Any, Any]) -> None:
        """Schedule a coroutine to run in the async thread.

        Args:
            coro: The coroutine to run.
        """
        if not self.is_running or self._loop is None:
            self.error_occurred.emit("AsyncBridge is not running")
            return

        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def run_coroutine_threadsafe(self, coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        """Run coroutine and return a Future for the result.

        Args:
            coro: The coroutine to run.

        Returns:
            A Future that will contain the result.

        Raises:
            RuntimeError: If the bridge is not running.
        """
        if not self.is_running or self._loop is None:
            raise RuntimeError("AsyncBridge is not running")

        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def run_with_callback(
        self,
        coro: Coroutine[Any, Any, Any],
        callback: Callable[[Any], None],
        error_callback: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        """Run a coroutine and call callback with result on completion.

        The callback is called in the async thread. For Qt thread safety,
        use signals instead.

        Args:
            coro: The coroutine to run.
            callback: Function called with result on success.
            error_callback: Optional function called with exception on error.
        """
        if not self.is_running or self._loop is None:
            if error_callback:
                error_callback(RuntimeError("AsyncBridge is not running"))
            return

        async def wrapped() -> None:
            try:
                result = await coro
                callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
                else:
                    self.error_occurred.emit(str(e))

        asyncio.run_coroutine_threadsafe(wrapped(), self._loop)

    @Slot()
    def shutdown(self) -> None:
        """Qt slot for clean shutdown."""
        self.stop()


# Global async bridge instance
_async_bridge: AsyncBridge | None = None


def get_async_bridge() -> AsyncBridge:
    """Get the global AsyncBridge instance."""
    global _async_bridge
    if _async_bridge is None:
        _async_bridge = AsyncBridge()
    return _async_bridge


def init_async_bridge(parent: QObject | None = None) -> AsyncBridge:
    """Initialize or reinitialize the AsyncBridge."""
    global _async_bridge
    if _async_bridge is not None:
        _async_bridge.stop()
    _async_bridge = AsyncBridge(parent)
    return _async_bridge
