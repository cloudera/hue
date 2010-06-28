#
# A higher level module for using sockets (or Windows named pipes)
#
# processing/connection.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Client', 'Listener', 'Pipe' ]

import os
import sys
import socket
import time
import tempfile
import itertools

from processing import _processing, currentProcess
from processing.finalize import Finalize
from processing.logger import subDebug
from processing.reduction import connections_are_picklable

try:
    from processing._processing import win32
except ImportError:
    pass

#
#
#

BUFSIZE = 8192

_nextId = itertools.count().next

default_family = 'AF_INET'
families = ['AF_INET']

if hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']

if sys.platform == 'win32':
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

#
#
#

def arbitraryAddress(family):
    '''
    Return an arbitrary free address for the given family
    '''
    if family == 'AF_INET':
        return ('localhost', 0)
    elif family == 'AF_UNIX':
        return tempfile.mktemp(prefix='pyc-%d-%d-' % (os.getpid(), _nextId()))
    elif family == 'AF_PIPE':
        return tempfile.mktemp(
            prefix=r'\\.\pipe\pyc-%d-%d-' % (os.getpid(), _nextId())
            )
    else:
        raise ValueError, 'unrecognized family'


def addressType(address):
    '''
    Return the types of the address

    This can be 'AF_INET', 'AF_UNIX', or 'AF_PIPE'
    '''
    if type(address) == tuple:
        return 'AF_INET'
    elif type(address) is str and address.startswith('\\\\'):
        return 'AF_PIPE'
    elif type(address) is str:
        return 'AF_UNIX'
    else:
        raise ValueError, 'address type of %r unrecognized' % address

#
# Public functions
#

class Listener(object):
    '''
    Returns a listener object.

    This is a wrapper for a bound socket which is 'listening' for
    connections, or for a Windows named pipe.
    '''
    def __init__(self, address=None, family=None, backlog=1,
                 authenticate=False, authkey=None):
        '''
        `address`
           The address to be used by the bound socket
           or named pipe of `self`.

        `family`
           The type of the socket or named pipe to use.

           This can be one of the strings 'AF_INET' (for a TCP
           socket), 'AF_UNIX' (for a Unix domain socket) or 'AF_PIPE'
           (for a Windows named pipe).  Of these only the first is
           guaranteed to be available.

           If `family` is None than the family is inferred by the
           format of `address`.  If `address` is unspecified then
           a default is chosen which is dependent on the platform.
           This default is the family which is assumed to be the
           fastest available.

        `backlog`
           If the `self` uses a socket then this is passed to the
           `listen()` method of the socket once it has been bound.

        `authenticate`
           If this is true then digest authentication is used even if
           `authkey` is` None`.

        `authkey`
           If `authkey` is a string then it will be used as the
           authentication key; otherwise it must be `None`.

           If `authkey` is `None` and `authenticate` is true then
           `currentProcess.getAuthKey()` is used as the authentication
           key.

           If `authkey` is `None` and `authentication` is false then
           no authentication is done.
        '''
        family = family or (address and addressType(address)) \
                 or default_family
        address = address or arbitraryAddress(family)

        if family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        else:
            self._listener = SocketListener(address, family, backlog)

        if authenticate and authkey is None:
            authkey = currentProcess().getAuthKey()
        elif authenticate:
            assert type(authkey) is str

        self._authkey = authkey

    def accept(self):
        '''
        Accept a connection on the bound socket or named pipe of `self`.

        Returns a `Connection` object.
        '''
        c = self._listener.accept()
        if self._authkey:
            deliverChallenge(c, self._authkey)
            answerChallenge(c, self._authkey)
        return c

    def close(self):
        '''
        Close the bound socket or named pipe of `self`.
        '''
        return self._listener.close()

    address = property(lambda self: self._listener._address)
    last_accepted = property(lambda self: self._listener._last_accepted)


