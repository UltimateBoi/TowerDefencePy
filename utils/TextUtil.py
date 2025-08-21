"""
Legacy Text Utilities - Backward Compatibility Layer
This module maintains the original TextUtil API for existing code
while delegating to the new enhanced text rendering system.
"""
import pygame
import sys
import os
from typing import Tuple

# Add the game directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'game'))

try:
    from ui.text_renderer import TextRenderer, TextAlignment, VerticalAlignment
except ImportError:
    # Fallback if new system is not available
    TextRenderer = None


class TextUtil:
    """
    Legacy text utility class for backward compatibility
    Maintains original API while using enhanced text rendering when available
    """
    
    def __init__(self):
        pass # Constructor empty, no initialization needed only static methods

    @staticmethod
    def draw_string(screen: pygame.Surface, font: pygame.font.Font, text: str, color: Tuple[int, int, int], x: int, y: int):
        """
        Draws a string on the screen centered at the specified position.
        """
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y)) # Center the text
        screen.blit(text_surface, text_rect)

    @staticmethod
    def draw_text_with_rounded_rect(
        screen: pygame.Surface, 
        text: str, 
        font: pygame.font.Font, 
        rect_color: Tuple[int, int, int], 
        text_color: Tuple[int, int, int], 
        x: int, 
        y: int, 
        padding: int = 12, 
        border_radius: int = 16
    ):
        """
        Draws text centered inside a rounded rectangle background at (x, y) (top-left of rect).
        """
        if TextRenderer:
            # Use new system if available
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect()
            rect = pygame.Rect(x, y, text_rect.width + 2*padding, text_rect.height + 2*padding)
            
            TextRenderer.render_text_with_background(
                screen, text, font, text_color, rect_color, rect,
                padding, border_radius, TextAlignment.CENTER, VerticalAlignment.MIDDLE
            )
        else:
            # Fallback to original implementation
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect()
            rect = pygame.Rect(x, y, text_rect.width + 2*padding, text_rect.height + 2*padding)
            pygame.draw.rect(screen, rect_color, rect, border_radius=border_radius)
            screen.blit(text_surface, (x + padding, y + padding))

    @staticmethod
    def draw_text_with_blur_rect(
        screen: pygame.Surface, 
        text: str, 
        font: pygame.font.Font, 
        x: int, 
        y: int, 
        padding: int = 12, 
        border_radius: int = 16, 
        blur_radius: int = 3
    ):
        """
        Draws text centered inside a blurred rounded rectangle background at (x, y) (top-left of rect).
        The blur is only behind the text, with proper rounded corners and tight sizing.
        
        Note: This feature requires PIL/Pillow and may not work in all environments.
        Falls back to simple rounded rectangle if PIL is not available.
        """
        try:
            from PIL import Image, ImageFilter, ImageDraw
            import numpy as np
            
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
            
        except (ImportError, Exception):
            # Fallback to simple rounded rectangle if PIL is not available or fails
            TextUtil.draw_text_with_rounded_rect(
                screen, text, font, (50, 50, 50, 128), (255, 255, 255), 
                x, y, padding, border_radius
            )

    @staticmethod
    def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list:
        """
        Wrap text to fit within a specified width
        New utility method that delegates to the enhanced text renderer
        """
        if TextRenderer:
            return TextRenderer.wrap_text(text, font, max_width)
        else:
            # Simple fallback implementation
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surface = font.render(test_line, True, (255, 255, 255))
                
                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
                
            return lines

    @staticmethod
    def render_wrapped_text(
        surface: pygame.Surface, 
        text: str, 
        font: pygame.font.Font, 
        color: Tuple[int, int, int], 
        rect: pygame.Rect, 
        center: bool = False
    ) -> int:
        """
        Render wrapped text within a rectangle
        New utility method for enhanced text rendering
        """
        if TextRenderer:
            alignment = TextAlignment.CENTER if center else TextAlignment.LEFT
            return TextRenderer.render_wrapped_text(
                surface, text, font, color, rect, alignment
            )
        else:
            # Simple fallback implementation
            lines = TextUtil.wrap_text(text, font, rect.width)
            line_height = font.get_height()
            
            for i, line in enumerate(lines):
                line_surface = font.render(line, True, color)
                y = rect.y + i * line_height
                
                if center:
                    x = rect.x + (rect.width - line_surface.get_width()) // 2
                else:
                    x = rect.x
                    
                surface.blit(line_surface, (x, y))
                
            return len(lines) * line_height
