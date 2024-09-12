# item.py
import pygame

# Define different item types
HEALTH_POTION = 'Health Potion'
ATTACK_BOOST = 'Attack Boost'
DEFENSE_BOOST = 'Defense Boost'

# Constants for item colors and sizes
ITEM_COLOR = (0, 0, 255)  # Blue for general items
ITEM_WIDTH = 30
ITEM_HEIGHT = 30

class Item:
    def __init__(self, item_type, x, y):
        """Initialize the item with a type and position on the world map."""
        self.item_type = item_type
        self.rect = pygame.Rect(x, y, ITEM_WIDTH, ITEM_HEIGHT)  # Position of the item on the map
    
    def apply_effect(self, player):
        """Applies the effect of the item to the player."""
        if self.item_type == HEALTH_POTION:
            player.health = min(100, player.health + 20)  # Heal the player by 20 points, max health is 100
            print(f"Player health increased to {player.health} by using a {self.item_type}.")
        elif self.item_type == ATTACK_BOOST:
            player.attack_power += 5  # Increase player's attack power
            print(f"Player's attack increased by 5.")
        elif self.item_type == DEFENSE_BOOST:
            player.defense_power += 5  # Increase player's defense power
            print(f"Player's defense increased by 5.")

    def draw(self, screen):
        """Draw the item on the screen."""
        pygame.draw.rect(screen, ITEM_COLOR, self.rect)

class Inventory:
    def __init__(self):
        """Initialize the player's inventory."""
        self.items = []  # List to store collected items

    def add_item(self, item):
        """Add an item to the inventory."""
        self.items.append(item)
        print(f"{item.item_type} added to inventory!")

    def use_item(self, item_type, player):
        """Use an item from the inventory and apply its effect."""
        for item in self.items:
            if item.item_type == item_type:
                item.apply_effect(player)
                self.items.remove(item)  # Remove item after use
                return
        print(f"No {item_type} found in inventory.")

    def display_inventory(self):
        """Display the current inventory."""
        print("Inventory:", [item.item_type for item in self.items])


COIN_WIDTH = 20
COIN_HEIGHT = 20

class Coin:
    def __init__(self, x, y, value=10):
        """Initialize the coin at a given position with a specific value."""
        self.rect = pygame.Rect(x, y, COIN_WIDTH, COIN_HEIGHT)
        self.value = value  # The value of the coin (how many coins the player collects)

    def draw(self, screen, graphics):
        """Draw the coin using the graphics module."""
        graphics.draw_coin(screen, self)

    def collect(self, player):
        """Add the coin's value to the player's currency when collected."""
        player.currency.add_coins(self.value)
        print(f"Collected {self.value} coins!")
