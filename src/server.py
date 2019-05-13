import sys
import time
import socket
import asyncore
import random
import pickle

from square import Square
from generator import Generator

BUFFERSIZE = 512
outgoing = []
clients = {}
pipes = {}
amount_of_players = 0
game_is_running = False
dead_players = {}
last_access_time = time.time()


def print_new_game():
    print("╔============================================╗")
    print("╠================= NEW GAME =================╣")
    print("╚============================================╝")


def update_world(message):
    global game_is_running
    try:
        arr = pickle.loads(message)

        if arr[0] == 'delete client':
            playerid = arr[1]
            if playerid in clients:
                dead_players[clients[playerid]] = clients[playerid].score
                del clients[playerid]
                print('Disconnect player: ', str(playerid))

            if len(clients) == 0:
                time.sleep(0.1)
                pipes.clear()
                print_stats()
                dead_players.clear()
                print_new_game()
                game_is_running = False

                for i in outgoing:
                    update = ['start adding']
                    try:
                        i.send(pickle.dumps(update))
                    except Exception:
                        outgoing.remove(i)
                        continue

        elif arr[0] == 'add client':
            id = arr[1]
            if len(clients) < amount_of_players and not game_is_running:
                nick = arr[2]
                if id not in clients:
                    client = Square(id)
                    client.nick = nick
                    clients[id] = client
                    print("Client", id, "added")
                    for i in outgoing:
                        update = ['client added', id]
                        try:
                            i.send(pickle.dumps(update))
                        except Exception:
                            outgoing.remove(i)
                            continue

                    if len(clients) == amount_of_players:
                        game_is_running = True
                        for i in outgoing:
                            start = ['start game']
                            try:
                                i.send(pickle.dumps(start))
                            except Exception:
                                outgoing.remove(i)
                                continue
            else:
                for i in outgoing:
                    update = ['game is running', id]

                    try:
                        i.send(pickle.dumps(update))
                    except Exception:
                        outgoing.remove(i)
                        continue

        elif arr[0] == 'could start game':
            if len(clients) == amount_of_players:
                for i in outgoing:
                    start = ['start game']
                    try:
                        i.send(pickle.dumps(start))
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

    except Exception:
        print(end='')


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.bind(('', port))
        except Exception:
            print("Port", port, "is busy")
            exit(0)
        self.listen(10)
        print("╔==================")
        print("║ port:\t\t", port, )
        print("║ players:\t", amount_of_players)
        print("╚==================")
        print_new_game()

    def handle_accept(self):
        conn, addr = self.accept()
        print('Connection address:' + addr[0] + " " + str(addr[1]))
        client_id = random.randint(1000, 1000000)
        conn.send(pickle.dumps(['add client', client_id]))
        outgoing.append(conn)
        SecondaryServer(conn)

    def handle_close(self):
        self.close()


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        received_data = self.recv(BUFFERSIZE)
        if received_data:
            update_world(received_data)
        else:
            self.close()


def print_stats():
    print()
    print("╔=============╗")
    print("╠=== STATS ===╣")
    print("╚=============╝")
    winner_nick = ''
    winner_score = -1
    for player in dead_players:
        print(player.nick, dead_players[player])
        if dead_players[player] > winner_score:
            winner_nick = player.nick
            winner_score = dead_players[player]

    print()
    print("╔======================")
    print("║ Winner:", winner_nick)
    print("╠======================")
    print("║ Score:", winner_score)
    print("╚======================")


def main(argv):
    global amount_of_players

    if len(argv) == 3:
        amount_of_players = int(argv[1])
        port = int(argv[2])

        MainServer(port)
        asyncore.loop()
    elif len(argv) != 3 or int(argv[1]) <= 0 or int(argv[2]) <= 0:
        print("Usage:")
        print(argv[0], "amount_of_players port")


if __name__ == '__main__':
    main(sys.argv)
