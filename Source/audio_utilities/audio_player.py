from audio_utilities.audio_morpher import AudioMorpher
import pygame


class AudioPlayer:
    def __init__(self, config_manager):
        self.player = AudioMorpher(pygame.mixer)
        self.config_manager = config_manager
        self.init_mixer()

    def init_mixer(self):
        self.player.mixer.init(frequency=22050, size=32)

    def play_audio(self, audio):
        self.player.play_audio(audio)

    def unpause_playing(self):
        self.player.unpause_playing()

    def pause_playing(self):
        self.player.pause_playing()

    def clear_playing(self):
        self.player.clear_playing()
