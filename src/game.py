import sys
import time

import pygame
from pygame.locals import *
import pickle
import select
import socket
import random

from pipe import Pipe
from square import Square
from generator import Generator

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512
multiplayer = True
BUFFERSIZE = 2048
server_address = '127.0.0.1'  # '192.168.1.104'
port = 4321


class Game:
    def __init__(self, nick, SCREEN, FPSCLOCK, FPS):
        self.SCREEN = SCREEN
        self.FPSCLOCK = FPSCLOCK
        self.FPS = FPS

        self.nick = nick
        self.game_over = False
        self.started = False
        self.wait_for_multiplayer_game = True
        self.restart_delay = 0
        self.pipes = []
        self.pipes_under_middle = []

        # self.server = Server()
        # self.server.add_client(os.getpid())
        # self.client = self.server.get_client(os.getpid())
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connected = False
        self.client = Square(-1)
        self.clients = {}

    def restart(self):
        self.started = False
        self.game_over = True
        self.client.dead = True
        self.wait_for_multiplayer_game = True
        if multiplayer:
            self.delete_client()
        self.restart_delay = 0
        self.pipes.clear()
        self.pipes_under_middle.clear()
        self.client = Square(random.randint(1000, 1000000))
        self.clients.clear()
        self.play()

    def play(self):
        self.clean_screen()
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

        if multiplayer:
            if not self.server_connected:
                self.s.connect((server_address, port))
                self.server_connected = True
            else:
                self.add_client()

        if multiplayer:
            while self.wait_for_multiplayer_game:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.delete_client()
                        pygame.quit()
                        sys.exit()
                self.update_multiplayer()

        self.show_screen_before_game()
        while not self.started:
            self.watch_for_start()

        if self.started:
            while not self.client.dead:
                self.update_multiplayer()
                self.watch_for_clickes()
                self.client.update()
                self.move_pipes()
                # self.check_collisions()

                if multiplayer:
                    self.s.send(pickle.dumps(
                        ['position update', self.client.pid, self.client.x, self.client.total_y, self.client.y,
                         self.client.score]))

                self.clean_screen()
                self.draw_square(self.client)
                self.draw_pipes()
                self.draw_score()

                pygame.display.update()
                self.FPSCLOCK.tick(self.FPS)

    def update_multiplayer(self):
        if multiplayer:
            ins, outs, ex = select.select([self.s], [], [], 0)
            for inm in ins:
                try:
                    game_event = pickle.loads(inm.recv(BUFFERSIZE))

                    if game_event[0] == 'add client':
                        self.client.pid = game_event[1]
                        self.add_client()
                    if game_event[0] == 'position update':
                        game_event.pop(0)
                        for act_client in game_event:
                            if act_client[0] != self.client.pid:
                                self.clients[act_client[0]] = [act_client[1], act_client[2], act_client[3]]
                    if game_event[0] == 'pipe location':
                        game_event.pop(0)
                        for act_pipe in game_event:
                            if act_pipe[0] == self.client.pid:
                                pipe = self.pipes[len(self.pipes) - 1]
                                pipe.left_pipe_width = act_pipe[1]
                                pipe.right_pipe_width = act_pipe[2]
                    if game_event[0] == 'start game':
                        # TODO
                        # animation 3 2 1 start
                        self.wait_for_multiplayer_game = False
                    if game_event[0] == 'game is running':
                        if game_event[1] == self.client.pid:
                            time.sleep(0.5)
                            self.add_client()
                except Exception as e:
                    print(end='')

    def show_screen_before_game(self):
        self.clean_screen()
        self.draw_square(self.client)
        self.draw_score()
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

    def watch_for_clickes(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.delete_client()
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
                    # self.client.escape_pressed = True
                    self.restart()
                self.started = True

    def watch_for_start(self):
        # self.move_pipes()
        self.watch_for_clickes()

    def clean_screen(self):
        self.SCREEN.fill((248, 248, 255))

    def draw_square(self, client):
        pygame.draw.rect(self.SCREEN, (255, 0, 0),
                         pygame.Rect(client.x, client.y, client.width, client.height))

        for pid in self.clients:
            actual_client = self.clients[pid]
            actual_client_x = actual_client[0]
            actual_client_total_y = actual_client[1]
            actual_client_y = actual_client[2]

            if abs(actual_client_total_y - self.client.total_y) < SCREENHEIGHT / 2 + self.client.height:
                pygame.draw.rect(self.SCREEN,
                                 (0, 0, 0),
                                 pygame.Rect(actual_client_x,
                                             SCREENHEIGHT / 2 - (
                                                     actual_client_total_y - self.client.total_y + self.client.height / 2) - SCREENHEIGHT / 2 + actual_client_y,
                                             self.client.width,
                                             self.client.height))

    def draw_pipes(self):
        for pipe in self.pipes:
            pygame.draw.rect(self.SCREEN, (255, 0, 0), pygame.Rect(0, pipe.y, pipe.left_pipe_width, pipe.height))
            pygame.draw.rect(self.SCREEN, (255, 0, 0),
                             pygame.Rect(SCREENWIDTH - pipe.right_pipe_width, pipe.y, pipe.right_pipe_width,
                                         pipe.height))

    def draw_score(self):
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.client.score), True, (0, 0, 0))
        self.SCREEN.blit(text, (0, 0))

    def move_pipes(self):
        in_middle = False
        y_value = 0
        delay = 0

        for pipe in self.pipes:
            if pipe.left_pipe_width == 0 and pipe.right_pipe_width == 0:
                self.get_pipe_size_from_server()

            if pipe.y > SCREENHEIGHT:
                self.pipes.remove(pipe)
                self.pipes_under_middle.remove(pipe)
                break
            elif pipe.y >= SCREENHEIGHT / 2 and pipe not in self.pipes_under_middle:
                in_middle = True
                self.pipes_under_middle.append(pipe)
                y_value = pipe.y_value
                delay = pipe.jump_delay
                self.client.score += 1

        if in_middle or len(self.pipes) == 0:
            if in_middle and multiplayer and self.pipes[len(self.pipes) - 1].left_pipe_width == 0 and self.pipes[
                len(self.pipes) - 1].right_pipe_width == 0:
                self.wait_for_server()
            self.add_pipe(y_value, delay)

        for pipe in self.pipes:
            pipe.update()

        if len(self.pipes) > 0:
            self.pipes[0].update_square()

    def wait_for_server(self):
        self.s.connect((server_address, port))
        while True:
            data = self.s.recv(4096)
            if len(data) == 0:
                self.s.connect((server_address, port))
            else:
                break

    def get_pipe_size_from_server(self):
        self.s.send(pickle.dumps(['pipe location', self.client.pid, self.client.score + 1]))

    def delete_client(self):
        self.s.send(pickle.dumps(['delete client', self.client.pid]))

    def add_client(self):
        self.s.send(pickle.dumps(['add client', self.client.pid, self.nick]))

    def add_pipe(self, y_value, delay):
        pipe = Pipe(0, 0, self.client)
        pipe.synchronize_with_other_pipes(y_value, delay)
        self.pipes.append(pipe)
        if multiplayer:
            self.get_pipe_size_from_server()
        else:
            left, right = Generator().get_width_left_and_beetween(self.client.score)
            pipe.left_pipe_width = left
            pipe.right_pipe_width = right

    def check_collisions(self):
        for pipe in self.pipes:
            if pipe.collides(self.client.x, self.client.y, self.client.width, self.client.height):
                self.restart()

        if self.client.y >= SCREENHEIGHT - self.client.height:
            self.restart()
