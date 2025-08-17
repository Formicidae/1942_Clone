# -*- coding: utf-8 -*-
"""
1942 Clone with threaded scrolling Reddit backgrounds
@author: Eddie
Laser sound effect: https://freesound.org/people/bubaproducer/sounds/151019/
Background music: https://soundcloud.com/crig-1/star-wars-theme-8bit
"""

import pygame, sys, random, requests, time, threading
from io import BytesIO

pygame.init()
pygame.mixer.init()

# --- Constants ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 120
BG_SCROLL_SPEED = 1

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)

# --- Sounds ---
shoot_sound = pygame.mixer.Sound("laser.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
pygame.mixer.music.load("background_music.mp3")
shoot_sound.set_volume(0.5)   # volume between 0.0 and 1.0
explosion_sound.set_volume(0.5)   # volume between 0.0 and 1.0

# --- Set window centered and always on top ---
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("1942 Clone")

# --- Helper to load unique Reddit images ---
used_urls = set()
reddit_lock = threading.Lock()

def fetch_reddit_image(used_urls, subreddits=["spaceporn","EarthPorn","astrophotography"], limit=50):
    headers = {"User-Agent": "Mozilla/5.0"}
    while True:
        try:
            subreddit = random.choice(subreddits)
            url = f"https://www.reddit.com/r/{subreddit}/top/.json?limit={limit}&t=month"
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            posts = data["data"]["children"]
            random.shuffle(posts)
            for post in posts:
                img_url = post["data"].get("url_overridden_by_dest") or post["data"].get("url","")
                with reddit_lock:
                    if img_url in used_urls:
                        continue
                if img_url.lower().endswith((".jpg",".jpeg",".png")):
                    img_response = requests.get(img_url, timeout=10)
                    img = pygame.image.load(BytesIO(img_response.content)).convert_alpha()
                    w,h = img.get_width(), img.get_height()
                    scale = min(WINDOW_WIDTH/w, WINDOW_HEIGHT/h, 1)
                    new_w,new_h = int(w*scale), int(h*scale)
                    img = pygame.transform.smoothscale(img,(new_w,new_h))
                    bg = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT))
                    bg.fill(BLACK)
                    bg.blit(img,((WINDOW_WIDTH-new_w)//2,(WINDOW_HEIGHT-new_h)//2))
                    with reddit_lock:
                        used_urls.add(img_url)
                    return bg, img_url
        except Exception as e:
            print("Failed to load Reddit image, retrying...", e)
            time.sleep(1)

# --- Background loader thread ---
next_bg = None
next_url = None
bg_ready_event = threading.Event()

def preload_next_bg():
    global next_bg, next_url
    while True:
        bg, url = fetch_reddit_image(used_urls)
        next_bg = bg
        next_url = url
        bg_ready_event.set()
        bg_ready_event.wait()  # wait until main thread consumes it
        bg_ready_event.clear()

bg_thread = threading.Thread(target=preload_next_bg, daemon=True)
bg_thread.start()

# --- Sprites ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("torpedo.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(8,16))
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 8
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("tie_fighter.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(64,64))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = random.uniform(1,3)
        self.health = 1
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT: self.kill()

class EnemyStrong(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("tie_bomber.png").convert_alpha()
            self.image = pygame.transform.scale(self.image,(72,72))
        except:
            self.image = pygame.Surface((72,72))
            self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = random.uniform(0.5,2)
        self.health = 3
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT: self.kill()
    def take_damage(self, dmg=1):
        self.health -= dmg
        return self.health <= 0

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("millennium_falcon.png").convert_alpha()
            self.image = pygame.transform.scale(self.image,(64,64))
        except:
            self.image = pygame.Surface((64,64),pygame.SRCALPHA)
            pygame.draw.polygon(self.image,GREEN,[(32,0),(0,64),(64,64)])
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = 5
        self.last_shot = 0
        self.shot_delay = 250
        self.health = 100
        self.max_health = 100
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left>0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right<WINDOW_WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top>WINDOW_HEIGHT//4: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom<WINDOW_HEIGHT: self.rect.y += self.speed
    def shoot(self, bullets_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets_group.add(bullet)
            shoot_sound.play()
            self.last_shot = now
    def take_damage(self,dmg): self.health = max(0,self.health-dmg)
    def is_alive(self): return self.health>0

# --- Groups ---
all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
player = Player(WINDOW_WIDTH//2-32, WINDOW_HEIGHT-100)
all_sprites.add(player)

# --- Load initial backgrounds ---
current_bg, current_url = fetch_reddit_image(used_urls)
bg_y = 0

# --- Game vars ---
score = 0
enemy_spawn_timer = 0
game_over = False
clock = pygame.time.Clock()


pygame.mixer.music.play(-1)  # -1 makes it loop forever
# --- Main loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        elif event.type==pygame.KEYDOWN and event.key==pygame.K_r and game_over:
            player = Player(WINDOW_WIDTH//2-32, WINDOW_HEIGHT-100)
            all_sprites.empty()
            enemies_group.empty()
            bullets_group.empty()
            all_sprites.add(player)
            score = 0
            enemy_spawn_timer = 0
            game_over = False

    keys = pygame.key.get_pressed()
    if not game_over:
        player.update(keys)
        if keys[pygame.K_SPACE]: player.shoot(bullets_group)

        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer>60:
            ex = random.randint(0, WINDOW_WIDTH-64)
            enemy = EnemyStrong(ex,-40) if random.random()<0.2 else Enemy(ex,-30)
            enemies_group.add(enemy)
            enemy_spawn_timer=0

        bullets_group.update()
        enemies_group.update()

        # Collisions
        hits = pygame.sprite.groupcollide(enemies_group, bullets_group, False, True)
        for enemy, bullets in hits.items():
            if isinstance(enemy, EnemyStrong):
                for _ in bullets:
                    if enemy.take_damage(1):
                        enemy.kill()
                        explosion_sound.play()
                        score += 300
            else:
                enemy.kill()
                explosion_sound.play()
                score += 100

        # Player collision
        for enemy in enemies_group:
            if player.rect.colliderect(enemy.rect):
                enemy.kill()
                player.take_damage(25)

        if not player.is_alive(): game_over = True

    # --- Background scroll ---
    bg_y += BG_SCROLL_SPEED
    if bg_y >= WINDOW_HEIGHT:
        current_bg = next_bg if next_bg else current_bg
        bg_y = 0
        if bg_ready_event.is_set():
            bg_ready_event.clear()  # allow loader thread to preload next

    if next_bg:
        screen.blit(current_bg,(0,bg_y-WINDOW_HEIGHT))
        screen.blit(next_bg,(0,bg_y))
    else:
        screen.blit(current_bg,(0,0))

    # --- Draw ---
    all_sprites.draw(screen)
    bullets_group.draw(screen)
    enemies_group.draw(screen)

    # UI
    font = pygame.font.Font(None,36)
    screen.blit(font.render(f"Score: {score}",True,WHITE),(10,10))
    screen.blit(font.render(f"Health: {player.health}",True,WHITE),(10,50))
    screen.blit(font.render(f"Enemies: {len(enemies_group)}",True,WHITE),(10,90))
    pygame.draw.rect(screen,RED,(10,130,200,20))
    pygame.draw.rect(screen,GREEN,(10,130,200*player.health/player.max_health,20))

    if game_over:
        font_big = pygame.font.Font(None,72)
        screen.blit(font_big.render("GAME OVER",True,WHITE),(WINDOW_WIDTH//2-200,WINDOW_HEIGHT//2-50))
        screen.blit(font.render(f"Final Score: {score}",True,WHITE),(WINDOW_WIDTH//2-100,WINDOW_HEIGHT//2+20))
        screen.blit(font.render("Press R to restart",True,WHITE),(WINDOW_WIDTH//2-100,WINDOW_HEIGHT//2+60))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
