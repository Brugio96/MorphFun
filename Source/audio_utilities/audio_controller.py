from audio_utilities.start_morphing import AudioClass
import pygame
import os
import numpy as np

from audio_utilities.handle_record import (
    start_recording,
    stop_recording,
    handle_recorded_audio,
)


class AudioController:
    def __init__(self, config_manager):
        self.audio_controller = AudioClass(pygame.mixer)
        self.config_manager = config_manager
        self.init_mixer()
        self.init_variables()

    def init_mixer(self):
        self.audio_controller.mixer.init(frequency=22050, size=32)

    def init_variables(self):
        config = self.config_manager.get_config("controller")
        max_duration = config["max_duration"]
        sr = config["sr"]
        self.recorded_audio = np.zeros((sr * max_duration, 1), np.float32)
        self.startRecording = True

    def handle_record_message(self):
        sr = self.config_manager.get_config("controller")["sr"]
        max_duration = self.config_manager.get_config("controller")["max_duration"]
        audio_folder = self.config_manager.get_config("files")["audio"]

        # Logic related to recording
        if self.startRecording:
            self.startRecording = False
            self.start_time = start_recording(self.recorded_audio)
        else:
            self.startRecording = True
            stop_recording()
            self.recorded_audio = handle_recorded_audio(
                recorded_audio=self.recorded_audio,
                start_time=self.start_time,
                max_duration=max_duration,
            )

            recorded_audio_path = os.path.join(audio_folder, "recorded_audio.npy")
            np.save(recorded_audio_path, self.recorded_audio)

            print("\n!!! M0RPH!NG B3G!N$ !!!\n")
            self.audio_controller.play_sd_audio(self.recorded_audio)
