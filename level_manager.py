# level_manager.py
from enemy import Enemy
import pygame
import random
from item import Coin

class LevelManager:
    def __init__(self, world, graphics):
        self.world = world  # Reference to the World object
        self.level = 1  # Start at level 1
        self.enemies = []  # List of enemies on the current level
        self.coins = []
        self.graphics = graphics

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

    def spawn_coins(self, x, y):
        """Spawn a coin at the given position (after enemy defeat)."""
        coin_value = random.randint(5, 20)  # Random coin value between 5 and 20
        coin = Coin(x, y, coin_value)
        self.coins.append(coin)

    def update(self):
        """Update enemies and check for level progression."""
        # Update all enemies
        for enemy in self.enemies:
            enemy.update()

            if not enemy.is_alive():
                self.level_manager.enemies.remove(enemy)
                # Drop coins at enemy's location
                self.spawn_coins(enemy.rect.x, enemy.rect.y)

        # If all enemies are defeated, go to the next level
        if not self.enemies:
            self.level += 1  # Increase level
            self.spawn_enemies()  # Spawn new enemies

    def render(self, screen):
        """Render the current level (world, enemies, etc.)."""
        self.world.draw(screen)  # Draw the world (background and obstacles)

        # Draw all enemies, passing the graphics object
        for enemy in self.enemies:
            enemy.draw(screen, self.graphics)  # Pass the graphics object here

    def collect_coins(self, player):
        """Check for coin collection by the player."""
        for coin in self.coins[:]:  # Use a copy of the list to safely modify it
            if player.rect.colliderect(coin.rect):
                coin.collect(player)
                self.coins.remove(coin)


    
