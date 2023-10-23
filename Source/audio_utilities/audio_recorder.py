import numpy as np
from audio_utilities.recorder import Recorder


class AudioRecorder:
    def __init__(self, config_manager):
        self.recorder = Recorder()
        self.config_manager = config_manager
        self.init_variables()

    def init_variables(self):
        config = self.config_manager.get_config("controller")
        max_duration = config["max_duration"]
        sr = config["sr"]
        self.recorded_audio = np.zeros((sr * max_duration, 1), np.float32)
        self.is_recording = False

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.start_time = self.recorder.start_recording()
        else:
            self.is_recording = False
            self.recorder.stop_recording(self.start_time)
            self.recorded_audio = self.recorder.get_recorded_audio()

    def get_recorded_audio(self):
        return self.recorded_audio
