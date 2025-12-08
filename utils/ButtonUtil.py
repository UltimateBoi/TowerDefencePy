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
        self.hover_color = self._calculate_hover_color(color)
        self.is_hovered = False
        self._last_hover_state = False

    def _calculate_hover_color(self, color):
        """Calculate a lighter/brighter version of the color for hover effect."""
        r, g, b = color
        # Increase brightness by 20% but cap at 255
        factor = 1.2
        hover_r = min(int(r * factor), 255)
        hover_g = min(int(g * factor), 255)
        hover_b = min(int(b * factor), 255)
        return (hover_r, hover_g, hover_b)
    
    def update_hover(self, mouse_x, mouse_y):
        """Update hover state and return True if hovered."""
        self.is_hovered = self.is_clicked(mouse_x, mouse_y)
        
        # Only change cursor if hover state changed
        if self.is_hovered != self._last_hover_state:
            if self.is_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self._last_hover_state = self.is_hovered
        
        return self.is_hovered
    
    def reset_cursor_on_click(self):
        """Reset cursor to default when button is clicked."""
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.is_hovered = False
        self._last_hover_state = False

    def draw(self, screen, mouse_pos=None):
        """Draw the button with hover effect if mouse position provided."""
        if mouse_pos:
            self.update_hover(mouse_pos[0], mouse_pos[1])
        
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, (self.x, self.y, self.width, self.height), border_radius=self.radius)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)
