"""
audio_recorder.py

This module defines the AudioRecorder class for the audio application. It includes logic for handling the recording of audio streams. The AudioRecorder class integrates with a Recorder component and a configuration manager to orchestrate the core functionalities of audio recording.

Classes:
    AudioRecorder: Handles the initialization and control of audio recording sessions.
"""

import numpy as np
from audio.recorder import Recorder


class AudioRecorder:
    """
    Handles the initialization and control of audio recording sessions.

    This class provides methods to start and stop recording audio, as well as to retrieve the recorded audio data. It utilizes a Recorder object for the actual audio capture and a configuration manager to set up parameters such as sample rate and maximum duration.

    Attributes:
        recorder (Recorder): A Recorder instance for handling the low-level recording functionality.
        config_manager: The configuration manager providing recording parameters.
        recorded_audio (np.ndarray): A buffer to hold the recorded audio data.
        is_recording (bool): A flag indicating if recording is currently active.
        start_time (float): The timestamp when recording started.

    Methods:
        init_variables: Initializes recording variables based on configuration.
        toggle_recording: Starts or stops the recording process.
        get_recorded_audio: Returns the recorded audio buffer.
    """

    def __init__(self, config_manager):
        """
        Initializes the AudioRecorder with the required components.

        Parameters:
            config_manager: The manager that provides configuration such as sample rate and max duration.
        """
        self.recorder = Recorder()
        self.config_manager = config_manager
        self.init_variables()

    def init_variables(self):
        """
        Initializes recording variables from configuration manager.
        """
        config = self.config_manager.get_config("controller")
        max_duration = config["max_duration"]
        sr = config["sr"]
        self.recorded_audio = np.zeros((sr * max_duration, 1), np.float32)
        self.is_recording = False

    def toggle_recording(self):
        """
        Toggles the recording state. If the recorder is not recording, it starts recording. If it is recording, it stops and saves the audio.
        """
        if not self.is_recording:
            self.is_recording = True
            self.start_time = self.recorder.start_recording()
        else:
            self.is_recording = False
            self.recorder.stop_recording(self.start_time)
            self.recorded_audio = self.recorder.get_recorded_audio()

    def get_recorded_audio(self):
        """
        Retrieves the recorded audio buffer.

        Returns:
            np.ndarray: A buffer containing the recorded audio data.
        """
        return self.recorded_audio
