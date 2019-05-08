import sys
import os
import pygame
from pygame.locals import *

from server import Server

pygame.init()


class Game:
    def __init__(self, SCREEN, FPSCLOCK, FPS):
        self.SCREEN = SCREEN
        self.FPSCLOCK = FPSCLOCK
        self.FPS = FPS

        self.server = Server()
        self.game_over = False
        self.started = False
        self.restartDelay = 0

        self.server = Server()
        self.server.add_client(os.getpid())
        self.client = self.server.get_client(os.getpid())

    def restart(self):
        self.started = False
        self.game_over = False
        self.restartDelay = 0

    def play(self):
        self.watch_for_start(self.client)

        self.draw_square(self.client)
        pygame.display.flip()
        self.FPSCLOCK.tick(self.FPS)

        if self.started:
            while not self.client.dead:
                self.client.update()

                self.clean_screen()
                self.draw_square(self.client)

                pygame.display.flip()
                self.FPSCLOCK.tick(self.FPS)

    def watch_for_start(self, client):
        for event in pygame.event.get():
            if not self.started and event.type == KEYDOWN and (event.key == K_LEFT or event.key == K_RIGHT):
                self.started = True
                client.y_value = self.client.YVALUE
                if event.key == K_LEFT:
                    client.x_value = -self.client.XVALUE
                else:
                    client.x_value = self.client.XVALUE

    def clean_screen(self):
        self.SCREEN.fill((248, 248, 255))

    def draw_square(self, client):
        pygame.draw.rect(self.SCREEN, (255, 0, 0),
                         pygame.Rect(client.x, client.y, client.WIDTH, client.HEIGHT))
