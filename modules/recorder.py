import wave
import os
from datetime import datetime

class AudioRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frames = []
        self.recording = False
        self.filename = None

    def start_recording(self, output_dir="recordings"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(output_dir, f"recording_{timestamp}.wav")
        self.frames = []
        self.recording = True
        print(f"🔴 Recording started: {self.filename}")

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        if self.frames:
            print(f"💾 Saving recording to {self.filename}")
            with wave.open(self.filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.frames))
        else:
            print("⚠️ No audio frames to save.")

    def write(self, frame_bytes):
        if self.recording:
            self.frames.append(frame_bytes)
