# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 12:47:01 2025

@author: Eddie
"""

import pygame
import sys

pygame.init()

# Constants - these won't change during the game
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1200
FPS = 120

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My 1942 Clone")

# Frame rate clock
clock = pygame.time.Clock()

#Main game loop
running = True
while running:
    #quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    #background
    screen.fill(BLACK)
    
    pygame.draw.rect(screen, GREEN, (100, 100, 50, 50))
    
    pygame.display.flip()
    
    clock.tick(FPS)
    
pygame.quit()
sys.exit()