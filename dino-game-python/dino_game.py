import pygame
import random
import sys
import os

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
CACTUS_IMG = pygame.image.load(os.path.join(ASSETS, "cactus.png"))
BG_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSETS, "background.png")), (WIDTH, HEIGHT)
)

dino_rect = None
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
font = pygame.font.SysFont("monospace", 24)


def draw_window():
    WIN.blit(BG_IMG, (0, 0))
    WIN.blit(DINO_FRAMES[frame_index // 10 % 2], dino_rect.topleft)
    for obs in obstacles:
        scaled_cactus = pygame.transform.scale(CACTUS_IMG, (obs.width, obs.height))
        WIN.blit(scaled_cactus, obs.topleft)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    WIN.blit(score_text, (10, 10))
    pygame.display.update()


def main():
    global dino_vel_y, is_jumping, obstacle_timer, score, obstacle_interval, frame_index, obstacle_speed, game_over

    # Reset game state variables
    dino_rect.y = GROUND_Y
    dino_vel_y = 0
    is_jumping = False
    frame_index = 0
    obstacles.clear()
    obstacle_timer = 0
    obstacle_interval = 1500
    obstacle_speed = 8
    score = 0
    game_over = False

    # Стартовый экран
    WIN.blit(BG_IMG, (0, 0))
    title_text = font.render("DINO RUN", True, (0, 0, 0))
    start_text = font.render("Press SPACE to start", True, (0, 0, 0))
    WIN.blit(title_text, (WIDTH // 2 - 60, HEIGHT // 2 - 40))
    WIN.blit(start_text, (WIDTH // 2 - 110, HEIGHT // 2))
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
            return main()

        if elapsed % 8000 < 20 and obstacle_speed < 14:
            obstacle_interval = max(700, obstacle_interval - 50)
            obstacle_speed += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not is_jumping:
                if event.key == pygame.K_SPACE:
                    dino_vel_y = jump_power
                    is_jumping = True

        dino_rect.y += dino_vel_y
        dino_vel_y += gravity
        if dino_rect.y >= GROUND_Y:
            dino_rect.y = GROUND_Y
            dino_vel_y = 0
            is_jumping = False

        # ⏳ Не спавним препятствия первые 2 секунды
        if elapsed > 2000 and now - obstacle_timer > obstacle_interval:
            obstacle_timer = now
            # Добавляем один или два кактуса
            new_cactus = pygame.Rect(WIDTH, GROUND_Y + 10, 34, 54)
            obstacles.append(new_cactus)

            # Если прошло больше 20 сек — шанс на двойной кактус
            if elapsed > 20000 and random.random() < 0.4:
                extra_cactus = pygame.Rect(WIDTH + 40, GROUND_Y + 10, 34, 54)
                obstacles.append(extra_cactus)

        for obs in obstacles[:]:
            obs.x -= obstacle_speed
            if obs.right < 0:
                obstacles.remove(obs)
                score += 1

            if dino_rect.colliderect(obs):
                game_over = True

        draw_window()


if __name__ == "__main__":
    main()
