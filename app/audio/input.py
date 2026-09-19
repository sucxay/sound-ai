"""
Input to STT. 
"""



import sounddevice as sd
import numpy as np 
import webrtcvad

class Microphone:
    def __init__(self,sample_rate = 16000 , frame_duration = 30 , silence_duration = 800):
        self.sample_rate =sample_rate 
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration/1000)
        self.vad = webrtcvad.Vad(2)
        self.silence_frames = int(
                silence_duration / frame_duration
            )
    def record_until_silence(self):
        print("listening...")
        frames =[]
        speech_started= False
        silence_count = 0
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.frame_size,
            dtype="int16",
        ) as stream:
            while True:
                audio , _ = stream.read(self.frame_size)
                audio = audio.flatten()
                is_speech = self.vad.is_speech(
                    audio.tobytes() ,
                    self.sample_rate

                )
                if is_speech:
                    if not speech_started:
                        print("Speaking...")
                        speech_started = True
                    silence_count = 0
                    frames.append(audio)
                else:
                    if speech_started:
                        silence_count += 1
                        frames.append(audio)
                        if silence_count >= self.silence_frames:
                            break
            print("Processing....")
            audio = np.concatenate(frames)
            normalized = audio.astype(np.float32)/32768.0
            print(f"[DEBUG] frames={len(frames)}, max_amp={np.abs(normalized).max():.4f}")
            return normalized

                
        

    
    
