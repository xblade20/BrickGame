import pygame
import random
import sys
import os

# Utility for PyInstaller resource pathing
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Brick Breaker")
clock = pygame.time.Clock()
font = pygame.font.SysFont("comicsans", 30)

# Colors
WHITE, RED, GREEN, BLUE, BLACK, YELLOW, PURPLE, CYAN = (255,255,255), (255,0,0), (0,255,0), (0,0,255), (0,0,0), (255,255,0), (160,32,240), (0,255,255)

# Load Sounds
bounce_sound = pygame.mixer.Sound(resource_path("bounce.wav"))
brick_sound = pygame.mixer.Sound(resource_path("brick.wav"))
powerup_sound = pygame.mixer.Sound(resource_path("powerup.wav"))
lose_life_sound = pygame.mixer.Sound(resource_path("lose_life.wav"))

# Game variables
paddle = pygame.Rect(350, 550, 100, 10)
ball = pygame.Rect(395, 300, 10, 10)
ball_dx, ball_dy = 5, -5
lives = 3
level = 1
score = 0
bricks = []
powerups = []
sound_on = True
paused = False
game_started = False

# Create brick pattern
def create_bricks(level):
    rows = min(6 + level, 10)
    cols = 10
    bricks.clear()
    for row in range(rows):
        for col in range(cols):
            x, y = col * 80, row * 30 + 50
            r = random.random()
            if r < 0.05:
                bricks.append({'rect': pygame.Rect(x+5, y, 70, 20), 'hits': -1})  # unbreakable
            elif r < 0.15 + level * 0.02:
                bricks.append({'rect': pygame.Rect(x+5, y, 70, 20), 'hits': 3})  # multi-hit
            else:
                bricks.append({'rect': pygame.Rect(x+5, y, 70, 20), 'hits': 1})  # normal

# Power-up object
def spawn_powerup(x, y):
    kind = random.choice(["expand", "shrink", "life", "slow"])
    powerups.append({'rect': pygame.Rect(x, y, 20, 20), 'kind': kind})

# Draw powerups
def draw_powerups():
    for pu in powerups:
        if pu['kind'] == "expand":
            pygame.draw.rect(screen, GREEN, pu['rect'], border_radius=5)
        elif pu['kind'] == "shrink":
            pygame.draw.ellipse(screen, RED, pu['rect'])
        elif pu['kind'] == "life":
            pygame.draw.polygon(screen, YELLOW, [(pu['rect'].centerx, pu['rect'].top), (pu['rect'].left, pu['rect'].bottom), (pu['rect'].right, pu['rect'].bottom)])
        elif pu['kind'] == "slow":
            pygame.draw.rect(screen, CYAN, pu['rect'])

# Draw bricks
def draw_bricks():
    for b in bricks:
        if b['hits'] == -1:
            pygame.draw.rect(screen, BLACK, b['rect'])
        elif b['hits'] == 3:
            pygame.draw.rect(screen, PURPLE, b['rect'])
        elif b['hits'] == 2:
            pygame.draw.rect(screen, BLUE, b['rect'])
        else:
            pygame.draw.rect(screen, RED, b['rect'])

# Collision fix: bounce direction
def handle_collision(ball, rect):
    overlap_left = ball.right - rect.left
    overlap_right = rect.right - ball.left
    overlap_top = ball.bottom - rect.top
    overlap_bottom = rect.bottom - ball.top
    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

    if min_overlap == overlap_left:
        ball.right = rect.left
        return -abs(ball_dx), ball_dy
    elif min_overlap == overlap_right:
        ball.left = rect.right
        return abs(ball_dx), ball_dy
    elif min_overlap == overlap_top:
        ball.bottom = rect.top
        return ball_dx, -abs(ball_dy)
    elif min_overlap == overlap_bottom:
        ball.top = rect.bottom
        return ball_dx, abs(ball_dy)
    return ball_dx, ball_dy

