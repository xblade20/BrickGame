import pygame
import random
import os
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker - Level Up Edition")

font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 60)
menu_font = pygame.font.SysFont("Arial", 36)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (150, 0, 200)
CYAN = (0, 255, 255)

sound_enabled = True
def play_sound(s):
    if sound_enabled:
        s.play()

bounce_sound = pygame.mixer.Sound("bounce.wav")
brick_sound = pygame.mixer.Sound("brick.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")
lose_life_sound = pygame.mixer.Sound("lose_life.wav")

paddle_width, paddle_height = 100, 10
ball_radius = 8

NORMAL = 1
DOUBLE = 2
TRIPLE = 3
UNBREAKABLE = -1

score = 0
lives = 3
level = 1
highscore = 0
paused = False
game_over = False
started = False
main_menu = True

paddle = pygame.Rect(WIDTH // 2 - paddle_width // 2, HEIGHT - 40, paddle_width, paddle_height)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, ball_radius * 2, ball_radius * 2)
ball_dx, ball_dy = 4, -4

powerups = []
POWERUP_TYPES = ["EXTEND_PADDLE", "SPEED_UP"]

# Load high score
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0

def get_brick_pattern(level):
    pattern = []
    rows = 5 + level
    cols = 10
    for row in range(rows):
        line = []
        for col in range(cols):
            if level >= 5 and (row + col) % 2 == 0:
                line.append(True)
            elif level >= 3 and row % 2 == 0:
                line.append(True)
            elif level >= 2:
                line.append(col % 2 == 0)
            else:
                line.append(True)
        pattern.append(line)
    return pattern

def generate_bricks(level):
    bricks = []
    pattern = get_brick_pattern(level)
    brick_width = WIDTH // 10
    brick_height = 30
    for row_idx, row in enumerate(pattern):
        for col_idx, active in enumerate(row):
            if not active:
                continue
            x = col_idx * brick_width + 1
            y = row_idx * brick_height + 1
            rect = pygame.Rect(x, y, brick_width - 2, brick_height - 2)

            r = random.random()
            if level <= 2:
                if r < 0.8:
                    btype, hits = NORMAL, 1
                elif r < 0.95:
                    btype, hits = DOUBLE, 2
                else:
                    btype, hits = UNBREAKABLE, -1
            elif level <= 4:
                if r < 0.5:
                    btype, hits = NORMAL, 1
                elif r < 0.8:
                    btype, hits = DOUBLE, 2
                elif r < 0.95:
                    btype, hits = TRIPLE, 3
                else:
                    btype, hits = UNBREAKABLE, -1
            else:
                if r < 0.3:
                    btype, hits = NORMAL, 1
                elif r < 0.6:
                    btype, hits = DOUBLE, 2
                elif r < 0.85:
                    btype, hits = TRIPLE, 3
                else:
                    btype, hits = UNBREAKABLE, -1

            bricks.append([rect, btype, hits])
    return bricks

bricks = generate_bricks(level)

def reset_ball_and_paddle():
    global ball_dx, ball_dy
    paddle.width = paddle_width
    ball.x, ball.y = WIDTH // 2, HEIGHT // 2
    ball_dx = 4 + (level - 1) * 0.5
    ball_dy = -4 - (level - 1) * 0.5
    paddle.x = WIDTH // 2 - paddle.width // 2

def draw_text_center(text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)

def draw_menu_button(text, y, hover):
    color = ORANGE if hover else GRAY
    pygame.draw.rect(screen, color, (WIDTH // 2 - 100, y, 200, 50))
    label = menu_font.render(text, True, WHITE)
    screen.blit(label, (WIDTH // 2 - label.get_width() // 2, y + 10))

def draw_powerup(pwr):
    rect = pwr["rect"]
    if pwr["type"] == "EXTEND_PADDLE":
        pygame.draw.rect(screen, YELLOW, rect)
    elif pwr["type"] == "SPEED_UP":
        points = [(rect.centerx, rect.top), (rect.right, rect.bottom), (rect.left, rect.bottom)]
        pygame.draw.polygon(screen, RED, points)

clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                sound_enabled = not sound_enabled
            if started and not game_over:
                if event.key == pygame.K_p:
                    paused = not paused
            if game_over and event.key == pygame.K_RETURN:
                score, lives, level = 0, 3, 1
                bricks = generate_bricks(level)
                reset_ball_and_paddle()
                powerups.clear()
                game_over = False
                started = True

    if main_menu:
        draw_text_center("BRICK BREAKER", big_font, WHITE, 120)
        hover_start = WIDTH // 2 - 100 < mouse[0] < WIDTH // 2 + 100 and 250 < mouse[1] < 300
        hover_quit = WIDTH // 2 - 100 < mouse[0] < WIDTH // 2 + 100 and 320 < mouse[1] < 370
        draw_menu_button("Start", 250, hover_start)
        draw_menu_button("Quit", 320, hover_quit)
        if hover_start and click[0]:
            started, main_menu = True, False
        elif hover_quit and click[0]:
            running = False

    elif started and not paused and not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-7, 0)
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.move_ip(7, 0)

        ball.x += ball_dx
        ball.y += ball_dy

        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx *= -1
            play_sound(bounce_sound)
        if ball.top <= 0:
            ball_dy *= -1
            play_sound(bounce_sound)
        if ball.bottom >= HEIGHT:
            lives -= 1
            play_sound(lose_life_sound)
            if lives <= 0:
                game_over = True
                if score > highscore:
                    highscore = score
                    with open("highscore.txt", "w") as f:
                        f.write(str(highscore))
            else:
                reset_ball_and_paddle()

        if ball.colliderect(paddle):
            ball_dy *= -1
            play_sound(bounce_sound)

        for brick in bricks[:]:
            rect, btype, hits = brick
            if ball.colliderect(rect):
                if btype != UNBREAKABLE:
                    brick[2] -= 1
                    if brick[2] <= 0:
                        bricks.remove(brick)
                        score += 10
                        play_sound(brick_sound)
                        if random.random() < 0.2:
                            ptype = random.choice(POWERUP_TYPES)
                            powerups.append({"rect": pygame.Rect(ball.centerx, ball.centery, 20, 20), "type": ptype})
                else:
                    play_sound(bounce_sound)
                ball_dy *= -1
                break

        for powerup in powerups[:]:
            powerup["rect"].y += 3
            if powerup["rect"].colliderect(paddle):
                if powerup["type"] == "EXTEND_PADDLE":
                    paddle.width = min(paddle.width + 40, WIDTH)
                elif powerup["type"] == "SPEED_UP":
                    ball_dx *= 1.3
                    ball_dy *= 1.3
                powerups.remove(powerup)
                play_sound(powerup_sound)
            elif powerup["rect"].top > HEIGHT:
                powerups.remove(powerup)

        for rect, btype, hits in bricks:
            if btype == UNBREAKABLE:
                color = GRAY
            elif btype == TRIPLE:
                color = RED
            elif btype == DOUBLE:
                color = ORANGE
            else:
                color = GREEN
            pygame.draw.rect(screen, color, rect)

        pygame.draw.rect(screen, BLUE, paddle)
        pygame.draw.ellipse(screen, WHITE, ball)

        for powerup in powerups:
            draw_powerup(powerup)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, HEIGHT - 30))
        screen.blit(font.render(f"Lives: {lives}", True, WHITE), (WIDTH - 120, HEIGHT - 30))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH // 2 - 40, HEIGHT - 30))
        screen.blit(font.render(f"High Score: {highscore}", True, WHITE), (WIDTH - 200, 10))
        screen.blit(font.render(f"Sound: {'ON' if sound_enabled else 'OFF'}", True, WHITE), (10, 10))

        if not any(b[1] != UNBREAKABLE for b in bricks):
            level += 1
            bricks = generate_bricks(level)
            reset_ball_and_paddle()

    elif paused:
        draw_text_center("PAUSED", big_font, WHITE, HEIGHT // 2)

    elif game_over:
        draw_text_center("GAME OVER", big_font, WHITE, HEIGHT // 2 - 60)
        draw_text_center(f"Score: {score}  |  High Score: {highscore}", font, WHITE, HEIGHT // 2)
        draw_text_center("Press ENTER to Restart", font, WHITE, HEIGHT // 2 + 40)

    pygame.display.flip()

pygame.quit()
