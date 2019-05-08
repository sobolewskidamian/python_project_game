import sys
import pygame
from pygame.locals import *

pygame.init()


class Game:
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.started = False
        self.restartDelay = 0

    def restart(self):
        self.started = False
        self.game_over = False
        self.score = 0
        self.restartDelay = 0

    def play(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_LEFT or event.key == K_RIGHT):
                    self.started = True

            while self.started and not self.game_over:
                print("*")
