from typing import Dict, List, Tuple
import pygame

from config import Config
from utils.helpers import DrawingUtil, ScalingUtil


class Button:
    """A clickable button component"""
    def __init__(self, rect: pygame.Rect, text: str):
        self.rect = rect
        self.text = text
        self.hovered = False
        self.adjusted_rect = rect.copy()
    
    def draw(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]) -> None:
        """Draw the button"""
        color = Config.BUTTON_HOVER if self.hovered else Config.BUTTON_IDLE
        DrawingUtil.draw_rounded_rect(surface, color, self.adjusted_rect, radius=8, border=2, border_color=Config.PANEL_BORDER)
        DrawingUtil.render_text_fit(surface, self.text, self.adjusted_rect, fonts, Config.BUTTON_TEXT, font_key='button')
    
    def update_position(self, offset_y: int, base_y: int) -> None:
        """Update the button's position based on scrolling offset"""
        self.adjusted_rect.y = self.rect.y - offset_y + base_y
    
    def is_hovered(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the button is being hovered"""
        return self.adjusted_rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if the button is clicked"""
        return self.adjusted_rect.collidepoint(mouse_pos)

class Panel:
    """A UI panel with optional header"""
    def __init__(self, rect: pygame.Rect, title: str = "", header_height_ratio: float = 0.3):
        self.rect = rect
        self.title = title
        self.header_height_ratio = header_height_ratio
        self.adjusted_rect = rect.copy()
        self.content_rect = None
        self.header_rect = None
        self._update_rects()
    
    def _update_rects(self) -> None:
        """Update the panel's rectangles"""
        self.content_rect = self.adjusted_rect.copy()
        if self.title:
            header_height = min(36, int(self.adjusted_rect.height * self.header_height_ratio))
            self.header_rect = pygame.Rect(
                self.adjusted_rect.x + 2, 
                self.adjusted_rect.y + 2, 
                self.adjusted_rect.width - 4, 
                header_height
            )
            self.content_rect.y += header_height + 5
            self.content_rect.height -= header_height + 5
    
    def update_position(self, offset_y: int, base_y: int) -> None:
        """Update panel position based on scrolling offset"""
        self.adjusted_rect = pygame.Rect(
            self.rect.x, 
            self.rect.y - offset_y + base_y, 
            self.rect.width, 
            self.rect.height
        )
        self._update_rects()
    
    def draw(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font]) -> None:
        """Draw the panel and its header if present"""
        # Only draw if at least partially visible
        if self.adjusted_rect.bottom < 0 or self.adjusted_rect.top > surface.get_height():
            return
            
        DrawingUtil.draw_rounded_rect(surface, Config.PANEL_BG, self.adjusted_rect, 
                                    radius=10, border=2, border_color=Config.PANEL_BORDER)
        
        if self.title and self.header_rect:
            DrawingUtil.draw_rounded_rect(surface, Config.HEADER_BG, self.header_rect, radius=8)
            
            header_text_rect = pygame.Rect(
                self.header_rect.x + 10,
                self.header_rect.y,
                self.header_rect.width - 20,
                self.header_rect.height
            )
            
            DrawingUtil.render_text_fit(surface, self.title, header_text_rect, 
                                      fonts, Config.HEADER_TEXT, 
                                      font_key='smaller_title', align="left")