# Draw multiple lines of text
def draw_text_lines(lines, start_y):
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, BLACK)
        screen.blit(text_surface, (200, start_y + i * 30))

# Main Game Loop
create_bricks(level)
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_started:
                game_started = True
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_m:
                sound_on = not sound_on

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-7, 0)
    if keys[pygame.K_RIGHT] and paddle.right < 800:
        paddle.move_ip(7, 0)

    if not game_started:
        title = font.render("Press any key to Start", True, BLACK)
        screen.blit(title, (270, 200))
        controls = [
            "Controls:",
            "← / → : Move Paddle",
            "P : Pause / Resume",
            "M : Toggle Sound"
        ]
        draw_text_lines(controls, 250)
    elif paused:
        pause_text = font.render("Paused - Press P to Resume", True, BLACK)
        screen.blit(pause_text, (250, 250))
    else:
        # Move ball
        ball.move_ip(ball_dx, ball_dy)

        # Wall collision
        if ball.left <= 0 or ball.right >= 800:
            ball_dx *= -1
            if sound_on: bounce_sound.play()
        if ball.top <= 0:
            ball.top = 0
            ball_dy = abs(ball_dy)
            if sound_on: bounce_sound.play()

        # Paddle collision
        if ball.colliderect(paddle) and ball_dy > 0:
            ball.bottom = paddle.top
            ball_dy = -abs(ball_dy)
            if sound_on: bounce_sound.play()

        # Brick collision
        hit_index = None
        for i, b in enumerate(bricks):
            if ball.colliderect(b['rect']):
                ball_dx, ball_dy = handle_collision(ball, b['rect'])
                if b['hits'] > 0:
                    b['hits'] -= 1
                    if b['hits'] == 0:
                        if random.random() < 0.2:
                            spawn_powerup(b['rect'].centerx, b['rect'].centery)
                        bricks.pop(i)
                        score += 10
                if sound_on: brick_sound.play()
                break

        # Move powerups
        for pu in powerups[:]:
            pu['rect'].move_ip(0, 3)
            if pu['rect'].colliderect(paddle):
                if pu['kind'] == "expand":
                    paddle.width = min(200, paddle.width + 20)
                elif pu['kind'] == "shrink":
                    paddle.width = max(60, paddle.width - 20)
                elif pu['kind'] == "life":
                    lives += 1
                elif pu['kind'] == "slow":
                    ball_dx *= 0.8
                    ball_dy *= 0.8
                powerups.remove(pu)
                if sound_on: powerup_sound.play()
            elif pu['rect'].top > 600:
                powerups.remove(pu)

        # Missed ball
        if ball.top > 600:
            lives -= 1
            if sound_on: lose_life_sound.play()
            ball.topleft = (395, 300)
            ball_dx, ball_dy = 5, -5
            paddle.width = 100
            pygame.time.delay(1000)

        if lives == 0:
            game_over = font.render("Game Over", True, RED)
            screen.blit(game_over, (340, 280))
            pygame.display.flip()
            pygame.time.wait(2000)
            lives = 3
            score = 0
            level = 1
            create_bricks(level)
            powerups.clear()
            game_started = False

        # Level complete
        if not any(b['hits'] > 0 for b in bricks):
            level += 1
            ball_dx *= 1.1
            ball_dy *= 1.1
            create_bricks(level)
            ball.topleft = (395, 300)
            paddle.width = 100
            pygame.time.delay(1000)

        # Draw
        pygame.draw.rect(screen, BLUE, paddle)
        pygame.draw.ellipse(screen, BLACK, ball)
        draw_bricks()
        draw_powerups()

    # HUD
    screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Lives: {lives}", True, BLACK), (700, 10))
    screen.blit(font.render(f"Level: {level}", True, BLACK), (350, 10))
    screen.blit(font.render(f"Sound: {'On' if sound_on else 'Off'} (Press M)", True, BLACK), (10, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
