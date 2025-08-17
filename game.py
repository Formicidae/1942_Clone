# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 12:47:01 2025

@author: Eddie
Laser sound effect: https://freesound.org/people/bubaproducer/sounds/151019/
"""
import pygame
import sys
import random

pygame.init()
pygame.mixer.init()

# Load sounds
shoot_sound = pygame.mixer.Sound("laser.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")

# Constants - these won't change during the game
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1200
FPS = 120

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

class Bullet(pygame.sprite.Sprite):
    """A bullet that moves up the screen"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("torpedo.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (8, 16))  # adjust size
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.speed = 8
    
    def update(self):
        """Move bullet up the screen"""
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # remove from group automatically
    
class Enemy(pygame.sprite.Sprite):
    """An enemy plane that moves down the screen"""
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.image.load("tie_fighter.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.uniform(1, 3)  # Random speed between 1-3
        self.health = 1  # Takes 1 hit to destroy
    
    def update(self):
        """Move enemy down the screen"""
        self.rect.y += self.speed
    
    def is_off_screen(self):
        """Check if enemy has gone off bottom of screen"""
        return self.rect.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Return rectangle for collision detection"""
        return self.rect

class EnemyStrong(pygame.sprite.Sprite):
    """A stronger enemy that takes more hits"""
    def __init__(self, x, y):
        super().__init__()

        try:
            self.image = pygame.image.load("tie_bomber.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (72, 72))  # slightly bigger
        except pygame.error:
            # fallback to red square
            self.image = pygame.Surface((72, 72))
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.uniform(0.5, 2)  # slower than normal enemies
        self.health = 3  # needs 3 hits to be destroyed

    def update(self):
        self.rect.y += self.speed

    def is_off_screen(self):
        return self.rect.y > SCREEN_HEIGHT

    def get_rect(self):
        return self.rect

    def take_damage(self, damage=1):
        self.health -= damage
        return self.health <= 0  # True if dead

class Player(pygame.sprite.Sprite):
    """Player class representing spaceship"""
    def __init__(self, x, y):
        super().__init__()
        # Load and scale the Millennium Falcon image
        try:
            self.image = pygame.image.load("millennium_falcon.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (64, 64))
        except pygame.error:
            # Fallback to triangle if image not found
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            points = [(32, 0), (0, 64), (64, 64)]  # Triangle shape
            pygame.draw.polygon(self.image, GREEN, points)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement speed
        self.speed = 5
        
        # Shooting mechanics
        self.last_shot = 0  # When we last shot
        self.shot_delay = 250  # Minimum milliseconds between shots
        
        # Health system
        self.health = 100
        self.max_health = 100
        
    def update(self, keys_pressed):
        """Update player position based on key presses"""
        # Move left (but don't go off screen)
        if keys_pressed[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        # Move right (but don't go off screen)
        if keys_pressed[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        # Move up (but only in bottom half of screen)
        if keys_pressed[pygame.K_UP] and self.rect.top > SCREEN_HEIGHT // 4:
            self.rect.y -= self.speed
        # Move down (but don't go off screen)
        if keys_pressed[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

    def shoot(self, bullets):
        """Create a new bullet if enough time has passed"""
        current_time = pygame.time.get_ticks()  # Get current time in milliseconds
        if current_time - self.last_shot > self.shot_delay:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets_group.add(bullet)
            shoot_sound.play()   # 🔊 play sound here
            self.last_shot = current_time
    
    def take_damage(self, damage):
        """Reduce player health"""
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def get_rect(self):
        return self.rect
    
    def is_alive(self):
        return self.health > 0

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)   # small to large stars
        self.speed = random.uniform(0.5, 2.5)  # parallax scrolling
        self.brightness = random.randint(100, 255)  # initial brightness
        self.twinkle_speed = random.choice([1, -1])  # direction of brightness change

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            # Recycle star to top
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

        # Twinkle effect (brightness up and down)
        self.brightness += self.twinkle_speed * 5
        if self.brightness >= 255:
            self.brightness = 255
            self.twinkle_speed = -1
        elif self.brightness <= 100:
            self.brightness = 100
            self.twinkle_speed = 1

    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My 1942 Clone")
clock = pygame.time.Clock()

# Create player at bottom center of screen
player = Player(SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT - 100)
all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
all_sprites.add(player)

stars = [Star() for _ in range(100)]  # adjust number of stars

# Game variables
bullets_group = pygame.sprite.Group()
score = 0
enemy_spawn_timer = 0
game_over = False

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                # Restart game
                player = Player(SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT - 100)
                all_sprites.empty()
                enemies_group.empty()
                all_sprites.add(player)
                score = 0
                enemy_spawn_timer = 0
                game_over = False
    
    if not game_over:
        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Update player
        player.update(keys)
        
        # Shooting
        if keys[pygame.K_SPACE]:
            player.shoot(bullets_group)
            
        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 60:
            enemy_x = random.randint(0, SCREEN_WIDTH - 64)
        
            if random.random() < 0.2:  # 20% chance for strong enemy
                enemy = EnemyStrong(enemy_x, -40)
            else:
                enemy = Enemy(enemy_x, -30)
        
            enemies_group.add(enemy)
            enemy_spawn_timer = 0       
        
        # Update bullets
        bullets_group.update()
        
        # Update enemies
        enemies_group.update()
        for enemy in list(enemies_group):
            if enemy.is_off_screen():
                enemies_group.remove(enemy)

        # Bullet hits enemy
        for bullet in bullets_group:
            for enemy in list(enemies_group):
                if bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    enemy.kill()
                    explosion_sound.play()  # 🔊 play explosion sound
                    score += 100
                    break

        # Check collisions between player and enemies
        for enemy in list(enemies_group):
            if player.get_rect().colliderect(enemy.get_rect()):
                # Collision! Remove enemy and damage player
                enemies_group.remove(enemy)
                player.take_damage(25)
        
        # Check if player is dead
        if not player.is_alive():
            game_over = True

    # Draw everything
    screen.fill(BLACK)
    
    if not game_over:
        # Draw player using sprite group
        all_sprites.draw(screen)
        
        # Draw starfield background
        for star in stars:
            star.update()
            star.draw(screen)
        
        # Draw all bullets
        bullets_group.draw(screen)
            
        # Draw all enemies
        enemies_group.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (10, 50))
        
        enemy_count = font.render(f"Enemies: {len(enemies_group)}", True, WHITE)
        screen.blit(enemy_count, (10, 90))
        
        # Health bar
        bar_width = 200
        bar_height = 20
        health_ratio = player.health / player.max_health
        pygame.draw.rect(screen, RED, (10, 130, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (10, 130, bar_width * health_ratio, bar_height))
        
    else:
        # Game over screen
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, text_rect)
        
        font = pygame.font.Font(None, 36)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(final_score_text, text_rect)
        
        restart_text = font.render("Press R to restart", True, WHITE)
        text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(restart_text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()
sys.exit()