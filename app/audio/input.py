"""
Input to STT. 
"""



from collections import deque
import sounddevice as sd
import numpy as np 
import webrtcvad

class Microphone:
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration: int = 30,
        silence_duration: int = 800,   # ms of silence before stopping; 800ms is a good balance
        pre_roll_duration: int = 300,  # ms of audio kept before speech starts to avoid clipping
        vad_aggressiveness: int = 1,   # 0=least aggressive, 3=most; lower = less likely to cut off quiet speech
    ):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.silence_frames = int(silence_duration / frame_duration)
        self.pre_roll_frames = int(pre_roll_duration / frame_duration)

    def record_until_silence(self):
        print("listening...")
        frames = []
        pre_roll = deque(maxlen=self.pre_roll_frames)
        speech_started = False
        silence_count = 0

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.frame_size,
            dtype="int16",
        ) as stream:
            while True:
                audio, _ = stream.read(self.frame_size)
                audio = audio.flatten()

                raw_bytes = audio.tobytes()
                # Ensure the frame byte length matches WebRTC VAD requirements (sample_rate * frame_duration * 2 / 1000)
                if len(raw_bytes) != self.frame_size * 2:
                    continue

                is_speech = self.vad.is_speech(raw_bytes, self.sample_rate)

                if is_speech:
                    if not speech_started:
                        print("Speaking...")
                        speech_started = True
                        # Prepend accumulated pre-speech frames so speech start isn't clipped
                        frames.extend(pre_roll)
                        pre_roll.clear()
                    silence_count = 0
                    frames.append(audio)
                else:
                    if not speech_started:
                        # Accumulate pre-speech frames in ring buffer
                        pre_roll.append(audio)
                    else:
                        silence_count += 1
                        frames.append(audio)
                        if silence_count >= self.silence_frames:
                            break

            print("Processing....")
            if not frames:
                return np.zeros(0, dtype=np.float32)

            audio = np.concatenate(frames)
            normalized = audio.astype(np.float32) / 32768.0
            print(f"[DEBUG] frames={len(frames)}, max_amp={np.abs(normalized).max():.4f}")
            return normalized

