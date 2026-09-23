from pocket_tts import TTSModel
import sounddevice as sd
import threading
import queue


class TTS:
    def __init__(self):
        self.model = TTSModel.load_model()
        self.voice_state = self.model.get_state_for_audio_prompt("alba")
        self._audio_queue = queue.Queue()
        self._playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self._playback_thread.start()

    def _playback_worker(self):
        """Continuously plays audio chunks from the queue as they arrive."""
        while True:
            audio = self._audio_queue.get()
            if audio is None:  # Sentinel to stop
                break
            sd.play(audio.numpy(), self.model.sample_rate)
            sd.wait()
            self._audio_queue.task_done()

    def speak(self, text: str):
        """Synthesizes text and queues audio for playback immediately."""
        audio = self.model.generate_audio(self.voice_state, text)
        self._audio_queue.put(audio)

    def wait_until_done(self):
        """Blocks until all queued audio has finished playing."""
        self._audio_queue.join()