"""
Voice Assistant — main entry point.

Listens for speech, transcribes via Whisper, generates a response with an LLM,
and streams the reply back through a local TTS engine.

Exit methods:
  • Say "exit", "quit", "stop", "goodbye", or "bye"
  • Press 'q' at any time
  • Press Ctrl+C
"""

import asyncio
import signal
import sys
import threading

from pynput import keyboard

from app.audio.input import Microphone
from app.llm.llm import LLM
from app.stt.whisper import WhisperSTT
from app.tts.tts import TTS

# ── Exit handling ────────────────────────────────────────────────────────────

_quit_event = threading.Event()

EXIT_PHRASES = frozenset({"exit", "quit", "stop", "goodbye", "bye"})


def _request_quit() -> None:
    """Signal all loops to stop."""
    _quit_event.set()


def _on_key_press(key: keyboard.Key) -> None:
    """Keyboard listener callback — press 'q' to quit."""
    try:
        if key.char == "q":
            _request_quit()
    except AttributeError:
        pass


# ── TTS chunking ─────────────────────────────────────────────────────────────

SENTENCE_ENDS = (".", "?", "!", "\n")
CLAUSE_ENDS = (",", ";", ":")
MIN_CHUNK_LEN = 30   # minimum chars before flushing on a clause boundary
MAX_CHUNK_LEN = 120  # flush even without a boundary if buffer grows large


def _should_flush(buf: str) -> bool:
    """Return True when *buf* contains enough text to send to TTS."""
    if not buf.strip():
        return False
    if buf[-1] in SENTENCE_ENDS:
        return True
    if len(buf) >= MIN_CHUNK_LEN and buf[-1] in CLAUSE_ENDS:
        return True
    if len(buf) >= MAX_CHUNK_LEN:
        return True
    return False


# ── Core loop ─────────────────────────────────────────────────────────────────

async def _run(
    microphone: Microphone,
    whisper: WhisperSTT,
    llm: LLM,
    tts: TTS,
) -> None:
    """Main listen → think → speak loop."""

    while not _quit_event.is_set():
        # 1. Listen
        audio = microphone.record_until_silence()
        if len(audio) == 0 or _quit_event.is_set():
            continue

        # 2. Transcribe
        text = whisper.transcribe(audio)
        if not text:
            continue

        print(f"\033[96m  YOU:\033[0m {text}")

        # 3. Check for exit commands
        if text.strip().lower() in EXIT_PHRASES:
            print(f"\033[93m  ASSISTANT:\033[0m Goodbye! Have a great day.")
            tts.speak("Goodbye! Have a great day.")
            tts.wait_until_done()
            _request_quit()
            break

        # 4. Generate & stream response
        print("\033[93m  ASSISTANT:\033[0m ", end="", flush=True)

        buffer = ""
        async for chunk in llm.generate_answer(text):
            if _quit_event.is_set():
                break

            # Normalize chunk to a plain string
            fragment = "".join(chunk) if isinstance(chunk, list) else chunk
            print(fragment, end="", flush=True)

            buffer += fragment
            if _should_flush(buffer):
                tts.speak(buffer.strip())
                buffer = ""

        # Flush remaining text in the buffer
        if buffer.strip() and not _quit_event.is_set():
            tts.speak(buffer.strip())

        # Wait for all queued audio to finish before listening again
        tts.wait_until_done()
        print()  # newline after streamed response


# ── Bootstrap ─────────────────────────────────────────────────────────────────

_BANNER = r"""
╔══════════════════════════════════════════════╗
║          🎙️  Voice Assistant Ready           ║
║──────────────────────────────────────────────║
║  Speak naturally — I'm listening.            ║
║                                              ║
║  Exit:  say "exit" / "quit" / "goodbye"      ║
║         press 'q'  ·  Ctrl+C                 ║
╚══════════════════════════════════════════════╝
"""


def main() -> None:
    """Initialise components, run the assistant, and clean up on exit."""

    # Ctrl+C → graceful shutdown
    signal.signal(signal.SIGINT, lambda *_: _request_quit())

    # Keyboard listener (non-blocking, daemon thread)
    key_listener = keyboard.Listener(on_press=_on_key_press)
    key_listener.daemon = True
    key_listener.start()

    # Initialise components (may take a moment on first run)
    print("\n  ⏳ Loading models — this may take a moment …")
    microphone = Microphone()
    llm = LLM()
    tts = TTS()
    whisper = WhisperSTT()
    print(_BANNER)

    try:
        asyncio.run(_run(microphone, whisper, llm, tts))
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  👋 Shutting down …")
        key_listener.stop()
        tts.shutdown()
        print("  ✅ Done. See you next time!\n")


if __name__ == "__main__":
    main()
