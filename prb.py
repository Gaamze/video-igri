import pygame
import sys
from pygame.locals import *
import time

# --- CONFIG ---
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 640
GRID_COLS = 8
GRID_ROWS = 6
CELL_SIZE = 64
STATUS_BAR = 70      # висина на статусното поле горе
MESSAGE_AREA = 70    # висина над мрежата за поголеми пораки
MARGIN = 30          # маргина околу мрежата
FPS = 60
REVEAL_SECONDS = 4.0  # колку долго се покажуваат стапиците при старт
MSG_DISPLAY_TIME = 1500  # ms: колку долго кратките пораки во статус бар се прикажуваат

# Colors
WHITE    = (255,255,255)
BLACK    = (0,0,0)
DARKGRAY = (30,30,30)
GRAY     = (180,180,180)
GREEN    = (0,180,0)
RED      = (200,40,40)
BLUE     = (50,120,220)
YELLOW   = (230,200,0)

# --- LEVEL (8x6) ---
# S = start, E = exit, T = trap, . = empty
LEVEL = [
    "........",
    ".T..T..E",
    "....T...",
    ".TT.....",
    ".S......",
    "........"
]

def parse_level():
    traps = set()
    start = exitp = None
    for r,row in enumerate(LEVEL):
        for c,ch in enumerate(row):
            if ch == "S": start = (c,r)
            if ch == "E": exitp = (c,r)
            if ch == "T": traps.add((c,r))
    return start, exitp, traps

# compute top-left origin of grid so grid is centered with margins
def grid_origin():
    grid_w = GRID_COLS * CELL_SIZE
    grid_h = GRID_ROWS * CELL_SIZE
    origin_x = (WINDOW_WIDTH - grid_w) // 2
    # reserve status bar at very top, then message area, then grid
    origin_y = STATUS_BAR + MESSAGE_AREA + (WINDOW_HEIGHT - STATUS_BAR - MESSAGE_AREA - grid_h)//2
    return origin_x, origin_y

