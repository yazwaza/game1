import pygame
import cv2
import webbrowser
import os
import sys
from sprites import * 
from config import *
from music import *

def get_asset_path(filename):
    """Returns the correct path for any asset in the 'assets' folder."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller bundle
        base_path = sys._MEIPASS
    else:  # Running from source
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets', filename)

class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Load font dynamically
        font_path = get_asset_path("font.ttf")
        print(f"Font path: {font_path}")  # Debugging statement
        self.font = pygame.font.Font(font_path, 36)
        self.all_enemies_dead = False

        # Load music and spritesheets using get_asset_path
        self.music = Music(get_asset_path("song.mp3"))
        print(f"Music path: {get_asset_path('song.mp3')}")  # Debugging statement
        self.music.play()

        self.character = Spritesheet(get_asset_path("Elmo_spritesheet.png"))
        print(f"Character spritesheet path: {get_asset_path('Elmo_spritesheet.png')}")  # Debugging statement
        self.enemy = Spritesheet(get_asset_path("enemy_spritesheet.png"))
        print(f"Enemy spritesheet path: {get_asset_path('enemy_spritesheet.png')}")  # Debugging statement
        self.intro_background = pygame.image.load(get_asset_path("intro_background.png"))
        print(f"Intro background path: {get_asset_path('intro_background.png')}")  # Debugging statement
        self.video = cv2.VideoCapture(get_asset_path("roses.mp4"))
        print(f"Video path: {get_asset_path('roses.mp4')}")  # Debugging statement
        self.attack_spritesheet = Spritesheet(get_asset_path("attack.png"))
        print(f"Attack spritesheet path: {get_asset_path('attack.png')}")  # Debugging statement

    def intro(self):
        """Display the intro screen with a full-screen background."""
        intro = True
        background = pygame.transform.scale(self.intro_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        title = self.font.render("Valentine's Day Game", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))

        play_button = Button(SCREEN_WIDTH // 2 - 100, 220, 200, 60, (255, 255, 255), (148, 3, 37), "Play", 36)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button.is_pressed(mouse_pos, (1, 0, 0)):
                        intro = False

            self.screen.blit(background, (0, 0))
            self.screen.blit(title, title_rect)
            play_button.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)

    def createTileMap(self):
        """Create the tile-based map from the tile_map array."""
        for i, row in enumerate(tile_map):
            for j, col in enumerate(row):
                if col == 'B':
                    Block(self, j, i)
                elif col == 'P':
                    self.player = Player(self, j, i)
                elif col == 'E':
                    Enemy(self, j, i)

    def new(self):
        """Start a new game."""
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.createTileMap()

    def events(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.player.facing == 'up':
                    Attack(self, self.player.rect.x, self.player.rect.y - TILE_SIZE, self.player.facing)
                elif self.player.facing == 'down':
                    Attack(self, self.player.rect.x, self.player.rect.y + TILE_SIZE, self.player.facing)
                elif self.player.facing == 'left':
                    Attack(self, self.player.rect.x - TILE_SIZE, self.player.rect.y, self.player.facing)
                elif self.player.facing == 'right':
                    Attack(self, self.player.rect.x + TILE_SIZE, self.player.rect.y, self.player.facing)

    def update(self):
        """Update all sprites."""
        self.all_sprites.update()
        if len(self.enemies) == 0 and not self.all_enemies_dead:
            self.all_enemies_dead = True
            webbrowser.open("https://www.youtube.com/watch?v=mI_Ycumremk")
            pygame.quit()

    def draw(self):
        """Draw all sprites directly to the screen without camera offset."""
        self.screen.fill((0, 0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def gameOver(self):
        text = self.font.render("Game Over", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        play_again_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, 250, 80, (255, 255, 255), (148, 3, 37), "Play Again", 36)

        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:  # Detect click on button
                    mouse_pos = pygame.mouse.get_pos()
                    if play_again_button.is_pressed(mouse_pos, (1, 0, 0)):
                        print("Play Again button clicked!")  # Debugging message
                        self.new()
                        self.main()
                        return  # Exit the gameOver loop and start the new game

            # Read video frame and render it
            ret, frame = self.video.read()
            if not ret:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            self.screen.blit(frame_surface, (0, 0))
            self.screen.blit(text, text_rect)
            play_again_button.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)

        self.video.release()


    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.gameOver()


# Run the game
g = Game()
g.intro()
g.new()
while g.running:
    g.main()

pygame.quit()
sys.exit()
