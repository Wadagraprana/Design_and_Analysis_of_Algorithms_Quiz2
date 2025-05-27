import pygame
import sys
import random
import time
from collections import deque
import heapq

pygame.init()
WIDTH, HEIGHT = 900, 600
tile_size = 15
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ghost-Cherry Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

font = pygame.font.SysFont(None, 30)

def render_text_fit(text, rect, color=BLACK, max_font_size=30):
    font_size = max_font_size
    font = pygame.font.SysFont(None, font_size)
    text_surf = font.render(text, True, color)
    while (text_surf.get_width() > rect.width - 10 or text_surf.get_height() > rect.height - 10) and font_size > 10:
        font_size -= 1
        font = pygame.font.SysFont(None, font_size)
        text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_button(text, rect):
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    render_text_fit(text, rect)

def load_map(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    return [[int(ch) for ch in line] for line in lines]

preset_map = load_map('map.txt')
rows, cols = len(preset_map), len(preset_map[0])

ghost_cyan = pygame.image.load("assets/ghost-cyan.png")
ghost_pink = pygame.image.load("assets/ghost-pink.png")
ghost_orange = pygame.image.load("assets/ghost-orange.png")
cherry_img = pygame.image.load("assets/cherry.png")
ghost_cyan = pygame.transform.scale(ghost_cyan, (tile_size, tile_size))
ghost_pink = pygame.transform.scale(ghost_pink, (tile_size, tile_size))
ghost_orange = pygame.transform.scale(ghost_orange, (tile_size, tile_size))
cherry_img = pygame.transform.scale(cherry_img, (tile_size, tile_size))

ranking_tile_size = 30
ghost_cyan_scaled = pygame.transform.scale(pygame.image.load("assets/ghost-cyan.png"), (ranking_tile_size, ranking_tile_size))
ghost_pink_scaled = pygame.transform.scale(pygame.image.load("assets/ghost-pink.png"), (ranking_tile_size, ranking_tile_size))
ghost_orange_scaled = pygame.transform.scale(pygame.image.load("assets/ghost-orange.png"), (ranking_tile_size, ranking_tile_size))

def draw_map(offset_x, offset_y):
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(offset_x + c*tile_size, offset_y + r*tile_size, tile_size, tile_size)
            if preset_map[r][c] == 1:
                pygame.draw.rect(screen, BLUE, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)

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

import heapq

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
        # {'img': ghost_orange, 'pos':[17,16], 'path':[], 'algorithm':'AStar', 'time':None, 'name':'Orange'}
        # {'img': ghost_orange, 'pos':[17,16], 'path':[], 'algorithm':'Dijkstra', 'time':None, 'name':'Orange'}
    ]
    popup_open, ranking, game_finished = False, [], False

time_rect = pygame.Rect(10, 10, 150, 50)
ranking_rect = pygame.Rect(10, 100, 200, 200)
arena_x, arena_y = 250, 10
arena_w, arena_h = cols*tile_size, rows*tile_size
btn_w, btn_h = 150, 40
start_btn = pygame.Rect(arena_x, arena_y+arena_h+10, btn_w, btn_h)
restart_btn = pygame.Rect(arena_x+btn_w+20, arena_y+arena_h+10, btn_w, btn_h)
gen_map_btn = pygame.Rect(arena_x, arena_y+arena_h+btn_h+20, btn_w, btn_h)
gen_cherry_btn = pygame.Rect(arena_x+btn_w+20, arena_y+arena_h+btn_h+20, btn_w, btn_h)

reset_game()
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, time_rect)
    pygame.draw.rect(screen, BLACK, time_rect,2)
    if timer_reset:
        elapsed = 0
    elif start_time:
        elapsed = round((end_time if end_time else time.time()) - start_time, 1)
    else:
        elapsed = 0
    render_text_fit(f"Time: {elapsed}s", time_rect)

    pygame.draw.rect(screen, GRAY, ranking_rect)
    pygame.draw.rect(screen, BLACK, ranking_rect,2)
    title_rect = pygame.Rect(ranking_rect.x, ranking_rect.y, ranking_rect.width, 30)
    render_text_fit("Ranking Sebelumnya:", title_rect)

    for i in range(3):
        row_y = ranking_rect.y + 30 + i*50
        num_rect = pygame.Rect(ranking_rect.x+5, row_y, 20, 40)
        img_rect = pygame.Rect(ranking_rect.x+30, row_y, 40, 40)
        algo_rect = pygame.Rect(ranking_rect.x+75, row_y, 60, 40)
        time_rect_row = pygame.Rect(ranking_rect.x+140, row_y, 50, 40)
        pygame.draw.rect(screen, BLACK, num_rect,1)
        pygame.draw.rect(screen, BLACK, img_rect,1)
        pygame.draw.rect(screen, BLACK, algo_rect,1)
        pygame.draw.rect(screen, BLACK, time_rect_row,1)
        if i < len(previous_ranking):
            render_text_fit(f"{i+1}.", num_rect)
            img = {'Cyan':ghost_cyan_scaled,'Pink':ghost_pink_scaled,'Orange':ghost_orange_scaled}[previous_ranking[i]['name']]
            screen.blit(img, (img_rect.x,img_rect.y))
            render_text_fit(f"{previous_ranking[i]['algorithm']}", algo_rect)
            render_text_fit(f"{previous_ranking[i]['time']}s", time_rect_row)

    draw_map(arena_x, arena_y)
    screen.blit(cherry_img, (arena_x+cherry_pos[0]*tile_size, arena_y+cherry_pos[1]*tile_size))
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
            popup_open, game_started, game_finished, timer_reset = True, False, True, True
            end_time = time.time()

    for g in ghosts:
        screen.blit(g['img'], (arena_x+g['pos'][0]*tile_size, arena_y+g['pos'][1]*tile_size))

    draw_button("Start", start_btn)
    draw_button("Restart", restart_btn)
    draw_button("Generate Map", gen_map_btn)
    draw_button("Generate Cherry", gen_cherry_btn)

    if popup_open:
        popup_rect=pygame.Rect(WIDTH//4,HEIGHT//4,WIDTH//2,HEIGHT//2)
        close_rect=pygame.Rect(popup_rect.right-40, popup_rect.y+10, 30, 30)
        pygame.draw.rect(screen,GRAY,popup_rect)
        pygame.draw.rect(screen,BLACK,popup_rect,2)
        render_text_fit("RANKING", pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 30))
        for idx,g in enumerate(ranking):
            r=pygame.Rect(popup_rect.x+20,popup_rect.y+40+idx*30, popup_rect.width-40,30)
            render_text_fit(f"{idx+1}. {g['name']} ({g['algorithm']}): {g['time']}s",r)
        draw_button("X", close_rect)

    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        elif e.type==pygame.MOUSEBUTTONDOWN:
            if popup_open:
                if close_rect.collidepoint(e.pos):
                    popup_open=False
            else:
                if start_btn.collidepoint(e.pos) and not game_started and not game_finished:
                    game_started,start_time,end_time,timer_reset = True,time.time(),None,False
                    reset_game()
                elif restart_btn.collidepoint(e.pos) and not game_started:
                    reset_game(); game_started=False; game_finished=False
                elif gen_map_btn.collidepoint(e.pos) and not game_started:
                    reset_game(True,True); game_started=False; game_finished=False
                elif gen_cherry_btn.collidepoint(e.pos) and not game_started:
                    reset_game(False,True); game_started=False; game_finished=False

    pygame.display.flip(); clock.tick(10)
