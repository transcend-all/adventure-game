# Animal Kingdom: Quest for the Golden Artifact

**Animal Kingdom: Quest for the Golden Artifact** is a pixel-art styled, 90s-inspired adventure game where the player embarks on a quest to defeat enemies, collect coins, and purchase items from the in-game store. The game combines exploration, combat, and freemium mechanics with a retro look.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Controls](#controls)
- [Game Mechanics](#game-mechanics)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Retro 16-bit Pixel Art**: Inspired by 90s games like *Legend of Zelda*.
- **Coin Collection**: Defeat enemies and collect coins to purchase power-ups.
- **In-Game Store**: Purchase items like health potions, attack boosts, and defense boosts to power up your character.
- **Infinite Levels**: Each level increases in difficulty, with new enemies spawning.
- **Freemium Store Mechanic**: Earn or buy coins to keep playing or overcome tougher challenges.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/animal-kingdom.git
    ```
   
2. **Navigate into the project directory**:
    ```bash
    cd animal-kingdom
    ```

3. **Install the required dependencies**:
    - Install Pygame:
    ```bash
    pip install pygame
    ```

4. **Run the game**:
    ```bash
    python game_engine.py
    ```

## How to Play

- Your goal is to defeat enemies, collect coins, and purchase items from the in-game store to become stronger.
- The game features infinite levels, each progressively harder than the last.
- Use your coins wisely to buy power-ups and defeat tougher enemies.

## Controls

- **Arrow Keys**: Move the player character.
- **S Key**: Open the in-game store.
- **B Key**: Purchase an item from the store.
- **P Key**: Pause the game.
- **M Key**: Simulate purchasing coins.

## Game Mechanics

1. **Combat**:
   - The player can collide with enemies to initiate combat. If the enemy's health drops to zero, it dies and drops coins.
   
2. **Coins**:
   - Enemies drop coins when defeated. The player can collect them to spend in the store.
   
3. **In-Game Store**:
   - Open the store by pressing the **S** key. Use your coins to buy power-ups like health potions, attack boosts, and defense boosts.
   - Coins can be earned in-game or purchased using real money.
   
4. **Items**:
   - **Health Potion**: Restores health.
   - **Attack Boost**: Temporarily increases attack power.
   - **Defense Boost**: Temporarily increases defense.

## Contributing

Contributions are welcome! If you'd like to contribute to the project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License.
