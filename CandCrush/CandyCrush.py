import pygame
import random

pygame.init()

# ---------------- SETTINGS ----------------
SIZE = 8
CELL = 64
WIDTH = HEIGHT = SIZE * CELL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Candy Crush")

clock = pygame.time.Clock()
FPS = 30
BG_COLOR = (200, 200, 200)
GRID_COLOR = (0, 0, 0)

# ---------------- IMAGES ----------------
images = []
for i in range(1, 5):
    img = pygame.image.load(f"assets/bon bon {i}.png")
    images.append(pygame.transform.scale(img, (CELL, CELL)))

# ---------------- BOARD ----------------
board = [[random.randint(0, 3) for _ in range(SIZE)] for _ in range(SIZE)]
selected = None
score = 0

# ---------------- FUNCTIONS ----------------
def draw():
    screen.fill(BG_COLOR)

    for r in range(SIZE):
        for c in range(SIZE):
            x = c * CELL
            y = r * CELL

            # 🔲 KUTUCUK (GRID)
            pygame.draw.rect(
                screen,
                GRID_COLOR,
                (x, y, CELL, CELL),
                1
            )

            # 🍬 BONBON
            screen.blit(
                images[board[r][c]],
                (x + 4, y + 4)
            )

def new_game():
    global board
    board = [[random.randint(0, 3) for _ in range(SIZE)] for _ in range(SIZE)]

def swap(a, b):
    board[a[0]][a[1]], board[b[0]][b[1]] = board[b[0]][b[1]], board[a[0]][a[1]]

def find_matches():
    matches = set()

    for r in range(SIZE):
        for c in range(SIZE - 2):
            if board[r][c] == board[r][c+1] == board[r][c+2]:
                matches.update({(r,c), (r,c+1), (r,c+2)})

    for c in range(SIZE):
        for r in range(SIZE - 2):
            if board[r][c] == board[r+1][c] == board[r+2][c]:
                matches.update({(r,c), (r+1,c), (r+2,c)})

    return matches

def remove(matches):
    global score
    for r,c in matches:
        board[r][c] = -1
    score += len(matches)

def drop():
    for c in range(SIZE):
        col = [board[r][c] for r in range(SIZE) if board[r][c] != -1]
        while len(col) < SIZE:
            col.insert(0, random.randint(0, 3))
        for r in range(SIZE):
            board[r][c] = col[r]

# ---------------- GAME LOOP ----------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:

            # ESC → ÇIKIŞ
            if event.key == pygame.K_ESCAPE:
                running = False

            # R → YENİ OYUN
            if event.key == pygame.K_r:
                new_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            r, c = y // CELL, x // CELL

            if selected:
                swap(selected, (r,c))
                m = find_matches()
                if m:
                    remove(m)
                    drop()
                else:
                    swap(selected, (r,c))
                selected = None
            else:
                selected = (r,c)

    draw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
