# ==========================================
# UTILITY CLASSES
# ==========================================
import random
from typing import Dict, Optional, Tuple

import pygame

from config import Config


class ScalingUtil:
    """Utility for scaling UI elements based on screen size"""
    @staticmethod
    def get_scale_factor(width: int, height: int) -> Tuple[float, float]:
        """Calculate horizontal and vertical scale factors"""
        scale_x = width / Config.BASE_WIDTH
        scale_y = height / Config.BASE_HEIGHT
        return scale_x, scale_y
    
    @staticmethod
    def scale_value(value: int, scale_factor: float) -> int:
        """Scale a single value by the given factor"""
        return int(value * scale_factor)
    
    @staticmethod
    def scale_rect(rect: pygame.Rect, scale_x: float, scale_y: float) -> pygame.Rect:
        """Scale a rectangle's position and size"""
        return pygame.Rect(
            int(rect.x * scale_x),
            int(rect.y * scale_y),
            int(rect.width * scale_x),
            int(rect.height * scale_y)
        )
    
    @staticmethod
    def scale_pos(pos: Tuple[int, int], scale_x: float, scale_y: float) -> Tuple[int, int]:
        """Scale a position tuple"""
        return (int(pos[0] * scale_x), int(pos[1] * scale_y))
    
    @staticmethod
    def create_fonts(scale_factor: Tuple[float, float]) -> Dict[str, pygame.font.Font]:
        """Create scaled fonts based on window size"""
        size_factor = min(scale_factor[0], scale_factor[1])
        size_factor = max(0.7, min(1.5, size_factor))
        
        return {
            'title': pygame.font.SysFont('Arial', int(32 * size_factor), bold=True),
            'button': pygame.font.SysFont('Arial', int(20 * size_factor), bold=True),
            'text': pygame.font.SysFont('Arial', int(20 * size_factor)),
            'small': pygame.font.SysFont('Arial', int(16 * size_factor)),
            'smaller_title': pygame.font.SysFont('Arial', int(24 * size_factor), bold=True)
        }

