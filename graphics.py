# graphics.py
import pygame

class Graphics:
    def __init__(self):
        """Initialize the graphics module (load images, animations, etc.)."""
        # Example of loading player and enemy sprites (replace with actual paths)
        self.player_sprite = pygame.image.load("assets/player.png").convert_alpha()
        self.enemy_sprite = pygame.image.load("assets/enemy.png").convert_alpha()
        self.item_sprites = {
            'Health Potion': pygame.image.load("assets/health_potion.png").convert_alpha(),
            'Attack Boost': pygame.image.load("assets/attack_boost.png").convert_alpha(),
            'Defense Boost': pygame.image.load("assets/defense_boost.png").convert_alpha(),
        }

    def draw_player(self, screen, player):
        """Draw the player sprite at the player's current position."""
        screen.blit(self.player_sprite, (player.rect.x, player.rect.y))

    def draw_enemy(self, screen, enemy):
        """Draw the enemy sprite at the enemy's current position."""
        screen.blit(self.enemy_sprite, (enemy.rect.x, enemy.rect.y))

    def draw_item(self, screen, item):
        """Draw the item sprite at the item's current position."""
        if item.item_type in self.item_sprites:
            screen.blit(self.item_sprites[item.item_type], (item.rect.x, item.rect.y))

    def load_sprites(self):
        """Load or reload any sprites if needed (can be extended)."""
        pass

    def draw_background(self, screen, background_image):
        """Draw the game background."""
        screen.blit(background_image, (0, 0))
