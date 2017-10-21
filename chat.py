"""
Handles the communication between the users.
"""

from asynchat import async_chat
from room import LoginRoom
from exceptions import EndSession


class ChatSession(async_chat):
    """
    A single session, which takes care of the communication with a single
    user.
    """

    def __init__(self, server, sock):
        super().__init__(sock)
        self.server = server
        self.set_terminator(b"\r\n")
        self.data = []
        self.enter(LoginRoom(server))

    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = b''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
