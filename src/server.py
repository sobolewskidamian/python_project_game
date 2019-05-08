from square import Square
from generator import Generator


class Server:
    def __init__(self):
        self.pipes = {}
        self.clients = {}

    def add_client(self, pid):
        self.clients[pid] = Square(pid)

    def get_client(self, pid):
        return self.clients[pid]

    def add_pipe(self, level):
        if level not in self.pipes:
            left, right = Generator().get_width_left_and_beetween(level)
            self.pipes[level] = [left, right]

    def get_pipe(self, level):
        self.add_pipe(level)
        return self.pipes[level]
