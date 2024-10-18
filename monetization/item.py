# item.py
import pygame
from database_manager import DatabaseManager

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
        self.pickup_sound = pygame.mixer.Sound('sounds/pickup_item.wav')
        self.pickup_sound.set_volume(0.5)

    
    def apply_effect(self, player):
        """Applies the effect of the item to the player."""
        self.pickup_sound.play()

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
    def __init__(self, player, db_manager):
        """Initialize the player's inventory."""
        self.items = []  # List to store collected items
        self.player = player
        self.db_manager = db_manager
        self.fetch_items_from_db()

    def add_item(self, item):
        """Add an item to the inventory."""
        self.items.append(item)
        print(f"{item.item_type} added to inventory!")

    def use_item(self, item_type):
        """Use an item from the inventory and apply its effect."""
        for item in self.items:
            if item.item_type == item_type:
                item.apply_effect(self.player)
                self.items.remove(item)  # Remove item after use
                return
        print(f"No {item_type} found in inventory.")

    def display_inventory(self):
        """Display the current inventory."""
        print("Inventory:", [item.item_type for item in self.items])

    def fetch_items_from_db(self):
        """Fetch the player's items from the database and populate the inventory."""
        item_counts = self.db_manager.get_user_items(self.player.name)
        if item_counts:
            self.items = []
            for _ in range(item_counts.get('health_potions', 0)):
                self.items.append(HealthPotion())
            for _ in range(item_counts.get('attack_boosts', 0)):
                self.items.append(AttackBoost())
            for _ in range(item_counts.get('defense_boosts', 0)):
                self.items.append(DefenseBoost())
            print("Inventory loaded from database.")
        else:
            print("Failed to load inventory from database.")


COIN_WIDTH = 20
COIN_HEIGHT = 20

class Coin:
    def __init__(self, x, y, value=10):
        """Initialize the coin at a given position with a specific value."""
        self.rect = pygame.Rect(x, y, COIN_WIDTH, COIN_HEIGHT)
        self.value = value  # The value of the coin (how many coins the player collects)
        self.collect_sound = pygame.mixer.Sound('sounds/coin_collect.wav')
        self.collect_sound.set_volume(0.5)

    def draw(self, screen, graphics):
        """Draw the coin using the graphics module."""
        graphics.draw_coin(screen, self)

    def collect(self, player):
        """Add the coin's value to the player's currency when collected."""
        player.currency.add_coins(self.value)
        self.collect_sound.play()
        print(f"Collected {self.value} coins!")


# health_potion.py

class HealthPotion(Item):
    def __init__(self):
        super().__init__(item_type=HEALTH_POTION, x=0, y=0)  # Default position, adjust as needed
        self.name = 'Health Potion'
        self.price = 50  # Example price
        self.description = 'Restores 20 health points.'

    def apply_effect(self, player):
        """Override to restore health."""
        player.health = min(100, player.health + 20)
        print(f"{self.name} used! Player's health increased to {player.health}.")

# attack_boost.py

class AttackBoost(Item):
    def __init__(self):
        super().__init__(item_type=ATTACK_BOOST, x=0, y=0)  # Default position, adjust as needed
        self.name = 'Attack Boost'
        self.price = 75  # Example price
        self.description = 'Increases attack power by 5 for a limited time.'

    def apply_effect(self, player):
        """Override to boost attack."""
        player.attack_power += 5
        print(f"{self.name} used! Player's attack power increased to {player.attack_power}.")

# defense_boost.py

class DefenseBoost(Item):
    def __init__(self):
        super().__init__(item_type=DEFENSE_BOOST, x=0, y=0)  # Default position, adjust as needed
        self.name = 'Defense Boost'
        self.price = 75  # Example price
        self.description = 'Increases defense power by 5 for a limited time.'

    def apply_effect(self, player):
        """Override to boost defense."""
        player.defense_power += 5
        print(f"{self.name} used! Player's defense power increased to {player.defense_power}.")
