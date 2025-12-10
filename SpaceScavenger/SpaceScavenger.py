import random, sys, pygame
from pygame.locals import *

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Object constants
INITIAL_SIZE = 70
INITIAL_SPEED = 3
DAMAGE_INCREMENT = 5


def reset_game():
    # initialize game variables
    return {
        "spaceship": {"x": 50, "y": SCREEN_HEIGHT // 2 - 60},
        "life_points": 100,
        "crystal_points": 0,
        "asteroids": [],
        "crystals": [],
        "speed": INITIAL_SPEED,
        "damage": 5,
        "game_over": False,
        "win": False,
        "timer": 0,
    }


def move_spaceship(keys):
    if keys[pygame.K_UP] and GAME["spaceship"]["y"] > 10:
        GAME["spaceship"]["y"] -= GAME["speed"]
    if keys[pygame.K_DOWN] and GAME["spaceship"]["y"] < SCREEN_HEIGHT - 150:
        GAME["spaceship"]["y"] += GAME["speed"]


def create_objects():
    # create new asteroids and crystals
    if len(GAME["asteroids"]) < 1 or random.randint(0, 99) <= 1:
        GAME["asteroids"].append({"x": SCREEN_WIDTH, "y": random.randint(0, SCREEN_HEIGHT - 150 - GAME["damage"])})
    if len(GAME["crystals"]) < 1 or random.randint(0, 99) <= 1:
        GAME["crystals"].append({"x": SCREEN_WIDTH, "y": random.randint(0, SCREEN_HEIGHT - 150)})


def move_objects():
    for asteroid in GAME["asteroids"]:
        asteroid["x"] -= GAME["speed"]
    for crystal in GAME["crystals"]:
        crystal["x"] -= GAME["speed"]


def remove_offscreen_objects():
    GAME["asteroids"] = [a for a in GAME["asteroids"] if a["x"] > -150]
    GAME["crystals"] = [c for c in GAME["crystals"] if c["x"] > -150]


def detect_collisions():
    # the dimensions are a bit off, to take into account the padding of the image objects
    spaceship_rect = pygame.Rect(GAME["spaceship"]["x"], GAME["spaceship"]["y"], INITIAL_SIZE, INITIAL_SIZE - 15)

    for asteroid in GAME["asteroids"]:
        asteroid_rect = pygame.Rect(asteroid["x"], asteroid["y"] + 25, INITIAL_SIZE + 2 * GAME["damage"], INITIAL_SIZE + 2 * GAME["damage"] - 45)
        if spaceship_rect.colliderect(asteroid_rect) and not GAME["game_over"]:
            CLASH_SOUND.play()
            GAME["life_points"] -= GAME["damage"]
            if GAME["life_points"] < 0:
                GAME["life_points"] = 0
            GAME["asteroids"].remove(asteroid)

    for crystal in GAME["crystals"]:
        crystal_rect = pygame.Rect(crystal["x"] + 5, crystal["y"] + 20, INITIAL_SIZE - 15, INITIAL_SIZE - 35)
        if spaceship_rect.colliderect(crystal_rect) and not GAME["game_over"]:
            # BEEP_SOUND.play()
            GAME["crystal_points"] += 5
            if GAME["crystal_points"] > 100:
                GAME["crystal_points"] = 100
            GAME["crystals"].remove(crystal)


def increase_difficulty():
    GAME["speed"] += 1
    GAME["damage"] += DAMAGE_INCREMENT
    GAME["timer"] = 0


def check_game_over():
    # if both conditions (win/lose) are true, let the player win
    if GAME["life_points"] <= 0:
        GAME["game_over"] = True
        GAME["win"] = False
    if GAME["crystal_points"] >= 100:
        GAME["game_over"] = True
        GAME["win"] = True


def draw_objects():
    # draw spaceship
    DISPLAYSURF.blit(SPACESHIP_IMG, (GAME["spaceship"]["x"], GAME["spaceship"]["y"]))

    # draw asteroids
    for asteroid in GAME["asteroids"]:
        scaled_asteroid = pygame.transform.scale(ASTEROID_IMG, (INITIAL_SIZE + 2 * GAME["damage"], INITIAL_SIZE + 2 * GAME["damage"]))
        DISPLAYSURF.blit(scaled_asteroid, (asteroid["x"], asteroid["y"]))
        font = pygame.font.Font(None, 24)
        damage_text = font.render(f"- {GAME['damage']}", True, WHITE)
        DISPLAYSURF.blit(damage_text, (asteroid["x"] + 75 + 2 * GAME["damage"], asteroid["y"] + 30 + GAME["damage"]))

    # draw crystals
    for crystal in GAME["crystals"]:
        DISPLAYSURF.blit(CRYSTAL_IMG, (crystal["x"], crystal["y"]))
        font = pygame.font.Font(None, 24)
        gain_text = font.render(f"+ 5", True, WHITE)
        DISPLAYSURF.blit(gain_text, (crystal["x"] + 65, crystal["y"] + 30))


def draw_progress_bars():
    # DISPLAYSURF.blit(HEART_ICON, (12, SCREEN_HEIGHT - 80))
    DISPLAYSURF.blit(CRYSTAL_ICON, (5, SCREEN_HEIGHT - 50))

    pygame.draw.rect(DISPLAYSURF, RED, (50, SCREEN_HEIGHT - 75, GAME["life_points"] * (SCREEN_WIDTH - 100) / 100, 20))
    pygame.draw.rect(DISPLAYSURF, YELLOW, (50, SCREEN_HEIGHT - 35, GAME["crystal_points"] * (SCREEN_WIDTH - 100) / 100, 20))
    pygame.draw.rect(DISPLAYSURF, WHITE, (50, SCREEN_HEIGHT - 75, SCREEN_WIDTH - 100, 20), 2)
    pygame.draw.rect(DISPLAYSURF, WHITE, (50, SCREEN_HEIGHT - 35, SCREEN_WIDTH - 100, 20), 2)

    font = pygame.font.Font(None, 24)
    life_text = font.render(f"{GAME['life_points']}", True, WHITE)
    crystals_text = font.render(f"{GAME['crystal_points']}", True, WHITE)
    DISPLAYSURF.blit(life_text, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 73))
    DISPLAYSURF.blit(crystals_text, (SCREEN_WIDTH - 40, SCREEN_HEIGHT - 33))


