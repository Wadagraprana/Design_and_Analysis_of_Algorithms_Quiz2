from abc import ABC, abstractmethod
from collections import deque
import heapq
import random
from typing import List, Tuple
from game.map import GameMap

class PathfindingAlgorithm(ABC):
    """Abstract base class for pathfinding algorithms"""
    def __init__(self, game_map: GameMap):
        self.game_map = game_map
        self.name = "Unknown"
    
    @abstractmethod
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find a path from start to goal"""
        pass

class BFSAlgorithm(PathfindingAlgorithm):
    """Breadth-first search implementation"""
    def __init__(self, game_map: GameMap):
        super().__init__(game_map)
        self.name = "BFS"
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using breadth-first search"""
        queue = deque([[start]])
        visited = set([start])
        
        while queue:
            path = queue.popleft()
            x, y = path[-1]
            
            if (x, y) == goal:
                return path
                
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.game_map.is_valid_position(nx, ny) and (nx, ny) not in visited:
                    queue.append(path + [(nx, ny)])
                    visited.add((nx, ny))
        
        return []  # No path found

class DFSAlgorithm(PathfindingAlgorithm):
    """Depth-first search implementation"""
    def __init__(self, game_map: GameMap):
        super().__init__(game_map)
        self.name = "DFS"
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using depth-first search"""
        stack = [[start]]
        visited = set([start])
        
        while stack:
            path = stack.pop()
            x, y = path[-1]
            
            if (x, y) == goal:
                return path
                
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.game_map.is_valid_position(nx, ny) and (nx, ny) not in visited:
                    stack.append(path + [(nx, ny)])
                    visited.add((nx, ny))
        
        return []  # No path found

class AStarAlgorithm(PathfindingAlgorithm):
    """A* pathfinding implementation"""
    def __init__(self, game_map: GameMap):
        super().__init__(game_map)
        self.name = "AStar"
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using A* search"""
        open_set = []
        heapq.heappush(open_set, (0, [start]))
        visited = set()
        
        while open_set:
            cost, path = heapq.heappop(open_set)
            x, y = path[-1]
            
            if (x, y) == goal:
                return path
                
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.game_map.is_valid_position(nx, ny) and (nx, ny) not in visited:
                    new_path = path + [(nx, ny)]
                    new_cost = len(new_path) + self.heuristic((nx, ny), goal)
                    heapq.heappush(open_set, (new_cost, new_path))
        
        return []  # No path found

class DijkstraAlgorithm(PathfindingAlgorithm):
    """Dijkstra's algorithm implementation"""
    def __init__(self, game_map: GameMap):
        super().__init__(game_map)
        self.name = "Dijkstra"
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using Dijkstra's algorithm"""
        open_set = []
        heapq.heappush(open_set, (0, [start]))
        visited = set()
        
        while open_set:
            cost, path = heapq.heappop(open_set)
            x, y = path[-1]
            
            if (x, y) == goal:
                return path
                
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.game_map.is_valid_position(nx, ny) and (nx, ny) not in visited:
                    new_path = path + [(nx, ny)]
                    new_cost = len(new_path) - 1  # Just the number of steps
                    heapq.heappush(open_set, (new_cost, new_path))
        
        return []  # No path found

class KruskalAlgorithm(PathfindingAlgorithm):
    """Random walk algorithm (named Kruskal for consistency with original code)"""
    def __init__(self, game_map: GameMap):
        super().__init__(game_map)
        self.name = "Kruskal"
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find a path using a randomized approach (not actual Kruskal's)"""
        path = [start]
        current = start
        
        max_iterations = 1000  # Prevent infinite loops
        iteration = 0
        
        while current != goal and iteration < max_iterations:
            x, y = current
            options = []
            
            # Find all valid adjacent cells
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.game_map.is_valid_position(nx, ny):
                    options.append((nx, ny))
            
            # If we have options, choose a random one and continue
            if options:
                current = random.choice(options)
                if current not in path:  # Avoid cycles
                    path.append(current)
            else:
                # If we're stuck, try to backtrack
                if len(path) > 1:
                    path.pop()
                    current = path[-1]
                else:
                    break  # Can't go anywhere
            
            iteration += 1
        
        return path

