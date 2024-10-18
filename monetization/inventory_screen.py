import pygame
from monetization.button import Button
from monetization.item import HealthPotion, AttackBoost, DefenseBoost

class InventoryScreen:
    def __init__(self, screen, inventory):
        self.screen = screen
        self.inventory = inventory
        self.font = pygame.font.Font(None, 32)
        self.message = ""
        self.back_button = Button(650, 500, 140, 40, text="Back", font=self.font, bg_color=(255, 0, 0))

    def draw(self):
        """Render the inventory screen."""
        self.screen.fill((0, 0, 0))  # Clear the screen with a black background
        title_surface = self.font.render("Inventory", True, (255, 255, 255))
        self.screen.blit(title_surface, (350, 50))

        # Display the items in the player's inventory
        for index, item in enumerate(self.inventory.items):
            item_text = f"{index + 1}. {item.item_type}"
            item_surface = self.font.render(item_text, True, (255, 255, 255))
            self.screen.blit(item_surface, (100, 100 + index * 50))

        # Draw the back button
        self.back_button.draw(self.screen)
        pygame.display.flip()

    def handle_event(self, event):
        """Handle events for the store, including buying items and going back."""
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                item_index = event.key - pygame.K_1  # Convert key press to index
                item_type = None

                if item_index < len(self.inventory.items):
                    if str(type(self.inventory.items[item_index])) == "<class 'monetization.item.HealthPotion'>":
                        item_type = 'Health Potion'
                    elif str(type(self.inventory.items[item_index])) == "<class 'monetization.item.AttackBoost'>":
                        item_type = 'Attack Boost'
                    elif str(type(self.inventory.items[item_index])) == "<class 'monetization.item.DefenseBoost'>":
                        item_type = 'Defense Boost'
                    
                    self.inventory.use_item(item_type)  # Use the item
                    self.message = f"Used {item_type}!"
                else:
                    self.message = "Invalid selection."
        
        if self.back_button.is_clicked(event):
            return "close_inventory"
