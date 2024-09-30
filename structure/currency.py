# currency.py
import pygame

from monetization import item
from monetization.item import Inventory

class Currency:
    def __init__(self):
        """Initialize the player's coin balance."""
        self.coins = 0  # Player starts with 0 coins
        #self.add_coin_sound = pygame.mixer.Sound('sounds\\coin_add.wav')
        self.add_coin_sound = pygame.mixer.Sound("D:/adv/adventuregame/sounds/coin_add.wav")
        self.spend_coin_sound = pygame.mixer.Sound('sounds/coin_spend.wav')
        self.add_coin_sound.set_volume(0.5)
        self.spend_coin_sound.set_volume(0.5)

    def add_coins(self, amount):
        """Add coins to the player's balance."""
        self.coins += amount
        self.add_coin_sound.play()
        print(f"Added {amount} coins. Total coins: {self.coins}")

    def spend_coins(self, amount):
        """Spend coins from the player's balance."""
        if self.coins >= amount:
            self.coins -= amount
            self.spend_coin_sound.play()
            print(f"Spent {amount} coins. Remaining coins: {self.coins}")
            return True
        else:
            print(f"Not enough coins. You only have {self.coins} coins.")
            return False

class Shop:
    def __init__(self, inventory):
        """Initialize the shop with available items and the player's inventory."""
        self.items_for_sale = {
            'Health Potion': 10,  # Costs 10 coins
            'Attack Boost': 20,   # Costs 20 coins
            'Defense Boost': 20   # Costs 20 coins
        }
        self.inventory = inventory  # Reference to the player's inventory

    def show_items(self):
        """Display the items for sale and their prices."""
        print("Items for sale:")
        for item, price in self.items_for_sale.items():
            print(f"{item}: {price} coins")

    def buy_item(self, item_name, currency):
        """Allow the player to purchase an item if they have enough coins."""
        if item_name in self.items_for_sale:
            price = self.items_for_sale[item_name]
            if currency.spend_coins(price):  # Check if the player has enough coins
                # Add the purchased item to the player's inventory
                purchased_item = item(item_name, 0, 0)  # Position is irrelevant in inventory
                self.inventory.add_item(purchased_item)
                print(f"Purchased {item_name} for {price} coins.")
            else:
                print(f"Not enough coins to buy {item_name}.")
        else:
            print(f"{item_name} is not available in the shop.")

# Example integration with the main game (not a full game loop)
if __name__ == "__main__":
    # Initialize currency, inventory, and shop
    player_currency = Currency()
    player_inventory = Inventory()
    game_shop = Shop(player_inventory)

    # Adding coins to simulate gameplay rewards
    player_currency.add_coins(50)  # Player receives 50 coins

    # Show available items in the shop
    game_shop.show_items()

    # Try to purchase a Health Potion
    game_shop.buy_item('Health Potion', player_currency)

    # Check inventory after purchase
    player_inventory.display_inventory()
