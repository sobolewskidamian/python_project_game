from square import Square

class Server:
    def __init__(self):
        self.pipes = []
        self.clients = {}

    def add_client(self, pid):
        self.clients[pid] = Square(pid)

    def get_client(self, pid):
        return self.clients[pid]
