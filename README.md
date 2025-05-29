<div align=center>

|    NRP     |             Name             |
| :--------: | :--------------------------: |
| 5025221101 | Lalu Aldo Wadagraprana       |
| 5025221052 | Muhammad Syarif Hidayatullah |
| 5025221038 | Rafli Syahputra Pane         |

# Quiz 2

</div>

## Instructions

1. Form a group of up to 3 students.
2. Develop a computer program for your group project (e.g., a game, start-up idea, etc.). The program must implement at least one algorithm discussed in the course (e.g., DFS, BFS, DAG, Prim-Jarnik, Kruskal, etc.). Examples: a game that finds the shortest path, a minesweeper game, or a web application that calculates the minimum delivery route between two locations.
3. You may use any programming language (e.g., C/C++, C#, Java, Python, etc.).
4. Upload your project to GitHub. Your contribution to the GitHub repository will be used to assess individual participation.
5. Grading Criteria
    - Design [ 20 points]
    - Implementation [ 50 points]
    - Analysis/Evaluation [ 25 points]
    - Conclusion [ 5 points]
    - Total: [100 points]


### Member's percentage of contribution and specific roles:
  - Aldo     — 33.33%: Implemented DFS, BFS, time, ranking section, and Button Function (non modular version).
  - Syarif   — 33.33%: handled Design user interface and developed the modularity structure.
  - Pane     — 33.33%: Implemented Djikstra Algorithm to get the shortes path and perform analysis, testing, also wrote the final report.

---

# Ghost-Cherry Race Simulation

A visual simulation of different pathfinding algorithms racing to catch a cherry. This educational game demonstrates how different pathfinding algorithms behave in a maze environment.

![image](https://github.com/user-attachments/assets/5ea769c0-e040-4a85-970a-92e459ec3cb8)

## Overview

Ghost-Cherry Race is a Pygame-based simulation that visualizes how different pathfinding algorithms navigate through a maze. Three ghosts, each powered by a different algorithm, race to reach a cherry on the map. This project serves as both an entertaining game and an educational tool to understand the behavior and efficiency of various pathfinding algorithms.

## Features

- **Algorithm Visualization**: Watch BFS, DFS, and randomized approach compete in real-time
- **Dynamic Map Generation**: Create new maps to test algorithms in different environments
- **Race Results**: Compare algorithm performance with time results
- **Responsive Design**: UI adapts to different window sizes
- **Interactive Controls**: Start races, generate new maps, or place new targets

## Game Components

### Ghosts

The game features three ghosts, each using a different pathfinding algorithm:

- **Cyan Ghost**: Uses Breadth-First Search (BFS) - methodically explores all possible paths level by level
- **Pink Ghost**: Uses Depth-First Search (DFS) - pursues a single path as far as possible before backtracking
- **Orange Ghost**: Uses Dijkstra ("Dijkstra") - a cost-based priority queue, in a uniform-cost environment

### Map

The game map consists of walls (obstacles) and open paths. The ghosts must navigate through the open paths to reach the cherry. You can generate new random maps to test the algorithms in different scenarios.

### Cherry

The cherry is the target that all ghosts are trying to reach. It pulsates with a glowing effect to make it easier to spot. You can generate a new cherry position without changing the map.

## How to Play

1. Launch the game
2. Click "Start Game" to begin the race
3. Watch as the ghosts race to reach the cherry
4. When all ghosts reach the cherry (or fail to), results will be displayed
5. Click "Restart Game" to reset positions
6. Click "Generate New Map" to create a different maze
7. Click "Generate New Cherry" to move just the target

## Code Structure

The codebase is organized into several modules:

```
├── main.py              # Entry point
├── config.py            # Game configuration and constants
├── game/
│   ├── entities.py      # Ghost and Cherry classes
│   ├── game.py          # Main game class
│   ├── map.py           # Map management
│   ├── pathfinding.py   # Pathfinding algorithms
│   └── state.py         # Game state management
├── ui/
│   └── components.py    # UI components (buttons, panels, etc.)
├── utils/
│   └── helpers.py       # Utility functions for drawing, scaling, etc.
└── assets/              # Game images
```

## Implementation Details

### Pathfinding Algorithms

The game implements several pathfinding algorithms:

1. **Breadth-First Search (BFS)**: 
   - Used by the Cyan ghost
   - Guarantees the shortest path in terms of steps
   - Works by exploring all neighbor nodes at the current depth before moving deeper

2. **Depth-First Search (DFS)**: 
   - Used by the Pink ghost
   - Explores as far as possible along a branch before backtracking
   - Not guaranteed to find the shortest path

3. **Dijkstra**: 
   - Used by the Orange ghost
   - Explore nodes in the order of increasing distance
   - A cost-based priority queue

4. **A*** and **Kruskal**: 
   - Implemented in the code but not used by default
   - Can be assigned to ghosts for additional comparison

### UI Components

- **Responsive Design**: All UI components scale based on window size
- **Scrollable Areas**: Content that doesn't fit is scrollable
- **Rounded Panels**: Clean, modern UI design with rounded corners
- **Results Popup**: Displays race results with rankings

### Map Generation

The map system can:
- Load predefined maps from files
- Generate random maps with a customizable density of walls
- Ensure all positions are reachable by all ghosts

## Dependencies

- Python 3.6+
- Pygame 2.0+

## Installation

1. Clone the repository
2. Install dependencies: `pip install pygame`
3. Run the game: `python main.py`

## Controls

- **Mouse**: Click buttons to interact with the game
- **Mouse Wheel**: Scroll vertically in scrollable areas
- **Shift + Mouse Wheel**: Scroll horizontally in the ranking panel
- **Arrow Keys**: Navigate scrollable areas

## Educational Value

This simulation helps visualize the differences between pathfinding algorithms:
- BFS always finds the shortest path but explores more nodes
- DFS might find longer paths but can be more direct in certain scenarios
- Random approaches show how unpredictability can sometimes be advantageous

The visual nature of the races makes it easy to understand these algorithm characteristics without diving into the mathematical details.

## Future Enhancements

- Add more pathfinding algorithms (A*, Kruskal)
- Visualize the explored paths for each algorithm
- Add obstacles that can be placed during the race
- Implement a map editor for custom maps
- Support for user-created algorithms


## Pledge
![image](https://github.com/user-attachments/assets/7e4bd91b-c512-4670-b8b8-15a19d2e296e)


<div align=center>

# Thank You

</div>
