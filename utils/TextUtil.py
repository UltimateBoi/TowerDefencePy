import pygame
from PIL import Image, ImageFilter
import numpy as np

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

    @staticmethod
    def draw_text_with_rounded_rect(screen, text, font, rect_color, text_color, x, y, padding=12, border_radius=16):
        """
        Draws text centered inside a rounded rectangle background at (x, y) (top-left of rect).
        """
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        rect = pygame.Rect(x, y, text_rect.width + 2*padding, text_rect.height + 2*padding)
        pygame.draw.rect(screen, rect_color, rect, border_radius=border_radius)
       # Center text inside rect
        screen.blit(text_surface, (x + padding, y + padding))

    @staticmethod
    def draw_text_with_blur_rect(screen, text, font, x, y, padding=12, border_radius=16, blur_radius=3):
        """
        Draws text centered inside a blurred rounded rectangle background at (x, y) (top-left of rect).
        The blur is only behind the text, with proper rounded corners and tight sizing.
        """
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        width = text_rect.width + 2*padding
        height = text_rect.height + 2*padding
        rect = pygame.Rect(x, y, width, height)

       # Extract the background region
        sub_surface = screen.subsurface(rect).copy()
        arr = pygame.surfarray.array3d(sub_surface)
        arr = np.transpose(arr, (1, 0, 2)) # Pygame is (width, height), PIL is (height, width)
        pil_img = Image.fromarray(arr)
        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

       # Create a rounded rectangle mask
        mask = Image.new('L', (width, height), 0)
        mask_draw = Image.new('RGBA', (width, height))
        mask_draw.paste((255, 255, 255, 255), (0, 0, width, height))
       # Use PIL's rounded rectangle drawing
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, width, height], radius=border_radius, fill=255)

       # Apply mask to blurred image
        blurred = blurred.convert('RGBA')
        blurred.putalpha(mask)
        blurred_surface = pygame.image.frombuffer(blurred.tobytes(), (width, height), 'RGBA')

       # Blit blurred rounded rect
        screen.blit(blurred_surface, (x, y))
       # Draw text on top
        screen.blit(text_surface, (x + padding, y + padding))
