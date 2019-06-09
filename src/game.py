import random
import sys
import time

import pygame
from pygame.locals import *
import pickle
import select
import socket

from bullets import Bullet, SPEED, FireBallLeft, FireBallRight, Rocket, BossBullet, DAMAGE_PLAYER, DAMAGE_BOSS
from pipe import Pipe
from square import Square
from generator import Generator

from boss import Boss

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512
BUFFERSIZE = 2048
LAP = 2

# pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=2048)
death_sound = pygame.mixer.Sound('sounds/death.wav')
shot_sound = pygame.mixer.Sound('sounds/laser1.wav')
boss_intro = pygame.mixer.Sound('sounds/4.wav')

music = pygame.mixer.music.load('sounds/5966459_space-shooter-theme_by_matthewpablo_preview.wav')


class Game:
    def __init__(self, nick, SCREEN, FPSCLOCK, FPS):
        self.SCREEN = SCREEN
        self.FPSCLOCK = FPSCLOCK
        self.FPS = FPS
        self.multiplayer = False
        self.port = 0
        self.server_address = ''
        self.game_id = 0

        self.boss_level = 1
        self.nick = nick
        self.game_ended = True
        self.started = False
        self.wait_for_multiplayer_game = True
        self.restart_delay = 0
        self.pipes = []
        self.pipes_under_middle = []
        self.bullets = []
        self.boss_bullets = []
        self.boss_rockets = []
        self.fire_balls_left = []
        self.fire_balls_right = []
        self.tick = 0

        self.s = None
        self.server_connected = False
        self.client_added = False
        self.client = Square(random.randint(1000, 1000000))
        self.clients = {}
        self.nicks_before_game = []
        self.last_update_nicks = time.time()
        self.client.boss_dead = True
        self.client.boss_mode = False
        if self.multiplayer:
            for id in self.clients:
                self.clients[id].boss_mode = False
                self.clients[id].boss_dead = True

    def restart(self):
        pygame.mixer.music.stop()
        self.game_id = 0
        self.client.boss_dead = True
        self.started = False
        self.boss_level = 1
        self.client.dead = True
        self.wait_for_multiplayer_game = True
        self.client_added = False
        self.client.boss_mode = False
        if self.multiplayer:
            self.delete_client()
            for id in self.clients:
                self.clients[id].boss_mode = False
                self.clients[id].boss_dead = True
                self.clients[id].boss_level = 1
        self.clients.clear()
        self.nicks_before_game.clear()
        self.restart_delay = 0
        self.pipes.clear()
        self.bullets.clear()
        self.pipes_under_middle.clear()
        self.client = Square(self.client.pid)
        self.boss_bullets.clear()
        self.boss_rockets.clear()
        self.fire_balls_left.clear()
        self.fire_balls_right.clear()
        pygame.mixer.music.stop()

    def play(self):
        pygame.mixer.music.play(-1)
        self.clean_screen()
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

        if self.multiplayer:
            if not self.server_connected:
                try:
                    self.draw_text_at_center("Trying connect to server...", False)
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.s.connect((self.server_address, self.port))
                    self.server_connected = True
                except Exception:
                    self.game_ended = True
                    self.client.dead = True
                    self.started = True
                    self.wait_for_multiplayer_game = False
                    t = time.time()
                    while time.time() - t < 3:
                        self.draw_text_at_center("Cannot connect to server.", False)
                        self.FPSCLOCK.tick(self.FPS)

            seconds = seconds_loop = time.time()
            seconds_bool = True
            while not self.client_added:
                self.draw_text_at_center("Waiting for joining the server", True, seconds_loop)
                if self.game_ended:
                    break
                self.update_multiplayer()
                if time.time() - seconds > 0.2 or seconds_bool:
                    self.add_client()
                    seconds = time.time()
                    seconds_bool = False
                self.check_if_pressed_escape()

            seconds = seconds_loop = time.time()
            seconds_bool = True
            while self.wait_for_multiplayer_game:
                self.draw_text_at_center("Waiting for players", True, seconds_loop, True)
                if self.game_ended:
                    break
                self.update_multiplayer()
                if time.time() - seconds > 0.2 or seconds_bool:
                    if time.time() - self.last_update_nicks > 3:
                        self.get_nicks()
                    self.could_start_game()
                    seconds = time.time()
                    seconds_bool = False
                self.check_if_pressed_escape()
            self.ready_steady_go()

        self.show_screen_before_game()
        while not self.started:
            self.watch_for_click()
            self.update_multiplayer()

        seconds = time.time()
        while not self.client.dead:
            self.update_multiplayer()
            self.watch_for_click()
            if not self.client.boss_mode:
                self.client.update()
            else:
                self.client.boss_mode_update()
            self.move_pipes()
            self.move_bullets()
            self.move_boss()
            self.check_collisions()
            if self.client.boss_dead:
                self.client.boss_mode = False
            if self.tick % 60 == 0 and self.client.boss_mode:
                self.add_rocket()
            if self.tick % 20 == 0 and self.client.boss_mode:
                self.add_boss_bullets()
            self.tick += 1
            if self.tick > 100000000:
                self.tick = 0
            if self.multiplayer and time.time() - seconds > 0.05:
                self.send_position_update()
                seconds = time.time()

            self.clean_screen()
            self.draw_square(self.client)
            self.draw_pipes()
            self.draw_score()
            self.draw_hp_bar()
            self.draw_bullets()
            if self.client.boss_mode and not self.client.boss_dead:
                self.draw_boss()
                self.draw_boss_hp_bar()

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

        self.restart()

    def action_when_quit_game(self):
        self.game_ended = True
        self.client.dead = True
        self.started = True
        pygame.mixer.music.stop()
        if self.multiplayer:
            self.delete_client()
            self.s.close()
            self.server_connected = False

    def check_if_pressed_escape(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.delete_client()
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.action_when_quit_game()
                pygame.mixer.music.stop()

    def ready_steady_go_text(self, number):
        seconds = time.time()
        while time.time() - seconds < 1:
            self.check_if_pressed_escape()
            if self.game_ended:
                break
            self.clean_screen()
            self.draw_square(self.client)
            self.draw_score()
            font = pygame.font.Font(None, 50)
            text = font.render(str(number), True, (0, 0, 0))
            self.SCREEN.blit(text, (SCREENWIDTH / 2 - 10, SCREENHEIGHT / 2 - 25))
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def ready_steady_go(self):
        self.ready_steady_go_text(3)
        self.ready_steady_go_text(2)
        self.ready_steady_go_text(1)

    def update_multiplayer(self):
        if self.multiplayer and self.server_connected:
            ins, outs, ex = select.select([self.s], [], [], 0)
            for inm in ins:
                try:
                    game_event = pickle.loads(inm.recv(BUFFERSIZE))

                    if game_event[0] == 'add client' and not self.client_added:
                        self.add_client()
                    if game_event[0] == 'client added' and game_event[1] == self.client.pid:
                        self.client_added = True
                    if game_event[0] == 'position update':
                        game_event.pop(0)
                        game_id = game_event.pop(0)
                        for act_client in game_event:
                            if act_client[0] != self.client.pid and self.game_id == game_id:
                                if act_client[0] not in self.clients:
                                    self.clients[act_client[0]] = Square(act_client[0])
                                self.clients[act_client[0]].x = act_client[1]
                                self.clients[act_client[0]].total_y = act_client[2]
                                self.clients[act_client[0]].y = act_client[3]
                                self.clients[act_client[0]].nick = act_client[4]

                    if game_event[0] == 'pipe location':
                        game_event.pop(0)
                        for act_pipe in game_event:
                            if act_pipe[0] == self.client.pid:
                                pipe = self.pipes[len(self.pipes) - 1]
                                pipe.left_pipe_width = act_pipe[1]
                                pipe.right_pipe_width = act_pipe[2]
                    if game_event[0] == 'start game':
                        game_event.pop(0)
                        game_id = game_event.pop(0)
                        if self.client.pid in game_event:
                            self.wait_for_multiplayer_game = False
                            self.game_id = game_id
                    if game_event[0] == 'start adding' and not self.client_added:
                        self.add_client()
                    if game_event[0] == 'client removed':
                        if game_event[1] == self.client.pid:
                            self.game_ended = True
                            self.client.dead = True
                            self.started = True
                            self.s.close()
                            self.server_connected = False
                    if game_event[0] == 'get nicks':
                        self.last_update_nicks = time.time()
                        game_event.pop(0)
                        self.nicks_before_game = game_event.copy()
                    if game_event[0] == 'init boss':
                        self.client.boss.hp = game_event[1]
                    if game_event[0] == 'get hp':
                        self.client.boss.hp = game_event[1]
                    if game_event[0] == 'boss dead':
                        for user in self.clients.values():
                            user.boss_mode = False
                            user.boss_dead = True
                            user.boss = None

                except Exception:
                    print(end='')

    def show_screen_before_game(self):
        self.clean_screen()
        self.draw_square(self.client)
        self.draw_score()
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

    def watch_for_click(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                if self.multiplayer:
                    self.delete_client()
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_LEFT or event.key == K_RIGHT or event.key == K_ESCAPE
                                          or event.key == K_SPACE):
                if event.key == K_LEFT:
                    self.client.left_pressed = True
                    for pipe in self.pipes:
                        pipe.left_pressed = True
                elif event.key == K_RIGHT:
                    self.client.right_pressed = True
                    for pipe in self.pipes:
                        pipe.right_pressed = True
                elif event.key == K_ESCAPE:
                    self.action_when_quit_game()
                elif event.key == K_SPACE:
                    if self.client.boss_mode:
                        self.add_bullet()

                self.started = True

    def clean_screen(self):
        self.SCREEN.fill((200, 255, 255))

    def draw_square(self, client):
        for pid in self.clients:
            actual_client = self.clients[pid]
            actual_client_x = actual_client.x
            actual_client_total_y = actual_client.total_y
            actual_client_y = actual_client.y
            actual_client_nick = actual_client.nick

            if abs(actual_client_total_y - self.client.total_y) < SCREENHEIGHT / 2 + self.client.height:
                pygame.draw.rect(self.SCREEN,
                                 (0, 0, 0),
                                 pygame.Rect(actual_client_x,
                                             SCREENHEIGHT / 2 - (
                                                     actual_client_total_y - self.client.total_y + self.client.height / 2) - SCREENHEIGHT / 2 + actual_client_y,
                                             self.client.width,
                                             self.client.height))
                font = pygame.font.Font(None, 15)
                text = font.render(actual_client_nick, True, (0, 0, 0))
                self.SCREEN.blit(text, (actual_client_x, SCREENHEIGHT / 2 - (
                        actual_client_total_y - self.client.total_y + self.client.height / 2) - SCREENHEIGHT / 2 + actual_client_y + self.client.height))

        img = pygame.image.load('images/pixil-frame-0.png')
        self.SCREEN.blit(img, (client.x, client.y))

    def draw_pipes(self):
        for pipe in self.pipes:
            pygame.draw.rect(self.SCREEN, (0, 0, 0), pygame.Rect(0, pipe.y, pipe.left_pipe_width, pipe.height))
            pygame.draw.rect(self.SCREEN, (0, 0, 0),
                             pygame.Rect(SCREENWIDTH - pipe.right_pipe_width, pipe.y, pipe.right_pipe_width,
                                         pipe.height))

    def draw_score(self):
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.client.score), True, (0, 0, 0))
        self.SCREEN.blit(text, (0, 0))

    def draw_bullets(self):
        for bullet in self.bullets:
            img = pygame.image.load('images/bullet.png')
            self.SCREEN.blit(img, (bullet.x, bullet.y))
        for bullet in self.boss_bullets:
            img = pygame.image.load('images/bullet.png')
            self.SCREEN.blit(img, (bullet.x, bullet.y))
        for rocket in self.boss_rockets:
            img = pygame.image.load('images/rocket.png')
            self.SCREEN.blit(img, (rocket.x, rocket.y))
        for ball in self.fire_balls_left:
            img = pygame.image.load('images/fireballleft.png')
            self.SCREEN.blit(img, (ball.x, ball.y))
        for ball in self.fire_balls_right:
            img = pygame.image.load('images/fireballright.png')
            self.SCREEN.blit(img, (ball.x, ball.y))

    def draw_boss(self):
        img = pygame.image.load('images/boss.png')
        self.SCREEN.blit(img, (self.client.boss.x, self.client.boss.y))

    def draw_hp_bar(self):
        pygame.draw.rect(self.SCREEN, (255, 0, 0), pygame.Rect(47, 490, 2 * self.client.hp, 10))

    def draw_boss_hp_bar(self):
        if self.multiplayer:
            self.send_data(['get hp', self.client.pid])
        pygame.draw.rect(self.SCREEN, (255, 0, 0), pygame.Rect(47, 10, self.client.boss.hp, 10))

    def draw_text_at_center(self, text_to_draw, dots, t=time.time(), nicks=False):
        if dots:
            if int(time.time() - t) % 4 == 1:
                text_to_draw += '.'
            elif int(time.time() - t) % 4 == 2:
                text_to_draw += '..'
            elif int(time.time() - t) % 4 == 3:
                text_to_draw += '...'
        self.clean_screen()
        font = pygame.font.Font(None, 16)
        text = font.render(text_to_draw, True, (0, 0, 0))
        self.SCREEN.blit(text, (10, SCREENHEIGHT / 2 - 8))
        size = 16
        y = SCREENHEIGHT / 2 + size
        if nicks:
            for nick in self.nicks_before_game:
                font = pygame.font.Font(None, size)
                text = font.render(nick, True, (0, 0, 0))
                self.SCREEN.blit(text, (10, y))
                y += size
        pygame.display.update()

    def move_boss(self):
        if self.client.boss.y < 10:
            self.client.boss.y += 0.5
        elif self.client.boss.destination != self.client.boss.x:
            if self.client.boss.x - self.client.boss.destination < 0:
                self.client.boss.x += 2
            else:
                self.client.boss.x -= 2
        else:
            self.client.boss.destination = random.randint(-70, 270)
            if self.client.boss.destination % 2 == 0:
                pass
            else:
                self.client.boss.destination += 2 - self.client.boss.destination % 2

    # def wait_for_server(self):
    # while True:
    # data = self.s.recv(4096)
    # if len(data) == 0:
    # self.s.connect((self.server_address, self.port))
    # else:
    # break
    def move_rockets(self):
        for rocket in self.boss_rockets:
            rocket.y += 2
            if rocket.y > rocket.altitude:
                self.rocket_explode(rocket.x, rocket.y)
                self.boss_rockets.remove(rocket)

    def move_bullets(self):
        for bullet in self.bullets:
            if bullet.y < 0:
                self.bullets.remove(bullet)
            else:
                bullet.y -= SPEED * 10
        for bullet in self.boss_bullets:
            if bullet.y < 0:
                self.boss_bullets.remove(bullet)
            else:
                bullet.y += SPEED * 10
        self.move_rockets()
        for fireball in self.fire_balls_left:
            fireball.x -= 2
            if fireball.x < 0:
                self.fire_balls_left.remove(fireball)
        for fireball in self.fire_balls_right:
            fireball.x += 2
            if fireball.x > 288:
                self.fire_balls_right.remove(fireball)

    def move_pipes(self):
        in_middle = False
        y_value = 0
        delay = 0

        if len(self.pipes) != 0 and (self.pipes[len(self.pipes) - 1].left_pipe_width == 0 or self.pipes[
            len(self.pipes) - 1].right_pipe_width == 0):
            self.get_pipe_size_from_server()

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
                self.client.score += 1
                if round(self.client.score) % LAP == 0:
                    if self.client.boss_level + 1 >= self.boss_level:
                        self.boss_level += 1
                        self.client.boss_level += 1
                        self.add_boss()
                    else:
                        self.client.boss_level += 1

        if in_middle or len(self.pipes) == 0:
            if len(self.pipes) == 0:
                y_value = -10
            if not self.client.boss_mode:
                self.add_pipe(y_value, delay)

        for pipe in self.pipes:
            pipe.update()

        if len(self.pipes) > 0:
            self.pipes[0].update_square()

    def send_data(self, data):
        if self.server_connected:
            try:
                self.s.send(pickle.dumps(data))
            except Exception:
                self.game_ended = True
                self.client.dead = True
                self.started = True
                self.s.close()
                self.server_connected = False
                t = time.time()
                while time.time() - t < 3:
                    self.draw_text_at_center("Server broke down.", False)
                    self.FPSCLOCK.tick(self.FPS)

    def send_position_update(self):
        self.send_data(
            ['position update', self.client.pid, self.client.x, self.client.total_y, self.client.y, self.client.score])

    def get_pipe_size_from_server(self):
        self.send_data(['pipe location', self.client.pid, self.client.score + 1])

    def send_boss_request(self):
        self.send_data(['boss', self.client.pid])

    def delete_client(self):
        self.send_data(['delete client', self.client.pid])

    def add_client(self):
        self.send_data(['add client', self.client.pid, self.nick])

    def add_bullets(self):
        self.send_data(['bullets location', self.client.pid])

    def could_start_game(self):
        self.send_data(['could start game'])

    def get_nicks(self):
        self.send_data(['get nicks'])

    def add_pipe(self, y_value, delay):
        pipe = Pipe(0, 0, self.client)
        pipe.synchronize_with_other_pipes(y_value, delay)
        self.pipes.append(pipe)
        if self.multiplayer:
            self.get_pipe_size_from_server()
        else:
            left, right = Generator().get_width_left_and_beetween(self.client.score)
            pipe.left_pipe_width = left
            pipe.right_pipe_width = right

    def add_bullet(self):
        bullet1 = Bullet(self.client.x + 1, self.client.y - 1)
        bullet2 = Bullet(self.client.x + 17, self.client.y - 1)
        shot_sound.play()
        self.bullets.append(bullet1)
        self.bullets.append(bullet2)

    def add_rocket(self):
        rocket = Rocket(self.client.boss.x + 31, self.client.boss.y + 67, random.randint(280, 490))
        self.boss_rockets.append(rocket)

    def add_boss_bullets(self):
        bullet1 = BossBullet(self.client.boss.x + 10, self.client.boss.y + 76)
        bullet2 = BossBullet(self.client.boss.x + 62, self.client.boss.y + 76)
        self.boss_bullets.append(bullet1)
        self.boss_bullets.append(bullet2)

    def check_collisions(self):
        for pipe in self.pipes:
            if pipe.collides(self.client.x, self.client.y, self.client.width, self.client.height):
                # death_sound.play()
                pygame.mixer.music.stop()
                self.client.dead = True

        for bullet in self.boss_bullets:
            if bullet.if_got_shot(self.client.x, self.client.y, self.client.width, self.client.height):
                self.client.hp -= DAMAGE_BOSS
                self.boss_bullets.remove(bullet)
                if self.client.hp < 0:
                    pygame.mixer.music.stop()
                    death_sound.play()
                    self.client.dead = True

        for fireball in self.fire_balls_right:
            if fireball.if_got_shot(self.client.x, self.client.y, self.client.width, self.client.height):
                self.client.hp -= DAMAGE_BOSS
                self.fire_balls_right.remove(fireball)
                if self.client.hp < 0:
                    death_sound.play()
                    self.client.dead = True

        for fireball in self.fire_balls_left:
            if fireball.if_got_shot(self.client.x, self.client.y, self.client.width, self.client.height):
                self.client.hp -= DAMAGE_BOSS
                self.fire_balls_left.remove(fireball)
                if self.client.hp < 0:
                    death_sound.play()
                    self.client.dead = True

        for rocket in self.boss_rockets:
            if rocket.if_got_shot(self.client.x, self.client.y, self.client.width, self.client.height):
                death_sound.play()
                self.client.dead = True

        for bullet in self.bullets:
            if bullet.if_hit(self.client.boss.x, self.client.boss.y, self.client.boss.width, self.client.boss.height):
                self.client.boss.hp -= DAMAGE_PLAYER
                if self.multiplayer:
                    self.send_data(['hit boss'])
                self.bullets.remove(bullet)
                self.client.score += 0.25
                if self.client.boss.hp < 0:
                    self.client.score += 10
                    pygame.mixer.Sound.play(pygame.mixer.Sound("sounds/round_end.wav"))
                    pygame.mixer.music.stop()
                    if not self.multiplayer:
                        self.client.boss_mode = False
                        self.client.boss.dead = True
                        self.client.boss = None
                        self.client.boss = Boss()
                    self.boss_bullets.clear()
                    self.fire_balls_right.clear()
                    self.fire_balls_left.clear()
                    self.boss_rockets.clear()
                    #if self.multiplayer:
                        #self.send_data(['boss dead', self.client.pid])

        if self.client.y >= SCREENHEIGHT - self.client.height:
            # death_sound.play()
            pygame.mixer.music.stop()
            self.client.dead = True

    def rocket_explode(self, x, y):
        pygame.mixer.Sound.play(pygame.mixer.Sound("sounds/8bit_bomb_explosion.wav"))
        pygame.mixer.music.stop()
        self.fire_balls_left.append(FireBallLeft(x, y))
        self.fire_balls_right.append(FireBallRight(x, y))

    def add_boss(self):
        self.client.boss_mode = True
        self.client.boss_dead = False
        boss_intro.play(5)
        if self.multiplayer:
            self.send_data(['init boss'])
        else:
            self.client.boss = Boss()
