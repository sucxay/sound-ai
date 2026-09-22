from pocket_tts import TTSModel
import sounddevice as sd


class TTS:
    def __init__(self):
        self.model = TTSModel.load_model()
        self.voice_state = self.model.get_state_for_audio_prompt("alba")

    def speak(self, text: str):
        audio = self.model.generate_audio(self.voice_state, text)

        sd.play(audio.numpy(), self.model.sample_rate)
        sd.wait()