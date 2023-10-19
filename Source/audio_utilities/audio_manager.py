from audio_utilities.audio_controller import AudioController
from audio_utilities.handle_record import (
    start_recording,
    stop_recording,
    handle_recorded_audio,
)
import numpy as np
import os


class AudioManager:
    def __init__(self, config_manager, morpher_manager):
        self.config_manager = config_manager
        self.audio_controller_instance = AudioController(config_manager)
        self.startRecording = False
        self.start_time = None
        self.morpher_manager = morpher_manager

    def toggle_recording(self, data_queue, morphing_queue):
        sr = self.config_manager.get_config("controller")["sr"]
        max_duration = self.config_manager.get_config("controller")["max_duration"]
        audio_folder = self.config_manager.get_config("files")["audio"]

        if not self.startRecording:
            self.startRecording = True
            self.start_time = start_recording(
                self.audio_controller_instance.recorded_audio
            )
        else:
            self.startRecording = False
            stop_recording()
            self.audio_controller_instance.recorded_audio = handle_recorded_audio(
                recorded_audio=self.audio_controller_instance.recorded_audio,
                start_time=self.start_time,
                max_duration=max_duration,
            )

            recorded_audio_path = os.path.join(audio_folder, "recorded_audio.npy")
            np.save(recorded_audio_path, self.audio_controller_instance.recorded_audio)

            print("\n!!! M0RPH!NG B3G!N$ !!!\n")
            self.play_recorded_audio()

            self.morpher_manager.transform_audio()
            self.morpher_manager.start_pose_estimation(morphing_queue, data_queue)
            self.morpher_manager.start_morphing(morphing_queue)

            data_queue.put("start")

    def play(self):
        self.audio_controller_instance.audio_controller.unpause_playing()

    def pause(self):
        self.audio_controller_instance.audio_controller.pause_playing()

    def clear(self):
        self.audio_controller_instance.audio_controller.clear_playing()

    def play_recorded_audio(self):
        self.audio_controller_instance.audio_controller.play_sd_audio(
            self.audio_controller_instance.recorded_audio
        )