class ScrollableArea:
    """A scrollable container for UI elements"""
    def __init__(self, rect: pygame.Rect, content_height: int):
        self.rect = rect
        self.content_height = content_height
        self.scroll_y = 0
        self.max_scroll = max(0, content_height - rect.height)
    
    def scroll(self, amount: int) -> None:
        """Scroll the area by the given amount"""
        self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + amount))
    
    def update_content_height(self, height: int) -> None:
        """Update the content height"""
        self.content_height = height
        self.max_scroll = max(0, self.content_height - self.rect.height)
        self.scroll_y = min(self.scroll_y, self.max_scroll)
    
    def draw_scroll_indicators(self, surface: pygame.Surface) -> None:
        """Draw scroll indicators if scrolling is available"""
        if self.max_scroll <= 0:
            return
            
        indicator_size = int(self.rect.width * 0.07)
        
        if self.scroll_y > 0:
            # Up arrow
            up_arrow = pygame.Rect(
                self.rect.right - indicator_size - 5, 
                self.rect.top + 5, 
                indicator_size, 
                indicator_size
            )
            DrawingUtil.draw_rounded_rect(surface, (200, 200, 220), up_arrow, radius=5)
            pygame.draw.polygon(surface, Config.BLACK, [
                (up_arrow.centerx, up_arrow.top + 5),
                (up_arrow.left + 5, up_arrow.bottom - 5),
                (up_arrow.right - 5, up_arrow.bottom - 5)
            ])
        
        if self.scroll_y < self.max_scroll:
            # Down arrow
            down_arrow = pygame.Rect(
                self.rect.right - indicator_size - 5, 
                self.rect.bottom - indicator_size - 5, 
                indicator_size, 
                indicator_size
            )
            DrawingUtil.draw_rounded_rect(surface, (200, 200, 220), down_arrow, radius=5)
            pygame.draw.polygon(surface, Config.BLACK, [
                (down_arrow.centerx, down_arrow.bottom - 5),
                (down_arrow.left + 5, down_arrow.top + 5),
                (down_arrow.right - 5, down_arrow.top + 5)
            ])

