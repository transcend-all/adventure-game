# player.py
from shutil import move
import pygame

# Constants for player settings
PLAYER_COLOR = (0, 0, 0)  # Black for the player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5

class Player:
    def __init__(self, name, currency, id=None):
        self.id = id  # Make sure this line is present
        self.name = name
        self.rect = pygame.Rect(100, 100, PLAYER_WIDTH, PLAYER_HEIGHT)  # Player's rectangle (x, y, width, height)
        self.speed = PLAYER_SPEED  # Movement speed
        self.health = 100  # Player's health
        self.attack_power = 10  # Player's base attack power
        self.defense_power = 10
        # self.inventory = []  # Player inventory to store items
        self.currency = currency
        self.move_sound = pygame.mixer.Sound('sounds/player_move.wav')
        self.move_sound.set_volume(0.3)
        self.attack_sound = pygame.mixer.Sound('sounds/player_attack.wav')
        self.attack_sound.set_volume(0.5)
        self.damage_sound = pygame.mixer.Sound('sounds/player_damage.wav')
        self.damage_sound.set_volume(0.5)
        self.pickup_sound = pygame.mixer.Sound('sounds/pickup_item.wav')
        self.pickup_sound.set_volume(0.5)
        
        # Lazy import of DatabaseManager
        from database_manager import DatabaseManager
        self.db_manager = DatabaseManager(db_mode='postgres')  # or 'dynamodb'

    def __str__(self):
        return f"Player(id={self.id}, name={self.name}, currency={self.currency})"

    def handle_input(self, world):
            """Handles player movement based on keyboard input and checks for collisions with the world."""
            keys = pygame.key.get_pressed()
            new_x, new_y = self.rect.x, self.rect.y
            moved = False  # Flag to check if the player has moved

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
            if moved:
                self.move_sound.play()

    def draw(self, screen):
        """Draws the player on the screen."""
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)

    def take_damage(self, amount):
        """Reduces player health by a specific amount."""
        self.health -= amount
        self.damage_sound.play()
        if self.health <= 0:
            print(f"{self.name} has died!")

    # def add_to_inventory(self, item):
    #     """Adds an item to the player's inventory."""
    #     self.inventory.append(item)
    #     print(f"{item} added to inventory!")

    # def display_inventory(self):
    #     """Displays the player's inventory (for now, print to console)."""
    #     print(f"Inventory: {self.inventory}")
