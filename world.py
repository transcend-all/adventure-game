# world.py
import pygame

# Colors for different terrain types
GREEN = (34, 177, 76)  # Grass color
BROWN = (139, 69, 19)  # Obstacles like trees, rocks

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Define the terrain grid (0: grass, 1: obstacle)
        self.terrain = [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
        ]

        # Automatically calculate tile size to fit screen width
        self.tile_size = self.width // len(self.terrain[0])

    def draw(self, screen):
        """Draw the terrain (grass and obstacles) based on the terrain grid."""
        for row_index, row in enumerate(self.terrain):
            for col_index, tile in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size

                if tile == 0:  # Grass
                    pygame.draw.rect(screen, GREEN, (x, y, self.tile_size, self.tile_size))
                elif tile == 1:  # Obstacle
                    pygame.draw.rect(screen, BROWN, (x, y, self.tile_size, self.tile_size))

    def is_walkable(self, x, y):
        """Check if the given x, y position is walkable (i.e., not an obstacle)."""
        grid_x = x // self.tile_size
        grid_y = y // self.tile_size

        # Check if the position is within the grid boundaries
        if 0 <= grid_x < len(self.terrain[0]) and 0 <= grid_y < len(self.terrain):
            # Walkable if the terrain is grass (0)
            return self.terrain[grid_y][grid_x] == 0
        return False
