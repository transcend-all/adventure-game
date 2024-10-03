# main.py
import pygame
import sys
import time
import logging
from monetization import accounts
from monetization.button import Button 
from monetization.input_box import InputBox
from characters.player import Player
from structure.world import World
from structure.level_manager import LevelManager
from structure.hud import HUD
from structure.combat import CombatSystem
from structure.graphics import Graphics
from monetization.currency import Currency
from monetization.item import Inventory, Coin
from monetization.store import Store
from monetization.monetization import Monetization
from data_processing.data_pipeline import EventStream
from data_processing.data_privacy import DataPrivacy
from data_processing.csv_logger import CSVLogger
from data_processing.psql_logger import PSQLLogger 
from data.kafka.producer import KafkaEventProducer

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions and FPS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Set up the clock
clock = pygame.time.Clock()

# Game configuration for logging method
USE_POSTGRESQL = True  # Change this to False to switch to CSV logging

# PostgreSQL database configuration
db_config = {
    'dbname': 'adventure_game',
    'user': 'adventure_game',
    'password': 'adventure_game',
    'host': 'localhost',
    'port': 5432
} 

# Configure logging (optional but recommended)
logging.basicConfig(
    filename='game_errors.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class GameEngine:
    def __init__(self, current_user):
        # Create the game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Quest for the Golden Artifact')

        # Initialize the game systems with user data
        self.currency = Currency()
        self.currency.coins = current_user.get('coins', 0)  # Initialize with user's coins
        self.player = Player(current_user.get('username', 'Player'), self.currency)
        self.hud = HUD(self.screen, self.player, self.currency)
        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)  # Corrected initialization
        self.combat_system = CombatSystem(self.player)
        self.graphics = Graphics()
        self.level_manager = LevelManager(self.world, self.graphics, self.currency)  # Passed currency
        self.level_manager.current_level = current_user.get('level', 1)  # Set current level
        self.event_stream = EventStream()
        self.data_privacy = DataPrivacy()
        self.monetization_system = Monetization(self.currency)

        # Initialize Kafka producer
        self.kafka_producer = KafkaEventProducer(
            bootstrap_servers=['localhost:9092'],  # Update if different
            topic='game_events'
        )

        try:
            pygame.mixer.music.load('path_to_music_file.mp3')  # Replace with your music file path
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # -1 loops the music indefinitely
        except Exception as e:
            logging.error(f"Failed to load or play background music: {e}")
            print(f"Failed to load or play background music: {e}")

        # Initialize the logger (either CSV or PostgreSQL based on config)
        try:
            if USE_POSTGRESQL:
                self.logger = PSQLLogger(db_config)
            else:
                self.logger = CSVLogger('data/player_movements.csv') 
        except Exception as e:
            logging.error(f"Failed to initialize logger: {e}")
            print("Error initializing logger. Logging disabled.")
            self.logger = None

        # Game state
        self.running = True
        self.paused = False
        self.current_user = current_user  # Store current user
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

    def on_level_complete(self, coins_collected):
        """Handle level completion: update level and coins, then save progress."""
        new_level = self.level_manager.current_level + 1
        new_coins = self.currency.coins + coins_collected
        self.level_manager.current_level = new_level
        self.currency.coins = new_coins

        # Update the user's data in the database
        try:
            import psycopg2  # Ensure psycopg2 is imported
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET level = %s, coins = %s WHERE id = %s', 
                           (new_level, new_coins, self.current_user['id']))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Level {new_level} completed! Coins: {new_coins}.")
        except Exception as e:
            logging.error(f"Failed to update user progress: {e}")
            print("Error saving progress.")

    def update(self):
        """Update game state (player, level, combat, etc.)."""
        if not self.paused:
            self.player.handle_input(self.world)
            self.level_manager.update()

            # Capture player movement event
            player_x, player_y = self.player.rect.x, self.player.rect.y
            event = {
                "type": "player_moved",
                "data": {"player_position": [player_x, player_y]},
                "timestamp": time.time()
            }

            # Send event to Kafka
            self.kafka_producer.send_event(event)

            # Existing event streaming and logging
            self.event_stream.send_event("player_moved", {"player_position": (player_x, player_y)})

            # Collect coins
            coins_collected = self.level_manager.collect_coins(self.player)
            if coins_collected is not None and coins_collected > 0:
                print(f"Collected {coins_collected} coins!")

            # Log the player's movement
            if self.logger:
                try:
                    self.logger.log_event(
                        "player_moved",
                        {"timestamp": event["timestamp"], "player_position": [player_x, player_y]}
                    )
                except Exception as e:
                    logging.error(f"Failed to log event: {e}")
                    print("Error logging event.")

            # Simulate combat between player and enemies
            for enemy in self.level_manager.enemies[:]:  # Use a copy of the list
                if self.player.rect.colliderect(enemy.rect):
                    self.combat_system.player_attack(enemy, self.level_manager)
                    if not enemy.is_alive():
                        self.level_manager.enemies.remove(enemy)
                        print(f"Enemy defeated! Total enemies left: {len(self.level_manager.enemies)}")
                        if len(self.level_manager.enemies) == 0:
                            # All enemies defeated, complete the level
                            self.on_level_complete(coins_collected=10)  # Example coin reward

    def render(self):
        """Draw everything on the screen."""
        self.screen.fill((255, 255, 255))  # Clear the screen with a white background
        self.level_manager.render(self.screen)
        self.graphics.draw_player(self.screen, self.player)

        # Draw HUD (health bar, coins)
        self.hud.draw()

        # Update the display
        pygame.display.flip()

    def close(self):
        """Close any connections (e.g., to PostgreSQL and Kafka)."""
        if USE_POSTGRESQL and self.logger:
            self.logger.close()
        if self.kafka_producer:
            self.kafka_producer.close()

    def save_progress(self):
        """Save the user's progress to the database."""
        try:
            if not self.current_user:
                raise ValueError("No current user to save progress for.")
            if 'id' not in self.current_user:
                raise KeyError("Current user does not have an 'id' key.")
            print(f"Attempting to save progress for user: {self.current_user}")  # Debugging line
            import psycopg2  # Ensure psycopg2 is imported
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET level = %s, coins = %s WHERE id = %s', 
                           (self.level_manager.current_level, self.currency.coins, self.current_user['id']))
            conn.commit()
            cursor.close()
            conn.close()
            print("Progress saved!")
        except KeyError as ke:
            logging.error(f"KeyError in save_progress: {ke}")
            print("Error saving progress: Missing user information.")
        except Exception as e:
            logging.error(f"Failed to save progress for user {self.current_user}: {e}")
            print("Error saving progress.")

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()  # Handle user inputs
            self.update()         # Update game objects and logic
            self.render()         # Draw everything to the screen

            # Cap the frame rate
            clock.tick(FPS)
        self.save_progress()  # Save progress when the game loop ends
        self.close()          # Ensure proper cleanup of resources 

        # Quit the game
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

