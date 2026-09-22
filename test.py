from app.llm.llm import LLM
from app.tts.tts import TTS
from app.audio.input import Microphone
from app.stt.whisper import WhisperSTT


microphone = Microphone(
    silence_duration=400
)

llm = LLM()
tts = TTS()
whisper = WhisperSTT()


while True:

    audio_numbers = microphone.record_until_silence()

    if len(audio_numbers) == 0:
        continue

    text = whisper.transcribe(audio_numbers)

    if not text:
        continue

    print("YOU:", text)

    if text.lower().strip() == "exit":
        print("Goodbye!")
        break

    print("ASSISTANT:", end=" ", flush=True)

    buffer = ""

    for chunk in llm.generate_answer(text):

        print(chunk, end="", flush=True)

        buffer += chunk

        if (
            len(buffer) >= 40
            and buffer.endswith((" ", ".", ",", "?", "!"))
        ):
            tts.speak(buffer)
            buffer = ""

    if buffer:
        tts.speak(buffer)

    print()