def Client(address, family=None, authenticate=False, authkey=None):
    '''
    Returns a connection to the address of a `Listener`
    '''
    family = family or addressType(address)
    if family == 'AF_PIPE':
        c = PipeClient(address)
    else:
        c = SocketClient(address)

    if authenticate and authkey is None:
        authkey = currentProcess().getAuthKey()
    elif authenticate:
        assert type(authkey) is str

    if authkey is not None:
        answerChallenge(c, authkey)
        deliverChallenge(c, authkey)

    return c


if sys.platform != 'win32':

    def Pipe(duplex=True):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        if duplex:
            s1, s2 = socket.socketpair()
            c1 = _processing.Connection(s1.fileno())
            c2 = _processing.Connection(s2.fileno())
            s1.close()
            s2.close()
        else:
            fd1, fd2 = os.pipe()
            c1 = _processing.Connection(fd1, duplicate=False)
            c2 = _processing.Connection(fd2, duplicate=False)

        return c1, c2
    
else:

    def Pipe(duplex=True):
        '''
        Returns pair of connection objects at either end of a pipe
        '''
        address = arbitraryAddress('AF_PIPE')
        if duplex:
            openmode = win32.PIPE_ACCESS_DUPLEX
            access = win32.GENERIC_READ | win32.GENERIC_WRITE
            obsize, ibsize = BUFSIZE, BUFSIZE
        else:
            openmode = win32.PIPE_ACCESS_INBOUND
            access = win32.GENERIC_WRITE
            obsize, ibsize = 0, BUFSIZE

        h1 = win32.CreateNamedPipe(
            address, openmode,
            win32.PIPE_TYPE_MESSAGE | win32.PIPE_READMODE_MESSAGE |
            win32.PIPE_WAIT,
            1, obsize, ibsize, win32.NMPWAIT_WAIT_FOREVER, win32.NULL
            )
        h2 = win32.CreateFile(
            address, access, 0, win32.NULL, win32.OPEN_EXISTING, 0, win32.NULL
            )
        win32.SetNamedPipeHandleState(
            h2, win32.PIPE_READMODE_MESSAGE, None, None
            )

        try:
            win32.ConnectNamedPipe(h1, win32.NULL)
        except WindowsError, e:
            if e.args[0] != win32.ERROR_PIPE_CONNECTED:
                raise

        c1 = _processing.PipeConnection(h1, duplicate=False)
        c2 = _processing.PipeConnection(h2, duplicate=False)
        
        return c1, c2

#
# Definitions for connections based on sockets
#

class SocketListener(object):
    '''
    Represtation of a socket which is bound to an address and listening
    '''
    def __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        self._socket.bind(address)
        if family == 'AF_UNIX':
            os.chmod(address, int('0600', 8))  # readable/writable only by user
        self._socket.listen(backlog)
        address = self._socket.getsockname()
        if type(address) is tuple:
            address = (socket.getfqdn(address[0]),) + address[1:]
        self._address = address
        self._family = family
        self._last_accepted = None

        subDebug('listener bound to address %r', self._address)

        if family == 'AF_UNIX':
            self._unlink = Finalize(
                self, os.unlink, args=(self._address,), exitpriority=0
                )
        else:
            self._unlink = None

    def accept(self):
        s, self._last_accepted = self._socket.accept()
        conn = _processing.Connection(s.fileno())
        s.close()
        return conn

    def close(self):
        self._socket.close()
        if self._unlink is not None:
            self._unlink()


def SocketClient(address):
    '''
    Return a connection object connected to the socket given by `address`
    '''
    family = addressType(address)
    s = socket.socket( getattr(socket, family) )

    endtime = time.time() + 10

    while endtime > time.time():
        try:
            s.connect(address)
        except socket.error, e:
            if e.args[0] != 10061:    # 10061 => connection refused
                raise
            time.sleep(0.01)
        else:
            break
    else:
        raise

    conn = _processing.Connection(s.fileno())
    s.close()
    return conn

