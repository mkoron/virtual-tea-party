from asyncore import dispatcher
from asynchat import async_chat
import asyncore, socket

PORT = 5005
NAME = 'TestChat'

class EndSession(Exception): pass

class CommandHandler():
    def uknnowm(self, session, cmd):
        session.push('Uknown command: {}\r\n'.format(cmd).encode())

    def handle(self, session, line):
        if not line.strip(): return
        parts = line.split(b' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        meth = getattr(self, 'do_' + cmd.decode(), None)
        if callable(meth):
            meth(session, line)
        else:
            self.uknnowm(session, cmd)

class Room(CommandHandler):
    
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
    
    def add(self, session):
        self.broadcast(session.name + b' has entered the room.\r\n')
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):
        Room.remove(self, session)
        self.broadcast(session.name.encode() + b' has left the room.\r\n')

    def do_say(self, session, line):
        self.broadcast(session.name+b': '+line+b'\r\n')

    def do_look(self, session, line):
        session.push(b'The following are in this room:\r\n')
        for other in self.sessions:
            session.push(other.name + b'\r\n')

    def do_who(self, session, line):
        session.push(b'The following are logged in:\r\n')
        for name in self.server.users:
            session.push(name + b'\r\n')


class LogoutRoom(Room):

    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatSession(async_chat):

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

class ChatServer(dispatcher):

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