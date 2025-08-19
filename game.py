"""
Tower Defense Game - Refactored Entry Point
This file now imports from the modular game package structure.
"""
from game import TowerDefenseGame

def main():
    game = TowerDefenseGame()
    game.run()

if __name__ == "__main__":
    main()
