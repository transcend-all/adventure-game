# player.py
import pygame

# Constants for player settings
PLAYER_COLOR = (0, 0, 0)  # Black for the player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5

class Player:
    def __init__(self, name, currency):
        self.name = name
        self.rect = pygame.Rect(100, 100, PLAYER_WIDTH, PLAYER_HEIGHT)  # Player's rectangle (x, y, width, height)
        self.speed = PLAYER_SPEED  # Movement speed
        self.health = 100  # Player's health
        self.attack_power = 10  # Player's base attack power
        self.inventory = []  # Player inventory to store items
        self.currency = currency

    def handle_input(self, world):
        """Handles player movement based on keyboard input and checks for collisions with the world."""
        keys = pygame.key.get_pressed()  # Get current state of keys
        new_x, new_y = self.rect.x, self.rect.y  # Track the player's new position

        # Movement based on key input
        if keys[pygame.K_LEFT]:
            new_x -= self.speed
        if keys[pygame.K_RIGHT]:
            new_x += self.speed
        if keys[pygame.K_UP]:
            new_y -= self.speed
        if keys[pygame.K_DOWN]:
            new_y += self.speed

        # Check if new position is valid (not colliding with unwalkable areas in the world)
        if world.is_walkable(new_x, self.rect.y):
            self.rect.x = new_x
        if world.is_walkable(self.rect.x, new_y):
            self.rect.y = new_y

    def draw(self, screen):
        """Draws the player on the screen."""
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)

    def take_damage(self, amount):
        """Reduces player health by a specific amount."""
        self.health -= amount
        if self.health <= 0:
            print(f"{self.name} has died!")

    def add_to_inventory(self, item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)
        print(f"{item} added to inventory!")

    def display_inventory(self):
        """Displays the player's inventory (for now, print to console)."""
        print(f"Inventory: {self.inventory}")
