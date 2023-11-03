"""
audio_manager.py

This module defines the AudioManager for an audio application. It includes logic for managing audio recording, playback, and audio morphing. The AudioManager integrates with various components like AudioRecorder, AudioPlayer, and ThreadManager to orchestrate the core functionalities of the audio application.

Classes:
    AudioManager: Manages the audio recording and playback activities.
"""

from audio.audio_recorder import AudioRecorder
from audio.audio_player import AudioPlayer
import numpy as np
import os


class AudioManager:
    """
    Manages the audio recording and playback activities within an audio application.

    This class serves as a facade for the audio recording and playback functionalities,
    coordinating the audio recorder and player components and providing an interface for
    the application to start audio morphing, toggle recording, and manage playback.

    Attributes:
        config_manager: An instance of a configuration manager to handle application settings.
        audio_recorder: The AudioRecorder object to manage audio recording.
        audio_player: The AudioPlayer object to manage audio playback.
    """

    def __init__(self, config_manager):
        """
        Initializes the AudioManager with the configuration manager and respective audio components.

        Parameters:
            config_manager: An instance of the configuration manager which provides settings for the audio components.
        """
        self.config_manager = config_manager
        self.audio_recorder = AudioRecorder(config_manager)
        self.audio_player = AudioPlayer()

    def load_sounds(self):
        """
        Loads the audio files into the audio player in preparation for playback.
        """
        self.audio_player.load_sounds()

    def toggle_recording(self):
        """
        Toggles the audio recording state between recording and not recording.
        """
        self.audio_recorder.toggle_recording()

    def play(self):
        """
        Resumes playing all paused sounds.
        """
        self.audio_player.unpause_all_sounds()

    def pause(self):
        """
        Pauses all currently playing sounds.
        """
        self.audio_player.pause_all_sounds()

    def clear(self):
        """
        Clears all loaded sounds from the audio player's memory.
        """
        self.audio_player.clear_sounds()

    def play_recorded_audio(self):
        """
        Loads and plays the audio that was most recently recorded.
        """
        self.audio_player.load_sound("recorded_audio.npy")
        self.audio_player.play_sound("recorded_audio.npy")

    def get_recorded_audio_path(self):
        """
        Constructs and returns the file path for the recorded audio file.

        Returns:
            str: The full file path of the recorded audio.
        """
        audio_folder = self.config_manager.get_config("files")["audio"]
        audio_file = os.path.join(audio_folder, "recorded_audio.npy")
        return audio_file

    def save_recorded_audio(self):
        """
        Saves the audio recorded by the AudioRecorder into a .npy file.
        """
        recorded_audio_path = self.get_recorded_audio_path()
        np.save(recorded_audio_path, self.audio_recorder.get_recorded_audio())
