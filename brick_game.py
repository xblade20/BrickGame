
import pygame, random, os, math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker - Level Up Edition")

font       = pygame.font.SysFont("Arial", 24)
big_font   = pygame.font.SysFont("Arial", 60)
menu_font  = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 20)

WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(80,80,80)
RED=(200,0,0); ORANGE=(255,165,0); GREEN=(0,200,0)
BLUE=(0,0,200); YELLOW=(255,255,0); CYAN=(0,255,255)

sound_enabled=True
def play_sound(s):
    if sound_enabled: s.play()

bounce_sound   = pygame.mixer.Sound("bounce.wav")
brick_sound    = pygame.mixer.Sound("brick.wav")
powerup_sound  = pygame.mixer.Sound("powerup.wav")
lose_life_sound= pygame.mixer.Sound("lose_life.wav")

paddle_width, paddle_height = 100, 10
ball_radius = 8
NORMAL=1; DOUBLE=2; TRIPLE=3; UNBREAKABLE=-1

score=0; lives=3; level=1
highscore=0
paused=game_over=started=False
main_menu=True

paddle=pygame.Rect(WIDTH//2-paddle_width//2, HEIGHT-40, paddle_width, paddle_height)
ball  =pygame.Rect(WIDTH//2, HEIGHT//2, ball_radius*2, ball_radius*2)
ball_dx, ball_dy = 4, -4

powerups=[]
POWERUP_TYPES=["EXTEND_PADDLE","SLOW_DOWN"]

if os.path.exists("highscore.txt"):
    try: highscore=int(open("highscore.txt").read())
    except: highscore=0

def get_brick_pattern(level):
    rows=5+level; cols=10; pat=[]
    for r in range(rows):
        row=[]
        for c in range(cols):
            if level>=5 and (r+c)%2==0: row.append(True)
            elif level>=3 and r%2==0:   row.append(True)
            elif level>=2:              row.append(c%2==0)
            else:                       row.append(True)
        pat.append(row)
    return pat

def generate_bricks(level):
    bricks=[]; bw=WIDTH//10; bh=30
    for r,row in enumerate(get_brick_pattern(level)):
        for c,active in enumerate(row):
            if not active: continue
            rect=pygame.Rect(c*bw+1, r*bh+1, bw-2, bh-2)
            rdm=random.random()
            if level<=2:
                btype,h=(NORMAL,1) if rdm<0.8 else (DOUBLE,2) if rdm<0.95 else (UNBREAKABLE,-1)
            elif level<=4:
                if   rdm<0.5 : btype,h=NORMAL,1
                elif rdm<0.8 : btype,h=DOUBLE,2
                elif rdm<0.95: btype,h=TRIPLE,3
                else         : btype,h=UNBREAKABLE,-1
            else:
                if   rdm<0.3 : btype,h=NORMAL,1
                elif rdm<0.6 : btype,h=DOUBLE,2
                elif rdm<0.85: btype,h=TRIPLE,3
                else         : btype,h=UNBREAKABLE,-1
            bricks.append([rect,btype,h])
    return bricks

bricks=generate_bricks(level)

def reset_ball_and_paddle():
    global ball_dx, ball_dy
    paddle.width=paddle_width
    ball.center=(WIDTH//2, HEIGHT//2)
    ball_dx, ball_dy = 4+(level-1)*0.5, -(4+(level-1)*0.5)
    paddle.centerx=WIDTH//2

def draw_center(txt, fnt, col, y):
    surf=fnt.render(txt,True,col); screen.blit(surf, surf.get_rect(center=(WIDTH//2,y)))

def draw_button(txt,y,hov):
    pygame.draw.rect(screen, ORANGE if hov else GRAY,(WIDTH//2-100,y,200,50))
    screen.blit(menu_font.render(txt,True,WHITE),(WIDTH//2- menu_font.size(txt)[0]//2, y+10))

def draw_powerup(p):
    if p['type']=="EXTEND_PADDLE": pygame.draw.rect(screen,YELLOW,p['rect'])
    else: pygame.draw.ellipse(screen,CYAN,p['rect'])

def get_brick_color(hits,btype):
    if btype==UNBREAKABLE: return GRAY
    return {3:RED,2:ORANGE,1:GREEN}[hits]

def reflect_about_normal(vx,vy,nx,ny):
    dot=vx*nx+vy*ny
    return vx-2*dot*nx, vy-2*dot*ny

clock=pygame.time.Clock(); running=True
while running:
    clock.tick(60); screen.fill(BLACK)
    mouse=pygame.mouse.get_pos(); click=pygame.mouse.get_pressed()

    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_m: sound_enabled=not sound_enabled
            if started and not game_over and e.key==pygame.K_p: paused=not paused
            if game_over and e.key==pygame.K_RETURN:
                score,lives,level=0,3,1
                bricks=generate_bricks(level); powerups.clear()
                game_over=False; started=True; reset_ball_and_paddle()

    if main_menu:
        draw_center("BRICK BREAKER", big_font, WHITE, 100)
        draw_center("Controls: ← →  Move   P Pause   M Mute", small_font, WHITE, 160)
        hs = WIDTH//2-100<mouse[0]<WIDTH//2+100 and 250<mouse[1]<300
        hq = WIDTH//2-100<mouse[0]<WIDTH//2+100 and 320<mouse[1]<370
        draw_button("Start",250,hs); draw_button("Quit",320,hq)
        if hs and click[0]: started=True; main_menu=False
        if hq and click[0]: running=False

    elif started and not paused and not game_over:
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left>0: paddle.move_ip(-7,0)
        if keys[pygame.K_RIGHT] and paddle.right<WIDTH: paddle.move_ip(7,0)

        ball.x+=ball_dx; ball.y+=ball_dy
        if ball.left<=0 or ball.right>=WIDTH: ball_dx*=-1; play_sound(bounce_sound)
        if ball.top<=0: ball_dy*=-1; play_sound(bounce_sound)

        if ball.bottom>=HEIGHT:
            lives-=1; play_sound(lose_life_sound)
            if lives==0:
                game_over=True
                if score>highscore:
                    highscore=score; open("highscore.txt","w").write(str(highscore))
            else: reset_ball_and_paddle()

        if ball.colliderect(paddle):
            if not ball_hit_paddle:
                ball_dy *= -1
                play_sound(bounce_sound)
                ball_hit_paddle = True
        else:
            ball_hit_paddle = False


        for br in bricks[:]:
            rect,btype,h=br
            if ball.colliderect(rect):
                # side reflection
                dx_left   = abs(ball.right-rect.left)
                dx_right  = abs(rect.right-ball.left)
                dy_top    = abs(ball.bottom-rect.top)
                dy_bottom = abs(rect.bottom-ball.top)
                m=min(dx_left,dx_right,dy_top,dy_bottom)
                if m in (dx_left,dx_right): ball_dx*=-1
                else: ball_dy*=-1
                if btype!=UNBREAKABLE:
                    br[2]-=1
                    if br[2]==0:
                        bricks.remove(br); score+=10
                        if random.random()<0.2:
                            t=random.choice(POWERUP_TYPES)
                            powerups.append({'rect':pygame.Rect(ball.centerx,ball.centery,20,20),'type':t})
                play_sound(brick_sound); break

        for p in powerups[:]:
            p['rect'].y+=3
            if p['rect'].colliderect(paddle):
                if p['type']=="EXTEND_PADDLE": paddle.width=min(paddle.width+40,WIDTH)
                elif p['type']=="SLOW_DOWN":
                    speed=(ball_dx**2+ball_dy**2)**0.5*0.7
                    speed=max(2,speed)
                    ang=math.atan2(ball_dy,ball_dx)
                    ball_dx,ball_dy=speed*math.cos(ang),speed*math.sin(ang)
                play_sound(powerup_sound); powerups.remove(p)
            elif p['rect'].top>HEIGHT: powerups.remove(p)

        for r,btype,h in bricks:
            pygame.draw.rect(screen,get_brick_color(h,btype),r)
        pygame.draw.rect(screen,BLUE,paddle); pygame.draw.ellipse(screen,WHITE,ball)
        for p in powerups: draw_powerup(p)

        screen.blit(font.render(f"Score: {score}",True,WHITE),(10,HEIGHT-30))
        screen.blit(font.render(f"Lives: {lives}",True,WHITE),(WIDTH-120,HEIGHT-30))
        screen.blit(font.render(f"Level: {level}",True,WHITE),(WIDTH//2-40,HEIGHT-30))
        screen.blit(font.render(f"High: {highscore}",True,WHITE),(WIDTH-180,10))
        screen.blit(font.render(f"Sound: {'ON' if sound_enabled else 'OFF'}",True,WHITE),(10,10))

        if not any(b[1]!=UNBREAKABLE for b in bricks):
            level+=1; bricks=generate_bricks(level); reset_ball_and_paddle()

    elif paused: draw_center("PAUSED", big_font, WHITE, HEIGHT//2)
    elif game_over:
        draw_center("GAME OVER", big_font, WHITE, HEIGHT//2-60)
        draw_center(f"Score {score}  |  High {highscore}", font, WHITE, HEIGHT//2)
        draw_center("Press ENTER to Restart", font, WHITE, HEIGHT//2+40)

    pygame.display.flip()

pygame.quit()
