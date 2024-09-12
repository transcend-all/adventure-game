# store.py

class Store:
    def __init__(self, player):
        """Initialize the store with the player and available items."""
        self.player = player
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
                self.player.inventory.append(item)  # Add the item to the player's inventory
                print(f"{item.name} purchased for {item.price} coins! It has been added to your inventory.")
            else:
                print(f"Not enough coins to buy {item.name}. You have {self.player.currency.coins} coins.")
        else:
            print("Invalid item selection.")
