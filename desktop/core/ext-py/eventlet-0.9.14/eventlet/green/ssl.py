__ssl = __import__('ssl')

globals().update(dict([(var, getattr(__ssl, var))
                       for var in dir(__ssl) 
                       if not var.startswith('__')]))

import sys
import errno
time = __import__('time')

from eventlet.support import get_errno
from eventlet.hubs import trampoline
from eventlet.greenio import set_nonblocking, GreenSocket, SOCKET_CLOSED, CONNECT_ERR, CONNECT_SUCCESS
orig_socket = __import__('socket')
socket = orig_socket.socket
if sys.version_info >= (2,7):
    has_ciphers = True
    timeout_exc = SSLError
else:
    has_ciphers = False
    timeout_exc = orig_socket.timeout

__patched__ = ['SSLSocket', 'wrap_socket', 'sslwrap_simple']

class GreenSSLSocket(__ssl.SSLSocket):
    """ This is a green version of the SSLSocket class from the ssl module added 
    in 2.6.  For documentation on it, please see the Python standard
    documentation.
    
    Python nonblocking ssl objects don't give errors when the other end
    of the socket is closed (they do notice when the other end is shutdown,
    though).  Any write/read operations will simply hang if the socket is
    closed from the other end.  There is no obvious fix for this problem;
    it appears to be a limitation of Python's ssl object implementation.
    A workaround is to set a reasonable timeout on the socket using
    settimeout(), and to close/reopen the connection when a timeout 
    occurs at an unexpected juncture in the code.
    """
    # we are inheriting from SSLSocket because its constructor calls 
    # do_handshake whose behavior we wish to override
    def __init__(self, sock, *args, **kw):
        if not isinstance(sock, GreenSocket):
            sock = GreenSocket(sock)

        self.act_non_blocking = sock.act_non_blocking
        self._timeout = sock.gettimeout()
        super(GreenSSLSocket, self).__init__(sock.fd, *args, **kw)
       
        # the superclass initializer trashes the methods so we remove
        # the local-object versions of them and let the actual class
        # methods shine through
        try:
            for fn in orig_socket._delegate_methods:
                delattr(self, fn)
        except AttributeError:
            pass
       
    def settimeout(self, timeout):
        self._timeout = timeout
        
    def gettimeout(self):
        return self._timeout
    
    def setblocking(self, flag):
        if flag:
            self.act_non_blocking = False
            self._timeout = None
        else:
            self.act_non_blocking = True
            self._timeout = 0.0

    def _call_trampolining(self, func, *a, **kw):
        if self.act_non_blocking:
            return func(*a, **kw)
        else:
            while True:
                try:
                    return func(*a, **kw)
                except SSLError, exc:
                    if get_errno(exc) == SSL_ERROR_WANT_READ:
                        trampoline(self, 
                                   read=True, 
                                   timeout=self.gettimeout(), 
                                   timeout_exc=timeout_exc('timed out'))
                    elif get_errno(exc) == SSL_ERROR_WANT_WRITE:
                        trampoline(self, 
                                   write=True, 
                                   timeout=self.gettimeout(), 
                                   timeout_exc=timeout_exc('timed out'))
                    else:
                        raise

        
    def write(self, data):
        """Write DATA to the underlying SSL channel.  Returns
        number of bytes of DATA actually transmitted."""
        return self._call_trampolining(
            super(GreenSSLSocket, self).write, data)

    def read(self, len=1024):
        """Read up to LEN bytes and return them.
        Return zero-length string on EOF."""
        return self._call_trampolining(
            super(GreenSSLSocket, self).read,len)

    def send (self, data, flags=0):
        # *NOTE: gross, copied code from ssl.py becase it's not factored well enough to be used as-is
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to send() on %s" %
                    self.__class__)
            while True:
                try:
                    v = self._sslobj.write(data)
                except SSLError, e:
                    if get_errno(e) == SSL_ERROR_WANT_READ:
                        return 0
                    elif get_errno(e) == SSL_ERROR_WANT_WRITE:
                        return 0
                    else:
                        raise
                else:
                    return v
        else:
            while True:
                try:
                    return socket.send(self, data, flags)
                except orig_socket.error, e:
                    if self.act_non_blocking:
                        raise
                    if get_errno(e) == errno.EWOULDBLOCK or \
                       get_errno(e) == errno.ENOTCONN:
                        return 0
                    raise

    def sendto (self, data, addr, flags=0):
        # *NOTE: gross, copied code from ssl.py becase it's not factored well enough to be used as-is
        if self._sslobj:
            raise ValueError("sendto not allowed on instances of %s" %
                             self.__class__)
        else:
            trampoline(self, write=True, timeout_exc=timeout_exc('timed out'))
            return socket.sendto(self, data, addr, flags)

    def sendall (self, data, flags=0):
        # *NOTE: gross, copied code from ssl.py becase it's not factored well enough to be used as-is
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to sendall() on %s" %
                    self.__class__)
            amount = len(data)
            count = 0
            while (count < amount):
                v = self.send(data[count:])
                count += v
            return amount
        else:
            while True:
                try:
                    return socket.sendall(self, buflen, flags)
                except orig_socket.error, e:
                    if self.act_non_blocking:
                        raise
                    if get_errno(e) == errno.EWOULDBLOCK:
                        trampoline(self, write=True, 
                                   timeout=self.gettimeout(), timeout_exc=timeout_exc('timed out'))
                    if get_errno(e) in SOCKET_CLOSED:
                        return ''
                    raise

    def recv(self, buflen=1024, flags=0):
        # *NOTE: gross, copied code from ssl.py becase it's not factored well enough to be used as-is
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to recv() on %s" %
                    self.__class__)
            read = self.read(buflen)
            return read
        else:
            while True:
                try:
                    return socket.recv(self, buflen, flags)
                except orig_socket.error, e:
                    if self.act_non_blocking:
                        raise
                    if get_errno(e) == errno.EWOULDBLOCK:
                        trampoline(self, read=True, 
                                   timeout=self.gettimeout(), timeout_exc=timeout_exc('timed out'))
                    if get_errno(e) in SOCKET_CLOSED:
                        return ''
                    raise

        
    def recv_into (self, buffer, nbytes=None, flags=0):
        if not self.act_non_blocking:
            trampoline(self, read=True, timeout=self.gettimeout(), timeout_exc=timeout_exc('timed out'))
        return super(GreenSSLSocket, self).recv_into(buffer, nbytes, flags)

    def recvfrom (self, addr, buflen=1024, flags=0):
        if not self.act_non_blocking:
            trampoline(self, read=True, timeout=self.gettimeout(), timeout_exc=timeout_exc('timed out'))
        return super(GreenSSLSocket, self).recvfrom(addr, buflen, flags)
        
    def recvfrom_into (self, buffer, nbytes=None, flags=0):
        if not self.act_non_blocking:
            trampoline(self, read=True, timeout=self.gettimeout(), timeout_exc=timeout_exc('timed out'))
        return super(GreenSSLSocket, self).recvfrom_into(buffer, nbytes, flags)

    def unwrap(self):
        return GreenSocket(super(GreenSSLSocket, self).unwrap())

    def do_handshake(self):    
        """Perform a TLS/SSL handshake."""
        return self._call_trampolining(
            super(GreenSSLSocket, self).do_handshake)

    def _socket_connect(self, addr):
        real_connect = socket.connect
        if self.act_non_blocking:
            return real_connect(self, addr)
        else:
            # *NOTE: gross, copied code from greenio because it's not factored
            # well enough to reuse
            if self.gettimeout() is None:
                while True:
                    try:
                        return real_connect(self, addr)
                    except orig_socket.error, exc:
                        if get_errno(exc) in CONNECT_ERR:
                            trampoline(self, write=True)
                        elif get_errno(exc) in CONNECT_SUCCESS:
                            return
                        else:
                            raise
            else:
                end = time.time() + self.gettimeout()
                while True:
                    try:
                        real_connect(self, addr)
                    except orig_socket.error, exc:
                        if get_errno(exc) in CONNECT_ERR:
                            trampoline(self, write=True, 
                                       timeout=end-time.time(), timeout_exc=timeout_exc('timed out'))
                        elif get_errno(exc) in CONNECT_SUCCESS:
                            return
                        else:
                            raise
                    if time.time() >= end:
                        raise timeout_exc('timed out')
    

    def connect(self, addr):
        """Connects to remote ADDR, and then wraps the connection in
        an SSL channel."""
        # *NOTE: grrrrr copied this code from ssl.py because of the reference
        # to socket.connect which we don't want to call directly
        if self._sslobj:
            raise ValueError("attempt to connect already-connected SSLSocket!")
        self._socket_connect(addr)
        if has_ciphers:
            self._sslobj = _ssl.sslwrap(self._sock, False, self.keyfile, self.certfile,
                                        self.cert_reqs, self.ssl_version,
                                        self.ca_certs, self.ciphers)
        else:
            self._sslobj = _ssl.sslwrap(self._sock, False, self.keyfile, self.certfile,
                                        self.cert_reqs, self.ssl_version,
                                        self.ca_certs)
        if self.do_handshake_on_connect:
            self.do_handshake()

    def accept(self):
        """Accepts a new connection from a remote client, and returns
        a tuple containing that new connection wrapped with a server-side
        SSL channel, and the address of the remote client."""
        # RDW grr duplication of code from greenio
        if self.act_non_blocking:
            newsock, addr = socket.accept(self)
        else:
            while True:
                try:
                    newsock, addr = socket.accept(self)
                    set_nonblocking(newsock)
                    break
                except orig_socket.error, e:
                    if get_errno(e) != errno.EWOULDBLOCK:
                        raise
                    trampoline(self, read=True, timeout=self.gettimeout(),
                                   timeout_exc=timeout_exc('timed out'))

        new_ssl = type(self)(newsock,
                          keyfile=self.keyfile,
                          certfile=self.certfile,
                          server_side=True,
                          cert_reqs=self.cert_reqs,
                          ssl_version=self.ssl_version,
                          ca_certs=self.ca_certs,
                          do_handshake_on_connect=self.do_handshake_on_connect,
                          suppress_ragged_eofs=self.suppress_ragged_eofs)
        return (new_ssl, addr)

    def dup(self):
        raise NotImplementedError("Can't dup an ssl object")
                               
SSLSocket = GreenSSLSocket

def wrap_socket(sock, *a, **kw):
    return GreenSSLSocket(sock, *a, **kw)


if hasattr(__ssl, 'sslwrap_simple'):
    def sslwrap_simple(sock, keyfile=None, certfile=None):
        """A replacement for the old socket.ssl function.  Designed
        for compability with Python 2.5 and earlier.  Will disappear in
        Python 3.0."""
        ssl_sock = GreenSSLSocket(sock, keyfile=keyfile, certfile=certfile,
                                  server_side=False, 
                                  cert_reqs=CERT_NONE, 
                                  ssl_version=PROTOCOL_SSLv23, 
                                  ca_certs=None)
        return ssl_sock
