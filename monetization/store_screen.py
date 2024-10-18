# store_screen.py
import pygame
from monetization.button import Button

class StoreScreen:
    def __init__(self, screen, store):
        self.screen = screen
        self.store = store
        self.font = pygame.font.Font(None, 32)
        self.message = ""
        self.back_button = Button(650, 500, 140, 40, text="Back", font=self.font, bg_color=(255, 0, 0))

    def draw(self):
        """Render the store UI."""
        self.screen.fill((0, 0, 0))  # Clear the screen with a black background
        title_surface = self.font.render("Store", True, (255, 255, 255))
        self.screen.blit(title_surface, (350, 50))

        # Display the items for sale
        for index, item in enumerate(self.store.items_for_sale):
            item_text = f"{index + 1}. {item.name} - {item.price} coins: {item.description}"
            item_surface = self.font.render(item_text, True, (255, 255, 255))
            self.screen.blit(item_surface, (100, 100 + index * 50))

        # Display message and draw back button
        if self.message:
            message_surface = self.font.render(self.message, True, (255, 255, 0))
            self.screen.blit(message_surface, (100, 400))
        
        self.back_button.draw(self.screen)

        pygame.display.flip()  # Update the display

    def handle_event(self, event):
        """Handle events for the store, including buying items and going back."""
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                item_index = event.key - pygame.K_1  # Convert key press to index
                if item_index < len(self.store.items_for_sale):
                    self.store.buy_item(item_index)  # Buy the item
                    self.message = f"Bought {self.store.items_for_sale[item_index].name}!"
                else:
                    self.message = "Invalid selection."
        
        if self.back_button.is_clicked(event):
            return "close_store"  # Signal to close the store