# Additional Classes for Account Screens
class LoginScreen:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.Font(None, 32)
        # Adjusted positions
        self.username_box = InputBox(320, 200, 200, 32)
        self.password_box = InputBox(320, 250, 200, 32, is_password=True)
        self.input_boxes = [self.username_box, self.password_box]
        self.active_box = 0  # Index of the currently active box
        self.input_boxes[self.active_box].active = True
        self.input_boxes[self.active_box].color = self.input_boxes[self.active_box].color_active
        self.message = ''

        self.back_button = Button(
            x=20,  # 20 pixels from the left
            y=20,  # 20 pixels from the top
            width=100,
            height=40,
            text="Back",
            font=pygame.font.Font(None, 24),
            bg_color=(220, 20, 60),  # Crimson color
            text_color=(255, 255, 255)  # White text
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            # Switch focus to the next input box
            self.input_boxes[self.active_box].active = False
            self.input_boxes[self.active_box].color = self.input_boxes[self.active_box].color_inactive
            self.active_box = (self.active_box + 1) % len(self.input_boxes)
            self.input_boxes[self.active_box].active = True
            self.input_boxes[self.active_box].color = self.input_boxes[self.active_box].color_active
        else:
            # Check if Back Button is clicked
            if self.back_button.is_clicked(event):
                self.game.state = 'start'  # Navigate back to Start Screen
                return  # Exit the method early to prevent further processing

            # Pass the event to the active input box
            result = self.input_boxes[self.active_box].handle_event(event)
            if result == 'submit':
                # Attempt to login
                user = accounts.login_user(self.username_box.text, self.password_box.text)
                if user:
                    print(f"Login successful for user: {user}")  # Debugging line
                    self.game.current_user = user
                    self.game.switch_to_game()
                else:
                    self.message = "Invalid credentials. Try again."

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        # Render labels
        label_font = pygame.font.Font(None, 32)
        username_label = label_font.render("Username:", True, (255, 255, 255))
        password_label = label_font.render("Password:", True, (255, 255, 255))
        self.screen.blit(username_label, (200, 200))  # y=200
        self.screen.blit(password_label, (200, 250))  # y=250
        # Draw input boxes
        for box in self.input_boxes:
            box.draw(self.screen)
        # Draw Back Button
        self.back_button.draw(self.screen)
        # Render message
        if self.message:
            message_surface = self.font.render(self.message, True, (255, 0, 0))
            self.screen.blit(message_surface, (300, 300))
        pygame.display.flip()


class RegisterScreen:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.Font(None, 32)
        # Adjusted positions
        self.username_box = InputBox(320, 200, 200, 32)
        self.password_box = InputBox(320, 250, 200, 32, is_password=True)
        self.input_boxes = [self.username_box, self.password_box]
        self.active_box = 0  # Index of the currently active box
        self.input_boxes[self.active_box].active = True
        self.input_boxes[self.active_box].color = self.input_boxes[self.active_box].color_active
        self.message = ''

        # Initialize the Back Button
        self.back_button = Button(
            x=20,  # 20 pixels from the left
            y=20,  # 20 pixels from the top
            width=100,
            height=40,
            text="Back",
            font=pygame.font.Font(None, 24),
            bg_color=(220, 20, 60),  # Crimson color
            text_color=(255, 255, 255)  # White text
        )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            # Switch focus to the next input box
            self.input_boxes[self.active_box].active = False
            self.input_boxes[self.active_box].color = self.input_boxes[self.active_box].color_inactive
            self.active_box = (self.active_box + 1) % len(self.input_boxes)
            self.input_boxes[self.active_box].active = True
            self.input_boxes[self.active_box].color = self.input_boxes[self.active_box].color_active
        else:
            # Check if Back Button is clicked
            if self.back_button.is_clicked(event):
                self.game.state = 'start'  # Navigate back to Start Screen
                return  # Exit the method early to prevent further processing

            # Pass the event to the active input box
            result = self.input_boxes[self.active_box].handle_event(event)
            if result == 'submit':
                # Attempt to register
                success = accounts.register_user(self.username_box.text, self.password_box.text)
                if success:
                    self.message = "Registration successful! Please log in."
                    # Optionally switch to login screen after a short delay
                    pygame.time.set_timer(pygame.USEREVENT, 2000)  # Set a timer to switch screens
                else:
                    self.message = "Username already exists. Try another."

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        # Render labels
        label_font = pygame.font.Font(None, 32)
        username_label = label_font.render("Username:", True, (255, 255, 255))
        password_label = label_font.render("Password:", True, (255, 255, 255))
        self.screen.blit(username_label, (200, 200))  # y=200
        self.screen.blit(password_label, (200, 250))  # y=250
        # Draw input boxes
        for box in self.input_boxes:
            box.draw(self.screen)
        # Draw Back Button
        self.back_button.draw(self.screen)
        # Render message
        if self.message:
            message_color = (0, 255, 0) if "successful" in self.message else (255, 0, 0)
            message_surface = self.font.render(self.message, True, message_color)
            self.screen.blit(message_surface, (200, 320))  # Adjusted y-position to avoid overlap
        pygame.display.flip()

class StartScreen:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.options = ['Login', 'Register']
        self.selected = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:
                    self.game.state = 'login'  # Corrected state transition
                elif self.selected == 1:
                    self.game.state = 'register'

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        title_surface = self.font.render("Welcome to Quest for the Golden Artifact", True, (255, 255, 255))
        self.screen.blit(title_surface, (50, 100))

        for idx, option in enumerate(self.options):
            color = (255, 255, 0) if idx == self.selected else (255, 255, 255)
            option_surface = self.small_font.render(option, True, color)
            self.screen.blit(option_surface, (100, 200 + idx * 50))
        pygame.display.flip()

class GameEngineWithAccounts:
    def __init__(self):
        # Initial state
        self.state = 'start'  # start, login, register, game
        self.current_user = None

        # Create the game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Quest for the Golden Artifact')

        # Initialize account screens
        self.start_screen = StartScreen(self.screen, self)
        self.login_screen = LoginScreen(self.screen, self)
        self.register_screen = RegisterScreen(self.screen, self)

        # Initialize GameEngine as None; will be created after login
        self.game_engine = None

    def run(self):
        """Main loop handling different states."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state == 'game' and self.game_engine:
                        self.game_engine.save_progress()
                        self.game_engine.close()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.USEREVENT:
                    # Timer event to switch to login screen after successful registration
                    if self.state == 'register':
                        self.state = 'login'
                else:
                    if self.state == 'start':
                        self.start_screen.handle_event(event)
                    elif self.state == 'login':
                        self.login_screen.handle_event(event)
                    elif self.state == 'register':
                        self.register_screen.handle_event(event)
                    elif self.state == 'game':
                        self.game_engine.handle_events()

            if self.state == 'start':
                self.start_screen.draw()
            elif self.state == 'login':
                self.login_screen.draw()
            elif self.state == 'register':
                self.register_screen.draw()
            elif self.state == 'game':
                self.game_engine.update()
                self.game_engine.render()

            # Cap the frame rate
            clock.tick(FPS)

    def switch_to_game(self):
        """Initialize the GameEngine with the current user and switch to game state."""
        try:
            self.game_engine = GameEngine(self.current_user)
            self.state = 'game'
            logging.info(f"Switched to game state for user {self.current_user['username']}.")
            print(f"Switched to game state for user {self.current_user['username']}.")
        except Exception as e:
            logging.error(f"Failed to switch to game: {e}")
            print(f"Error switching to game mode: {e}")  # Print exception details


# Entry point to start the game
if __name__ == "__main__":
    game_with_accounts = GameEngineWithAccounts()
    game_with_accounts.run()
