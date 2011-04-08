import socket
import sys
import errno
from code import InteractiveConsole

import eventlet
from eventlet import hubs
from eventlet.support import greenlets, get_errno

try:
    sys.ps1
except AttributeError:
    sys.ps1 = '>>> '
try:
    sys.ps2
except AttributeError:
    sys.ps2 = '... '


class FileProxy(object):
    def __init__(self, f):
        self.f = f

    def isatty(self): 
        return True

    def flush(self): 
        pass

    def write(self, *a, **kw):
        self.f.write(*a, **kw)
        self.f.flush()

    def readline(self, *a):
        return self.f.readline(*a).replace('\r\n', '\n')

    def __getattr__(self, attr):
        return getattr(self.f, attr)


# @@tavis: the `locals` args below mask the built-in function.  Should
# be renamed.
class SocketConsole(greenlets.greenlet):
    def __init__(self, desc, hostport, locals):
        self.hostport = hostport
        self.locals = locals
        # mangle the socket
        self.desc = FileProxy(desc)
        greenlets.greenlet.__init__(self)

    def run(self):
        try:
            console = InteractiveConsole(self.locals)
            console.interact()
        finally:
            self.switch_out()
            self.finalize()

    def switch(self, *args, **kw):
        self.saved = sys.stdin, sys.stderr, sys.stdout
        sys.stdin = sys.stdout = sys.stderr = self.desc
        greenlets.greenlet.switch(self, *args, **kw)

    def switch_out(self):
        sys.stdin, sys.stderr, sys.stdout = self.saved

    def finalize(self):
        # restore the state of the socket
        self.desc = None
        print "backdoor closed to %s:%s" % self.hostport


def backdoor_server(sock, locals=None):
    """ Blocking function that runs a backdoor server on the socket *sock*,
    accepting connections and running backdoor consoles for each client that
    connects.

    The *locals* argument is a dictionary that will be included in the locals()
    of the interpreters.  It can be convenient to stick important application
    variables in here.
    """
    print "backdoor server listening on %s:%s" % sock.getsockname()
    try:
        try:
            while True:
                socketpair = sock.accept()
                backdoor(socketpair, locals)
        except socket.error, e:
            # Broken pipe means it was shutdown
            if get_errno(e) != errno.EPIPE:
                raise
    finally:
        sock.close()


def backdoor((conn, addr), locals=None):
    """Sets up an interactive console on a socket with a single connected
    client.  This does not block the caller, as it spawns a new greenlet to
    handle the console.  This is meant to be called from within an accept loop
    (such as backdoor_server).
    """
    host, port = addr
    print "backdoor to %s:%s" % (host, port)
    fl = conn.makefile("rw")
    console = SocketConsole(fl, (host, port), locals)
    hub = hubs.get_hub()
    hub.schedule_call_global(0, console.switch)


if __name__ == '__main__':
    backdoor_server(eventlet.listen(('127.0.0.1', 9000)), {})
