import pygame
import random
import sys
import os
import json

pygame.init()
WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Run")

WHITE = (255, 255, 255)
FPS = 60
clock = pygame.time.Clock()

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
DINO_FRAMES = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ASSETS, "dino1.png")), (64, 64)
    ),
    pygame.transform.scale(
        pygame.image.load(os.path.join(ASSETS, "dino2.png")), (64, 64)
    ),
]
# Load original cactus image (not scaled)
CACTUS_IMG = pygame.image.load(os.path.join(ASSETS, "cactus.png"))
# Pre-scaled obstacle sprites to avoid runtime scaling
CACTUS_SCALED = pygame.transform.scale(CACTUS_IMG, (34, 54))
# DINO sliding frames
DINO_SLIDE_FRAMES = [
    pygame.transform.scale(frame, (64, 32)) for frame in DINO_FRAMES
]
# First background image, scaled
BG_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSETS, "background.png")), (WIDTH, HEIGHT)
)
BIRD_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSETS, "bird.png")), (64, 44)
)
# Puddle image
PUDDLE_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSETS, "puddle.png")), (50, 30)
)

GROUND_Y = HEIGHT - 80
dino_rect = pygame.Rect(50, GROUND_Y, 64, 64)
dino_vel_y = 0
gravity = 1
jump_power = -20
is_jumping = False
frame_index = 0

obstacles = []
obstacle_timer = 0
obstacle_interval = 1500
obstacle_speed = 8

game_over = False

score = 0
font = pygame.font.SysFont("arial", 32)

# Leaderboard support
LEADERBOARD_FILE = os.path.join(ASSETS, "leaderboard.json")

# Load or initialize leaderboard
try:
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    leaderboard = []

next_difficulty_score = 50
sliding = False
slide_timer = 0
SLIDE_DURATION = 500  # milliseconds

# Day–Night cycle
DAY_LENGTH = 30000  # milliseconds per phase
is_night = False
last_cycle_switch = 0

def get_player_name():
    name = ""
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 50)
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable():
                    name += event.unicode
        # draw static background behind input
        WIN.blit(BG_IMG, (0, 0))
        # semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))
        WIN.blit(overlay, (0, 0))
        # prompt and input box
        prompt = font.render("Введите ваше имя:", True, (0, 0, 0))
        WIN.blit(prompt, (input_box.x, input_box.y - 50))
        pygame.draw.rect(WIN, (0, 0, 0), input_box, 3, border_radius=8)
        text_surface = font.render(name, True, (0, 0, 0))
        WIN.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.update()
        clock.tick(FPS)
    return name

