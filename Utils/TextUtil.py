class TextUtil:
    def __init__(self):
        pass # Constructor empty, no initialization needed only static methods

    @staticmethod
    def draw_string(screen, font, text: str, color: tuple, x: int, y: int):
        """
        Draws a string on the screen centered at the specified position.
        """
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y)) # Center the text
        screen.blit(text_surface, text_rect)