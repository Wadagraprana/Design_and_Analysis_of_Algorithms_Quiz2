import pygame
import sys
import random
import time
from collections import deque
import heapq
import math

pygame.init()

# Starting window size
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # Added RESIZABLE flag
pygame.display.set_caption("Ghost-Cherry Game")

# Base resolution for scaling calculations
BASE_WIDTH, BASE_HEIGHT = 1000, 700

# Enhanced color scheme
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

# Base tile size (will be scaled)
BASE_TILE_SIZE = 16
tile_size = BASE_TILE_SIZE  # Will be updated when screen is resized

# Scaling and layout utility functions
def get_scale_factor():
    """Calculate horizontal and vertical scale factors based on current window size"""
    scale_x = WIDTH / BASE_WIDTH
    scale_y = HEIGHT / BASE_HEIGHT
    return scale_x, scale_y

def scale_value(value, scale_factor):
    """Scale a single value by the given factor"""
    return int(value * scale_factor)

def scale_rect(rect, scale_x, scale_y):
    """Scale a rectangle's position and size"""
    return pygame.Rect(
        int(rect.x * scale_x),
        int(rect.y * scale_y),
        int(rect.width * scale_x),
        int(rect.height * scale_y)
    )

def scale_pos(pos, scale_x, scale_y):
    """Scale a position tuple"""
    return (int(pos[0] * scale_x), int(pos[1] * scale_y))

def create_fonts(scale_factor):
    """Create scaled fonts based on window size"""
    size_factor = min(scale_factor[0], scale_factor[1])  # Use minimum to prevent overly large fonts
    
    # Limit the scaling to prevent fonts from becoming too large or too small
    size_factor = max(0.7, min(1.5, size_factor))
    
    return {
        'title': pygame.font.SysFont('Arial', int(32 * size_factor), bold=True),
        'button': pygame.font.SysFont('Arial', int(20 * size_factor), bold=True),
        'text': pygame.font.SysFont('Arial', int(20 * size_factor)),
        'small': pygame.font.SysFont('Arial', int(16 * size_factor)),
        'smaller_title': pygame.font.SysFont('Arial', int(24 * size_factor), bold=True)
    }

# Initialize fonts (will be updated when screen is resized)
fonts = create_fonts(get_scale_factor())

# Load and prepare images
def load_scaled_image(path, size):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)

def update_images():
    """Update image sizes based on current tile size"""
    global ghost_cyan, ghost_pink, ghost_orange, cherry_img
    global ghost_cyan_scaled, ghost_pink_scaled, ghost_orange_scaled, ranking_tile_size
    
    ghost_cyan = load_scaled_image("assets/ghost-cyan.png", (tile_size, tile_size))
    ghost_pink = load_scaled_image("assets/ghost-pink.png", (tile_size, tile_size))
    ghost_orange = load_scaled_image("assets/ghost-orange.png", (tile_size, tile_size))
    cherry_img = load_scaled_image("assets/cherry.png", (tile_size, tile_size))
    
    # Fixed-ratio elements for rankings
    ranking_tile_size = scale_value(30, min(get_scale_factor()))
    ghost_cyan_scaled = load_scaled_image("assets/ghost-cyan.png", (ranking_tile_size, ranking_tile_size))
    ghost_pink_scaled = load_scaled_image("assets/ghost-pink.png", (ranking_tile_size, ranking_tile_size))
    ghost_orange_scaled = load_scaled_image("assets/ghost-orange.png", (ranking_tile_size, ranking_tile_size))

# Load background texture
def create_bg_texture(width, height):
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

background_texture = create_bg_texture(WIDTH, HEIGHT)

# Fixed rounded rectangle drawing function to properly handle borders
def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
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

def render_text_fit(text, rect, color=BLACK, max_font_size=30, font='text', align="center"):
    font_obj = fonts[font]
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
        
    screen.blit(text_surf, text_rect)
    
    # Return the width of the text for horizontal scaling
    return text_surf.get_width()

def draw_button(text, rect, hover=False):
    color = BUTTON_HOVER if hover else BUTTON_IDLE
    draw_rounded_rect(screen, color, rect, radius=8, border=2, border_color=PANEL_BORDER)
    render_text_fit(text, rect, BUTTON_TEXT, font='button')

def handle_resize(width, height):
    """Update all size-dependent variables when window is resized"""
    global WIDTH, HEIGHT, background_texture, tile_size, fonts
    
    # Update window dimensions
    WIDTH, HEIGHT = width, height
    
    # Regenerate background texture
    background_texture = create_bg_texture(WIDTH, HEIGHT)
    
    # Update fonts
    fonts = create_fonts(get_scale_factor())
    
    # Scale tile size based on available screen space and map dimensions
    scale_x, scale_y = get_scale_factor()
    arena_w_ratio = 0.7  # 70% of window width for game area
    arena_h_ratio = 0.8  # 80% of window height for game area
    
    # Calculate tile size to fit map in available space
    horizontal_tiles = cols
    vertical_tiles = rows
    
    # Use the smaller of horizontal and vertical constraints
    horizontal_tile_size = int((WIDTH * arena_w_ratio) / horizontal_tiles)
    vertical_tile_size = int((HEIGHT * arena_h_ratio) / vertical_tiles)
    tile_size = max(8, min(horizontal_tile_size, vertical_tile_size))  # Minimum tile size of 8px
    
    # Update all images with new scales
    update_images()

