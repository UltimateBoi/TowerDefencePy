import pygame
from Utils.TextUtil import *

pygame.init()

screen = pygame.display.set_mode((1280, 720)) # Fixed resolution of 1280x720
pygame.display.set_caption("Hello World!")
screen.fill((0, 0, 0)) # Fill black background

def main():
    running = True
    while running:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0)) # Fill the screen with black
        TextUtil.draw_string(screen, pygame.font.SysFont(None, 72), "Hello World!", (255, 255, 255), 640, 360) # Draw text at centre of the screen
        pygame.display.flip() # Update the display

    pygame.quit()

if __name__ == "__main__":
    main()