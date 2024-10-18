# store.py

import pygame
from monetization.item import HealthPotion, AttackBoost, DefenseBoost



class Store:
    def __init__(self, player, current_user, level_manager, inventory, database_manager):
        """Initialize the store with the player and available items."""
        self.player = player
        self.current_user = current_user
        self.level_manager = level_manager
        self.database_manager = database_manager
        self.inventory = inventory
        self.purchase_sound = pygame.mixer.Sound('sounds/purchase_item.wav')
        self.purchase_sound.set_volume(0.5)
        self.items_for_sale = [
            HealthPotion(),
            AttackBoost(),
            DefenseBoost()
        ]

    def show_items(self):
        """Display available items in the store."""
        print("Welcome to the store! Here are the available items:")
        for index, item in enumerate(self.items_for_sale):
            print(f"{index + 1}. {item.name} - {item.price} coins: {item.description}")

    def buy_item(self, item_index):
        """Allow the player to buy an item if they have enough coins."""
        if 0 <= item_index < len(self.items_for_sale):
            item = self.items_for_sale[item_index]
            if self.player.currency.coins >= item.price:
                self.player.currency.spend_coins(item.price)  # Deduct coins
                self.purchase_sound.play()
                self.inventory.add_item(item)  # Add the item to the player's inventory
                print(f"{item.name} purchased for {item.price} coins! It has been added to your inventory.")

                username = self.current_user['username']
                level = self.level_manager.current_level # Assuming the player's level is tracked here
                coins = self.player.currency.coins
                inventory_items = [item.item_type for item in self.inventory.items]
                
                # Count the types of items in the inventory
                health_potions = inventory_items.count('Health Potion')
                attack_boosts = inventory_items.count('Attack Boost')
                defense_boosts = inventory_items.count('Defense Boost')
                
                # Call save_progress with the correct parameters
                self.database_manager.save_progress(username, level, coins, health_potions, attack_boosts, defense_boosts)
            else:
                print(f"Not enough coins to buy {item.name}. You have {self.player.currency.coins} coins.")
        else:
            print("Invalid item selection.")