# draw everything: status bar, message area, grid, cells, player
def draw_all(screen, fonts, state):
    screen.fill(DARKGRAY)

    # status bar (top)
    pygame.draw.rect(screen, BLACK, (0,0, WINDOW_WIDTH, STATUS_BAR))
    status_text = f"Животи: {state['lives']}    Потези: {state['moves']}"
    status_surf = fonts['status'].render(status_text, True, WHITE)
    screen.blit(status_surf, (20, (STATUS_BAR - status_surf.get_height())//2))

    # short status message (shows for a limited time)
    if state['status_msg'] and pygame.time.get_ticks() - state['status_msg_time'] < MSG_DISPLAY_TIME:
        msg_surf = fonts['small'].render(state['status_msg'], True, WHITE)
        screen.blit(msg_surf, (300, (STATUS_BAR - msg_surf.get_height())//2))

    # message area (above grid, bigger text centered)
    pygame.draw.rect(screen, DARKGRAY, (0, STATUS_BAR, WINDOW_WIDTH, MESSAGE_AREA))
    if state['big_msg']:
        big_surf = fonts['big'].render(state['big_msg'], True, WHITE)
        big_rect = big_surf.get_rect(center=(WINDOW_WIDTH//2, STATUS_BAR + MESSAGE_AREA//2))
        screen.blit(big_surf, big_rect)

    # grid background
    gx, gy = grid_origin()
    grid_w = GRID_COLS * CELL_SIZE
    grid_h = GRID_ROWS * CELL_SIZE
    pygame.draw.rect(screen, BLACK, (gx - 4, gy - 4, grid_w + 8, grid_h + 8))
    # draw cells
    start, exitp, traps = parse_level()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell_rect = pygame.Rect(gx + c*CELL_SIZE, gy + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, cell_rect)
            pygame.draw.rect(screen, BLACK, cell_rect, 2)

            # draw exit
            if (c,r) == exitp:
                inner = cell_rect.inflate(-8,-8)
                pygame.draw.rect(screen, BLUE, inner)

            # if in reveal phase, show traps
            if state['reveal'] and (c,r) in state['traps']:
                inner = cell_rect.inflate(-16,-16)
                pygame.draw.rect(screen, RED, inner)

    # draw player (simple circle)
    px, py = state['player']
    prect = pygame.Rect(gx + px*CELL_SIZE, gy + py*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    center = prect.center
    pygame.draw.circle(screen, GREEN, center, CELL_SIZE//3)

    pygame.display.flip()

# helper: move player if valid; returns (moved, reason_message or None)
def try_move(state, dx, dy):
    if state['game_over'] or state['won']:
        return False, None
    px, py = state['player']
    nx, ny = px + dx, py + dy
    if not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
        # invalid move
        return False, "Не можете да се движите таму."
    # valid
    state['player'] = [nx, ny]
    state['moves'] += 1
    return True, None

def reset_state():
    start, exitp, traps = parse_level()
    s = {}
    s['start'] = start
    s['exit'] = exitp
    s['traps'] = set(traps)
    s['player'] = [start[0], start[1]]
    s['lives'] = 3
    s['moves'] = 0
    s['status_msg'] = ""
    s['status_msg_time'] = 0
    s['big_msg'] = ""
    s['reveal'] = True
    s['reveal_start'] = pygame.time.get_ticks()
    s['game_over'] = False
    s['won'] = False
    return s

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Лавиринт со стапици")
    clock = pygame.time.Clock()

    # fonts
    fonts = {}
    fonts['status'] = pygame.font.SysFont(None, 28)
    fonts['small'] = pygame.font.SysFont(None, 24)
    fonts['big'] = pygame.font.SysFont(None, 42)

    state = reset_state()

    # ensure there are >=5 traps (spec). If fewer, we can add random ones not on start/exit.
    if len(state['traps']) < 5:
        import random
        all_cells = [(c,r) for r in range(GRID_ROWS) for c in range(GRID_COLS)]
        forb = {state['start'], state['exit']}
        candidates = [p for p in all_cells if p not in forb and p not in state['traps']]
        random.shuffle(candidates)
        while len(state['traps']) < 5 and candidates:
            state['traps'].add(candidates.pop())

    # initial draw
    draw_all(screen, fonts, state)

    # Run loop
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == K_r:
                    # restart
                    state = reset_state()
                    draw_all(screen, fonts, state)
                    continue

                if state['game_over'] or state['won']:
                    # accept only R and ESC in this state
                    continue

                moved = False
                reason = None
                if event.key == K_LEFT:
                    moved, reason = try_move(state, -1, 0)
                elif event.key == K_RIGHT:
                    moved, reason = try_move(state, 1, 0)
                elif event.key == K_UP:
                    moved, reason = try_move(state, 0, -1)
                elif event.key == K_DOWN:
                    moved, reason = try_move(state, 0, 1)

                if not moved and reason:
                    state['status_msg'] = reason
                    state['status_msg_time'] = pygame.time.get_ticks()
                elif moved:
                    # after a move, check trap / exit
                    pos = tuple(state['player'])
                    if pos in state['traps']:
                        state['lives'] -= 1
                        state['status_msg'] = f"Удривте во стапица! Преостанати животи: {state['lives']}"
                        state['status_msg_time'] = pygame.time.get_ticks()
                        # reset player to start
                        state['player'] = [state['start'][0], state['start'][1]]
                        # if no lives -> game over
                        if state['lives'] <= 0:
                            state['big_msg'] = "Играта заврши"
                            state['game_over'] = True
                    elif pos == state['exit']:
                        state['big_msg'] = "Успешно го завршивте нивото!"
                        state['won'] = True

        # update reveal state
        if state['reveal'] and (pygame.time.get_ticks() - state['reveal_start'])/1000.0 >= REVEAL_SECONDS:
            state['reveal'] = False
            # show small "Go!" message shortly
            state['status_msg'] = "Тргни!"
            state['status_msg_time'] = pygame.time.get_ticks()

        draw_all(screen, fonts, state)

if __name__ == "__main__":
    main()
