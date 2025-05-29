import pygame

pygame.init()
# Now import the game
from game.game import GhostCherryGame

def main():
    game = GhostCherryGame()
    game.run()

if __name__ == "__main__":
    main()