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

class TextButton(Button):
    def __init__(self, name, x, y, width, height, text, radius=0, color=(0, 177, 47)):
        super().__init__(name, x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, 36)
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=self.radius)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)
