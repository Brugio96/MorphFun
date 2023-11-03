"""
audio_player.py

This module defines the AudioPlayer class for the audio application. It includes logic for loading, playing, pausing, stopping, and morphing sounds using the pygame mixer. The AudioPlayer class interacts with file system components and pygame library to orchestrate the core functionalities of audio manipulation.

Classes:
    AudioPlayer: Handles the loading, playing, and morphing of audio files.
"""

import pygame
import numpy as np
import os
from queue import Empty
from utils import load_config, CONFIG_PATH


class AudioPlayer:
    """
    Manages the audio playback and morphing for the application.

    Attributes:
        config (dict): Configuration settings for the player, loaded from a file.
        audio_folder (str): The directory path where audio files are stored.
        loops (int): Number of times to loop the audio.
        sounds (dict): A dictionary of loaded pygame Sound objects.
        sound_to_mute (int): Index of the sound that will be muted during morphing.

    Methods:
        load_sound: Loads a single sound file.
        load_sounds: Loads all sound files from the audio directory.
        play_sound: Plays a specific sound file.
        play_all_sounds: Plays all loaded sounds.
        stop_sound: Stops a specific sound file.
        stop_all_sounds: Stops all sounds.
        pause_all_sounds: Pauses all sounds.
        unpause_all_sounds: Unpauses all sounds.
        clear_sounds: Clears all loaded sounds from memory.
        start_morphing: Begins the audio morphing process.
        _process_message: Processes a message from the morphing queue.
    """

    def __init__(self):
        """
        Initializes the AudioPlayer with configuration settings and state variables.
        """
        # Load configuration
        self.config = load_config(CONFIG_PATH)
        self.audio_folder = self.config["files"]["audio"]
        self.loops = self.config["morphing"]["loops"]
        pygame.mixer.init(frequency=22050, size=32)

        # Initialize variables
        self.sounds = {}
        self.sound_to_mute = 0

    def load_sound(self, file_name):
        """
        Loads a single sound file and converts it into a pygame Sound object.

        Parameters:
            file_name (str): The name of the audio file to load.
        """
        # Load a single sound and convert it to a pygame Sound object
        audio = np.load(os.path.join(self.audio_folder, file_name))
        sound = pygame.mixer.Sound(audio)
        self.sounds[file_name] = sound

    def load_sounds(self):
        """
        Loads all sound files from the audio directory into pygame Sound objects.
        """
        # Load multiple sounds and convert them to pygame Sound objects
        for file_name in sorted(os.listdir(self.audio_folder)):
            self.load_sound(file_name)

    def play_sound(self, file_name, loops=0):
        """
        Plays a single sound file.

        Parameters:
            file_name (str): The name of the sound file to play.
            loops (int): The number of times to loop the sound. Default is 0 (no loop).
        """
        # Play a single sound
        sound = self.sounds.get(file_name)
        if sound:
            sound.play(loops=loops)

    def play_all_sounds(self, loops=0):
        """
        Plays all loaded sounds at a default volume of 0.0, which will be adjusted during morphing.

        Parameters:
            loops (int): The number of times to loop the sounds. Default is 0 (no loop).
        """
        # Play all loaded sounds at volume 0.0, will be adjusted during morphing
        for sound in self.sounds.values():
            sound.play(loops=loops)
            sound.set_volume(0.0)

        # Set the volume of the first sound to 1.0 to start the morphing
        first_sound = next(iter(self.sounds.values()), None)
        if first_sound:
            first_sound.set_volume(1.0)
            self.sound_to_mute = list(self.sounds.keys())[0]

    def stop_sound(self, file_name):
        """
        Stops a single sound file from playing.

        Parameters:
            file_name (str): The name of the sound file to stop.
        """
        # Stop a single sound
        sound = self.sounds.get(file_name)
        if sound:
            sound.stop()

    def stop_all_sounds(self):
        """
        Stops all sounds from playing.
        """
        # Stop all sounds
        pygame.mixer.stop()

    def pause_all_sounds(self):
        """
        Pauses all currently playing sounds.
        """
        # Pause all sounds
        if self.sounds:
            pygame.mixer.pause()

    def unpause_all_sounds(self):
        """
        Unpauses all currently paused sounds.
        """
        # Unpause all sounds
        if self.sounds:
            pygame.mixer.unpause()

    def clear_sounds(self):
        """
        Stops all sounds and removes them from the internal dictionary.
        """
        # Stop all sounds and clear them from the dictionary
        self.stop_all_sounds()
        self.sounds.clear()

    def start_morphing(self, thread_manager, stop_event):
        """
        Starts the morphing process that handles the cross-fading between sounds.

        Parameters:
            thread_manager (ThreadManager): The thread manager object
            stop_event (Event): An event to signal when to stop morphing.
        """

        morphing_queue = thread_manager.get_queue("morphing_data")
        self.play_all_sounds(loops=self.loops)

        while not stop_event.is_set():
            try:
                message = morphing_queue.get(timeout=1)  # Use timeout to avoid blocking
            except Empty:
                continue  # Continue the loop if no message is received

            if message == 4:
                continue
            elif message != -1:  # -1 could be the message to stop morphing
                self._process_message(message)
            else:
                break

        self.stop_all_sounds()

    def _process_message(self, message):
        """
        Handles a message from the morphing queue to transition sound volume levels.

        Parameters:
            message (int): The index of the sound to activate.
        """
        sound_to_activate = message
        current_sound = self.sounds.get(self.sound_to_mute)

        if current_sound:
            current_sound.set_volume(0.0)  # Mute the current sound

        new_sound_name = sorted(list(self.sounds.keys()))[sound_to_activate]
        new_sound = self.sounds.get(new_sound_name)
        if new_sound:
            new_sound.set_volume(1.0)  # Max volume for the new sound

        self.sound_to_mute = new_sound_name
