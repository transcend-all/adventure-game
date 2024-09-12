# combat.py
import random

class CombatSystem:
    def __init__(self, player):
        """Initialize the combat system with a reference to the player."""
        self.player = player

    def player_attack(self, enemy):
        """Handle the player attacking an enemy."""
        damage = self.calculate_damage(self.player.attack_power)
        if enemy.take_damage(damage):
            print(f"Enemy defeated! Player dealt {damage} damage.")
        else:
            print(f"Player dealt {damage} damage to the enemy. Enemy's remaining health: {enemy.health}")

    def enemy_attack(self, enemy):
        """Handle an enemy attacking the player."""
        damage = self.calculate_damage(enemy.attack_power)
        self.player.take_damage(damage)
        print(f"Enemy attacked! Player took {damage} damage. Player's remaining health: {self.player.health}")

    def calculate_damage(self, base_attack_power):
        """Calculate the amount of damage based on the attacker's power and randomness."""
        return base_attack_power + random.randint(-2, 5)  # Adds some randomness to damage output
