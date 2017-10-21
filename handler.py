"""
A cmd lookalike handler.
"""


class CommandHandler():
    def uknnowm(self, session, cmd):
        session.push('Unknown command: {}\r\n'.format(cmd).encode())

    def handle(self, session, line):
        if not line.strip():
            return
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
