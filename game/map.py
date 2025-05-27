import random
from typing import List
import pygame

from config import Config


class GameMap:
    """Represents the game map with walls and paths"""
    def __init__(self, filename: str):
        self.filename = filename
        self.grid = self.load_map(filename)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.grid else 0
    
    def load_map(self, filename: str) -> List[List[int]]:
        """Load a map from a file"""
        try:
            with open(filename) as f:
                lines = [line.strip() for line in f if line.strip()]
            return [[int(ch) for ch in line] for line in lines]
        except (FileNotFoundError, IOError):
            print(f"Error: Could not load map file {filename}")
            # Create a simple default map
            return [[1 for _ in range(20)] for _ in range(20)]
    
    def save_map(self, filename: str) -> None:
        """Save the current map to a file"""
        try:
            with open(filename, 'w') as f:
                for row in self.grid:
                    f.write(''.join(map(str, row)) + '\n')
        except IOError:
            print(f"Error: Could not save map to {filename}")
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid (within bounds and not a wall)"""
        return (0 <= x < self.cols and 0 <= y < self.rows and self.grid[y][x] == 0)
    
    def generate_random_map(self) -> None:
        """Generate a random map with walls"""
        map_lines = self.load_map(self.filename)
        new_grid = []
        
        for r in range(self.rows):
            if r in [0, 14, 15, 16, 17, 18, 31]:
                new_grid.append(map_lines[r])
            else:
                row = [1 if random.random() < 0.3 else 0 for c in range(self.cols)]
                row[0], row[-1] = 1, 1
                new_grid.append(row)
        
        self.grid = new_grid
    
    def draw(self, surface: pygame.Surface, x: int, y: int, tile_size: int) -> None:
        """Draw the map on the given surface"""
        map_surface = pygame.Surface((self.cols*tile_size, self.rows*tile_size), pygame.SRCALPHA)
        
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c*tile_size, r*tile_size, tile_size, tile_size)
                if self.grid[r][c] == 1:
                    # Draw walls with a 3D effect
                    pygame.draw.rect(map_surface, Config.WALL_COLOR, rect)
                    pygame.draw.line(map_surface, (Config.WALL_COLOR[0]-30, Config.WALL_COLOR[1]-30, Config.WALL_COLOR[2]-30), 
                                  (c*tile_size, r*tile_size), (c*tile_size, (r+1)*tile_size), 1)
                    pygame.draw.line(map_surface, (Config.WALL_COLOR[0]-30, Config.WALL_COLOR[1]-30, Config.WALL_COLOR[2]-30), 
                                  (c*tile_size, r*tile_size), ((c+1)*tile_size, r*tile_size), 1)
                    pygame.draw.line(map_surface, (min(Config.WALL_COLOR[0]+30, 255), min(Config.WALL_COLOR[1]+30, 255), min(Config.WALL_COLOR[2]+30, 255)), 
                                  ((c+1)*tile_size-1, r*tile_size), ((c+1)*tile_size-1, (r+1)*tile_size), 1)
                    pygame.draw.line(map_surface, (min(Config.WALL_COLOR[0]+30, 255), min(Config.WALL_COLOR[1]+30, 255), min(Config.WALL_COLOR[2]+30, 255)), 
                                  (c*tile_size, (r+1)*tile_size-1), ((c+1)*tile_size, (r+1)*tile_size-1), 1)
                else:
                    # Draw path tiles with a subtle grid
                    pygame.draw.rect(map_surface, Config.WHITE, rect)
                    pygame.draw.line(map_surface, (230, 230, 230), 
                                  (c*tile_size, r*tile_size), (c*tile_size+tile_size, r*tile_size), 1)
                    pygame.draw.line(map_surface, (230, 230, 230), 
                                  (c*tile_size, r*tile_size), (c*tile_size, r*tile_size+tile_size), 1)
        
        # Draw a border around the map
        pygame.draw.rect(map_surface, Config.BLACK, (0, 0, self.cols*tile_size, self.rows*tile_size), 2)
        
        surface.blit(map_surface, (x, y))

