import pygame

class Button:
    def __init__(self, name, x, y, width, height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def is_clicked(self, mouse_x, mouse_y):
        return (self.x <= mouse_x <= self.x + self.width) and (self.y <= mouse_y <= self.y + self.height)

class RoundedButton(Button):
    def __init__(self, name, x, y, width, height, radius):
        super().__init__(name, x, y, width, height) # Initialize as a subclass inheriting methods
        self.radius = radius

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height), border_radius=self.radius) 

class TextButton(Button):
    def __init__(self, name, x, y, width, height, text):
        super().__init__(name, x, y, width, height) # Initialize as a subclass inheriting methods
        self.text = text
        self.font = pygame.font.SysFont(None, 36) # Default font and size

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height)) # Draw the button
        text_surface = self.font.render(self.text, True, (0, 0, 0)) # Render the text
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2)) # Center the text
        screen.blit(text_surface, text_rect) # Draw the text on the button