def draw_window():
    # static background
    WIN.blit(BG_IMG, (0, 0))
    # apply night tint if needed
    if is_night:
        tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        tint.fill((0, 0, 50, 100))  # dark blue overlay
        WIN.blit(tint, (0, 0))
    img = DINO_FRAMES[frame_index // 10 % 2]
    if sliding:
        img = DINO_SLIDE_FRAMES[frame_index // 10 % 2]
    WIN.blit(img, dino_rect.topleft)
    for obs, kind in obstacles:
        if kind == "bird":
            WIN.blit(BIRD_IMG, obs.topleft)
        elif kind == "puddle":
            WIN.blit(PUDDLE_IMG, obs.topleft)
        else:
            WIN.blit(CACTUS_SCALED, obs.topleft)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    WIN.blit(score_text, (10, 10))
    pygame.display.update()


def main():
    global dino_vel_y, is_jumping, obstacle_timer, score, obstacle_interval, frame_index, obstacle_speed, game_over, jump_power, next_difficulty_score, sliding, slide_timer, jump_count, is_night, last_cycle_switch

    # Prompt player for name via game interface
    player_name = get_player_name()

    # Reset game state variables
    dino_rect.y = GROUND_Y
    dino_vel_y = 0
    is_jumping = False
    jump_count = 0
    frame_index = 0
    obstacles.clear()
    obstacle_timer = 0
    obstacle_interval = 2000
    obstacle_speed = 8
    score = 0
    next_difficulty_score = 50
    game_over = False
    jump_power = -20
    sliding = False
    slide_timer = 0
    wave_index = 0
    # For spawn logic
    is_night = False
    last_cycle_switch = pygame.time.get_ticks()

    # Стартовый экран
    WIN.blit(BG_IMG, (0, 0))
    title_text = font.render("DINO RUN", True, (0, 0, 0))
    start_text = font.render("Press SPACE to start", True, (0, 0, 0))
    WIN.blit(title_text, (WIDTH // 2 - 60, HEIGHT // 2 - 40))
    WIN.blit(start_text, (WIDTH // 2 - 110, HEIGHT // 2))
    # Display top 5 leaderboard
    # for idx, entry in enumerate(leaderboard):
    #     lb_text = font.render(f"{idx+1}. {entry['name']} - {entry['score']}", True, (0,0,0))
    #     WIN.blit(lb_text, (WIDTH//2 - 100, HEIGHT// 2 + 40 + idx*30))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    running = True
    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(FPS)
        frame_index += 1
        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if game_over:
            pygame.time.delay(2000)
            # After delay, show leaderboard overlay
            WIN.blit(BG_IMG, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            WIN.blit(overlay, (0, 0))
            title = font.render("Таблица результатов", True, (0, 0, 0))
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            for idx, entry in enumerate(leaderboard):
                lb_text = font.render(f"{idx+1}. {entry['name']} - {entry['score']}", True, (0,0,0))
                WIN.blit(lb_text, (WIDTH//2 - 100, HEIGHT//4 + 50 + idx*40))
            pygame.display.update()
            pygame.time.delay(3000)
            # Update leaderboard
            leaderboard.append({"name": player_name, "score": score})
            leaderboard[:] = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:5]
            with open(LEADERBOARD_FILE, "w") as f:
                json.dump(leaderboard, f)
            return main()

        if elapsed % 8000 < 20 and obstacle_speed < 14:
            obstacle_interval = max(700, obstacle_interval - 50)
            obstacle_speed += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not is_jumping:
                        dino_vel_y = jump_power
                        is_jumping = True
                        jump_count = 1
                    elif jump_count == 1:
                        dino_vel_y = jump_power
                        jump_count = 2
                if event.key in (pygame.K_DOWN, pygame.K_LSHIFT, pygame.K_RSHIFT):
                    if not sliding and not is_jumping:
                        sliding = True
                        slide_timer = pygame.time.get_ticks()
                        # shrink hitbox for slide
                        dino_rect.height = 32
                        dino_rect.y = GROUND_Y + 32

        dino_rect.y += dino_vel_y
        dino_vel_y += gravity
        if dino_rect.y >= GROUND_Y:
            dino_rect.y = GROUND_Y
            dino_vel_y = 0
            is_jumping = False
            jump_count = 0

        if sliding and pygame.time.get_ticks() - slide_timer > SLIDE_DURATION:
            sliding = False
            # restore hitbox
            dino_rect.height = 64
            dino_rect.y = GROUND_Y

        # ⏳ Не спавним препятствия первые 2 секунды
        # Handle day–night transition
        if now - last_cycle_switch > DAY_LENGTH:
            is_night = not is_night
            last_cycle_switch = now

        if elapsed > 2000 and now - obstacle_timer > obstacle_interval:
            # ensure minimum horizontal gap between obstacle waves
            if not obstacles or obstacles[-1][0].x < WIDTH - 200:
                obstacle_timer = now
                # choose obstacle type
                prob = random.random()
                if prob < 0.5:
                    kind = "cactus"
                elif prob < 0.85:
                    kind = "bird"
                else:
                    kind = "puddle"
                # alternate count: 1 or 2 for cactus/bird
                count = 2 if kind in ("cactus", "bird") and wave_index % 3 == 1 else 1
                wave_index += 1
                for i in range(count):
                    x_pos = WIDTH + i * (34 if kind=="cactus" else 60)
                    if kind == "cactus":
                        new_obs = pygame.Rect(x_pos, GROUND_Y + 10, 34, 54)
                    elif kind == "bird":
                        new_obs = pygame.Rect(x_pos, GROUND_Y - 100, 64, 44)
                    else:
                        new_obs = pygame.Rect(WIDTH, GROUND_Y + 50, 50, 30)
                    obstacles.append((new_obs, kind))

        for entry in obstacles[:]:
            obs, kind = entry
            obs.x -= obstacle_speed
            if obs.right < 0:
                obstacles.remove(entry)
                score += 1
                if score >= next_difficulty_score:
                    obstacle_speed += 1
                    obstacle_interval = max(300, obstacle_interval - 50)
                    next_difficulty_score += 50
            elif dino_rect.colliderect(obs):
                if kind == "puddle":
                    obstacle_speed += 4  # make obstacles approach faster after puddle
                    jump_power = -15     # reduce jump height
                    obstacles.remove(entry)
                    slide_timer = pygame.time.get_ticks()  # reset slide timer to avoid overlap
                else:
                    game_over = True

        # Removed background scroll logic for static background

        draw_window()


if __name__ == "__main__":
    main()
