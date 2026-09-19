import string

from app.audio.input import Microphone
from app.stt.whisper import WhisperSTT
def main():
    microphone = Microphone()
    whisper = WhisperSTT()

    while True:
        audio = microphone.record_until_silence()
        text = whisper.transcribe(audio)

        print("YOU:" , text)

        command = text.lower().strip()
        command = command.translate(
            str.maketrans("", "", string.punctuation)
        )
        if command in ['exit','quit','stop']:
            print("Assistant stopped ")
            break



if __name__ =="__main__":
    main()