def load_map(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    return [[int(ch) for ch in line] for line in lines]

preset_map = load_map('map.txt')
rows, cols = len(preset_map), len(preset_map[0])

# Initialize image variables
ghost_cyan = None
ghost_pink = None
ghost_orange = None
cherry_img = None
ghost_cyan_scaled = None
ghost_pink_scaled = None
ghost_orange_scaled = None
ranking_tile_size = 30

# Initial image loading
update_images()

def draw_map(offset_x, offset_y):
    map_surface = pygame.Surface((cols*tile_size, rows*tile_size), pygame.SRCALPHA)
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c*tile_size, r*tile_size, tile_size, tile_size)
            if preset_map[r][c] == 1:
                # Draw walls with a 3D effect
                pygame.draw.rect(map_surface, WALL_COLOR, rect)
                pygame.draw.line(map_surface, (WALL_COLOR[0]-30, WALL_COLOR[1]-30, WALL_COLOR[2]-30), 
                               (c*tile_size, r*tile_size), (c*tile_size, (r+1)*tile_size), 1)
                pygame.draw.line(map_surface, (WALL_COLOR[0]-30, WALL_COLOR[1]-30, WALL_COLOR[2]-30), 
                               (c*tile_size, r*tile_size), ((c+1)*tile_size, r*tile_size), 1)
                pygame.draw.line(map_surface, (min(WALL_COLOR[0]+30, 255), min(WALL_COLOR[1]+30, 255), min(WALL_COLOR[2]+30, 255)), 
                               ((c+1)*tile_size-1, r*tile_size), ((c+1)*tile_size-1, (r+1)*tile_size), 1)
                pygame.draw.line(map_surface, (min(WALL_COLOR[0]+30, 255), min(WALL_COLOR[1]+30, 255), min(WALL_COLOR[2]+30, 255)), 
                               (c*tile_size, (r+1)*tile_size-1), ((c+1)*tile_size, (r+1)*tile_size-1), 1)
            else:
                # Draw path tiles with a subtle grid
                pygame.draw.rect(map_surface, WHITE, rect)
                pygame.draw.line(map_surface, (230, 230, 230), 
                               (c*tile_size, r*tile_size), (c*tile_size+tile_size, r*tile_size), 1)
                pygame.draw.line(map_surface, (230, 230, 230), 
                               (c*tile_size, r*tile_size), (c*tile_size, r*tile_size+tile_size), 1)
    
    # Draw a border around the map
    pygame.draw.rect(map_surface, BLACK, (0, 0, cols*tile_size, rows*tile_size), 2)
    
    screen.blit(map_surface, (offset_x, offset_y))

def a_star(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, [start]))
    visited = set()

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    while open_set:
        cost, path = heapq.heappop(open_set)
        x, y = path[-1]
        if (x, y) == goal:
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and preset_map[ny][nx] == 0 and (nx, ny) not in visited:
                new_cost = len(path) + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (new_cost, path + [(nx, ny)]))
    return []

def dijkstra(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, [start]))
    visited = set()

    while open_set:
        cost, path = heapq.heappop(open_set)
        x, y = path[-1]
        if (x, y) == goal:
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and preset_map[ny][nx] == 0 and (nx, ny) not in visited:
                new_cost = cost + 1  # Increment cost for each step
                heapq.heappush(open_set, (new_cost, path + [(nx, ny)]))
    return []

def bfs(start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        x,y = path[-1]
        if (x,y) == goal:
            return path
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<cols and 0<=ny<rows and preset_map[ny][nx]==0 and (nx,ny) not in visited:
                queue.append(path+[(nx,ny)])
                visited.add((nx,ny))
    return []

def dfs(start, goal):
    stack = [[start]]
    visited = set()
    while stack:
        path = stack.pop()
        x,y = path[-1]
        if (x,y) == goal:
            return path
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<cols and 0<=ny<rows and preset_map[ny][nx]==0 and (nx,ny) not in visited:
                stack.append(path+[(nx,ny)])
                visited.add((nx,ny))
    return []

def kruskal_path(start, goal):
    path = [start]
    current = start
    while current != goal:
        x,y = current
        options = [(x+dx,y+dy) for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]
                   if 0<=x+dx<cols and 0<=y+dy<rows and preset_map[y+dy][x+dx]==0]
        if options:
            current = random.choice(options)
            if current not in path:
                path.append(current)
        else:
            break
    return path

ghosts, popup_open, ranking, previous_ranking = [], False, [], []
cherry_pos = [2,1]
game_started, start_time, end_time, game_finished, timer_reset = False, None, None, False, False
close_rect = pygame.Rect(0, 0, 0, 0)

