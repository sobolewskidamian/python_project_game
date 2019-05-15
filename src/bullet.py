import pygame

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512

SPEED = 0.7
DAMAGE = 1


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.y_change = 0

    def update(self):
        self.y_change -= SPEED
