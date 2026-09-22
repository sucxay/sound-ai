from app.llm.llm import LLM
from app.stt.whisper import WhisperSTT
from app.audio.input import Microphone
from app.tts.tts import TTS 



microphone = Microphone()
whisper = WhisperSTT()
llm = LLM()
tts = TTS()

while True:

    audio = microphone.record_until_silence()

    text = whisper.transcribe(audio)

    print("You:", text)

    if text.lower().strip() == "exit":
        break

    response = llm.generate_answer(text)

    print("Assistant:", response)

    tts.speak(response)