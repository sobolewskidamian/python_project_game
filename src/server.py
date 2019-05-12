import pygame
from pygame.locals import *
import sys
import socket
import asyncore
import random
import pickle

from square import Square
from generator import Generator

from objects.inputBox import InputBox
from objects.submitBox import SubmitBox

FPS = 70
SCREENWIDTH = 800
SCREENHEIGHT = 600

BUFFERSIZE = 512
outgoing = []
clients = {}
pipes = {}
amount_of_players = 0
game_is_running = False
server = None


# port = 4321


def update_world(message):
    arr = pickle.loads(message)

    if arr[0] == 'add client':
        if len(clients) < amount_of_players:
            id = arr[1]
            nick = arr[2]
            client = Square(id)
            client.nick = nick
            clients[id] = client
            print("Client", id, "added")

        if len(clients) == amount_of_players:
            global game_is_running
            game_is_running = True

    elif arr[0] == 'position update':
        playerid = arr[1]
        x = arr[2]
        total_y = arr[3]
        y = arr[4]
        score = arr[5]

        if playerid == -1 or playerid not in clients: return

        clients[playerid].x = x
        clients[playerid].total_y = total_y
        clients[playerid].y = y
        clients[playerid].score = score

        for i in outgoing:
            update = [arr[0]]

            for key, value in clients.items():
                update.append([value.pid, value.x, value.total_y, value.y])

            try:
                i.send(pickle.dumps(update))
            except Exception:
                outgoing.remove(i)
                continue

    elif arr[0] == 'pipe location':
        playerid = arr[1]
        score = arr[2]

        if playerid not in clients: return

        if score not in pipes:
            left, right = Generator().get_width_left_and_beetween(score)
            pipes[score] = [left, right]

        for i in outgoing:
            update = [arr[0], [playerid, pipes[score][0], pipes[score][1]]]

            try:
                i.send(pickle.dumps(update))
            except Exception:
                outgoing.remove(i)
                continue

    elif arr[0] == 'delete client':
        playerid = arr[1]
        if playerid in clients:
            del clients[playerid]
            print('Disconnect player: ', str(playerid))

        if len(clients) == 0:
            pipes.clear()
            game_is_running = False
            asyncore.close_all()

    show_server_info()


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        print('Connection address:' + addr[0] + " " + str(addr[1]))
        client_id = random.randint(1000, 1000000)
        conn.send(pickle.dumps(['add client', client_id]))
        outgoing.append(conn)
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        recieved_data = self.recv(BUFFERSIZE)
        if recieved_data:
            update_world(recieved_data)
        else:
            self.close()


def clean_screen():
    SCREEN.fill((248, 248, 255))
    pygame.display.update()


def set_options():
    clean_screen()
    SCREEN.blit(pygame.font.Font(None, 25).render('Amount of players:', True, pygame.Color('lightskyblue3')),
                (20, SCREENHEIGHT / 2 - 50))
    input_box = InputBox(200, SCREENHEIGHT / 2 - 55, 100, 25)

    SCREEN.blit(pygame.font.Font(None, 25).render('Port:', True, pygame.Color('lightskyblue3')),
                (20, SCREENHEIGHT / 2 - 20))
    input_box2 = InputBox(200, SCREENHEIGHT / 2 - 25, 100, 25)

    submit_box = SubmitBox(SCREENWIDTH / 2 - 65, SCREENHEIGHT / 2 + 50, 130, 32, "Run server")

    while not submit_box.get_active() or input_box.get_text() == '' or input_box2.get_text() == '':
        submit_box.set_not_active()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            input_box.handle_event(event)
            input_box2.handle_event(event)
            submit_box.handle_event(event)

        input_box.draw(SCREEN)
        input_box2.draw(SCREEN)
        submit_box.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    return [input_box.get_text(), input_box2.get_text()]


def show_players():
    SCREEN.fill((248, 248, 255))
    players = ''
    for client in clients:
        players += clients[client].nick + ' ' + str(clients[client].score) + '\n'
    SCREEN.blit(pygame.font.Font(None, 25).render(players, True, pygame.Color('lightskyblue3')),
                (20, SCREENHEIGHT / 2 - 50))

    pygame.display.update()
    FPSCLOCK.tick(FPS)


def show_server_info():
    show_players()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()


def main():
    global SCREEN, FPSCLOCK, amount_of_players
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode([SCREENWIDTH, SCREENHEIGHT], 0, 32)
    pygame.display.set_caption('Vertical game server')

    while True:
        options = set_options()
        amount_of_players = int(options[0])
        port = int(options[1])
        clean_screen()

        MainServer(port)
        asyncore.loop()


if __name__ == '__main__':
    main()
