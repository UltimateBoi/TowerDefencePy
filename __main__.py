import pygame
from utils.TextUtil import *
from MainMenu import main_menu

pygame.init()

screen = pygame.display.set_mode((1280, 720)) # Fixed resolution of 1280x720
pygame.display.set_caption("Hello World!")
screen.fill((0, 0, 0)) # Fill black background

if __name__ == "__main__":
    main_menu()