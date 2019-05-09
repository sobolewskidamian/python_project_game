import sys
import os
import pygame
from pygame.locals import *

from server import Server
from pipe import Pipe

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512

hi_type = 20


class Game:
    def __init__(self, SCREEN, FPSCLOCK, FPS):
        self.SCREEN = SCREEN
        self.FPSCLOCK = FPSCLOCK
        self.FPS = FPS

        self.server = Server()
        self.score = 0
        self.game_over = False
        self.started = False
        self.restart_delay = 0
        self.pipes = []
        self.pipes_under_middle = []

        self.server = Server()
        self.server.add_client(os.getpid())
        self.client = self.server.get_client(os.getpid())

    def restart(self):
        self.started = False
        self.game_over = False
        self.restart_delay = 0

    def play(self):
        self.watch_for_start()
        self.show_screen_before_game()

        if self.started:
            while not self.client.dead:
                self.watch_for_clickes()
                self.client.update()
                self.move_pipes()
                # self.check_collisions()

                self.clean_screen()
                self.draw_square(self.client)
                self.draw_pipes()

                pygame.display.update()
                self.FPSCLOCK.tick(self.FPS)

    def show_screen_before_game(self):
        self.clean_screen()
        self.draw_square(self.client)
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

    def watch_for_clickes(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.client.left_pressed = True
                    for pipe in self.pipes:
                        pipe.left_pressed = True
                elif event.key == K_RIGHT:
                    self.client.right_pressed = True
                    for pipe in self.pipes:
                        pipe.right_pressed = True
                elif event.key == K_ESCAPE:
                    self.client.escape_pressed = True
                self.started = True

    def watch_for_start(self):
        self.move_pipes()
        self.watch_for_clickes()

    def clean_screen(self):
        self.SCREEN.fill((248, 248, 255))

    def draw_square(self, client):
        pygame.draw.rect(self.SCREEN, (255, 0, 0),
                         pygame.Rect(client.x, client.y, client.width, client.height))
        all_clients = self.server.get_all_clients()
        if self.client.pid in all_clients:
            del all_clients[self.client.pid]

        for pid in all_clients:
            actual_client = all_clients[pid]
            if abs(actual_client.total_y - self.client.total_y) < SCREENHEIGHT / 2 + actual_client.height:
                pygame.draw.rect(self.SCREEN, (0, 0, 0),
                                 pygame.Rect(actual_client.x, SCREENHEIGHT / 2 - (
                                             actual_client.total_y - self.client.total_y + actual_client.height / 2),
                                             actual_client.width,
                                             actual_client.height))

    def draw_pipes(self):
        for pipe in self.pipes:
            pygame.draw.rect(self.SCREEN, (255, 0, 0), pygame.Rect(0, pipe.y, pipe.left_pipe_width, pipe.height))
            pygame.draw.rect(self.SCREEN, (255, 0, 0),
                             pygame.Rect(SCREENWIDTH - pipe.right_pipe_width, pipe.y, pipe.right_pipe_width,
                                         pipe.height))

    def move_pipes(self):
        in_middle = False
        y_value = 0
        delay = 0

        for pipe in self.pipes:
            if pipe.y > SCREENHEIGHT:
                self.pipes.remove(pipe)
                self.pipes_under_middle.remove(pipe)
                break
            elif pipe.y >= SCREENHEIGHT / 2 and pipe not in self.pipes_under_middle:
                in_middle = True
                self.pipes_under_middle.append(pipe)
                y_value = pipe.y_value
                delay = pipe.jump_delay
                self.score += 1
                print(self.score)



        if in_middle or len(self.pipes) == 0:
            self.add_pipe(y_value, delay)

        for pipe in self.pipes:
            pipe.update()
        if len(self.pipes) > 0:
            self.pipes[0].update_square()

    def add_pipe(self, y_value, delay):
        server_pipe = self.server.get_pipe(self.score + 1)

        pipe = Pipe(server_pipe[0], server_pipe[1], self.client)
        self.pipes.append(pipe)

        pipe.synchronize_with_other_pipes(y_value, delay)

    def check_collisions(self):
        for pipe in self.pipes:
            if pipe.collides(self.client.x, self.client.y, self.client.width, self.client.height):
                self.game_over = True
                self.client.dead = True

        if self.client.y >= SCREENHEIGHT - self.client.height:
            self.game_over = True
            self.client.dead = True
