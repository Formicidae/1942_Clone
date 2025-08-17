import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.health = 100
        self.last_shot = 0
        self.shot_delay = 200  # milliseconds
        
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > SCREEN_HEIGHT // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
            
    def shoot(self, bullets):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_delay:
            bullets.append(Bullet(self.x + self.width // 2, self.y, -8, True))
            self.last_shot = current_time
            
    def draw(self, screen):
        # Simple plane shape
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width // 4, self.y + self.height - 5),
            (self.x + 3 * self.width // 4, self.y + self.height - 5),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, GREEN, points)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Enemy:
    def __init__(self, x, y, enemy_type=1):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 25
        self.speed = random.uniform(1, 3)
        self.enemy_type = enemy_type
        self.health = enemy_type * 20
        self.last_shot = 0
        self.shot_delay = random.randint(1000, 3000)
        self.movement_pattern = random.choice(['straight', 'sine', 'diagonal'])
        self.time_alive = 0
        
    def update(self, bullets):
        self.time_alive += 1
        
        # Movement patterns
        if self.movement_pattern == 'straight':
            self.y += self.speed
        elif self.movement_pattern == 'sine':
            self.y += self.speed
            self.x += math.sin(self.time_alive * 0.1) * 2
        elif self.movement_pattern == 'diagonal':
            self.y += self.speed
            if self.x < SCREEN_WIDTH // 2:
                self.x += 1
            else:
                self.x -= 1
                
        # Keep enemies on screen horizontally
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shot_delay and self.y > 0:
            bullets.append(Bullet(self.x + self.width // 2, self.y + self.height, 4, False))
            self.last_shot = current_time
            self.shot_delay = random.randint(1500, 4000)
            
    def draw(self, screen):
        # Different colors for different enemy types
        colors = [RED, YELLOW, (255, 165, 0)]  # Red, Yellow, Orange
        color = colors[min(self.enemy_type - 1, len(colors) - 1)]
        
        # Simple enemy plane shape
        points = [
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y),
            (self.x + self.width // 4, self.y + 5),
            (self.x + 3 * self.width // 4, self.y + 5),
            (self.x + self.width, self.y)
        ]
        pygame.draw.polygon(screen, color, points)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet:
    def __init__(self, x, y, speed, is_player_bullet):
        self.x = x
        self.y = y
        self.speed = speed
        self.is_player_bullet = is_player_bullet
        self.width = 3
        self.height = 8
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        color = BLUE if self.is_player_bullet else RED
        pygame.draw.rect(screen, color, (self.x - self.width // 2, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type  # 'health', 'rapid_fire', 'double_shot'
        self.speed = 2
        self.width = 20
        self.height = 20
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        colors = {'health': GREEN, 'rapid_fire': BLUE, 'double_shot': YELLOW}
        color = colors.get(self.power_type, WHITE)
        pygame.draw.circle(screen, color, (int(self.x + self.width // 2), int(self.y + self.height // 2)), self.width // 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1942 Clone")
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.score = 0
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.background_y = 0
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        
    def spawn_enemy(self):
        if len(self.enemies) < 8:  # Limit number of enemies
            enemy_type = random.randint(1, 3)
            x = random.randint(0, SCREEN_WIDTH - 30)
            self.enemies.append(Enemy(x, -30, enemy_type))
            
    def spawn_powerup(self):
        if random.random() < 0.3:  # 30% chance
            power_type = random.choice(['health', 'rapid_fire', 'double_shot'])
            x = random.randint(0, SCREEN_WIDTH - 20)
            self.powerups.append(PowerUp(x, -20, power_type))
            
    def handle_collisions(self):
        # Player bullets vs enemies
        for bullet in self.bullets[:]:
            if bullet.is_player_bullet:
                for enemy in self.enemies[:]:
                    if bullet.get_rect().colliderect(enemy.get_rect()):
                        enemy.health -= 20
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += enemy.enemy_type * 100
                            
        # Enemy bullets vs player
        for bullet in self.bullets[:]:
            if not bullet.is_player_bullet:
                if bullet.get_rect().colliderect(self.player.get_rect()):
                    self.player.health -= 10
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                        
        # Player vs enemies
        for enemy in self.enemies[:]:
            if self.player.get_rect().colliderect(enemy.get_rect()):
                self.player.health -= 30
                self.enemies.remove(enemy)
                
        # Player vs powerups
        for powerup in self.powerups[:]:
            if self.player.get_rect().colliderect(powerup.get_rect()):
                if powerup.power_type == 'health':
                    self.player.health = min(100, self.player.health + 30)
                elif powerup.power_type == 'rapid_fire':
                    self.player.shot_delay = max(50, self.player.shot_delay - 50)
                self.powerups.remove(powerup)
                
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        
        # Update player
        self.player.update(keys)
        if keys[pygame.K_SPACE]:
            self.player.shoot(self.bullets)
            
        # Spawn enemies
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 60:  # Spawn every second
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
            
        # Spawn powerups
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer > 600:  # Spawn every 10 seconds
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
            
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.bullets)
            if enemy.y > SCREEN_HEIGHT:
                self.enemies.remove(enemy)
                
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < -10 or bullet.y > SCREEN_HEIGHT + 10:
                self.bullets.remove(bullet)
                
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.y > SCREEN_HEIGHT:
                self.powerups.remove(powerup)
                
        # Handle collisions
        self.handle_collisions()
        
        # Check game over
        if self.player.health <= 0:
            self.game_over = True
            
        # Scrolling background effect
        self.background_y += 2
        if self.background_y > 50:
            self.background_y = 0
            
    def draw_background(self):
        # Simple scrolling effect with dots
        for y in range(-50, SCREEN_HEIGHT + 50, 50):
            for x in range(0, SCREEN_WIDTH, 100):
                pygame.draw.circle(self.screen, GRAY, (x, y + self.background_y), 2)
                
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw scrolling background
        self.draw_background()
        
        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            for bullet in self.bullets:
                bullet.draw(self.screen)
                
            for powerup in self.powerups:
                powerup.draw(self.screen)
                
            # Draw UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(health_text, (10, 50))
            
            # Health bar
            pygame.draw.rect(self.screen, RED, (150, 55, 100, 20))
            pygame.draw.rect(self.screen, GREEN, (150, 55, self.player.health, 20))
            
        else:
            # Game over screen
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
            
        pygame.display.flip()
        
    def reset_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemies.clear()
        self.bullets.clear()
        self.powerups.clear()
        self.score = 0
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.game_over = False
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                        
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()