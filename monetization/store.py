# store.py

import pygame


class Store:
    def __init__(self, player):
        """Initialize the store with the player and available items."""
        self.player = player
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
                self.player.inventory.append(item)  # Add the item to the player's inventory
                print(f"{item.name} purchased for {item.price} coins! It has been added to your inventory.")
            else:
                print(f"Not enough coins to buy {item.name}. You have {self.player.currency.coins} coins.")
        else:
            print("Invalid item selection.")
