"""
The program is a simple chat server with just one room.

Example:

    You can use the program as following:

        python server.py

    After the server is up you can connect with it using for example:

        telnet 127.0.0.1 5005

    Once connected this are the commands:

        login <name>     Used to log into the server

        logout           Used to logout from the server

        say <statement>  Used to say something

        look             Used to find out who is in the same room

        who              Used to find out who is logged onto the server

"""
from room import LoginRoom, LogoutRoom, ChatRoom
from chat import ChatSession
from exceptions import EndSession
import asyncore

PORT = 5005
NAME = 'TestChat'

import socket
from asyncore import dispatcher


class ChatServer(dispatcher):
    """
    A simple chat server with a single room.
    """

    def __init__(self, port, name):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.name = name
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)


if __name__ == '__main__':
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()
