import sys
import time
import socket
import asyncore
import pickle

from generator import Generator
from square import Square
from boss import Boss
from bullets import DAMAGE_PLAYER

BUFFERSIZE = 512
offline_time = 10
outgoing = []
clients = {}
client_times = {}
pipes = {}
boss = Boss()
amount_of_clients = 0
game_is_running = False
dead_clients = {}
last_access_time = time.time()
boss_number = 1
game_id = 1


def print_new_game():
    print("╔════════════════════════════════════════════╗")
    print("╠═════════════════ NEW GAME ═════════════════╣")
    print("╠════════════════════════════════════════════╝")


def send_to_all(data):
    for i in outgoing:
        try:
            i.send(pickle.dumps(data))
        except Exception:
            outgoing.remove(i)
            continue


def action_when_no_players():
    global game_is_running, game_id, boss
    time.sleep(0.1)
    pipes.clear()
    print_stats()
    dead_clients.clear()
    boss = Boss()
    print_new_game()
    game_is_running = False
    game_id += 1
    send_to_all(['start adding'])


def update_world(message):
    global game_is_running, boss
    try:
        arr = pickle.loads(message)

        if arr[0] == 'delete client':
            client_id = arr[1]
            if client_id in clients:
                dead_clients[clients[client_id]] = clients[client_id].score
                del clients[client_id]
                if client_id in client_times: del client_times[client_id]
                print('║ Disconnect player: ', str(client_id))

            if len(clients) == 0:
                action_when_no_players()

        elif arr[0] == 'add client':
            id = arr[1]
            if id == -1: return
            if id in clients:
                send_to_all(['client added', id])
                return
            if len(clients) < amount_of_clients and not game_is_running:
                nick = arr[2]
                if id not in clients:
                    client = Square(id)
                    client.nick = nick
                    clients[id] = client
                    print("║ Client", id, "added")
                    send_to_all(['client added', id])

                    if len(clients) == amount_of_clients:
                        game_is_running = True
                        for id in clients:
                            client_times[id] = time.time()
                        send_to_all(['start game', game_id, id])

            remove_offline_clients()

        elif arr[0] == 'could start game':
            if len(clients) == amount_of_clients:
                start = ['start game', game_id]
                for id in clients:
                    start.append(id)
                send_to_all(start)

        elif arr[0] == 'position update':
            client_id = arr[1]
            x = arr[2]
            total_y = arr[3]
            y = arr[4]
            score = arr[5]

            if client_id == -1 or client_id not in clients: return

            client_times[client_id] = time.time()
            clients[client_id].x = x
            clients[client_id].total_y = total_y
            clients[client_id].y = y
            clients[client_id].score = score

            to_send = ['position update', game_id]
            for key, value in clients.items():
                to_send.append([value.pid, value.x, value.total_y, value.y, value.nick])
            send_to_all(to_send)

        elif arr[0] == 'pipe location':
            client_id = arr[1]
            score = arr[2]

            if client_id not in clients: return

            if score not in pipes:
                left, right = Generator().get_width_left_and_beetween(score)
                pipes[score] = [left, right]

            send_to_all(['pipe location', [client_id, pipes[score][0], pipes[score][1]]])

        elif arr[0] == 'get nicks':
            data = [arr[0]]
            for id in clients:
                data.append(clients[id].nick)

            send_to_all(data)

        elif arr[0] == 'init boss':
            if boss.hp <= 0:
                boss = Boss()
            send_to_all(['init boss', boss.hp])

        elif arr[0] == 'hit boss':
            boss.hp -= DAMAGE_PLAYER
            if boss.hp <= 0:
                send_to_all(['boss dead'])
            else:
                send_to_all(['get hp', boss.hp])

        elif arr[0] == 'get hp':
            send_to_all(['get hp', boss.hp])

    except Exception:
        print(end='')


def remove_offline_clients():
    global client_times
    for id in client_times:
        if time.time() - client_times[id] > offline_time:
            if id in clients:
                del clients[id]
            print('║ Disconnect player: ', str(id), "(offline)")
            send_to_all(['client removed', id])

    client_times = {key: val for key, val in client_times.items() if key in clients}

    if len(clients) == 0:
        action_when_no_players()


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
        print("╔══════════════════════")
        print("║ ip:", socket.gethostbyname(socket.gethostname()))
        print("║ port:\t\t", port, )
        print("║ players:\t", amount_of_clients)
        print("╚══════════════════════")
        print_new_game()

    def handle_accept(self):
        if game_is_running:
            remove_offline_clients()
        else:
            conn, addr = self.accept()
            print('║ Connection address:' + addr[0] + " " + str(addr[1]))
            conn.send(pickle.dumps(['add client']))
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
    print("╠══════════════════════╗")
    print("╠═══════ STATS ════════╣")
    print("╠══════════════════════╝")
    winner_nick = ''
    winner_score = -1
    for client in dead_clients:
        print("║", client.nick, dead_clients[client])
        if dead_clients[client] > winner_score:
            winner_nick = client.nick
            winner_score = dead_clients[client]

    print("╠══════════════════════")
    print("║ Winner:", winner_nick)
    print("║ Score:", winner_score)
    print("╚═════════════════════════════════════════════")


def main(argv):
    global amount_of_clients

    if len(argv) == 3:
        amount_of_clients = int(argv[1])
        port = int(argv[2])

        try:
            MainServer(port)
            asyncore.loop()
        except Exception:
            # MainServer.close()
            print("Server stopped")
    elif len(argv) != 3 or int(argv[1]) <= 0 or int(argv[2]) <= 0:
        print("Usage:")
        print(argv[0], "amount_of_players port")


if __name__ == '__main__':
    main(sys.argv)