#
# Definitions for connections based on named pipes
#

if sys.platform == 'win32':

    class PipeListener(object):
        '''
        Representation of a named pipe
        '''        
        def __init__(self, address, backlog=None):
            self._address = address
            handle = win32.CreateNamedPipe(
                address, win32.PIPE_ACCESS_DUPLEX,
                win32.PIPE_TYPE_MESSAGE | win32.PIPE_READMODE_MESSAGE |
                win32.PIPE_WAIT,
                win32.PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE,
                win32.NMPWAIT_WAIT_FOREVER, win32.NULL
                )
            self._handle_queue = [handle]
            self._last_accepted = None
            
            subDebug('listener created with address=%r', self._address)

            self.close = Finalize(
                self, PipeListener._finalize_pipelistener,
                args=(self._handle_queue, self._address), exitpriority=0
                )
            
        def accept(self):
            newhandle = win32.CreateNamedPipe(
                self._address, win32.PIPE_ACCESS_DUPLEX,
                win32.PIPE_TYPE_MESSAGE | win32.PIPE_READMODE_MESSAGE |
                win32.PIPE_WAIT,
                win32.PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE,
                win32.NMPWAIT_WAIT_FOREVER, win32.NULL
                )
            self._handle_queue.append(newhandle)
            handle = self._handle_queue.pop(0)
            try:
                win32.ConnectNamedPipe(handle, win32.NULL)
            except WindowsError, e:
                if e.args[0] != win32.ERROR_PIPE_CONNECTED:
                    raise
            return _processing.PipeConnection(handle, duplicate=False)

        @staticmethod
        def _finalize_pipelistener(queue, address):
            subDebug('closing listener with address=%r', address)
            for handle in queue:
                win32.CloseHandle(handle)
        
    def PipeClient(address):
        '''
        Return a connection object connected to the pipe given by `address`
        '''
        endtime = time.time() + 10

        while endtime > time.time():
            try:
                win32.WaitNamedPipe(address, 1000)
                h = win32.CreateFile(
                    address, win32.GENERIC_READ | win32.GENERIC_WRITE,
                    0, win32.NULL, win32.OPEN_EXISTING, 0, win32.NULL
                    )
            except WindowsError, e:
                if e.args[0] not in (win32.ERROR_SEM_TIMEOUT,
                                     win32.ERROR_PIPE_BUSY):
                    raise
            else:
                break
        else:
            raise

        win32.SetNamedPipeHandleState(
            h, win32.PIPE_READMODE_MESSAGE, None, None
            )
        return _processing.PipeConnection(h, duplicate=False)

#
# Authentication stuff
#

class AuthenticationError(Exception):
    pass

def deliverChallenge(connection, authkey):
    import hmac, sha
    assert type(authkey) is str, '%r is not a string' % authkey
    try:
        message = os.urandom(20)
    except AttributeError:
        import random
        message = ''.join(str(random.randrange(256)) for i in range(20))
    connection.sendBytes('#CHALLENGE:' + message)
    digest = hmac.new(authkey, message, sha).digest()
    response = connection.recvBytes()
    if response == digest:
        connection.sendBytes('#WELCOME')
    else:
        connection.sendBytes('#AUTHENTICATION_FAILED')
        raise AuthenticationError, 'digest received was wrong'

def answerChallenge(connection, authkey):
    import hmac, sha
    assert type(authkey) is str, '%r is not a string' % authkey
    message = connection.recvBytes()
    assert message[:11] == '#CHALLENGE:', 'message = %r' % message
    message = message[11:]
    digest = hmac.new(authkey, message, sha).digest()
    connection.sendBytes(digest)
    response = connection.recvBytes()
    if response != '#WELCOME':
        raise AuthenticationError, 'digest sent was rejected'

# deprecated
deliver_Challenge = deliverChallenge
answer_challenge = answerChallenge
