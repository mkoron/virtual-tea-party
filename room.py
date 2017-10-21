"""
Represents normal chat rooms and other states.
"""
import handler
from exceptions import EndSession


class Room(handler.CommandHandler):
    """
    A generic environment that may contain one or more users.
    It takes care of basic command handling and broadcasting.
    """

    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        self.sessions.append(session)

    def remove(self, session):
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        raise EndSession


class LoginRoom(Room):
    """
    A room for a single person who has just connected.
    """

    def add(self, session):
        Room.add(self, session)
        self.broadcast('Welcome to {}\r\n'.format(self.server.name).encode())

    def unknown(self, session, cmd):
        session.push(b'Please log in\nUse "login <nick>"\r\n')

    def do_login(self, session, line):
        name = line.strip()

        if not name:
            session.push(b'Please enter a name\r\n')
        elif name in self.server.users:
            session.push(b'The name "{}" is taken.\r\n'.format(name).encode())
            session.push(b'Please try again.\r\n')
        else:
            session.name = name
            session.enter(self.server.main_room)


class ChatRoom(Room):
    """
    A room for multiple users who can chat with each others.
    """

    def add(self, session):
        self.broadcast(session.name + b' has entered the room.\r\n')
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):
        Room.remove(self, session)
        self.broadcast(session.name.encode() + b' has left the room.\r\n')

    def do_say(self, session, line):
        self.broadcast(session.name + b': ' + line + b'\r\n')

    def do_look(self, session, line):
        session.push(b'The following are in this room:\r\n')
        for other in self.sessions:
            session.push(other.name + b'\r\n')

    def do_who(self, session, line):
        session.push(b'The following are logged in:\r\n')
        for name in self.server.users:
            session.push(name + b'\r\n')


class LogoutRoom(Room):
    """
    The sole purpose is to remove the user's name from the server.
    """

    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass
