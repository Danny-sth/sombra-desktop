"""Global hotkey service using pynput."""

import threading
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from ..config.settings import get_settings

# Try to import pynput - it requires Xlib on Linux
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except (ImportError, Exception) as e:
    keyboard = None  # type: ignore
    PYNPUT_AVAILABLE = False
    print(f"Warning: pynput not available ({e}). Global hotkeys disabled.")


class HotkeyService(QObject):
    """Global hotkey management using pynput.

    Listens for global keyboard shortcuts even when the app is not focused.
    Uses Qt signals to safely communicate with the main thread.
    """

    # Signals
    hotkey_pressed = Signal(str)  # Hotkey name
    hotkey_released = Signal(str)  # Hotkey name
    error = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self._listener: Optional[Any] = None  # keyboard.Listener when available
        self._hotkeys: dict[str, set[str]] = {}  # name -> set of key strings
        self._pressed_keys: set[str] = set()
        self._active_hotkey: Optional[str] = None
        self._running = False
        self._lock = threading.Lock()

        # Build modifier keys mapping if pynput is available
        self._modifier_keys: dict[str, set] = {}
        if PYNPUT_AVAILABLE and keyboard is not None:
            self._modifier_keys = {
                "ctrl": {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
                "alt": {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
                "shift": {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
                "cmd": {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
                "win": {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r},
            }

        # Load default hotkey from settings
        settings = get_settings()
        if settings.global_hotkey:
            self.register_hotkey("push_to_talk", settings.global_hotkey)

    def register_hotkey(self, name: str, keys: str) -> None:
        """Register a hotkey combination.

        Args:
            name: Unique name for this hotkey.
            keys: Key combination string (e.g., 'ctrl+shift+s').
        """
        # Parse key combination
        key_parts = {k.strip().lower() for k in keys.split("+")}
        self._hotkeys[name] = key_parts

    def unregister_hotkey(self, name: str) -> None:
        """Remove a registered hotkey.

        Args:
            name: Name of the hotkey to remove.
        """
        self._hotkeys.pop(name, None)

    def start(self) -> None:
        """Start listening for hotkeys."""
        if not PYNPUT_AVAILABLE:
            self.error.emit("Global hotkeys not available (pynput library not found)")
            return

        if self._running:
            return

        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self) -> None:
        """Stop the hotkey listener."""
        self._running = False

        if self._listener is not None:
            self._listener.stop()
            self._listener = None

        with self._lock:
            self._pressed_keys.clear()
            self._active_hotkey = None

    def _key_to_string(self, key: Any) -> str:
        """Convert a key to its string representation."""
        if not PYNPUT_AVAILABLE or keyboard is None:
            return str(key)

        # Check modifiers
        for mod_name, mod_keys in self._modifier_keys.items():
            if key in mod_keys:
                return mod_name

        # Regular key
        if isinstance(key, keyboard.KeyCode):
            if key.char:
                return key.char.lower()
            elif key.vk:
                return f"vk_{key.vk}"
        elif isinstance(key, keyboard.Key):
            return key.name.lower()

        return str(key)

    def _on_press(self, key: Any) -> None:
        """Handle key press event (called in listener thread)."""
        if not self._running:
            return

        key_str = self._key_to_string(key)

        with self._lock:
            self._pressed_keys.add(key_str)

            # Check if any hotkey combination is satisfied
            for name, required_keys in self._hotkeys.items():
                if required_keys <= self._pressed_keys:
                    if self._active_hotkey != name:
                        self._active_hotkey = name
                        # Emit signal (thread-safe)
                        self.hotkey_pressed.emit(name)
                    break

    def _on_release(self, key: Any) -> None:
        """Handle key release event (called in listener thread)."""
        if not self._running:
            return

        key_str = self._key_to_string(key)

        with self._lock:
            self._pressed_keys.discard(key_str)

            # Check if active hotkey is no longer satisfied
            if self._active_hotkey:
                required_keys = self._hotkeys.get(self._active_hotkey, set())
                if not required_keys <= self._pressed_keys:
                    released_hotkey = self._active_hotkey
                    self._active_hotkey = None
                    # Emit signal (thread-safe)
                    self.hotkey_released.emit(released_hotkey)

    def set_hotkey(self, name: str, keys: str) -> None:
        """Update or create a hotkey.

        Args:
            name: Hotkey name.
            keys: New key combination.
        """
        self.register_hotkey(name, keys)

    def get_current_hotkey(self, name: str) -> Optional[str]:
        """Get the current key combination for a hotkey.

        Args:
            name: Hotkey name.

        Returns:
            Key combination string or None.
        """
        keys = self._hotkeys.get(name)
        if keys:
            return "+".join(sorted(keys))
        return None

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
