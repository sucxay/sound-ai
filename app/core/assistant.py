import asyncio
import os
import subprocess
import threading
from typing import Optional

from app.audio.input import Microphone
from app.core.state import AssistantState
from app.llm.llm import LLM
from app.stt.whisper import WhisperSTT
from app.tts.tts import TTS

# TTS chunking delimiters
SENTENCE_ENDS = (".", "?", "!", "\n")
CLAUSE_ENDS = (",", ";", ":")
MIN_CHUNK_LEN = 30
MAX_CHUNK_LEN = 120


def should_flush(buf: str) -> bool:
    """Return True when buf contains enough text to flush to TTS."""
    if not buf.strip():
        return False
    if buf[-1] in SENTENCE_ENDS:
        return True
    if len(buf) >= MIN_CHUNK_LEN and buf[-1] in CLAUSE_ENDS:
        return True
    if len(buf) >= MAX_CHUNK_LEN:
        return True
    return False


class VoiceAssistant:
    """Thread-safe voice assistant pipeline coordinator managing the state machine:
    IDLE -> LISTENING -> PROCESSING -> SPEAKING -> IDLE
    """

    def __init__(
        self,
        microphone: Optional[Microphone] = None,
        whisper: Optional[WhisperSTT] = None,
        llm: Optional[LLM] = None,
        tts: Optional[TTS] = None,
    ):
        self.microphone = microphone or Microphone()
        self.whisper = whisper or WhisperSTT()
        self.llm = llm or LLM()
        self.tts = tts or TTS()

        self._state = AssistantState.IDLE
        self._lock = threading.Lock()
        self._shutdown_event = threading.Event()

    def _play_chime(self, sound_name: str = "Tink") -> None:
        """Play a native macOS alert chime for tactile feedback without blocking."""
        try:
            sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
            if os.path.exists(sound_path):
                subprocess.Popen(
                    ["afplay", sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass

    @property
    def state(self) -> AssistantState:
        with self._lock:
            return self._state

    def is_idle(self) -> bool:
        with self._lock:
            return self._state == AssistantState.IDLE

    def _set_state(self, new_state: AssistantState) -> None:
        with self._lock:
            self._state = new_state
        print(f"[{new_state.value}]")

    def trigger_voice_input(self) -> bool:
        """Triggered by the hotkey listener.

        Returns True if the assistant successfully switched to LISTENING and started
        processing in a background thread; Returns False if the assistant was busy.
        """
        with self._lock:
            if self._state != AssistantState.IDLE:
                # Requirement: Ignore additional hotkey presses when not IDLE
                return False
            self._state = AssistantState.LISTENING

        # Play quick alert sound and start background worker
        self._play_chime("Tink")
        print(f"[{AssistantState.LISTENING.value}]")
        worker = threading.Thread(
            target=self._process_voice_turn,
            name="voice-assistant-turn",
            daemon=True,
        )
        worker.start()
        return True

    def _process_voice_turn(self) -> None:
        """Runs the complete voice pipeline in a background thread:
        record -> transcribe -> LLM streaming -> TTS playback.
        Always returns to IDLE even on exceptions.
        """
        try:
            if self._shutdown_event.is_set():
                return

            # 1. Record microphone audio until silence is detected
            audio = self.microphone.record_until_silence()
            if self._shutdown_event.is_set():
                return

            if audio is None or len(audio) == 0:
                print("[INFO] No audio captured.")
                return

            # 2. Transcribe using Whisper
            self._set_state(AssistantState.PROCESSING)
            text = self.whisper.transcribe(audio)

            # Requirement: If transcript is empty, return to IDLE without calling LLM
            if not text or not text.strip():
                print("[INFO] Empty transcript detected.")
                return

            clean_text = text.strip()
            print(f"[USER] {clean_text}")

            # 3. Stream LLM answer and play audio via TTS
            self._set_state(AssistantState.SPEAKING)
            print("[ASSISTANT] ", end="", flush=True)

            asyncio.run(self._stream_and_speak(clean_text))
            print()  # newline after streaming completes

            # Wait until all queued audio finishes playing
            self.tts.wait_until_done()

        except Exception as exc:
            print(f"\n[ERROR] An error occurred during voice processing: {exc}")
        finally:
            # Requirement: Always return to IDLE after processing or errors
            self._set_state(AssistantState.IDLE)

    async def _stream_and_speak(self, user_text: str) -> None:
        """Streams text from LLM, prints it, and flushes sentence chunks to TTS."""
        buffer = ""
        async for chunk in self.llm.generate_answer(user_text):
            if self._shutdown_event.is_set():
                break

            fragment = "".join(chunk) if isinstance(chunk, list) else chunk
            print(fragment, end="", flush=True)

            buffer += fragment
            if should_flush(buffer):
                self.tts.speak(buffer.strip())
                buffer = ""

        # Flush remaining buffer
        if buffer.strip() and not self._shutdown_event.is_set():
            self.tts.speak(buffer.strip())

    def shutdown(self) -> None:
        """Cleanly stop the assistant and audio threads."""
        self._shutdown_event.set()
        try:
            self.tts.shutdown()
        except Exception:
            pass
        self._set_state(AssistantState.IDLE)
