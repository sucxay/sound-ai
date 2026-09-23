
from faster_whisper import WhisperModel

class WhisperSTT:
    def __init__(self):
        self.model = WhisperModel(
            "small" , 

            device = "cpu",

            compute_type="int8"
        )


    def transcribe(self, audio):
        segments, _ = self.model.transcribe(
            audio,
            beam_size=1,
            language="en",
            task="transcribe",
            temperature=0,
            vad_filter=True,  # skip silent audio edges — faster processing
            initial_prompt="The speaker is speaking English. Proper nouns and names should be transcribed accurately.",
        )
        return " ".join(
            segment.text for segment in segments
        ).strip()







        
            