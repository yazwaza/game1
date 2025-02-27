# music.py

import pygame

class Music:
    def __init__(self, file_path, volume=0.5):
        pygame.mixer.init()
        self.file_path = file_path
        self.volume = volume
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.set_volume(self.volume)

    def play(self, loops=-1):
        """Play the music. Loops = -1 means it loops indefinitely."""
        pygame.mixer.music.play(loops=loops)

    def stop(self):
        """Stop the music."""
        pygame.mixer.music.stop()