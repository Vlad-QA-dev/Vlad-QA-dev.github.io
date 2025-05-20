import pygame
import random
import sys
import os

pygame.init()
WIDTH, HEIGHT = 800, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Run")

WHITE = (255, 255, 255)
FPS = 60
clock = pygame.time.Clock()

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
DINO_FRAMES = [
    pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "dino1.png")), (64, 64)),
    pygame.transform.scale(pygame.image.load(os.path.join(ASSETS, "dino2.png")), (64, 64)),
]
CACTUS_IMG = pygame.image.load(os.path.join(ASSETS, "cactus.png"))
BG_IMG = pygame.image.load(os.path.join(ASSETS, "background.png"))

dino_rect = pygame.Rect(50, HEIGHT - 100, 64, 64)
dino_vel_y = 0
gravity = 1
jump_power = -16
is_jumping = False
frame_index = 0

obstacles = []
obstacle_timer = 0
obstacle_interval = 1500
obstacle_speed = 8

score = 0
font = pygame.font.SysFont("monospace", 24)

def draw_window():
    WIN.blit(BG_IMG, (0, 0))
    WIN.blit(DINO_FRAMES[frame_index // 10 % 2], dino_rect.topleft)
    for obs in obstacles:
        WIN.blit(CACTUS_IMG, obs.topleft)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    WIN.blit(score_text, (10, 10))
    pygame.display.update()

def main():
    global dino_vel_y, is_jumping, obstacle_timer, score, obstacle_interval, frame_index, obstacle_speed
    running = True
    start_time = pygame.time.get_ticks()

    while running:
        dt = clock.tick(FPS)
        frame_index += 1
        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed % 5000 < 20 and obstacle_interval > 700:
            obstacle_interval -= 50
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
        if dino_rect.y >= HEIGHT - 90:
            dino_rect.y = HEIGHT - 90
            dino_vel_y = 0
            is_jumping = False

        if now - obstacle_timer > obstacle_interval:
            obstacle_timer = now
            new_cactus = pygame.Rect(WIDTH, HEIGHT - 70, 34, 70)
            obstacles.append(new_cactus)

        for obs in obstacles[:]:
            obs.x -= obstacle_speed
            if obs.right < 0:
                obstacles.remove(obs)
                score += 1

            if dino_rect.colliderect(obs):
                pygame.quit()
                print(f"Game Over! Your score: {score}")
                sys.exit()

        draw_window()

if __name__ == "__main__":
    main()
