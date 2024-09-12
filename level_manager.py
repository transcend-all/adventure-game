# level_manager.py
from enemy import Enemy
import pygame
import random

class LevelManager:
    def __init__(self, world):
        self.world = world  # Reference to the World object
        self.level = 1  # Start at level 1
        self.enemies = []  # List of enemies on the current level

        # Create initial enemies for level 1
        self.spawn_enemies()

    def spawn_enemies(self):
        """Populate the world with enemies based on the current level."""
        self.enemies.clear()  # Clear previous enemies
        num_enemies = self.level + 2  # Number of enemies increases as level increases

        for _ in range(num_enemies):
            # Randomly generate positions within the bounds of the world
            x = random.randint(0, self.world.width - 50)
            y = random.randint(0, self.world.height - 50)

            # Ensure enemies spawn on walkable tiles
            while not self.world.is_walkable(x, y):
                x = random.randint(0, self.world.width - 50)
                y = random.randint(0, self.world.height - 50)

            # Create and append a new enemy
            enemy = Enemy(x, y, self.level)
            self.enemies.append(enemy)

    def update(self):
        """Update enemies and check for level progression."""
        # Update all enemies
        for enemy in self.enemies:
            enemy.update()

        # If all enemies are defeated, go to the next level
        if not self.enemies:
            self.level += 1  # Increase level
            self.spawn_enemies()  # Spawn new enemies

    def render(self, screen):
        """Render the current level (world, enemies, etc.)."""
        self.world.draw(screen)  # Draw the world (background and obstacles)

        # Draw all enemies
        for enemy in self.enemies:
            enemy.draw(screen)
