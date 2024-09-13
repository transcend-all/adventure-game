# hud.py - the GUI
import pygame

# Constants for HUD display
FONT_SIZE = 24
FONT_COLOR = (0, 0, 0)  # Black for text
HEALTH_COLOR = (255, 0, 0)  # Red for health bar
COIN_COLOR = (255, 223, 0)  # Gold for coins

class HUD:
    def __init__(self, screen, player, currency):
        """Initialize the HUD with references to the player and currency system."""
        self.screen = screen
        self.player = player
        self.currency = currency
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        # self.store_button = pygame.image.load(store_button_image).convert_alpha()
        # self.store_button_rect = self.store_button.get_rect(topleft=(700, 20))

    def draw_health_bar(self):
        """Draw the player's health bar on the screen."""
        max_health_bar_width = 200
        health_percentage = self.player.health / 100
        current_health_bar_width = max_health_bar_width * health_percentage

        # Draw the health bar background (gray)
        pygame.draw.rect(self.screen, (128, 128, 128), (20, 20, max_health_bar_width, 20))
        # Draw the current health (red)
        pygame.draw.rect(self.screen, HEALTH_COLOR, (20, 20, current_health_bar_width, 20))

    def draw_coins(self):
        """Draw the player's current coin balance on the screen."""
        coin_text = self.font.render(f"Coins: {self.currency.coins}", True, FONT_COLOR)
        self.screen.blit(coin_text, (20, 50))

    def draw(self):
        """Draw the entire HUD on the screen (health bar, coins, etc.)."""
        self.draw_health_bar()
        self.draw_coins()
        # self.screen.blit(self.store_button, self.store_button_rect)


