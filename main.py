#!/usr/bin/env python3
"""Voice Assistant — Keyboard-Activated Hotkey Entry Point.

Press the configured hotkey (default: CTRL + SPACE) from any application/window
to activate the voice assistant microphone and start speaking.

Exit:
  • Press Ctrl+C at any time
"""

import os
import signal
import sys
import threading
from dotenv import load_dotenv

# Ensure project root is in sys.path and .env is loaded
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv(os.path.join(project_root, ".env"))

from app.core import AssistantState, KeyboardController, VoiceAssistant

_shutdown_event = threading.Event()


def _signal_handler(sig, frame):
    """Handle interrupt signals for graceful termination."""
    _shutdown_event.set()


def main() -> None:
    # Register Ctrl+C / SIGINT and SIGTERM handlers
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    print("\n⏳ Initializing Voice Assistant models (Whisper, LLM, TTS)...")
    try:
        assistant = VoiceAssistant()
    except Exception as exc:
        print(f"\n[FATAL] Failed to initialize Voice Assistant: {exc}")
        sys.exit(1)

    # Initialize and start keyboard controller
    keyboard_controller = KeyboardController(on_trigger=assistant.trigger_voice_input)
    try:
        keyboard_controller.start()
    except Exception as exc:
        print(f"\n[WARNING] Could not start global keyboard listener: {exc}")
        print("Note: On macOS, Accessibility permission is required for global hotkeys.")
        print("Go to: System Settings -> Privacy & Security -> Accessibility -> Allow your Terminal/IDE.")

    hotkey_display = keyboard_controller.hotkey_str.upper().replace("<", "").replace(">", "").replace("+", " + ")

    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║               🎙️  Voice Assistant (Hotkey Mode)               ║
║──────────────────────────────────────────────────────────────║
║  Hotkey:  {hotkey_display:<49}║
║  Action:  Press hotkey -> Speak -> Auto-reply aloud          ║
║  Exit:    Press Ctrl+C to terminate                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"[{AssistantState.IDLE.value}] Waiting for hotkey...")

    try:
        # Keep the main thread alive until shutdown signal is received
        while not _shutdown_event.is_set():
            _shutdown_event.wait(timeout=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n\n👋 Shutting down Voice Assistant...")
        keyboard_controller.stop()
        assistant.shutdown()
        print("✅ Shutdown complete. Goodbye!\n")


if __name__ == "__main__":
    main()