def reset_game(new_map=False, new_cherry=False):
    global ghosts, cherry_pos, popup_open, ranking, game_finished, preset_map
    if new_map:
        map_lines = load_map('map.txt')
        preset_map = []
        for r in range(rows):
            if r in [0,14,15,16,17,18,31]:
                preset_map.append(map_lines[r])
            else:
                row = [1 if random.random()<0.3 else 0 for c in range(cols)]
                row[0], row[-1] = 1, 1
                preset_map.append(row)
    if new_cherry or new_map or not bfs((15,16), tuple(cherry_pos)) or not bfs((16,17), tuple(cherry_pos)) or not bfs((17,16), tuple(cherry_pos)):
        while True:
            x, y = random.randint(1, cols-2), random.randint(1, rows-2)
            if preset_map[y][x] == 0:
                if (bfs((15,16), (x,y)) and bfs((16,17), (x,y)) and bfs((17,16), (x,y))):
                    cherry_pos = [x, y]
                    break
    ghosts = [
        {'img': ghost_cyan, 'pos':[15,16], 'path':[], 'algorithm':'BFS', 'time':None, 'name':'Cyan'},
        {'img': ghost_pink, 'pos':[16,17], 'path':[], 'algorithm':'DFS', 'time':None, 'name':'Pink'},
        {'img': ghost_orange, 'pos':[17,16], 'path':[], 'algorithm':'Kruskal', 'time':None, 'name':'Orange'}
    ]
    popup_open, ranking, game_finished = False, [], False

# Initialize the game
reset_game()
clock = pygame.time.Clock()
running = True
scroll_speed = 20

# Dynamic UI layout calculation
def calculate_layout():
    scale_x, scale_y = get_scale_factor()
    
    # Calculate sidebar dimensions (30% of width, full height)
    sidebar_width_ratio = 0.28
    sidebar_width_px = int(WIDTH * sidebar_width_ratio)
    sidebar_x = int(WIDTH * 0.02)  # 2% margin
    sidebar_top_y = int(HEIGHT * 0.03)  # 3% margin from top
    
    # Calculate game area dimensions (65% of width, 80% of height)
    main_area_ratio = 1.0 - sidebar_width_ratio - 0.05  # 5% margin between sidebar and game
    main_x = sidebar_x + sidebar_width_px + int(WIDTH * 0.02)
    main_width = int(WIDTH * main_area_ratio)
    
    # Arena positioning
    arena_x = main_x
    arena_y = int(HEIGHT * 0.1)  # 10% from top
    arena_w = cols * tile_size
    arena_h = rows * tile_size
    
    # Panel heights (as % of available height)
    time_panel_height = int(HEIGHT * 0.12)
    ranking_panel_height = int(HEIGHT * 0.4)
    btn_h = int(HEIGHT * 0.07)
    
    # Panels positioning
    time_rect = pygame.Rect(sidebar_x, sidebar_top_y, sidebar_width_px, time_panel_height)
    
    # Spacing between panels (scaled)
    panel_spacing = int(HEIGHT * 0.02)
    
    ranking_rect = pygame.Rect(
        sidebar_x, 
        time_rect.bottom + panel_spacing,
        sidebar_width_px, 
        ranking_panel_height
    )
    
    # Button dimensions
    btn_w = sidebar_width_px
    btn_margin = int(HEIGHT * 0.02)
    
    # Button positions
    controls_y = ranking_rect.bottom + panel_spacing
    start_btn = pygame.Rect(sidebar_x, controls_y, btn_w, btn_h)
    restart_btn = pygame.Rect(sidebar_x, controls_y + btn_h + btn_margin, btn_w, btn_h)
    gen_map_btn = pygame.Rect(sidebar_x, controls_y + (btn_h + btn_margin) * 2, btn_w, btn_h)
    gen_cherry_btn = pygame.Rect(sidebar_x, controls_y + (btn_h + btn_margin) * 3, btn_w, btn_h)
    
    # Calculate total sidebar content height for scrolling
    sidebar_content_height = gen_cherry_btn.bottom - time_rect.top + int(HEIGHT * 0.03)
    sidebar_visible_height = HEIGHT - int(HEIGHT * 0.03)
    
    # Title area
    game_title = pygame.Rect(arena_x, int(HEIGHT * 0.03), arena_w, int(HEIGHT * 0.06))
    
    # Algorithm info below the game board
    algorithm_info = pygame.Rect(arena_x, arena_y + arena_h + int(HEIGHT * 0.01), arena_w, int(HEIGHT * 0.12))
    
    # Store original time_rect for scrolling calculations
    time_rect_original = time_rect.copy()
    
    return {
        'sidebar_width': sidebar_width_px,
        'sidebar_x': sidebar_x,
        'sidebar_top_y': sidebar_top_y,
        'time_rect': time_rect,
        'time_rect_original': time_rect_original,
        'ranking_rect': ranking_rect,
        'start_btn': start_btn,
        'restart_btn': restart_btn,
        'gen_map_btn': gen_map_btn,
        'gen_cherry_btn': gen_cherry_btn,
        'sidebar_content_height': sidebar_content_height,
        'sidebar_visible_height': sidebar_visible_height,
        'main_x': main_x, 
        'main_width': main_width,
        'arena_x': arena_x,
        'arena_y': arena_y,
        'arena_w': arena_w,
        'arena_h': arena_h,
        'game_title': game_title,
        'algorithm_info': algorithm_info,
        'btn_h': btn_h,
    }

# Button hover detection
def is_button_hovered(btn, layout):
    mouse_pos = pygame.mouse.get_pos()
    # Adjust for scrolling in sidebar
    adjusted_rect = pygame.Rect(
        btn.x, 
        btn.y - sidebar_scroll_y + layout['sidebar_top_y'], 
        btn.width, 
        btn.height
    )
    return adjusted_rect.collidepoint(mouse_pos)

