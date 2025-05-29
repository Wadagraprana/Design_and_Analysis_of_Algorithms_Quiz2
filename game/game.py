# ==========================================
# MAIN GAME CLASS
# ==========================================
import time
import sys
from typing import List
import pygame

from config import Config
from game.entities import Cherry, Ghost
from game.map import GameMap
from game.pathfinding import AStarAlgorithm, BFSAlgorithm, DFSAlgorithm, DijkstraAlgorithm, KruskalAlgorithm
from game.state import GameState
from ui.components import Button, Panel, RankingPanel, ResultsPopup, ScrollableArea
from utils.helpers import DrawingUtil, ImageLoader, ScalingUtil


class GhostCherryGame:
    """Main game class that coordinates all the components"""
    def __init__(self):
        # Initialize display
        self.width = Config.BASE_WIDTH
        self.height = Config.BASE_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Ghost-Cherry Game")
        
        # Initialize game objects and state
        self.map = GameMap(Config.ASSETS['map'])
        self.cherry = Cherry(self.map)
        self.game_state = GameState()
        self.tile_size = Config.BASE_TILE_SIZE
        
        # Initialize pathfinding algorithms
        self.algorithms = {
            'BFS': BFSAlgorithm(self.map),
            'DFS': DFSAlgorithm(self.map),
            'AStar': AStarAlgorithm(self.map),
            'Dijkstra': DijkstraAlgorithm(self.map),
            'Kruskal': KruskalAlgorithm(self.map),
        }
        
        # Initialize ghosts
        self.create_ghosts()
        
        # Initialize UI
        self.fonts = ScalingUtil.create_fonts(ScalingUtil.get_scale_factor(self.width, self.height))
        self.background_texture = DrawingUtil.create_bg_texture(self.width, self.height)
        self.load_images()
        
        # Initialize UI components
        self.sidebar_scroll = ScrollableArea(
            pygame.Rect(0, 0, 0, 0),  # Will be set in calculate_layout
            0  # Will be set in calculate_layout
        )
        
        self.results_popup = ResultsPopup(self.width, self.height)
        
        # Set up UI layout
        self.layout = {}
        self.ui_components = {}
        self.calculate_layout()
        
        # Initialize game clock
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Previous rankings for display
        self.previous_ranking = []
    
    def create_ghosts(self) -> None:
        """Create ghost entities with their algorithms"""
        self.ghosts = [
            Ghost("Cyan", "cyan", (15, 16), self.algorithms['BFS']),
            Ghost("Pink", "pink", (16, 17), self.algorithms['DFS']),
            Ghost("Orange", "orange", (17, 16), self.algorithms['Dijkstra']),
        ]
    
    def load_images(self) -> None:
        """Load and scale all game images"""
        self.ghost_images = {
            'cyan': ImageLoader.load_scaled_image(Config.ASSETS['ghost_cyan'], (self.tile_size, self.tile_size)),
            'pink': ImageLoader.load_scaled_image(Config.ASSETS['ghost_pink'], (self.tile_size, self.tile_size)),
            'orange': ImageLoader.load_scaled_image(Config.ASSETS['ghost_orange'], (self.tile_size, self.tile_size)),
        }
        
        self.cherry_img = ImageLoader.load_scaled_image(Config.ASSETS['cherry'], (self.tile_size, self.tile_size))
        
        # Scaled images for the ranking panel
        ranking_tile_size = ScalingUtil.scale_value(30, min(ScalingUtil.get_scale_factor(self.width, self.height)))
        self.ghost_scaled_images = {
            'cyan': ImageLoader.load_scaled_image(Config.ASSETS['ghost_cyan'], (ranking_tile_size, ranking_tile_size)),
            'pink': ImageLoader.load_scaled_image(Config.ASSETS['ghost_pink'], (ranking_tile_size, ranking_tile_size)),
            'orange': ImageLoader.load_scaled_image(Config.ASSETS['ghost_orange'], (ranking_tile_size, ranking_tile_size)),
        }
    
    def calculate_layout(self) -> None:
        """Calculate responsive layout based on window size"""
        scale_x, scale_y = ScalingUtil.get_scale_factor(self.width, self.height)
        
        # Calculate sidebar dimensions
        sidebar_width_ratio = 0.28
        sidebar_width_px = int(self.width * sidebar_width_ratio)
        sidebar_x = int(self.width * 0.02)  # 2% margin
        sidebar_top_y = int(self.height * 0.03)  # 3% margin from top
        
        # Calculate game area dimensions
        main_area_ratio = 1.0 - sidebar_width_ratio - 0.05  # 5% margin between sidebar and game
        main_x = sidebar_x + sidebar_width_px + int(self.width * 0.02)
        main_width = int(self.width * main_area_ratio)
        
        # Arena positioning
        arena_x = main_x
        arena_y = int(self.height * 0.1)  # 10% from top
        arena_w = self.map.cols * self.tile_size
        arena_h = self.map.rows * self.tile_size
        
        # Panel heights
        time_panel_height = int(self.height * 0.12)
        ranking_panel_height = int(self.height * 0.4)
        btn_h = int(self.height * 0.07)
        
        # Panel spacing
        panel_spacing = int(self.height * 0.02)
        
        # Create UI components
        time_rect = pygame.Rect(sidebar_x, sidebar_top_y, sidebar_width_px, time_panel_height)
        
        ranking_rect = pygame.Rect(
            sidebar_x, 
            time_rect.bottom + panel_spacing,
            sidebar_width_px, 
            ranking_panel_height
        )
        
        # Button dimensions and positions
        btn_w = sidebar_width_px
        btn_margin = int(self.height * 0.02)
        controls_y = ranking_rect.bottom + panel_spacing
        
        # Store layout information
        self.layout = {
            'sidebar_width': sidebar_width_px,
            'sidebar_x': sidebar_x,
            'sidebar_top_y': sidebar_top_y,
            'time_rect': time_rect,
            'ranking_rect': ranking_rect,
            'start_btn': pygame.Rect(sidebar_x, controls_y, btn_w, btn_h),
            'restart_btn': pygame.Rect(sidebar_x, controls_y + btn_h + btn_margin, btn_w, btn_h),
            'gen_map_btn': pygame.Rect(sidebar_x, controls_y + (btn_h + btn_margin) * 2, btn_w, btn_h),
            'gen_cherry_btn': pygame.Rect(sidebar_x, controls_y + (btn_h + btn_margin) * 3, btn_w, btn_h),
            'main_x': main_x, 
            'main_width': main_width,
            'arena_x': arena_x,
            'arena_y': arena_y,
            'arena_w': arena_w,
            'arena_h': arena_h,
            'game_title': pygame.Rect(arena_x, int(self.height * 0.03), arena_w, int(self.height * 0.06)),
            'algorithm_info': pygame.Rect(arena_x, arena_y + arena_h + int(self.height * 0.01), 
                                         arena_w, int(self.height * 0.06)),
            'btn_h': btn_h,
        }
        
        # Calculate total sidebar content height for scrolling
        sidebar_content_height = self.layout['gen_cherry_btn'].bottom - time_rect.top + int(self.height * 0.03)
        sidebar_visible_height = self.height - int(self.height * 0.03)
        
        # Update scrollable area
        self.sidebar_scroll = ScrollableArea(
            pygame.Rect(sidebar_x, sidebar_top_y, sidebar_width_px, sidebar_visible_height),
            sidebar_content_height
        )
        
        # Create or update UI components
        self.ui_components = {
            'time_panel': Panel(time_rect, "TIME", 0.4),
            'ranking_panel': RankingPanel(ranking_rect),
            'start_btn': Button(self.layout['start_btn'], "Start Game"),
            'restart_btn': Button(self.layout['restart_btn'], "Restart Game"),
            'gen_map_btn': Button(self.layout['gen_map_btn'], "Generate New Map"),
            'gen_cherry_btn': Button(self.layout['gen_cherry_btn'], "Generate New Cherry"),
        }
    
    def handle_resize(self, width: int, height: int) -> None:
        """Update all size-dependent variables when window is resized"""
        self.width = width
        self.height = height
        
        # Regenerate background texture
        self.background_texture = DrawingUtil.create_bg_texture(width, height)
        
        # Update fonts
        self.fonts = ScalingUtil.create_fonts(ScalingUtil.get_scale_factor(width, height))
        
        # Scale tile size based on available screen space and map dimensions
        scale_x, scale_y = ScalingUtil.get_scale_factor(width, height)
        arena_w_ratio = 0.7  # 70% of window width for game area
        arena_h_ratio = 0.8  # 80% of window height for game area
        
        # Calculate tile size to fit map in available space
        horizontal_tiles = self.map.cols
        vertical_tiles = self.map.rows
        
        # Use the smaller of horizontal and vertical constraints
        horizontal_tile_size = int((width * arena_w_ratio) / horizontal_tiles)
        vertical_tile_size = int((height * arena_h_ratio) / vertical_tiles)
        self.tile_size = max(8, min(horizontal_tile_size, vertical_tile_size))  # Minimum tile size of 8px
        
        # Update all images with new scales
        self.load_images()
        
        # Update UI layout
        self.calculate_layout()
        
        # Update popup dimensions
        self.results_popup.update_size(width, height)
    
    def reset_game(self, new_map: bool = False, new_cherry: bool = False, keep_game_state: bool = False) -> None:
        """Reset the game state and entities"""
        # Reset game state only if not keeping it
        if not keep_game_state:
            self.game_state.reset_game()
        
        # Generate new map if requested
        if new_map:
            self.map.generate_random_map()
        
        # Reset ghost positions
        for ghost in self.ghosts:
            if ghost.name == "Cyan":
                ghost.reset((15, 16))
            elif ghost.name == "Pink":
                ghost.reset((16, 17))
            elif ghost.name == "Orange":
                ghost.reset((17, 16))
        
        # Generate new cherry position if needed
        if new_cherry or new_map:
            ghost_positions = [tuple(ghost.position) for ghost in self.ghosts]
            self.cherry.generate_position(ghost_positions)
            
            # Verify cherry is reachable by all ghosts
            while not all(self.is_reachable(ghost.position, self.cherry.position) for ghost in self.ghosts):
                self.cherry.generate_position(ghost_positions)
        
        # Initialize paths for all ghosts - ADD THIS SECTION
        for ghost in self.ghosts:
            ghost.find_path_to(tuple(self.cherry.position))
        
        # Close any open popup
        self.results_popup.hide()
    
    def is_reachable(self, start: List[int], end: List[int]) -> bool:
        """Check if there's a path between two positions"""
        bfs = BFSAlgorithm(self.map)
        path = bfs.find_path(tuple(start), tuple(end))
        return len(path) > 0
    
    def update(self) -> None:
        """Update game state for the current frame"""
        if not self.game_state.started:
            return
        
        # Update ghost positions and check for winners
        all_finished = True
        for ghost in self.ghosts:
            if not ghost.finish_time:  # If ghost hasn't finished yet
                all_finished = False
                
                # Find path if needed
                if not ghost.path:
                    ghost.find_path_to(tuple(self.cherry.position))
                
                # Move ghost
                ghost.move()
                
                # Check if reached cherry
                if ghost.reached_position(self.cherry.position) and not ghost.finish_time:
                    ghost.finish_time = round(time.time() - self.game_state.start_time, 2)
        
        # Check if race is complete
        if all_finished and not self.results_popup.visible:
            self.game_state.end_game()
            self.results_popup.show(self.ghosts)
            self.previous_ranking = [
                {'name': g.name, 'algorithm': g.algorithm_name, 'time': g.finish_time} 
                for g in sorted(self.ghosts, key=lambda x: x.finish_time if x.finish_time else float('inf'))
            ]
            self.ui_components['ranking_panel'].update_data(self.previous_ranking)
    
    def handle_events(self) -> None:
        """Process user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if results popup is open and close button is clicked
                    if self.results_popup.is_close_clicked(mouse_pos):
                        self.results_popup.hide()
                        continue
                    
                    # Check for button clicks in sidebar
                    if not self.results_popup.visible:
                        # Start button
                        if (self.ui_components['start_btn'].is_clicked(mouse_pos) and 
                        not self.game_state.started and not self.game_state.finished):
                            # Reset positions without resetting game state
                            self.reset_game(keep_game_state=True)  
                            # Now start the game
                            self.game_state.start_game()
                            
                        # Restart button
                        elif self.ui_components['restart_btn'].is_clicked(mouse_pos) and not self.game_state.started:
                            self.reset_game()
                            
                        # Generate new map button
                        elif self.ui_components['gen_map_btn'].is_clicked(mouse_pos) and not self.game_state.started:
                            self.reset_game(True, True)
                            
                        # Generate new cherry button
                        elif self.ui_components['gen_cherry_btn'].is_clicked(mouse_pos) and not self.game_state.started:
                            self.reset_game(False, True)
                            
                        # Check for ranking panel scroll buttons
                        ranking_panel = self.ui_components['ranking_panel']
                        if ranking_panel.is_scroll_left_clicked(mouse_pos):
                            ranking_panel.scroll_horizontally(-30)
                        elif ranking_panel.is_scroll_right_clicked(mouse_pos):
                            ranking_panel.scroll_horizontally(30)
                
                # Mouse wheel scrolling
                elif event.button == 4:  # Scroll up
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Horizontal scroll with Shift held
                        if self.ui_components['ranking_panel'].adjusted_rect.collidepoint(pygame.mouse.get_pos()):
                            self.ui_components['ranking_panel'].scroll_horizontally(-Config.SCROLL_SPEED)
                    else:
                        # Vertical scrolling
                        self.sidebar_scroll.scroll(-Config.SCROLL_SPEED)
                        
                elif event.button == 5:  # Scroll down
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # Horizontal scroll with Shift held
                        if self.ui_components['ranking_panel'].adjusted_rect.collidepoint(pygame.mouse.get_pos()):
                            self.ui_components['ranking_panel'].scroll_horizontally(Config.SCROLL_SPEED)
                    else:
                        # Vertical scrolling
                        self.sidebar_scroll.scroll(Config.SCROLL_SPEED)
                        
            # Add keyboard support for scrolling
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.ui_components['ranking_panel'].scroll_horizontally(-Config.SCROLL_SPEED)
                elif event.key == pygame.K_RIGHT:
                    self.ui_components['ranking_panel'].scroll_horizontally(Config.SCROLL_SPEED)
                elif event.key == pygame.K_UP:
                    self.sidebar_scroll.scroll(-Config.SCROLL_SPEED)
                elif event.key == pygame.K_DOWN:
                    self.sidebar_scroll.scroll(Config.SCROLL_SPEED)
    
    def draw(self) -> None:
        """Render the game to the screen"""
        # Draw background
        self.screen.blit(self.background_texture, (0, 0))
        
        # Update UI component positions based on scroll
        for name, component in self.ui_components.items():
            component.update_position(self.sidebar_scroll.scroll_y, self.layout['sidebar_top_y'])
        
        # Set up clipping region for sidebar scrolling
        sidebar_area = pygame.Rect(
            self.layout['sidebar_x'], 
            self.layout['sidebar_top_y'], 
            self.layout['sidebar_width'], 
            self.height - self.layout['sidebar_top_y'] - int(self.height * 0.03)
        )
        sidebar_clip = self.screen.get_clip()
        self.screen.set_clip(sidebar_area)
        
        # Draw UI components in sidebar
        self.ui_components['time_panel'].draw(self.screen, self.fonts)
        timer_value_rect = pygame.Rect(
            self.ui_components['time_panel'].content_rect.x + 15, 
            self.ui_components['time_panel'].content_rect.y + 5, 
            self.ui_components['time_panel'].content_rect.width - 30, 
            self.ui_components['time_panel'].content_rect.height - 10
        )
        DrawingUtil.render_text_fit(
            self.screen,
            f"{self.game_state.get_elapsed_time():.1f} seconds", 
            timer_value_rect, 
            self.fonts, 
            Config.BLACK, 
            'text'
        )
        
        # Draw ranking panel with ghost images
        self.ui_components['ranking_panel'].draw(
            self.screen, 
            self.fonts, 
            self.ghost_scaled_images
        )
        
        # Update button hover states and draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for name in ['start_btn', 'restart_btn', 'gen_map_btn', 'gen_cherry_btn']:
            btn = self.ui_components[name]
            btn.hovered = btn.is_hovered(mouse_pos)
            if btn.adjusted_rect.bottom > self.layout['sidebar_top_y'] and btn.adjusted_rect.top < self.height:
                btn.draw(self.screen, self.fonts)
        
        # Draw scroll indicators
        self.sidebar_scroll.draw_scroll_indicators(self.screen)
        
        # Reset clip
        self.screen.set_clip(sidebar_clip)
        
        # Draw game title
        DrawingUtil.draw_rounded_rect(self.screen, Config.HEADER_BG, self.layout['game_title'], 10)
        DrawingUtil.render_text_fit(
            self.screen, 
            "Ghost-Cherry Race", 
            self.layout['game_title'], 
            self.fonts, 
            Config.HEADER_TEXT, 
            'title'
        )
        
        # Draw game board with shadow effect
        shadow_offset = max(3, int(min(self.width, self.height) * 0.005))
        shadow_rect = pygame.Rect(
            self.layout['arena_x'] + shadow_offset, 
            self.layout['arena_y'] + shadow_offset, 
            self.layout['arena_w'], 
            self.layout['arena_h']
        )
        DrawingUtil.draw_rounded_rect(self.screen, (0, 0, 0, 100), shadow_rect, radius=5)
        
        board_rect = pygame.Rect(
            self.layout['arena_x'], 
            self.layout['arena_y'], 
            self.layout['arena_w'], 
            self.layout['arena_h']
        )
        DrawingUtil.draw_rounded_rect(self.screen, Config.WHITE, board_rect, radius=5, border=2, border_color=Config.PANEL_BORDER)
        
        # Draw the game map
        self.map.draw(self.screen, self.layout['arena_x'], self.layout['arena_y'], self.tile_size)
        
        # Draw algorithm info
        DrawingUtil.draw_rounded_rect(self.screen, Config.PANEL_BG, self.layout['algorithm_info'], 5, 2, Config.PANEL_BORDER)
        algo_text = "Algorithms: Cyan (BFS), Pink (DFS), Orange (Djikstra)"
        DrawingUtil.render_text_fit(
            self.screen, 
            algo_text, 
            self.layout['algorithm_info'], 
            self.fonts, 
            Config.BLACK, 
            'small'
        )
        
        # Draw cherry
        self.cherry.draw(
            self.screen, 
            self.layout['arena_x'], 
            self.layout['arena_y'], 
            self.tile_size, 
            self.cherry_img
        )
        
        # Draw ghosts
        for ghost in self.ghosts:
            self.screen.blit(
                self.ghost_images[ghost.color], 
                (
                    self.layout['arena_x'] + ghost.position[0] * self.tile_size, 
                    self.layout['arena_y'] + ghost.position[1] * self.tile_size
                )
            )
        
        # Draw results popup if visible
        self.results_popup.draw(self.screen, self.fonts, self.ghost_scaled_images)
    
    def run(self) -> None:
        """Run the main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(Config.FRAME_RATE)
        
        pygame.quit()
        sys.exit()
