import socket


class client:

    def __init__(self, id:str, name:str, socket: socket.socket):
        self.id = id
        self.name = name
        self.socket = socket