class ImageLoader:
    """Handles loading and scaling images"""
    _image_cache: Dict[str, pygame.Surface] = {}
    
    @classmethod
    def load_scaled_image(cls, path: str, size: Tuple[int, int]) -> pygame.Surface:
        """Load an image and scale it to the specified size"""
        cache_key = f"{path}_{size[0]}x{size[1]}"
        if cache_key not in cls._image_cache:
            img = pygame.image.load(path)
            cls._image_cache[cache_key] = pygame.transform.scale(img, size)
        return cls._image_cache[cache_key]
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the image cache"""
        cls._image_cache = {}

class DrawingUtil:
    """Utility for drawing UI elements"""
    @staticmethod
    def draw_rounded_rect(surface: pygame.Surface, color: Tuple[int, int, int], 
                         rect: pygame.Rect, radius: int = 10, 
                         border: int = 0, border_color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a rectangle with rounded corners"""
        rect = pygame.Rect(rect)
        
        # Limiting the radius
        radius = min(radius, rect.width // 2, rect.height // 2)
        
        if border > 0 and border_color:
            # First draw the border rectangle that's larger
            border_rect = pygame.Rect(rect)
            pygame.draw.rect(surface, border_color, 
                          (border_rect.x, border_rect.y + radius, border_rect.width, border_rect.height - 2*radius), 0)
            pygame.draw.rect(surface, border_color, 
                          (border_rect.x + radius, border_rect.y, border_rect.width - 2*radius, border_rect.height), 0)
            pygame.draw.circle(surface, border_color, (border_rect.left + radius, border_rect.top + radius), radius)
            pygame.draw.circle(surface, border_color, (border_rect.right - radius, border_rect.top + radius), radius)
            pygame.draw.circle(surface, border_color, (border_rect.left + radius, border_rect.bottom - radius), radius)
            pygame.draw.circle(surface, border_color, (border_rect.right - radius, border_rect.bottom - radius), radius)
            
            # Then draw the inner fill rectangle that's smaller
            inner_rect = pygame.Rect(rect.x + border, rect.y + border, rect.width - 2*border, rect.height - 2*border)
            inner_radius = max(0, radius - border)
            pygame.draw.rect(surface, color, 
                         (inner_rect.x, inner_rect.y + inner_radius, inner_rect.width, inner_rect.height - 2*inner_radius), 0)
            pygame.draw.rect(surface, color, 
                         (inner_rect.x + inner_radius, inner_rect.y, inner_rect.width - 2*inner_radius, inner_rect.height), 0)
            pygame.draw.circle(surface, color, (inner_rect.left + inner_radius, inner_rect.top + inner_radius), inner_radius)
            pygame.draw.circle(surface, color, (inner_rect.right - inner_radius, inner_rect.top + inner_radius), inner_radius)
            pygame.draw.circle(surface, color, (inner_rect.left + inner_radius, inner_rect.bottom - inner_radius), inner_radius)
            pygame.draw.circle(surface, color, (inner_rect.right - inner_radius, inner_rect.bottom - inner_radius), inner_radius)
        else:
            # Just draw a filled rectangle with no border
            pygame.draw.rect(surface, color, 
                          (rect.x, rect.y + radius, rect.width, rect.height - 2*radius), 0)
            pygame.draw.rect(surface, color, 
                          (rect.x + radius, rect.y, rect.width - 2*radius, rect.height), 0)
            pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
            pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
            pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
            pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
    
    @staticmethod
    def render_text_fit(surface: pygame.Surface, text: str, rect: pygame.Rect, 
                      fonts: Dict[str, pygame.font.Font], color: Tuple[int, int, int] = Config.BLACK, 
                      font_key: str = 'text', align: str = "center") -> int:
        """Render text that fits within a rectangle"""
        font_obj = fonts[font_key]
        text_surf = font_obj.render(text, True, color)
        
        # Scale text if needed
        width_ratio = rect.width / max(1, text_surf.get_width())
        if width_ratio < 0.9:  # Only scale if text is really too wide
            new_size = int(font_obj.get_height() * width_ratio * 0.9)
            if new_size >= 10:  # Prevent too small text
                font_obj = pygame.font.SysFont(font_obj.get_name(), new_size, 
                                            font_obj.get_bold(), font_obj.get_italic())
                text_surf = font_obj.render(text, True, color)
        
        if align == "center":
            text_rect = text_surf.get_rect(center=rect.center)
        elif align == "left":
            text_rect = text_surf.get_rect(midleft=(rect.left + 10, rect.centery))
        elif align == "right":
            text_rect = text_surf.get_rect(midright=(rect.right - 10, rect.centery))
            
        surface.blit(text_surf, text_rect)
        
        # Return the width of the text for horizontal scaling
        return text_surf.get_width()

    @staticmethod
    def create_bg_texture(width: int, height: int) -> pygame.Surface:
        """Create a textured background surface"""
        texture = pygame.Surface((width, height))
        cell_size = max(10, int(width / 100))  # Scale the texture cells with screen size
        
        for y in range(0, height, cell_size * 2):
            for x in range(0, width, cell_size * 2):
                shade = random.randint(235, 245)
                pygame.draw.rect(texture, (shade, shade, shade+5), (x, y, cell_size, cell_size))
                shade = random.randint(235, 245)
                pygame.draw.rect(texture, (shade, shade, shade+5), (x+cell_size, y, cell_size, cell_size))
                shade = random.randint(235, 245)
                pygame.draw.rect(texture, (shade, shade, shade+5), (x, y+cell_size, cell_size, cell_size))
                shade = random.randint(235, 245)
                pygame.draw.rect(texture, (shade, shade, shade+5), (x+cell_size, y+cell_size, cell_size, cell_size))
        
        return texture

