# game_engine.py
import pygame
import sys
from player import Player
from world import World
from level_manager import LevelManager
from hud import HUD
from combat import CombatSystem
from currency import Currency
from item import Inventory
from graphics import Graphics
from monetization import Monetization
from data_pipeline import EventStream
from data_privacy import DataPrivacy

# Initialize Pygame
pygame.init()

# Screen dimensions and FPS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Set up the clock
clock = pygame.time.Clock()

class GameEngine:
    def __init__(self):
        # Create the game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Animal Kingdom: Quest for the Golden Artifact')

        # Initialize the game systems
        self.player = Player("Explorer")
        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_manager = LevelManager(self.world)
        self.inventory = Inventory()
        self.currency = Currency()
        self.hud = HUD(self.screen, self.player, self.currency)
        self.combat_system = CombatSystem(self.player)
        self.graphics = Graphics()
        self.event_stream = EventStream()
        self.data_privacy = DataPrivacy()
        self.monetization_system = Monetization(self.currency)

        # Game state
        self.running = True
        self.paused = False

    def handle_events(self):
        """Handle input events (keyboard, quitting)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused  # Toggle pause
                if event.key == pygame.K_m:
                    # Simulate purchasing coins when the player presses 'M'
                    self.monetization_system.show_coin_packages()
                    self.monetization_system.purchase_coins('small', payment_method='usd')

    def update(self):
        """Update game state (player, level, combat, etc.)."""
        if not self.paused:
            self.player.handle_input(self.world)
            self.level_manager.update()
            self.event_stream.send_event("player_moved", {"player_position": (self.player.rect.x, self.player.rect.y)})

            # Simulate combat between player and enemies
            for enemy in self.level_manager.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.combat_system.player_attack(enemy)
                    if not enemy.is_alive():
                        self.level_manager.enemies.remove(enemy)

    def render(self):
        """Draw everything on the screen."""
        self.screen.fill((255, 255, 255))  # Clear the screen with a white background
        self.level_manager.render(self.screen)
        self.graphics.draw_player(self.screen, self.player)

        # Draw HUD (health bar, coins)
        self.hud.draw()

        # Update the display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()  # Handle user inputs
            self.update()         # Update game objects and logic
            self.render()         # Draw everything to the screen

            # Cap the frame rate
            clock.tick(FPS)

        # Quit the game
        pygame.quit()
        sys.exit()


# Entry point to start the game
if __name__ == "__main__":
    game = GameEngine()
    game.run()
