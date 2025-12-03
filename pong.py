import pygame
import random
import sys

pygame.init()

# Window
WIDTH = 900
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GRAY = (230, 230, 230)

# Paddle
paddle_width = 20
paddle_height = 120
paddle_x = 30
paddle_y = HEIGHT // 2 - paddle_height // 2
paddle_speed = 7

# Ball
ball_size = 20
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 5
ball_speed_y = 5

score = 0
game_over = False
paused = False

font_score = pygame.font.SysFont("arial", 32, bold=True)
font_big = pygame.font.SysFont("arial", 50, bold=True)
button_font = pygame.font.SysFont("arial", 22, bold=True)

# PAUSE button (moved to the right)
pause_button = pygame.Rect(WIDTH - 300, 20, 100, 40)

def draw_buttons():
    pygame.draw.rect(screen, GRAY, pause_button, border_radius=7)
    pygame.draw.rect(screen, BLACK, pause_button, 2, border_radius=7)
    text_p = button_font.render("PAUSE", True, RED)
    screen.blit(text_p, (pause_button.x + 20, pause_button.y + 8))


def reset_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, score, game_over
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_speed_x = 5
    ball_speed_y = 5
    score = 0
    game_over = False


# ---------------- GAME LOOP ----------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        # Mouse support for PAUSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pause_button.collidepoint(event.pos):
                paused = not paused

        # Keyboard support
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Pause
                paused = not paused

            if event.key == pygame.K_r:  # Reset after game over
                if game_over:
                    reset_game()

    keys = pygame.key.get_pressed()

    # Paddle movement
    if not game_over and not paused:
        if keys[pygame.K_UP] and paddle_y > 0:
            paddle_y -= paddle_speed
        if keys[pygame.K_DOWN] and paddle_y < HEIGHT - paddle_height:
            paddle_y += paddle_speed

        # Move ball
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Top/bottom collision
        if ball_y <= 0 or ball_y >= HEIGHT - ball_size:
            ball_speed_y *= -1

        # Right wall = bounce
        if ball_x >= WIDTH - ball_size:
            ball_speed_x *= -1

        # Paddle collision
        paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
        ball_rect = pygame.Rect(ball_x, ball_y, ball_size, ball_size)

        if ball_rect.colliderect(paddle_rect):
            ball_speed_x *= -1

            # random Y change
            ball_speed_y += random.randint(-3, 3)

            # increase speed
            if ball_speed_x > 0:
                ball_speed_x += 1
            else:
                ball_speed_x -= 1

            score += 1

        # MISS → GAME OVER
        if ball_x < -ball_size:
            game_over = True

    # DRAW
    screen.fill(BLACK)

    draw_buttons()

    # Paddle
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Ball
    pygame.draw.rect(screen, WHITE, (ball_x, ball_y, ball_size, ball_size))

    # Score
    score_text = font_score.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 20))

    # GAME OVER
    if game_over:
        over_text = font_big.render("GAME OVER", True, RED)
        screen.blit(over_text, (WIDTH // 2 - 160, HEIGHT // 2 - 50))

        retry_text = font_score.render("Press R to restart", True, WHITE)
        screen.blit(retry_text, (WIDTH // 2 - 150, HEIGHT // 2 + 20))

    # PAUSED
    if paused and not game_over:
        pause_text = font_big.render("PAUSED", True, RED)
        screen.blit(pause_text, (WIDTH // 2 - 110, HEIGHT // 2 - 40))

    pygame.display.flip()
    clock.tick(60)