class ResultsPopup:
    """Popup window for displaying race results"""
    def __init__(self, width: int, height: int):
        self.visible = False
        self.width = width
        self.height = height
        self.results = []
        self.update_size(width, height)
    
    def update_size(self, width: int, height: int) -> None:
        """Update popup size based on screen dimensions"""
        self.width = width
        self.height = height
        
        # Scale popup based on screen size
        popup_width = min(width * 0.8, 600)
        popup_height = min(height * 0.8, 400)
        
        self.rect = pygame.Rect(
            (width - popup_width) // 2,
            (height - popup_height) // 2,
            popup_width,
            popup_height
        )
        
        # Scale header based on popup size
        header_height = min(54, int(popup_height * 0.15))
        self.header_rect = pygame.Rect(
            self.rect.x + 3, 
            self.rect.y + 3, 
            self.rect.width - 6, 
            header_height
        )
        
        # Close button - scaled to popup size
        close_btn_size = min(30, int(popup_width * 0.05))
        self.close_rect = pygame.Rect(
            self.rect.right - close_btn_size - 15, 
            self.rect.y + 15, 
            close_btn_size, 
            close_btn_size
        )
    
    def show(self, results: List[Dict]) -> None:
        """Show the popup with the given results"""
        self.visible = True
        self.results = sorted(results, key=lambda x: x.finish_time if x.finish_time else float('inf'))
    
    def hide(self) -> None:
        """Hide the popup"""
        self.visible = False
    
    def is_close_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the close button is clicked"""
        return self.visible and self.close_rect.collidepoint(pos)
    
    def draw(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font], ghost_images: Dict[str, pygame.Surface]) -> None:
        """Draw the results popup"""
        if not self.visible:
            return
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        # Main popup
        DrawingUtil.draw_rounded_rect(surface, Config.WHITE, self.rect, 15, 3, Config.PANEL_BORDER)
        
        # Header
        DrawingUtil.draw_rounded_rect(surface, Config.HEADER_BG, self.header_rect, 12)
        
        header_text_rect = pygame.Rect(
            self.header_rect.x + int(self.rect.width * 0.05), 
            self.header_rect.y, 
            self.header_rect.width - int(self.rect.width * 0.1), 
            self.header_rect.height
        )
        DrawingUtil.render_text_fit(surface, "RACE RESULTS", header_text_rect, 
                                   fonts, Config.HEADER_TEXT, 'title', align="left")
        
        # Close button
        DrawingUtil.draw_rounded_rect(surface, (220, 100, 100), self.close_rect, 
                                     self.close_rect.width//2, 2, (180, 80, 80))
        DrawingUtil.render_text_fit(surface, "X", self.close_rect, fonts, Config.WHITE, 'button')
        
        # Display ranking results with colorful medals
        available_height = self.rect.height - self.header_rect.height - 30
        row_height = min(60, available_height / len(self.results)) if self.results else 60
        
        for idx, ghost in enumerate(self.results):
            r = pygame.Rect(
                self.rect.x + int(self.rect.width * 0.05), 
                self.rect.y + self.header_rect.height + 15 + idx*row_height, 
                self.rect.width - int(self.rect.width * 0.1), 
                row_height
            )
            
            # Different colors for different ranks
            if idx == 0:
                medal_color = (255, 215, 0)  # Gold
                txt_color = (150, 100, 0)
            elif idx == 1:
                medal_color = (192, 192, 192)  # Silver
                txt_color = (100, 100, 100)
            else:
                medal_color = (205, 127, 50)  # Bronze
                txt_color = (120, 80, 40)
            
            # Medal size based on row height
            medal_size = min(50, int(row_height * 0.8))
            
            # Draw medal
            medal_rect = pygame.Rect(
                r.x, 
                r.y + (row_height - medal_size) // 2, 
                medal_size, 
                medal_size
            )
            DrawingUtil.draw_rounded_rect(surface, medal_color, medal_rect, radius=medal_size//2)
            DrawingUtil.render_text_fit(surface, f"{idx+1}", medal_rect, fonts, txt_color, 'title')
            
            # Draw ghost image
            img = ghost_images.get(ghost.name.lower(), None)
            if img:
                ghost_rect = pygame.Rect(
                    r.x + medal_size + 20, 
                    r.y + (row_height - img.get_height()) // 2, 
                    img.get_width(), 
                    img.get_height()
                )
                surface.blit(img, ghost_rect)
            
            # Draw name and algorithm
            info_width = min(200, int(self.rect.width * 0.4))
            info_rect = pygame.Rect(
                r.x + medal_size + 20 + img.get_width() + 20 if img else r.x + medal_size + 20, 
                r.y + (row_height - 50) // 2, 
                info_width, 
                50
            )
            DrawingUtil.render_text_fit(surface, f"{ghost.name} ({ghost.algorithm_name})", 
                                       info_rect, fonts, Config.BLACK, 'text')
            
            # Draw time
            time_str = f"{ghost.finish_time:.2f}s" if ghost.finish_time else "DNF"
            time_width = min(90, int(self.rect.width * 0.15))
            time_rect = pygame.Rect(
                r.right - time_width, 
                r.y + (row_height - 50) // 2, 
                time_width, 
                50
            )
            DrawingUtil.render_text_fit(surface, time_str, time_rect, fonts, txt_color, 'title')

class RankingPanel(Panel):
    """Panel showing race rankings"""
    def __init__(self, rect: pygame.Rect):
        super().__init__(rect, "PREVIOUS RANKING", 0.12)
        self.h_scroll_x = 0
        self.max_h_scroll = 0
        self.ranking_data = []
    
    def update_data(self, ranking_data: List[Dict]) -> None:
        """Update the ranking data to display"""
        self.ranking_data = ranking_data
    
    def scroll_horizontally(self, amount: int) -> None:
        """Scroll the panel horizontally"""
        self.h_scroll_x = max(0, min(self.max_h_scroll, self.h_scroll_x + amount))
    
    def draw_content(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font], 
                    ghost_images: Dict[str, pygame.Surface]) -> None:
        """Draw the ranking table with horizontal scrolling"""
        if not self.header_rect:
            return
            
        # Create a content area for ranking that can scroll horizontally
        content_margin = int(self.adjusted_rect.width * 0.04)  # 4% margin
        
        # Calculate real widths based on text lengths for columns
        col_base_widths = [50, 60]  # First two columns have fixed widths
        algorithm_width = max([fonts['text'].size(g['algorithm'])[0] + 20 for g in self.ranking_data] + [100]) if self.ranking_data else 100
        time_width = max([fonts['text'].size(f"{g['time']}s")[0] + 20 for g in self.ranking_data] + [70]) if self.ranking_data else 70
        
        # Scale column widths based on screen size
        scale_factor = min(ScalingUtil.get_scale_factor(surface.get_width(), surface.get_height()))
        col_widths = [
            max(30, int(50 * scale_factor)),
            max(40, int(60 * scale_factor)),
            max(80, int(algorithm_width * scale_factor)),
            max(50, int(time_width * scale_factor))
        ]
        
        total_cols_width = sum(col_widths) + 30  # Add spacing between columns
        
        # Calculate max horizontal scroll
        self.max_h_scroll = max(0, total_cols_width - (self.adjusted_rect.width - 2*content_margin))
        self.h_scroll_x = min(self.max_h_scroll, max(0, self.h_scroll_x))
        
        # Content area with scrolling
        ranking_content_area = pygame.Rect(
            self.adjusted_rect.x + content_margin - self.h_scroll_x, 
            self.header_rect.bottom + 10,
            total_cols_width,  # Make this wider than visible area to accommodate content
            self.adjusted_rect.height - self.header_rect.height - 20
        )
        
        # Draw table headers with horizontal scrolling
        header_y = ranking_content_area.y
        header_height = int(ranking_content_area.height * 0.1)  # 10% of content area height
        headers = ["Rank", "Ghost", "Algorithm", "Time"]
        
        header_x = ranking_content_area.x  # Start position considering scroll
        
        for i, header in enumerate(headers):
            rect = pygame.Rect(header_x, header_y, col_widths[i], header_height)
            DrawingUtil.draw_rounded_rect(surface, (180, 180, 220), rect, radius=5)
            DrawingUtil.render_text_fit(surface, header, rect, fonts, Config.BLACK, 'small', align="center")
            header_x += col_widths[i] + 10  # Add spacing between columns
        
        # Draw ranking data with proper spacing and horizontal scrolling
        row_height = max(30 + 5, int(ranking_content_area.height * 0.25))  # assuming 30 is the ranking_tile_size
        for i in range(min(3, len(self.ranking_data))):
            row_y = header_y + header_height + 10 + i*row_height
            g = self.ranking_data[i]
            
            # Draw a row background that spans the full content width
            row_rect = pygame.Rect(
                ranking_content_area.x, 
                row_y, 
                total_cols_width,  # Use the full content width
                row_height - 5
            )
            DrawingUtil.draw_rounded_rect(surface, (245, 245, 255), row_rect, radius=5)
            
            # Place items with proper spacing, accounting for horizontal scroll
            col_x = ranking_content_area.x  # Start at left edge of content area
            
            # Calculate vertical center of the row
            row_center_y = row_y + (row_height - 5) // 2
            
            # Draw rank (always visible) - CENTER ALIGNED BOTH HORIZONTALLY AND VERTICALLY
            rank_rect = pygame.Rect(col_x, row_y, col_widths[0], row_height - 5)  # Full height of row
            DrawingUtil.render_text_fit(surface, f"{i+1}", rank_rect, fonts, Config.BLACK, 'text', align="center")
            col_x += col_widths[0] + 10
            
            # Draw ghost icon - CENTER IN COLUMN
            ghost_x = col_x + (col_widths[1] - 30) // 2  # Center the 30px ghost in the column
            img = ghost_images.get(g['name'].lower(), None)
            if img:
                ghost_y = row_y + (row_height - 5 - img.get_height()) // 2  # Center vertically
                surface.blit(img, (ghost_x, ghost_y))
            col_x += col_widths[1] + 10
            
            # Draw algorithm - CENTER ALIGNED BOTH HORIZONTALLY AND VERTICALLY
            algo_rect = pygame.Rect(col_x, row_y, col_widths[2], row_height - 5)  # Full height of row
            DrawingUtil.render_text_fit(surface, g['algorithm'], algo_rect, fonts, Config.BLACK, 'text', align="center")
            col_x += col_widths[2] + 10
            
            # Draw time - CENTER ALIGNED BOTH HORIZONTALLY AND VERTICALLY
            time_rect_row = pygame.Rect(col_x, row_y, col_widths[3], row_height - 5)  # Full height of row
            DrawingUtil.render_text_fit(surface, f"{g['time']}s", time_rect_row, fonts, Config.BLACK, 'text', align="center")
        
        # Draw horizontal scroll indicators if needed
        scroll_indicator_size = int(self.adjusted_rect.width * 0.07)
        if self.h_scroll_x > 0:
            # Left scroll indicator
            left_arrow = pygame.Rect(
                self.adjusted_rect.x + 5, 
                self.adjusted_rect.bottom - scroll_indicator_size - 5, 
                scroll_indicator_size, 
                scroll_indicator_size
            )
            DrawingUtil.draw_rounded_rect(surface, (200, 200, 220), left_arrow, radius=5)
            pygame.draw.polygon(surface, Config.BLACK, [
                (left_arrow.centerx - 5, left_arrow.centery),
                (left_arrow.centerx + 3, left_arrow.top + 5),
                (left_arrow.centerx + 3, left_arrow.bottom - 5)
            ])
        
        if self.h_scroll_x < self.max_h_scroll:
            # Right scroll indicator
            right_arrow = pygame.Rect(
                self.adjusted_rect.right - scroll_indicator_size - 5, 
                self.adjusted_rect.bottom - scroll_indicator_size - 5, 
                scroll_indicator_size, 
                scroll_indicator_size
            )
            DrawingUtil.draw_rounded_rect(surface, (200, 200, 220), right_arrow, radius=5)
            pygame.draw.polygon(surface, Config.BLACK, [
                (right_arrow.centerx + 5, right_arrow.centery),
                (right_arrow.centerx - 3, right_arrow.top + 5),
                (right_arrow.centerx - 3, right_arrow.bottom - 5)
            ])
    
    def draw(self, surface: pygame.Surface, fonts: Dict[str, pygame.font.Font], 
            ghost_images: Dict[str, pygame.Surface]) -> None:
        """Draw the ranking panel and its content"""
        super().draw(surface, fonts)
        # Draw the content if the panel is at least partially visible
        if (self.adjusted_rect.top < surface.get_height() and 
            self.adjusted_rect.top + 40 > 0):
            self.draw_content(surface, fonts, ghost_images)
    
    def is_scroll_left_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if left scroll button is clicked"""
        if not self.adjusted_rect.collidepoint(pos) or self.h_scroll_x <= 0:
            return False
            
        scroll_indicator_size = int(self.adjusted_rect.width * 0.07)
        left_arrow = pygame.Rect(
            self.adjusted_rect.x + 5, 
            self.adjusted_rect.bottom - scroll_indicator_size - 5,
            scroll_indicator_size, 
            scroll_indicator_size
        )
        return left_arrow.collidepoint(pos)
    
    def is_scroll_right_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if right scroll button is clicked"""
        if not self.adjusted_rect.collidepoint(pos) or self.h_scroll_x >= self.max_h_scroll:
            return False
            
        scroll_indicator_size = int(self.adjusted_rect.width * 0.07)
        right_arrow = pygame.Rect(
            self.adjusted_rect.right - scroll_indicator_size - 5, 
            self.adjusted_rect.bottom - scroll_indicator_size - 5,
            scroll_indicator_size, 
            scroll_indicator_size
        )
        return right_arrow.collidepoint(pos)

