# combat.py
import random
import pygame

class CombatSystem:
    def __init__(self, player):
        """Initialize the combat system with a reference to the player."""
        self.player = player
        self.player_attack_sound = pygame.mixer.Sound('sounds/player_attack.wav')
        self.enemy_attack_sound = pygame.mixer.Sound('sounds/enemy_attack.wav')
        self.enemy_death_sound = pygame.mixer.Sound('sounds/enemy_death.wav')
        self.player_attack_sound.set_volume(0.5)
        self.enemy_attack_sound.set_volume(0.5)
        self.enemy_death_sound.set_volume(0.5)

    def player_attack(self, enemy, level_manager):
        """Handle the player attacking an enemy."""
        self.player_attack_sound.play()
        damage = self.calculate_damage(self.player.attack_power)
        if enemy.take_damage(damage, level_manager):
            self.enemy_death_sound.play()
            print(f"Enemy defeated! Player dealt {damage} damage.")
        else:
            print(f"Player dealt {damage} damage to the enemy. Enemy's remaining health: {enemy.health}")

    def enemy_attack(self, enemy):
        """Handle an enemy attacking the player."""
        self.enemy_attack_sound.play()
        damage = self.calculate_damage(enemy.attack_power)
        self.player.take_damage(damage)
        print(f"Enemy attacked! Player took {damage} damage. Player's remaining health: {self.player.health}")

    def calculate_damage(self, base_attack_power):
        """Calculate the amount of damage based on the attacker's power and randomness."""
        return base_attack_power + random.randint(-2, 5)  # Adds some randomness to damage output
