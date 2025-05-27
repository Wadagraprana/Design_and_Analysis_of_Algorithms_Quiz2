
import math
import random
import time
from typing import List, Tuple
import pygame

from config import Config
from game.pathfinding import PathfindingAlgorithm
from game.map import GameMap

class Ghost:
    """Represents a ghost in the game"""
    def __init__(self, name: str, color: str, start_pos: Tuple[int, int], algorithm: PathfindingAlgorithm):
        self.name = name
        self.color = color
        self.position = list(start_pos)
        self.algorithm = algorithm
        self.path = []
        self.finish_time = None
        self.algorithm_name = algorithm.name
    
    def reset(self, start_pos: Tuple[int, int]) -> None:
        """Reset the ghost to its start position"""
        self.position = list(start_pos)
        self.path = []
        self.finish_time = None
    
    def find_path_to(self, target: Tuple[int, int]) -> None:
        """Find a path to the target position"""
        self.path = self.algorithm.find_path(tuple(self.position), target)
        if self.path:
            self.path.pop(0)  # Remove current position
    
    def move(self) -> bool:
        """Move along the path if available, return True if moved"""
        if self.path:
            self.position = list(self.path.pop(0))
            return True
        return False
    
    def reached_position(self, pos: Tuple[int, int]) -> bool:
        """Check if the ghost reached a specific position"""
        return self.position == list(pos)

class Cherry:
    """Represents the target cherry in the game"""
    def __init__(self, game_map: GameMap):
        self.game_map = game_map
        self.position = [2, 1]  # Default position
        self.generate_position()
    
    def generate_position(self, ghost_positions: List[Tuple[int, int]] = None) -> None:
        """Generate a valid position for the cherry"""
        if ghost_positions is None:
            ghost_positions = []
            
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(1, self.game_map.cols - 2)
            y = random.randint(1, self.game_map.rows - 2)
            
            if self.game_map.is_valid_position(x, y):
                # Check if the position is reachable from all ghost positions
                reachable = True
                for ghost_pos in ghost_positions:
                    # We'd need a proper pathfinding check here
                    # But for simplicity, we'll assume it's reachable
                    pass
                    
                if reachable:
                    self.position = [x, y]
                    return
        
        # If we couldn't find a valid position, use a default
        self.position = [2, 1]
    
    def draw(self, surface: pygame.Surface, x: int, y: int, tile_size: int, cherry_img: pygame.Surface) -> None:
        """Draw the cherry with a pulsating effect"""
        cherry_pulse = math.sin(time.time() * 5) * 2 + 2
        cherry_glow = pygame.Surface((tile_size + cherry_pulse*2, tile_size + cherry_pulse*2), pygame.SRCALPHA)
        pygame.draw.circle(cherry_glow, (Config.CHERRY_RED[0], Config.CHERRY_RED[1], Config.CHERRY_RED[2], 100), 
                        (cherry_glow.get_width()//2, cherry_glow.get_height()//2), tile_size//2 + cherry_pulse)
        
        surface.blit(cherry_glow, 
                  (x + self.position[0]*tile_size - cherry_pulse, 
                   y + self.position[1]*tile_size - cherry_pulse))
        
        surface.blit(cherry_img, (x + self.position[0]*tile_size, y + self.position[1]*tile_size))
