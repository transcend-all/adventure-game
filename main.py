# game_engine.py
import pygame
import sys
from characters.player import Player
from structure.world import World
from structure.level_manager import LevelManager
from structure.hud import HUD
from structure.combat import CombatSystem
from structure.currency import Currency
from monetization.item import Inventory
from monetization.item import Coin
from structure.graphics import Graphics
from monetization.monetization import Monetization
from data.data_pipeline import EventStream
from data.data_privacy import DataPrivacy
from monetization.store import Store

# Initialize Pygame
pygame.init()
pygame.mixer.init()

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
        pygame.display.set_caption('Quest for the Golden Artifact')

        # Initialize the game systems
        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.inventory = Inventory()
        self.currency = Currency()
        self.player = Player("Explorer", self.currency)
        self.hud = HUD(self.screen, self.player, self.currency)
        self.combat_system = CombatSystem(self.player)
        self.graphics = Graphics()
        self.level_manager = LevelManager(self.world, self.graphics)
        self.event_stream = EventStream()
        self.data_privacy = DataPrivacy()
        self.monetization_system = Monetization(self.currency)

        # Game state
        self.running = True
        self.paused = False
        self.sound_on = True  # Variable to track sound state

        # Load and play background music
        pygame.mixer.music.load('sounds/background_music.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # -1 means the music loops indefinitely

    def handle_events(self):
        """Handle input events (keyboard, quitting)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused  # Toggle pause
                    if self.paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_m:
                    # Simulate purchasing coins when the player presses 'M'
                    self.monetization_system.show_coin_packages()
                    self.monetization_system.purchase_coins('small', payment_method='usd')
                if event.key == pygame.K_s:
                    # Toggle sound on/off when 'S' is pressed
                    self.toggle_sound()

    def toggle_sound(self):
        """Toggle the sound on or off."""
        if self.sound_on:
            pygame.mixer.music.set_volume(0)
            self.sound_on = False
            # Optionally notify other classes to mute their sound effects
        else:
            pygame.mixer.music.set_volume(0.5)
            self.sound_on = True
            # Optionally notify other classes to unmute their sound effects

    def update(self):
        """Update game state (player, level, combat, etc.)."""
        if not self.paused:
            self.player.handle_input(self.world)
            self.level_manager.update()
            self.event_stream.send_event("player_moved", {"player_position": (self.player.rect.x, self.player.rect.y)})

            self.level_manager.collect_coins(self.player)

            # Simulate combat between player and enemies
            for enemy in self.level_manager.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.combat_system.player_attack(enemy, self.level_manager)
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
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

# Entry point to start the game
if __name__ == "__main__":
    game = GameEngine()
    game.run()
