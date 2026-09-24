

import asyncio

from app.llm.llm import LLM
from app.tts.tts import TTS
from app.audio.input import Microphone
from app.stt.whisper import WhisperSTT

from pynput import keyboard


quit_requested = False


def on_press(key):
    global quit_requested

    try:
        if key.char == "q":
            quit_requested = True
    except AttributeError:
        pass


listener = keyboard.Listener(on_press=on_press)
listener.start()


microphone = Microphone()  # uses default 1500ms silence — adjust silence_duration= if needed

llm = LLM()
tts = TTS()
whisper = WhisperSTT()

# Characters that signal a good TTS chunk boundary
SENTENCE_ENDS = (".", "?", "!", "\n")
CLAUSE_ENDS = (",", ";", ":")
MIN_CHUNK_LEN = 30   # minimum chars before flushing on a clause boundary
MAX_CHUNK_LEN = 120  # flush even without a boundary if buffer grows large


def should_flush(buf: str) -> bool:
    #Return True if buf is ready to be sent to TTS.
    if not buf.strip():
        return False
    if buf[-1] in SENTENCE_ENDS:
        return True
    if len(buf) >= MIN_CHUNK_LEN and buf[-1] in CLAUSE_ENDS:
        return True
    if len(buf) >= MAX_CHUNK_LEN:
        return True
    return False


async def main():

    while True:

        if quit_requested:
            print("Goodbye!")
            break

        audio_numbers = microphone.record_until_silence()

        if len(audio_numbers) == 0:
            continue

        text = whisper.transcribe(audio_numbers)

        if not text:
            continue

        print("YOU:", text)

        if text.lower().strip() == "exit" or quit_requested:
            print("Goodbye!")
            break

        print("ASSISTANT:", end=" ", flush=True)

        buffer = ""

        async for chunk in llm.generate_answer(text):

            if quit_requested:
                break

            print(chunk, end="", flush=True)

            buffer += chunk

            if should_flush(buffer):
                tts.speak(buffer.strip())
                buffer = ""

        # Flush any remaining text
        if buffer.strip() and not quit_requested:
            tts.speak(buffer.strip())

        # Wait for all queued audio to finish before listening again
        tts.wait_until_done()

        print()


listener.stop()

asyncio.run(main())
