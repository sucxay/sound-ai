from app.audio.input import Microphone 
from app.llm.llm import LLM 
from app.stt.whisper import WhisperSTT 

microphone = Microphone()
llm = LLM()
whisper=WhisperSTT()


text_numbers = microphone.record_until_silence()
text = whisper.transcribe(text_numbers)
answer = llm(text)
print(answer)



