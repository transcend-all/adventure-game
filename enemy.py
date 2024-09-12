# enemy.py
import pygame
import random

# Constants for enemy settings
ENEMY_COLOR = (255, 0, 0)  # Red color for enemies
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
ENEMY_BASE_HEALTH = 50
ENEMY_BASE_SPEED = 2

class Enemy:
    def __init__(self, x, y, level):
        """Initialize the enemy at a given position, with attributes scaling based on the level."""
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.health = ENEMY_BASE_HEALTH + (level * 10)  # Enemy health scales with level
        self.speed = ENEMY_BASE_SPEED + (level * 0.5)  # Enemy speed scales with level
        self.attack_power = 5 + level  # Added attack power for enemy

    def move_towards_player(self, player):
        """Move the enemy towards the player's position."""
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        if self.rect.x > player.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        if self.rect.y > player.rect.y:
            self.rect.y -= self.speed

    def update(self):
        """Placeholder for future enemy AI behavior."""
        pass

    def take_damage(self, amount, level_manager):
        """Reduces health and triggers death effects."""
        self.health -= amount
        if self.health <= 0:
            print(f"Enemy defeated at ({self.rect.x}, {self.rect.y})")
            level_manager.spawn_coins(self.rect.x, self.rect.y)  # Spawn coins on death
            return True  # Enemy is dead
        return False

    # def take_damage(self, amount):
    #     """Reduces enemy health by a specific amount, and removes enemy if health is <= 0."""
    #     self.health -= amount
    #     if self.health <= 0:
    #         print(f"Enemy defeated at position ({self.rect.x}, {self.rect.y})")
    #         return True  # Indicates the enemy has been killed
    #     return False  # Enemy still alive

    def is_alive(self):
        """Check if the enemy is still alive."""
        return self.health > 0

    def draw(self, screen, graphics):
        """Draw the enemy using the enemy sprite."""
        graphics.draw_enemy(screen, self)  # Call graphics module to draw sprite