from audio_utilities.audio_recorder import AudioRecorder
from audio_utilities.audio_player import AudioPlayer
import numpy as np
import os


class AudioManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.audio_recorder = AudioRecorder(config_manager)
        self.audio_player = AudioPlayer(config_manager)

    def toggle_recording(self):
        self.audio_recorder.toggle_recording()

    def play(self):
        self.audio_player.unpause_playing()

    def pause(self):
        self.audio_player.pause_playing()

    def clear(self):
        self.audio_player.clear_playing()

    def play_recorded_audio(self):
        self.audio_player.play_audio(self.audio_recorder.get_recorded_audio())

    def get_recorded_audio_path(self):
        audio_folder = self.config_manager.get_config("files")["audio"]
        return os.path.join(audio_folder, "recorded_audio.npy")

    def save_recorded_audio(self):
        recorded_audio_path = self.get_recorded_audio_path()
        np.save(recorded_audio_path, self.audio_recorder.get_recorded_audio())
