import sounddevice as sd
import numpy as np
import time


class Recorder:
    RECORDING_SR = 44100

    def __init__(self, max_duration=14):
        self.max_duration = max_duration
        self.recorded_audio = np.zeros(
            (int(self.RECORDING_SR * self.max_duration), 1), dtype=np.float32
        )

    def start_recording(self):
        start_time = time.time()
        sd.rec(
            samplerate=self.RECORDING_SR,
            channels=1,
            dtype=np.float32,
            out=self.recorded_audio,
        )
        print("RECORDING ON")
        return start_time

    def stop_recording(self, start_time):
        sd.stop()
        total_time = time.time() - start_time
        samples_to_keep = int(min(total_time, self.max_duration) * self.RECORDING_SR)
        self.recorded_audio = self.recorded_audio[:samples_to_keep, :]
        print("RECORDING STOPPED")

    def get_recorded_audio(self):
        return self.recorded_audio
