import asyncio
import os
import subprocess
import sys
import threading
import time
import rumps

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))

from app.audio.input import Microphone
from app.llm.llm import LLM
from app.tts.tts import TTS
from app.stt.whisper import WhisperSTT


class VoiceAssistantMenuBar(rumps.App):
    def __init__(self):
        super().__init__("🎙️", quit_button=None)

        self.status_item = rumps.MenuItem("Status: Starting...", callback=None)
        self.toggle_item = rumps.MenuItem("Pause Assistant", callback=self.toggle_pause)
        self.last_heard_item = rumps.MenuItem("Last Heard: None", callback=None)
        self.open_folder_item = rumps.MenuItem("Open Project Folder", callback=self.open_project_folder)
        self.quit_item = rumps.MenuItem("Quit", callback=self.quit_app)

        self.menu = [
            self.status_item,
            self.toggle_item,
            None,  # Separator
            self.last_heard_item,
            None,  # Separator
            self.open_folder_item,
            self.quit_item,
        ]

        self.is_paused = False
        self.is_running = True

        # Start the background worker thread
        self.worker_thread = threading.Thread(target=self._worker_entry, daemon=True)
        self.worker_thread.start()

    def toggle_pause(self, _):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.title = "⏸️"
            self.status_item.title = "Status: Paused"
            self.toggle_item.title = "Resume Assistant"
        else:
            self.title = "🎙️"
            self.status_item.title = "Status: Listening..."
            self.toggle_item.title = "Pause Assistant"

    def open_project_folder(self, _):
        subprocess.run(["open", project_root])

    def quit_app(self, _):
        self.is_running = False
        rumps.quit_application()

    def _worker_entry(self):
        asyncio.run(self._assistant_loop())

    async def _assistant_loop(self):
        try:
            self.status_item.title = "Status: Initializing models..."
            microphone = Microphone(silence_duration=400)
            llm = LLM()
            tts = TTS()
            whisper = WhisperSTT()

            self.title = "🎙️"
            self.status_item.title = "Status: Listening..."

            while self.is_running:
                if self.is_paused:
                    time.sleep(0.5)
                    continue

                # Record audio
                audio = microphone.record_until_silence()
                if not self.is_running or self.is_paused:
                    continue

                if len(audio) == 0:
                    continue

                # Transcribe
                self.title = "🧠"
                self.status_item.title = "Status: Transcribing..."
                text = whisper.transcribe(audio)

                if not text:
                    self.title = "🎙️"
                    self.status_item.title = "Status: Listening..."
                    continue

                # Update Last Heard
                display_text = (text[:35] + "...") if len(text) > 35 else text
                self.last_heard_item.title = f'Last Heard: "{display_text}"'

                if text.lower().strip() == "exit":
                    self.title = "👋"
                    self.status_item.title = "Status: Exiting..."
                    break

                # Stream LLM answer and speak
                self.title = "🔊"
                self.status_item.title = "Status: Speaking..."
                buffer = ""

                async for chunk in llm.generate_answer(text):
                    if not self.is_running:
                        break
                    if isinstance(chunk, list):
                        buffer += "".join(chunk)
                    else:
                        buffer += chunk

                    if buffer and buffer[-1] in ".!?\n":
                        tts.speak(buffer.strip())
                        buffer = ""

                if buffer.strip() and self.is_running:
                    tts.speak(buffer.strip())

                tts.wait_until_done()

                # Reset to Listening state
                if not self.is_paused:
                    self.title = "🎙️"
                    self.status_item.title = "Status: Listening..."

        except Exception as e:
            self.title = "⚠️"
            self.status_item.title = f"Error: {str(e)[:30]}"
            print(f"[ERROR in MenuBar Assistant]: {e}", file=sys.stderr)


def run_menu_app():
    app = VoiceAssistantMenuBar()
    app.run()


if __name__ == "__main__":
    run_menu_app()
