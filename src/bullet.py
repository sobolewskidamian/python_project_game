import pygame

pygame.init()

SPEED = 0.7
DAMAGE = 50


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.y_change = 0

    def update(self):
        self.y_change -= SPEED

    def collides(self, x, y, width, height):
        if y + height >= self.y and y <= self.y + self.height:
            return True
        return False
