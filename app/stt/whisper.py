
from faster_whisper import WhisperModel

class WhisperSTT:
    def __init__(self):
        self.model = WhisperModel(
            "small" , 
            device = "cpu",
            compute_type="int8"
        )
    def transcribe(self,audio):
        segments , _ = self.model.transcribe(audio , beam_size=1)
        return " ".join(
            segment.text for segment in segments
        ).strip()

    