def display_game_over_message():
    font = pygame.font.Font(None, 74)
    message = "You Won!" if GAME["win"] else "You Lost!"
    text = font.render(message, True, WHITE)
    DISPLAYSURF.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height()))
    restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, WHITE)
    DISPLAYSURF.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))


def main():
    global DISPLAYSURF, FPSCLOCK, GAME
    global SPACESHIP_IMG, ASTEROID_IMG, CRYSTAL_IMG, CRYSTAL_ICON, HEART_ICON, BACKGROUND_IMG
    global BACKGROUND_MUSIC, CLASH_SOUND, BEEP_SOUND

    pygame.init()

    DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Scavenger")

    # image files
    SPACESHIP_IMG = pygame.image.load("assets/images/spaceship.png")
    ASTEROID_IMG = pygame.image.load("assets/images/asteroid.png")
    CRYSTAL_IMG = pygame.image.load("assets/images/energy_crystal.png")
    # HEART_ICON = pygame.image.load("assets/images/heart-icon.png")
    # BACKGROUND_IMG = pygame.image.load("assets/images/background_image.bmp")

    pygame.display.set_icon(SPACESHIP_IMG)

    SPACESHIP_IMG = pygame.transform.scale(SPACESHIP_IMG, (INITIAL_SIZE, INITIAL_SIZE))
    ASTEROID_IMG = pygame.transform.rotate(ASTEROID_IMG, -45)
    ASTEROID_IMG = pygame.transform.scale(ASTEROID_IMG, (INITIAL_SIZE, INITIAL_SIZE))
    CRYSTAL_IMG = pygame.transform.scale(CRYSTAL_IMG, (INITIAL_SIZE, INITIAL_SIZE))
    CRYSTAL_ICON = pygame.transform.scale(CRYSTAL_IMG, (45, 45))
    # HEART_ICON = pygame.transform.scale(HEART_ICON, (30, 30))
    # BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT - 90))

    # audio files
    BACKGROUND_MUSIC = "assets/sounds/background_music.wav"
    CLASH_SOUND = pygame.mixer.Sound("assets/sounds/clash_sound.wav")
    # BEEP_SOUND = pygame.mixer.Sound("assets/sounds/space-scavenger_assets_sounds_beep.ogg")

    pygame.mixer.music.load(BACKGROUND_MUSIC)

    GAME = reset_game()

    # start background music
    pygame.mixer.music.play(-1)

    FPSCLOCK = pygame.time.Clock()

    while True:  # main game loop
        DISPLAYSURF.fill(BLACK)
        # DISPLAYSURF.blit(BACKGROUND_IMG, (0, 0))
        GAME["timer"] += FPSCLOCK.get_time()

        check_for_quit()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if GAME["game_over"] and event.key == pygame.K_r:
                    GAME = reset_game()

        if not GAME["game_over"]:
            keys = pygame.key.get_pressed()
            move_spaceship(keys)

        if not GAME["game_over"]:
            create_objects()

        move_objects()
        remove_offscreen_objects()

        if not GAME["game_over"]:
            detect_collisions()

        # increase speed and damage every 10 seconds
        if GAME["timer"] >= 10000:
            increase_difficulty()

        check_game_over()

        draw_objects()

        draw_progress_bars()

        if GAME["game_over"]:
            display_game_over_message()

        pygame.display.flip()
        FPSCLOCK.tick(60)


def terminate():
    pygame.quit()
    sys.exit()


def check_for_quit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)


if __name__ == '__main__':
    main()