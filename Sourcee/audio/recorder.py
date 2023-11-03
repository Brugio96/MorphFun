"""
recorder.py

This module defines the Recorder class. It includes logic for capturing audio input from the default microphone using the sounddevice library. The Recorder class manages the recording process, allowing for start, stop, and retrieval of the recorded audio, integrating with NumPy to handle audio data and time to manage recording durations.

Classes:
    Recorder: Handles the audio recording functionality.
"""

import sounddevice as sd
import numpy as np
import time


class Recorder:
    """
    Handles the audio recording functionality, capturing audio input and storing it in an array.

    Attributes:
        max_duration (int): Maximum duration in seconds that the recorder can capture.
        recorded_audio (np.ndarray): Array that stores the recorded audio data.
        RECORDING_SR (int): Sampling rate for the audio recording.

    Methods:
        start_recording(blocksize): Begins the recording of audio data.
        stop_recording(start_time): Stops the recording of audio data.
        get_recorded_audio(): Retrieves the recorded audio data.
    """

    RECORDING_SR = 44100  # Sampling rate for the audio recording

    def __init__(self, max_duration=14):
        """
        Initializes the Recorder with the specified maximum recording duration.

        Parameters:
            max_duration (int): The maximum duration in seconds for the recording.
        """
        self.max_duration = max_duration
        self.recorded_audio = np.zeros(
            (int(self.RECORDING_SR * self.max_duration), 1), dtype=np.float32
        )

    def start_recording(self, blocksize=1024):
        """
        Starts the recording of audio data for the duration specified when the class was initialized.

        Parameters:
            blocksize (int): The block size to use for the recording buffer.

        Returns:
            float: The start time of the recording.
        """
        start_time = time.time()
        sd.rec(
            frames=int(self.RECORDING_SR * self.max_duration),
            samplerate=self.RECORDING_SR,
            channels=1,
            dtype=np.float32,
            out=self.recorded_audio,
            blocksize=blocksize,
        )
        print("RECORDING ON")
        return start_time

    def stop_recording(self, start_time):
        """
        Stops the recording of audio data and trims the recorded_audio buffer to the length of the actual recording.

        Parameters:
            start_time (float): The start time of the recording to calculate the total recorded duration.
        """
        sd.stop()
        total_time = time.time() - start_time
        samples_to_keep = int(min(total_time, self.max_duration) * self.RECORDING_SR)
        self.recorded_audio = self.recorded_audio[:samples_to_keep, :]
        print("RECORDING STOPPED")

    def get_recorded_audio(self):
        """
        Retrieves the recorded audio data.

        Returns:
            np.ndarray: The array containing the recorded audio data up to the maximum duration.
        """
        return self.recorded_audio
