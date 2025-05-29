# ==========================================
# CONSTANTS AND CONFIGURATION
# ==========================================
class Config:
    """Configuration constants for the game"""
    # Base dimensions
    BASE_WIDTH = 1000
    BASE_HEIGHT = 700
    BASE_TILE_SIZE = 16
    
    # Colors
    BACKGROUND = (240, 240, 255)
    WHITE = (255, 255, 255)
    BLACK = (30, 30, 30)
    BLUE = (70, 105, 175)
    WALL_COLOR = (70, 80, 140)
    CHERRY_RED = (220, 20, 60)
    BUTTON_IDLE = (220, 220, 240)
    BUTTON_HOVER = (200, 200, 230)
    BUTTON_TEXT = (50, 50, 80)
    PANEL_BG = (230, 230, 245)
    PANEL_BORDER = (180, 180, 210)
    HEADER_BG = (100, 120, 200)
    HEADER_TEXT = (255, 255, 255)
    
    # Assets paths
    ASSETS = {
        'ghost_cyan': "assets/ghost-cyan.png",
        'ghost_pink': "assets/ghost-pink.png",
        'ghost_orange': "assets/ghost-orange.png",
        'ghost_red': "assets/ghost-red.png",
        'cherry': "assets/cherry.png",
        'map': "map.txt"
    }
    
    # Game settings
    SCROLL_SPEED = 20
    FRAME_RATE = 10