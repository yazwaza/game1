# sprites.py
import pygame
import random
import os
import sys
from config import TILE_SIZE, PLAYER_LAYER, BLOCK_LAYER, PLAYER_SPEED, ENEMY_LAYER, BLACK, ENEMY_SPEED

def get_asset_path(filename):
    """Returns the correct path for any asset in the 'assets' folder."""
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller bundle
        base_path = sys._MEIPASS
    else:  # Running from source
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets', filename)

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)  # Preserve transparency
        sprite.blit(self.spritesheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)# Set black as transparent
        return sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.facing = 'setUp'
        self.animation_loop = 0

        # Initial static image
        self.image = self.game.character.get_sprite(-7, 5, 20, 32)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

        self.pos = pygame.Vector2(self.rect.topleft)
        self.speed = PLAYER_SPEED

        self.animations = {
            'setUp': [self.game.character.get_sprite(-7, 5, 20, 32)],
            'down': [self.game.character.get_sprite(70, 80, 32, 32), self.game.character.get_sprite(102, 80, 32, 32)],
            'up': [pygame.transform.flip(self.game.character.get_sprite(70, 80, 32, 32), False, True) for _ in range(2)],
            'left': [pygame.transform.flip(self.game.character.get_sprite(0, 40, 20, 32), True, False) for _ in range(2)],
            'right': [self.game.character.get_sprite(0, 40, 20, 32), self.game.character.get_sprite(32, 40, 32, 32)]
        }

    def update(self):
        self.movement()
        self.animate()

        # Convert to integer to prevent floating-point errors
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.collide_blocks('x')
        self.collide_blocks('y')
        self.collide_enemy()


    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pos.x -= self.speed
            self.facing = 'left'
        elif keys[pygame.K_RIGHT]:
            self.pos.x += self.speed
            self.facing = 'right'
        elif keys[pygame.K_UP]:
            self.pos.y -= self.speed
            self.facing = 'up'
        elif keys[pygame.K_DOWN]:
            self.pos.y += self.speed
            self.facing = 'down'

    def collide_enemy(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.kill()  # Kill the player sprite
            self.game.playing = False  # Stop the game loop, transition to gameOver


    def collide_blocks(self, direction):
        """Handle collision with blocks more accurately."""
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            for hit in hits:
                if self.rect.centerx < hit.rect.centerx:
                    self.pos.x = hit.rect.left - self.rect.width
                elif self.rect.centerx > hit.rect.centerx:
                    self.pos.x = hit.rect.right
                self.rect.x = self.pos.x  # Sync position

        elif direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            for hit in hits:
                if self.rect.centery < hit.rect.centery:
                    self.pos.y = hit.rect.top - self.rect.height
                elif self.rect.centery > hit.rect.centery:
                    self.pos.y = hit.rect.bottom
                self.rect.y = self.pos.y  # Sync position


    def animate(self):
        animation = self.animations[self.facing]

        if self.rect.topleft != (int(self.pos.x), int(self.pos.y)):  # Check if player is moving
            self.image = animation[int(self.animation_loop)]
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
            self.image.set_colorkey(BLACK)
            self.animation_loop += 0.1
            if self.animation_loop >= len(animation):
                self.animation_loop = 0
        else:
            self.image = animation[0]  # Use first frame of the current direction when idle

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.x_change = 0
        self.y_change = 0
        self.facing = random.choice(['left', 'right'])
        self.animation_loop = 0
        self.movement_loop = 0
        self.max_travel = random.randint(7, 30)

        self.image = self.game.enemy.get_sprite(0, 53, 20, 20)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

        self.animations = {
            'left': [self.game.enemy.get_sprite(0, 53, 20, 20), self.game.enemy.get_sprite(20, 53, 20, 20)],
            'right': [self.game.enemy.get_sprite(95, 53, 20, 20), self.game.enemy.get_sprite(40, 53, 20, 20)]
        }

    def update(self):
        self.movement()
        self.animate()
        self.rect.x += self.x_change
        self.x_change = 0  # Reset movement after applying changes

    def movement(self):
        """Update enemy movement in a more stable loop."""
        if self.facing == 'left':
            self.x_change = -ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel:
                self.facing = 'right'

        elif self.facing == 'right':
            self.x_change = ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = 'left'


        elif self.facing == 'right':
            self.x_change = ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = 'left'

    def animate(self):
        animation = self.animations[self.facing]
        self.image = animation[int(self.animation_loop)]

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        block_path = get_asset_path("block.png")
        print(f"Block path in Block class: {block_path}")  # Debugging statement
        self.image = pygame.image.load(block_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILE_SIZE, y * TILE_SIZE)
 
class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        font_path = get_asset_path("font.ttf")
        print(f"Font path in Button class: {font_path}")  # Debugging statement
        self.font = pygame.font.Font(font_path, fontsize)
        self.content = content
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fg = fg
        self.bg = bg

        # Create a surface for the button
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Use SRCALPHA for transparency

    def draw(self, screen):
        """Draw a heart-shaped button with text centered."""
        pygame.draw.polygon(self.image, self.bg, [
            (self.width // 2, self.height),       # Bottom point
            (0, self.height // 3),                # Left curve
            (self.width // 4, 0),                 # Top-left
            (self.width // 2, self.height // 4),  # Middle-top
            (3 * self.width // 4, 0),             # Top-right
            (self.width, self.height // 3)        # Right curve
        ])

        text = self.font.render(self.content, True, self.fg)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.image.blit(text, text_rect)
        screen.blit(self.image, (self.x, self.y))

    def is_pressed(self, mouse_pos, mouse_pressed):
        """Check if the mouse is inside the heart's approximate bounding box."""
        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            if mouse_pressed[0]:  # Left mouse button pressed
                return True
        return False

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.direction = direction

        self.animation_loop = 0
        self.image = self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.animations = self.load_animations()

    def load_animations(self):
        """Load and return all animations for each direction."""
        return {
            'up': [self.game.attack_spritesheet.get_sprite(i * 32, 0, self.width, self.height) for i in range(5)],
            'down': [self.game.attack_spritesheet.get_sprite(i * 32, 32, self.width, self.height) for i in range(5)],
            'left': [self.game.attack_spritesheet.get_sprite(i * 32, 96, self.width, self.height) for i in range(5)],
            'right': [self.game.attack_spritesheet.get_sprite(i * 32, 64, self.width, self.height) for i in range(5)]
        }

    def update(self):
        """Update attack animation and check for collisions."""
        self.animate()
        self.collide_enemy()

    def animate(self):
        """Animate the attack and remove it once the animation completes."""
        animation = self.animations[self.direction]
        frame_index = min(int(self.animation_loop), len(animation) - 1)
        self.image = animation[frame_index]

        self.animation_loop += 0.2  # Adjust animation speed for smoother animation
        if self.animation_loop >= len(animation):
            self.kill()  # Remove the attack after animation ends



    def collide_enemy(self):
        """Check for collisions with enemies and handle them."""
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for hit in hits:
            hit.kill()  # Remove the enemy on collision
            self.kill()  # Remove the attack after hitting an enemy

