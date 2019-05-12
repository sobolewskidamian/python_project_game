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
dead_players = {}


# port = 4321


def update_world(message):
    global game_is_running
    arr = pickle.loads(message)

    if arr[0] == 'add client':
        if len(clients) < amount_of_players and not game_is_running:
            id = arr[1]
            nick = arr[2]
            client = Square(id)
            client.nick = nick
            clients[id] = client
            print("Client", id, "added")

            if len(clients) == amount_of_players:
                game_is_running = True

                for i in outgoing:
                    update = ['start game']

                    try:
                        i.send(pickle.dumps(update))
                    except Exception:
                        outgoing.remove(i)
                        continue
        else:
            for i in outgoing:
                update = ['game is running', arr[1]]

                try:
                    i.send(pickle.dumps(update))
                except Exception:
                    outgoing.remove(i)
                    continue

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
            dead_players[clients[playerid].nick] = clients[playerid].score
            del clients[playerid]
            print('Disconnect player: ', str(playerid))

        if len(clients) == 0:
            pipes.clear()
            game_is_running = False
            print_stats()
            print("============== NEW GAME ==============")


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)
        print("-------------------------")
        print(port, amount_of_players)
        print("-------------------------")

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


def print_stats():
    winner_nick = ''
    winner_score = 0
    for nick in dead_players:
        print(nick, dead_players[nick])
        if dead_players[nick] > winner_score:
            winner_nick = nick
            winner_score = dead_players[nick]
    print()
    print("Winner:", winner_nick, "score:", winner_score)


def main():
    global SCREEN, FPSCLOCK, amount_of_players

    # options = set_options()
    amount_of_players = 2  # int(options[0])
    port = 4321  # int(options[1])

    MainServer(port)
    asyncore.loop()


if __name__ == '__main__':
    main()
