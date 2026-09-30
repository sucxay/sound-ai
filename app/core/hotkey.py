import os
from typing import Callable, Optional
from pynput import keyboard


class KeyboardController:
    """Manages global hotkey listening using pynput.
    The callback is executed without blocking the keyboard listener thread.
    """

    DEFAULT_HOTKEY = "<ctrl>+<space>"

    def __init__(
        self,
        on_trigger: Callable[[], None],
        hotkey: Optional[str] = None,
    ):
        """Initialize the keyboard controller.

        Args:
            on_trigger: Zero-argument callback invoked when the hotkey is pressed.
            hotkey: Hotkey string (e.g. '<ctrl>+<space>'). Defaults to HOTKEY env var or '<ctrl>+<space>'.
        """
        self._on_trigger = on_trigger
        self._hotkey_str = hotkey or os.getenv("HOTKEY", self.DEFAULT_HOTKEY)
        self._listener: Optional[keyboard.GlobalHotKeys] = None

    @property
    def hotkey_str(self) -> str:
        return self._hotkey_str

    def _handle_hotkey(self) -> None:
        """Invoked when the hotkey combination is detected."""
        try:
            self._on_trigger()
        except Exception as exc:
            print(f"[ERROR] Exception in hotkey callback: {exc}")

    def start(self) -> None:
        """Start listening for the global hotkey in a background thread."""
        if self._listener is not None and self._listener.is_alive():
            return

        hotkey_map = {
            self._hotkey_str: self._handle_hotkey
        }

        self._listener = keyboard.GlobalHotKeys(hotkey_map)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """Stop the global hotkey listener."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
