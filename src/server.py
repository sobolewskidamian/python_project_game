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
port = 4321


def update_world(message):
    arr = pickle.loads(message)

    if arr[0] == 'add client':
        id = arr[1]
        client = Square(id)
        clients[id] = client
        print("Client", id, "added")

    elif arr[0] == 'position update':
        playerid = arr[1]
        x = arr[2]
        total_y = arr[3]
        y = arr[4]

        if playerid == -1 or playerid not in clients: return

        clients[playerid].x = x
        clients[playerid].total_y = total_y
        clients[playerid].y = y

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


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        print('Connection address:' + addr[0] + " " + str(addr[1]))
        outgoing.append(conn)
        client_id = random.randint(1000, 1000000)
        conn.send(pickle.dumps(['add client', client_id]))
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        recieved_data = self.recv(BUFFERSIZE)
        if recieved_data:
            update_world(recieved_data)
        else:
            self.close()


if __name__ == '__main__':
    MainServer(port)
    asyncore.loop()
