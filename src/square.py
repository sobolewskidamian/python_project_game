import sys
import pygame
from pygame.locals import *

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512

GRAVITY = 0.5


class Square:
    def __init__(self, pid):
        self.pid = pid
        self.score = 0
        self.WIDTH = 20
        self.HEIGHT = 20
        self.x = SCREENWIDTH / 2 - self.WIDTH / 2
        self.y = SCREENHEIGHT / 2 - self.HEIGHT / 2
        self.XVALUE = 3
        self.YVALUE = -10
        self.x_value = 0
        self.y_value = 0
        self.jump_delay = 0
        self.dead = False

    def update(self):
        self.y_value += GRAVITY

        if self.jump_delay > 0:
            self.jump_delay -= 1

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.dead = True

            if not self.dead and self.jump_delay <= 0 and event.type == KEYDOWN and (
                    event.key == K_LEFT or event.key == K_RIGHT):
                self.y_value = self.YVALUE
                self.jump_delay = 5
                if event.key == K_LEFT:
                    self.x_value = -self.XVALUE
                elif event.key == K_RIGHT:
                    self.x_value = self.XVALUE

        if self.y_value > 0 or self.y > SCREENHEIGHT / 2 - self.HEIGHT / 2:
            self.y += self.y_value

        self.x += self.x_value

        if self.x >= SCREENWIDTH:
            self.x = -self.WIDTH + 1
        elif self.x <= -self.WIDTH:
            self.x = SCREENWIDTH - 1
