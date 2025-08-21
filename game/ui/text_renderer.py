"""
Enhanced Text Rendering System for Tower Defense Game
Provides comprehensive text rendering capabilities with automatic wrapping,
alignment, and layout management.
"""
import pygame
from typing import List, Tuple, Optional, Union
from enum import Enum


class TextAlignment(Enum):
    """Text alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlignment(Enum):
    """Vertical alignment options"""
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class TextRenderer:
    """
    Advanced text rendering system with automatic wrapping and layout management
    """
    
    @staticmethod
    def wrap_text(text: str, font: pygame.font.Font, max_width: int, max_lines: Optional[int] = None) -> List[str]:
        """
        Wrap text to fit within a specified width
        
        Args:
            text: Text to wrap
            font: Pygame font object
            max_width: Maximum width in pixels
            max_lines: Maximum number of lines (None for unlimited)
            
        Returns:
            List of text lines that fit within the width
        """
        if not text:
            return []
            
        words = text.split()
        if not words:
            return []
            
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
                else:
                    # Single word too long, add it anyway
                    lines.append(word)
                    current_line = ""
                    
                # Check max_lines limit
                if max_lines and len(lines) >= max_lines:
                    break
        
        if current_line and (not max_lines or len(lines) < max_lines):
            lines.append(current_line)
            
        return lines
    
    @staticmethod
    def render_wrapped_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        rect: pygame.Rect,
        alignment: TextAlignment = TextAlignment.LEFT,
        vertical_alignment: VerticalAlignment = VerticalAlignment.TOP,
        line_spacing: int = 2,
        max_lines: Optional[int] = None
    ) -> int:
        """
        Render wrapped text within a rectangle
        
        Args:
            surface: Surface to render on
            text: Text to render
            font: Font to use
            color: Text color
            rect: Rectangle to render within
            alignment: Horizontal text alignment
            vertical_alignment: Vertical text alignment
            line_spacing: Additional spacing between lines
            max_lines: Maximum number of lines to render
            
        Returns:
            Total height of rendered text
        """
        if not text:
            return 0
            
        lines = TextRenderer.wrap_text(text, font, rect.width, max_lines)
        if not lines:
            return 0
            
        line_height = font.get_height() + line_spacing
        total_height = len(lines) * line_height - line_spacing
        
        # Calculate starting Y position based on vertical alignment
        if vertical_alignment == VerticalAlignment.TOP:
            start_y = rect.y
        elif vertical_alignment == VerticalAlignment.MIDDLE:
            start_y = rect.y + (rect.height - total_height) // 2
        else: # BOTTOM
            start_y = rect.y + rect.height - total_height
            
        # Render each line
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_y = start_y + i * line_height
            
            # Calculate X position based on alignment
            if alignment == TextAlignment.LEFT:
                line_x = rect.x
            elif alignment == TextAlignment.CENTER:
                line_x = rect.x + (rect.width - line_surface.get_width()) // 2
            else: # RIGHT
                line_x = rect.x + rect.width - line_surface.get_width()
                
            surface.blit(line_surface, (line_x, line_y))
            
        return total_height
    
    @staticmethod
    def render_text_with_background(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        text_color: Tuple[int, int, int],
        bg_color: Tuple[int, int, int],
        rect: pygame.Rect,
        padding: int = 8,
        border_radius: int = 5,
        alignment: TextAlignment = TextAlignment.CENTER,
        vertical_alignment: VerticalAlignment = VerticalAlignment.MIDDLE
    ) -> pygame.Rect:
        """
        Render text with a background rectangle
        
        Returns:
            The actual rectangle used for the background
        """
        # Draw background
        pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)
        
        # Render text within the padded area
        text_rect = pygame.Rect(
            rect.x + padding,
            rect.y + padding,
            rect.width - 2 * padding,
            rect.height - 2 * padding
        )
        
        TextRenderer.render_wrapped_text(
            surface, text, font, text_color, text_rect,
            alignment, vertical_alignment
        )
        
        return rect
    
    @staticmethod
    def measure_wrapped_text(text: str, font: pygame.font.Font, max_width: int) -> Tuple[int, int]:
        """
        Measure the dimensions of wrapped text
        
        Returns:
            (width, height) tuple
        """
        if not text:
            return (0, 0)
            
        lines = TextRenderer.wrap_text(text, font, max_width)
        if not lines:
            return (0, 0)
            
        max_line_width = 0
        for line in lines:
            line_surface = font.render(line, True, (255, 255, 255))
            max_line_width = max(max_line_width, line_surface.get_width())
            
        height = len(lines) * font.get_height() + (len(lines) - 1) * 2 # 2px line spacing
        return (max_line_width, height)
    
    @staticmethod
    def fit_text_to_rect(
        text: str,
        base_font_name: Optional[str],
        max_font_size: int,
        rect: pygame.Rect,
        padding: int = 4
    ) -> pygame.font.Font:
        """
        Find the largest font size that fits text within a rectangle
        
        Returns:
            Font object that fits the text
        """
        available_width = rect.width - 2 * padding
        available_height = rect.height - 2 * padding
        
        # Try font sizes from max down to minimum readable size
        for font_size in range(max_font_size, 8, -1):
            font = pygame.font.SysFont(base_font_name, font_size)
            width, height = TextRenderer.measure_wrapped_text(text, font, available_width)
            
            if height <= available_height:
                return font
                
        # Return minimum size if nothing fits
        return pygame.font.SysFont(base_font_name, 8)


class LegacyTextUtil:
    """
    Legacy text utilities for backward compatibility
    Maintains the original API while using the new TextRenderer internally
    """
    
    @staticmethod
    def draw_string(screen: pygame.Surface, font: pygame.font.Font, text: str, color: Tuple[int, int, int], x: int, y: int):
        """Draw centered text at position (legacy compatibility)"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
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
        """Draw text with rounded background (legacy compatibility)"""
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        rect = pygame.Rect(x, y, text_rect.width + 2*padding, text_rect.height + 2*padding)
        
        TextRenderer.render_text_with_background(
            screen, text, font, text_color, rect_color, rect,
            padding, border_radius
        )


# Maintain backward compatibility
TextUtil = LegacyTextUtil