# Scroll variables
sidebar_scroll_y = 0
sidebar_h_scroll_x = 0
max_h_scroll = 0  # Will be calculated during rendering

# Main game loop
while running:
    # Calculate responsive layout
    layout = calculate_layout()
    
    # Background
    screen.blit(background_texture, (0, 0))
    
    # Calculate sidebar scroll limits
    max_scroll = max(0, layout['sidebar_content_height'] - layout['sidebar_visible_height'])
    sidebar_scroll_y = min(max_scroll, max(0, sidebar_scroll_y))
    
    # Adjust rect positions for scrolling
    adjusted_time_rect = pygame.Rect(
        layout['time_rect'].x, 
        layout['time_rect'].y - sidebar_scroll_y + layout['sidebar_top_y'], 
        layout['time_rect'].width, 
        layout['time_rect'].height
    )
    
    adjusted_ranking_rect = pygame.Rect(
        layout['ranking_rect'].x, 
        layout['ranking_rect'].y - sidebar_scroll_y + layout['sidebar_top_y'], 
        layout['ranking_rect'].width, 
        layout['ranking_rect'].height
    )
    
    adjusted_start_btn = pygame.Rect(
        layout['start_btn'].x, 
        layout['start_btn'].y - sidebar_scroll_y + layout['sidebar_top_y'], 
        layout['start_btn'].width, 
        layout['start_btn'].height
    )
    
    adjusted_restart_btn = pygame.Rect(
        layout['restart_btn'].x, 
        layout['restart_btn'].y - sidebar_scroll_y + layout['sidebar_top_y'], 
        layout['restart_btn'].width, 
        layout['restart_btn'].height
    )
    
    adjusted_gen_map_btn = pygame.Rect(
        layout['gen_map_btn'].x, 
        layout['gen_map_btn'].y - sidebar_scroll_y + layout['sidebar_top_y'], 
        layout['gen_map_btn'].width, 
        layout['gen_map_btn'].height
    )
    
    adjusted_gen_cherry_btn = pygame.Rect(
        layout['gen_cherry_btn'].x, 
        layout['gen_cherry_btn'].y - sidebar_scroll_y + layout['sidebar_top_y'], 
        layout['gen_cherry_btn'].width, 
        layout['gen_cherry_btn'].height
    )
    
    # Create a clipping rect for the sidebar area to prevent drawing outside
    sidebar_area = pygame.Rect(
        layout['sidebar_x'], 
        layout['sidebar_top_y'], 
        layout['sidebar_width'], 
        HEIGHT - layout['sidebar_top_y'] - int(HEIGHT * 0.03)
    )
    sidebar_clip = screen.get_clip()
    screen.set_clip(sidebar_area)
    
    # Draw timer panel
    draw_rounded_rect(screen, PANEL_BG, adjusted_time_rect, 10, 2, PANEL_BORDER)
    
    # Create header inside the panel
    header_height = min(36, int(adjusted_time_rect.height * 0.4))  # Scale header height
    timer_header = pygame.Rect(
        adjusted_time_rect.x + 2, 
        adjusted_time_rect.y + 2, 
        adjusted_time_rect.width - 4, 
        header_height
    )
    draw_rounded_rect(screen, HEADER_BG, timer_header, radius=8, border=0)
    
    # Add margin to the header text
    timer_header_text = pygame.Rect(
        timer_header.x + 10, 
        timer_header.y, 
        timer_header.width - 20, 
        timer_header.height
    )
    render_text_fit("TIME", timer_header_text, HEADER_TEXT, font='title', align="left")

    if timer_reset or (not game_started and not start_time):
        elapsed = 0
    elif start_time:
        elapsed = round((end_time if end_time else time.time()) - start_time, 1)
    else:
        elapsed = 0
        
    timer_value_rect = pygame.Rect(
        adjusted_time_rect.x + 15, 
        timer_header.bottom + 5, 
        adjusted_time_rect.width - 30, 
        adjusted_time_rect.height - timer_header.height - 10
    )
    render_text_fit(f"{elapsed:.1f} seconds", timer_value_rect, BLACK, font='text')
    
    # Draw ranking panel
    if adjusted_ranking_rect.top < HEIGHT and adjusted_ranking_rect.top + 40 > layout['sidebar_top_y']:
        draw_rounded_rect(screen, PANEL_BG, adjusted_ranking_rect, 10, 2, PANEL_BORDER)
        
        # Create header inside the panel
        ranking_header_height = min(32, int(adjusted_ranking_rect.height * 0.12))
        ranking_header = pygame.Rect(
            adjusted_ranking_rect.x + 2, 
            adjusted_ranking_rect.y + 2, 
            adjusted_ranking_rect.width - 4, 
            ranking_header_height
        )
        draw_rounded_rect(screen, HEADER_BG, ranking_header, radius=8, border=0)
        
        # Add margin to the header text
        ranking_header_text = pygame.Rect(
            ranking_header.x + 10, 
            ranking_header.y, 
            ranking_header.width - 20, 
            ranking_header.height
        )
        render_text_fit("PREVIOUS RANKING", ranking_header_text, HEADER_TEXT, font='smaller_title', align="left")
    
        # Create a content area for ranking that can scroll horizontally
        content_margin = int(adjusted_ranking_rect.width * 0.04)  # 4% margin
        ranking_content_area = pygame.Rect(
            adjusted_ranking_rect.x + content_margin - sidebar_h_scroll_x, 
            adjusted_ranking_rect.y + ranking_header_height + 10,
            500,  # Make this wider than visible area to accommodate content
            adjusted_ranking_rect.height - ranking_header_height - 20
        )
        
        # Calculate real widths based on text lengths for columns
        col_base_widths = [50, 60]  # First two columns have fixed widths
        algorithm_width = max([fonts['text'].size(g['algorithm'])[0] + 20 for g in previous_ranking] + [100]) if previous_ranking else 100
        time_width = max([fonts['text'].size(f"{g['time']}s")[0] + 20 for g in previous_ranking] + [70]) if previous_ranking else 70
        
        # Scale column widths based on screen size
        scale_factor = min(get_scale_factor())
        col_widths = [
            max(30, int(50 * scale_factor)),
            max(40, int(60 * scale_factor)),
            max(80, int(algorithm_width * scale_factor)),
            max(50, int(time_width * scale_factor))
        ]
        
        total_cols_width = sum(col_widths) + 30  # Add spacing between columns
        
        # Draw table background
        table_bg = pygame.Rect(
            ranking_content_area.x,
            ranking_content_area.y,
            total_cols_width,
            ranking_content_area.height
        )
        
        # Calculate max horizontal scroll
        max_h_scroll = max(0, total_cols_width - (adjusted_ranking_rect.width - 2*content_margin))
        sidebar_h_scroll_x = min(max_h_scroll, max(0, sidebar_h_scroll_x))
        
        # Draw ranking table headers with horizontal scrolling
        header_y = ranking_content_area.y
        header_height = int(ranking_content_area.height * 0.1)  # 10% of content area height
        headers = ["Rank", "Ghost", "Algorithm", "Time"]
        
        header_x = ranking_content_area.x  # Start position considering scroll
        
        for i, header in enumerate(headers):
            rect = pygame.Rect(header_x, header_y, col_widths[i], header_height)
            draw_rounded_rect(screen, (180, 180, 220), rect, radius=5)
            render_text_fit(header, rect, BLACK, font='small')
            header_x += col_widths[i] + 10  # Add spacing between columns
        
        # Draw previous ranking data with proper spacing and horizontal scrolling
        row_height = max(ranking_tile_size + 5, int(ranking_content_area.height * 0.25))
        for i in range(3):
            row_y = header_y + header_height + 10 + i*row_height
            
            if i < len(previous_ranking):
                g = previous_ranking[i]
                
                # Draw a row background that spans the full content width
                row_rect = pygame.Rect(
                    ranking_content_area.x, 
                    row_y, 
                    total_cols_width,  # Use the full content width
                    row_height - 5
                )
                draw_rounded_rect(screen, (245, 245, 255), row_rect, radius=5)
                
                # Place items with proper spacing, accounting for horizontal scroll
                col_x = ranking_content_area.x  # Start at left edge of content area
                
                # Draw rank (always visible)
                rank_rect = pygame.Rect(col_x, row_y + 3, col_widths[0], ranking_tile_size)
                render_text_fit(f"{i+1}", rank_rect, BLACK, font='text')
                col_x += col_widths[0] + 10
                
                # Draw ghost icon
                ghost_x = col_x
                img = {'Cyan': ghost_cyan_scaled, 'Pink': ghost_pink_scaled, 'Orange': ghost_orange_scaled}[g['name']]
                screen.blit(img, (ghost_x, row_y))
                col_x += col_widths[1] + 10
                
                # Draw algorithm - with enough space for the text
                algo_rect = pygame.Rect(col_x, row_y + 3, col_widths[2], ranking_tile_size)
                render_text_fit(g['algorithm'], algo_rect, BLACK, font='text', align="left")
                col_x += col_widths[2] + 10
                
                # Draw time - with enough space for the time
                time_rect_row = pygame.Rect(col_x, row_y + 3, col_widths[3], ranking_tile_size)
                render_text_fit(f"{g['time']}s", time_rect_row, BLACK, font='text', align="center")
        
        # Draw horizontal scroll indicators if needed
        scroll_indicator_size = int(adjusted_ranking_rect.width * 0.07)
        if sidebar_h_scroll_x > 0:
            # Left scroll indicator
            left_arrow = pygame.Rect(
                adjusted_ranking_rect.x + 5, 
                adjusted_ranking_rect.bottom - scroll_indicator_size - 5, 
                scroll_indicator_size, 
                scroll_indicator_size
            )
            draw_rounded_rect(screen, (200, 200, 220), left_arrow, radius=5)
            pygame.draw.polygon(screen, BLACK, [
                (left_arrow.centerx - 5, left_arrow.centery),
                (left_arrow.centerx + 3, left_arrow.top + 5),
                (left_arrow.centerx + 3, left_arrow.bottom - 5)
            ])
        
        if sidebar_h_scroll_x < max_h_scroll:
            # Right scroll indicator
            right_arrow = pygame.Rect(
                adjusted_ranking_rect.right - scroll_indicator_size - 5, 
                adjusted_ranking_rect.bottom - scroll_indicator_size - 5, 
                scroll_indicator_size, 
                scroll_indicator_size
            )
            draw_rounded_rect(screen, (200, 200, 220), right_arrow, radius=5)
            pygame.draw.polygon(screen, BLACK, [
                (right_arrow.centerx + 5, right_arrow.centery),
                (right_arrow.centerx - 3, right_arrow.top + 5),
                (right_arrow.centerx - 3, right_arrow.bottom - 5)
            ])

    # Draw buttons if they're in view
    if adjusted_start_btn.bottom > layout['sidebar_top_y'] and adjusted_start_btn.top < HEIGHT:
        draw_button("Start Game", adjusted_start_btn, is_button_hovered(layout['start_btn'], layout))
        
    if adjusted_restart_btn.bottom > layout['sidebar_top_y'] and adjusted_restart_btn.top < HEIGHT:
        draw_button("Restart Game", adjusted_restart_btn, is_button_hovered(layout['restart_btn'], layout))
        
    if adjusted_gen_map_btn.bottom > layout['sidebar_top_y'] and adjusted_gen_map_btn.top < HEIGHT:
        draw_button("Generate New Map", adjusted_gen_map_btn, is_button_hovered(layout['gen_map_btn'], layout))
        
    if adjusted_gen_cherry_btn.bottom > layout['sidebar_top_y'] and adjusted_gen_cherry_btn.top < HEIGHT:
        draw_button("Generate New Cherry", adjusted_gen_cherry_btn, is_button_hovered(layout['gen_cherry_btn'], layout))
    
    # Draw vertical scroll indicators if needed
    scroll_indicator_size = int(layout['sidebar_width'] * 0.07)
    if sidebar_scroll_y > 0:
        # Draw up scroll indicator
        up_arrow = pygame.Rect(
            layout['sidebar_x'] + layout['sidebar_width'] - scroll_indicator_size - 5, 
            layout['sidebar_top_y'] + 5, 
            scroll_indicator_size, 
            scroll_indicator_size
        )
        draw_rounded_rect(screen, (200, 200, 220), up_arrow, radius=5)
        pygame.draw.polygon(screen, BLACK, [
            (up_arrow.centerx, up_arrow.top + 5),
            (up_arrow.left + 5, up_arrow.bottom - 5),
            (up_arrow.right - 5, up_arrow.bottom - 5)
        ])
    
    if sidebar_scroll_y < max_scroll:
        # Draw down scroll indicator
        down_arrow = pygame.Rect(
            layout['sidebar_x'] + layout['sidebar_width'] - scroll_indicator_size - 5, 
            HEIGHT - scroll_indicator_size - 5, 
            scroll_indicator_size, 
            scroll_indicator_size
        )
        draw_rounded_rect(screen, (200, 200, 220), down_arrow, radius=5)
        pygame.draw.polygon(screen, BLACK, [
            (down_arrow.centerx, down_arrow.bottom - 5),
            (down_arrow.left + 5, down_arrow.top + 5),
            (down_arrow.right - 5, down_arrow.top + 5)
        ])
    
    # Reset clip
    screen.set_clip(sidebar_clip)
    
    # Draw title and info
    title_rect = pygame.Rect(layout['arena_x'], int(HEIGHT * 0.03), layout['arena_w'], int(HEIGHT * 0.06))
    draw_rounded_rect(screen, HEADER_BG, title_rect, 10)
    render_text_fit("Ghost-Cherry Race", title_rect, HEADER_TEXT, font='title')
    
    # Draw the game board with a shadow effect
    shadow_offset = max(3, int(min(WIDTH, HEIGHT) * 0.005))  # Scale shadow with screen size
    shadow_rect = pygame.Rect(
        layout['arena_x'] + shadow_offset, 
        layout['arena_y'] + shadow_offset, 
        layout['arena_w'], 
        layout['arena_h']
    )
    draw_rounded_rect(screen, (0, 0, 0, 100), shadow_rect, radius=5)
    
    board_rect = pygame.Rect(
        layout['arena_x'], 
        layout['arena_y'], 
        layout['arena_w'], 
        layout['arena_h']
    )
    draw_rounded_rect(screen, WHITE, board_rect, radius=5, border=2, border_color=PANEL_BORDER)
    
    draw_map(layout['arena_x'], layout['arena_y'])
    
    # Draw algorithm info
    algo_info_rect = pygame.Rect(
        layout['arena_x'], 
        layout['arena_y'] + layout['arena_h'] + int(HEIGHT * 0.01), 
        layout['arena_w'], 
        int(HEIGHT * 0.06)
    )
    draw_rounded_rect(screen, PANEL_BG, algo_info_rect, 5, 2, PANEL_BORDER)
    algo_text = "Algorithms: Cyan (BFS), Pink (DFS), Orange (Kruskal)"
    render_text_fit(algo_text, algo_info_rect, BLACK, font='small')
    
    # Draw cherry with a pulsating effect
    cherry_pulse = math.sin(time.time() * 5) * 2 + 2
    cherry_glow = pygame.Surface((tile_size + cherry_pulse*2, tile_size + cherry_pulse*2), pygame.SRCALPHA)
    pygame.draw.circle(cherry_glow, (CHERRY_RED[0], CHERRY_RED[1], CHERRY_RED[2], 100), 
                     (cherry_glow.get_width()//2, cherry_glow.get_height()//2), tile_size//2 + cherry_pulse)
    
    screen.blit(cherry_glow, 
               (layout['arena_x'] + cherry_pos[0]*tile_size - cherry_pulse, 
                layout['arena_y'] + cherry_pos[1]*tile_size - cherry_pulse))
    
    screen.blit(cherry_img, (layout['arena_x'] + cherry_pos[0]*tile_size, layout['arena_y'] + cherry_pos[1]*tile_size))
    
    # Update and draw ghosts
    if game_started:
        for g in ghosts:
            if not g['path']:
                g['path'] = {'BFS':bfs,'DFS':dfs,'Kruskal':kruskal_path, 'AStar': a_star, 'Dijkstra': dijkstra}[g['algorithm']](tuple(g['pos']), tuple(cherry_pos))
            if g['path']:
                g['pos'] = list(g['path'].pop(0))
                if g['pos'] == cherry_pos and g['time'] is None and start_time is not None:
                    g['time'] = round(time.time() - start_time, 2)

        if all(g['time'] for g in ghosts) and not popup_open:
            ranking = sorted(ghosts, key=lambda x:x['time'])
            previous_ranking = ranking.copy()
            popup_open, game_started, game_finished = True, False, True
            end_time = time.time()

    for g in ghosts:
        screen.blit(g['img'], (layout['arena_x'] + g['pos'][0]*tile_size, layout['arena_y'] + g['pos'][1]*tile_size))

    # Draw popup if needed
    if popup_open:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Scale popup based on screen size
        popup_width = min(WIDTH * 0.8, 600)  # Cap width at 600px or 80% of screen
        popup_height = min(HEIGHT * 0.8, 400)  # Cap height at 400px or 80% of screen
        
        popup_rect = pygame.Rect(
            (WIDTH - popup_width) // 2,
            (HEIGHT - popup_height) // 2,
            popup_width,
            popup_height
        )
        draw_rounded_rect(screen, WHITE, popup_rect, 15, 3, PANEL_BORDER)
        
        # Scale header based on popup size
        header_height = min(54, int(popup_height * 0.15))
        header_rect = pygame.Rect(
            popup_rect.x + 3, 
            popup_rect.y + 3, 
            popup_rect.width - 6, 
            header_height
        )
        draw_rounded_rect(screen, HEADER_BG, header_rect, 12, 0)
        
        header_text_rect = pygame.Rect(
            header_rect.x + int(popup_width * 0.05), 
            header_rect.y, 
            header_rect.width - int(popup_width * 0.1), 
            header_rect.height
        )
        render_text_fit("RACE RESULTS", header_text_rect, HEADER_TEXT, font='title', align="left")
        
        # Close button - scaled to popup size
        close_btn_size = min(30, int(popup_width * 0.05))
        close_rect = pygame.Rect(
            popup_rect.right - close_btn_size - 15, 
            popup_rect.y + 15, 
            close_btn_size, 
            close_btn_size
        )
        draw_rounded_rect(screen, (220, 100, 100), close_rect, close_btn_size//2, 2, (180, 80, 80))
        render_text_fit("X", close_rect, WHITE, font='button')
        
        # Display ranking results with colorful medals
        available_height = popup_height - header_height - 30
        row_height = min(60, available_height / 3)  # Divide available height by the number of ghosts
        
        for idx, g in enumerate(ranking):
            r = pygame.Rect(
                popup_rect.x + int(popup_width * 0.05), 
                popup_rect.y + header_height + 15 + idx*row_height, 
                popup_rect.width - int(popup_width * 0.1), 
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
            draw_rounded_rect(screen, medal_color, medal_rect, radius=medal_size//2)
            render_text_fit(f"{idx+1}", medal_rect, txt_color, font='title')
            
            # Draw ghost image
            img = {'Cyan': ghost_cyan_scaled, 'Pink': ghost_pink_scaled, 'Orange': ghost_orange_scaled}[g['name']]
            ghost_rect = pygame.Rect(
                r.x + medal_size + 20, 
                r.y + (row_height - ranking_tile_size) // 2, 
                ranking_tile_size, 
                ranking_tile_size
            )
            screen.blit(img, ghost_rect)
            
            # Draw name and algorithm
            info_width = min(200, int(popup_width * 0.4))
            info_rect = pygame.Rect(
                ghost_rect.right + 20, 
                r.y + (row_height - 50) // 2, 
                info_width, 
                50
            )
            render_text_fit(f"{g['name']} ({g['algorithm']})", info_rect, BLACK, font='text')
            
            # Draw time with animation
            time_str = f"{g['time']}s"
            time_width = min(90, int(popup_width * 0.15))
            time_rect = pygame.Rect(
                r.right - time_width, 
                r.y + (row_height - 50) // 2, 
                time_width, 
                50
            )
            render_text_fit(time_str, time_rect, txt_color, font='title')

    # Event handling
    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            running = False
        
        elif e.type == pygame.VIDEORESIZE:
            # Handle window resize event
            WIDTH, HEIGHT = e.w, e.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            handle_resize(WIDTH, HEIGHT)
        
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:  # Left click
                if popup_open:
                    if close_rect.collidepoint(e.pos):
                        popup_open = False
                else:
                    # Check button clicks with adjusted positions
                    if adjusted_start_btn.collidepoint(e.pos) and not game_started and not game_finished:
                        game_started = True
                        start_time = time.time()
                        end_time = None
                        timer_reset = False
                        reset_game()
                    elif adjusted_restart_btn.collidepoint(e.pos) and not game_started:
                        reset_game()
                        # Reset timer when restarting the game
                        start_time = None
                        end_time = None
                        timer_reset = True
                        game_started = False
                        game_finished = False
                    elif adjusted_gen_map_btn.collidepoint(e.pos) and not game_started:
                        reset_game(True, True)
                        # Reset timer when generating new map
                        start_time = None
                        end_time = None
                        timer_reset = True
                        game_started = False
                        game_finished = False
                    elif adjusted_gen_cherry_btn.collidepoint(e.pos) and not game_started:
                        reset_game(False, True)
                        # Reset timer when generating new cherry
                        start_time = None
                        end_time = None
                        timer_reset = True
                        game_started = False
                        game_finished = False
                    # Check for horizontal scroll arrow clicks
                    elif adjusted_ranking_rect.collidepoint(e.pos):
                        arrow_size = int(layout['sidebar_width'] * 0.07)
                        left_arrow = pygame.Rect(
                            adjusted_ranking_rect.x + 5, 
                            adjusted_ranking_rect.bottom - arrow_size - 5,
                            arrow_size, 
                            arrow_size
                        )
                        right_arrow = pygame.Rect(
                            adjusted_ranking_rect.right - arrow_size - 5, 
                            adjusted_ranking_rect.bottom - arrow_size - 5,
                            arrow_size, 
                            arrow_size
                        )
                        if left_arrow.collidepoint(e.pos) and sidebar_h_scroll_x > 0:
                            sidebar_h_scroll_x = max(0, sidebar_h_scroll_x - 30)
                        elif right_arrow.collidepoint(e.pos) and sidebar_h_scroll_x < max_h_scroll:
                            sidebar_h_scroll_x = min(max_h_scroll, sidebar_h_scroll_x + 30)
                    
                    # Check vertical scroll arrows
                    arrow_size = int(layout['sidebar_width'] * 0.07)
                    up_arrow = pygame.Rect(
                        layout['sidebar_x'] + layout['sidebar_width'] - arrow_size - 5, 
                        layout['sidebar_top_y'] + 5,
                        arrow_size, 
                        arrow_size
                    )
                    down_arrow = pygame.Rect(
                        layout['sidebar_x'] + layout['sidebar_width'] - arrow_size - 5, 
                        HEIGHT - arrow_size - 5,
                        arrow_size, 
                        arrow_size
                    )
                    if up_arrow.collidepoint(e.pos) and sidebar_scroll_y > 0:
                        sidebar_scroll_y = max(0, sidebar_scroll_y - 50)
                    elif down_arrow.collidepoint(e.pos) and sidebar_scroll_y < max_scroll:
                        sidebar_scroll_y = min(max_scroll, sidebar_scroll_y + 50)
                        
            elif e.button == 4:  # Mouse wheel up
                if sidebar_area.collidepoint(pygame.mouse.get_pos()):
                    # Check if mouse is over ranking panel for horizontal scroll with Shift held down
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT and adjusted_ranking_rect.collidepoint(pygame.mouse.get_pos()):
                        sidebar_h_scroll_x = max(0, sidebar_h_scroll_x - scroll_speed)
                    else:
                        # Vertical scrolling
                        sidebar_scroll_y = max(0, sidebar_scroll_y - scroll_speed)
                        
            elif e.button == 5:  # Mouse wheel down
                if sidebar_area.collidepoint(pygame.mouse.get_pos()):
                    # Check if mouse is over ranking panel for horizontal scroll with Shift held down
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT and adjusted_ranking_rect.collidepoint(pygame.mouse.get_pos()):
                        sidebar_h_scroll_x = min(max_h_scroll, sidebar_h_scroll_x + scroll_speed)
                    else:
                        # Vertical scrolling
                        sidebar_scroll_y = min(max_scroll, sidebar_scroll_y + scroll_speed)
                        
        # Add keyboard support for scrolling
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT and adjusted_ranking_rect.collidepoint(pygame.mouse.get_pos()):
                sidebar_h_scroll_x = max(0, sidebar_h_scroll_x - scroll_speed)
            elif e.key == pygame.K_RIGHT and adjusted_ranking_rect.collidepoint(pygame.mouse.get_pos()):
                sidebar_h_scroll_x = min(max_h_scroll, sidebar_h_scroll_x + scroll_speed)
            elif e.key == pygame.K_UP and sidebar_area.collidepoint(pygame.mouse.get_pos()):
                sidebar_scroll_y = max(0, sidebar_scroll_y - scroll_speed)
            elif e.key == pygame.K_DOWN and sidebar_area.collidepoint(pygame.mouse.get_pos()):
                sidebar_scroll_y = min(max_scroll, sidebar_scroll_y + scroll_speed)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()