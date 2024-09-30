# health_system.py

import pygame

class HealthSystem:
    def __init__(self, max_health):
        """Initialize the health system with the maximum health value."""
        self.max_health = max_health
        self.current_health = max_health
        self.damage_sound = pygame.mixer.Sound('sounds/player_damage.wav')
        self.heal_sound = pygame.mixer.Sound('sounds/player_heal.wav')
        self.damage_sound.set_volume(0.5)
        self.heal_sound.set_volume(0.5)

    def take_damage(self, amount):
        """Reduce current health by a specified amount."""
        self.current_health -= amount
        self.damage_sound.play()
        if self.current_health <= 0:
            self.current_health = 0
            print("Health has dropped to 0!")
            return True  # Indicates death
        else:
            print(f"Health reduced by {amount}. Current health: {self.current_health}")
            return False  # Still alive

    def heal(self, amount):
        """Increase current health by a specified amount up to the maximum health."""
        self.current_health = min(self.current_health + amount, self.max_health)
        self.heal_sound.play()
        print(f"Healed by {amount}. Current health: {self.current_health}")

    def is_alive(self):
        """Check if the entity is still alive."""
        return self.current_health > 0

    def display_health(self):
        """Display the current health."""
        print(f"Current health: {self.current_health}/{self.max_health}")
