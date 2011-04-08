from eventlet.support import get_errno
from eventlet.hubs import trampoline
BUFFER_SIZE = 4096

import errno
import os
import socket
from socket import socket as _original_socket
import sys
import time
import warnings

__all__ = ['GreenSocket', 'GreenPipe', 'shutdown_safe']

CONNECT_ERR = set((errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK))
CONNECT_SUCCESS = set((0, errno.EISCONN))
if sys.platform[:3]=="win":
    CONNECT_ERR.add(errno.WSAEINVAL)   # Bug 67

# Emulate _fileobject class in 3.x implementation
# Eventually this internal socket structure could be replaced with makefile calls.
try:
    _fileobject = socket._fileobject
except AttributeError:
   def _fileobject(sock, *args, **kwargs):
        return _original_socket.makefile(sock, *args, **kwargs)

def socket_connect(descriptor, address):
    """
    Attempts to connect to the address, returns the descriptor if it succeeds,
    returns None if it needs to trampoline, and raises any exceptions.
    """
    err = descriptor.connect_ex(address)
    if err in CONNECT_ERR:
        return None
    if err not in CONNECT_SUCCESS:
        raise socket.error(err, errno.errorcode[err])
    return descriptor

def socket_checkerr(descriptor):
    err = descriptor.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    if err not in CONNECT_SUCCESS:
        raise socket.error(err, errno.errorcode[err])

def socket_accept(descriptor):
    """
    Attempts to accept() on the descriptor, returns a client,address tuple
    if it succeeds; returns None if it needs to trampoline, and raises
    any exceptions.
    """
    try:
        return descriptor.accept()
    except socket.error, e:
        if get_errno(e) == errno.EWOULDBLOCK:
            return None
        raise


if sys.platform[:3]=="win":
    # winsock sometimes throws ENOTCONN
    SOCKET_BLOCKING = set((errno.EWOULDBLOCK,))
    SOCKET_CLOSED = set((errno.ECONNRESET, errno.ENOTCONN, errno.ESHUTDOWN))
else:
    # oddly, on linux/darwin, an unconnected socket is expected to block,
    # so we treat ENOTCONN the same as EWOULDBLOCK
    SOCKET_BLOCKING = set((errno.EWOULDBLOCK, errno.ENOTCONN))
    SOCKET_CLOSED = set((errno.ECONNRESET, errno.ESHUTDOWN, errno.EPIPE))


def set_nonblocking(fd):
    """
    Sets the descriptor to be nonblocking.  Works on many file-like
    objects as well as sockets.  Only sockets can be nonblocking on
    Windows, however.
    """
    try:
        setblocking = fd.setblocking
    except AttributeError:
        # fd has no setblocking() method. It could be that this version of
        # Python predates socket.setblocking(). In that case, we can still set
        # the flag "by hand" on the underlying OS fileno using the fcntl
        # module.
        try:
            import fcntl
        except ImportError:
            # Whoops, Windows has no fcntl module. This might not be a socket
            # at all, but rather a file-like object with no setblocking()
            # method. In particular, on Windows, pipes don't support
            # non-blocking I/O and therefore don't have that method. Which
            # means fcntl wouldn't help even if we could load it.
            raise NotImplementedError("set_nonblocking() on a file object "
                                      "with no setblocking() method "
                                      "(Windows pipes don't support non-blocking I/O)")
        # We managed to import fcntl.
        fileno = fd.fileno()
        flags = fcntl.fcntl(fileno, fcntl.F_GETFL)
        fcntl.fcntl(fileno, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    else:
        # socket supports setblocking()
        setblocking(0)


try:
    from socket import _GLOBAL_DEFAULT_TIMEOUT
except ImportError:
    _GLOBAL_DEFAULT_TIMEOUT = object()


class GreenSocket(object):
    """
    Green version of socket.socket class, that is intended to be 100%
    API-compatible.
    """
    def __init__(self, family_or_realsock=socket.AF_INET, *args, **kwargs):
        if isinstance(family_or_realsock, (int, long)):
            fd = _original_socket(family_or_realsock, *args, **kwargs)
        else:
            fd = family_or_realsock
            assert not args, args
            assert not kwargs, kwargs

        # import timeout from other socket, if it was there
        try:
            self._timeout = fd.gettimeout() or socket.getdefaulttimeout()
        except AttributeError:
            self._timeout = socket.getdefaulttimeout()
        
        set_nonblocking(fd)
        self.fd = fd
        # when client calls setblocking(0) or settimeout(0) the socket must
        # act non-blocking
        self.act_non_blocking = False

    @property
    def _sock(self):
        return self

    #forward unknown attibutes to fd
    # cache the value for future use.
    # I do not see any simple attribute which could be changed
    # so caching everything in self is fine,
    # If we find such attributes - only attributes having __get__ might be cahed.
    # For now - I do not want to complicate it.
    def __getattr__(self, name):
        attr = getattr(self.fd, name)
        setattr(self, name, attr)
        return attr

    def accept(self):
        if self.act_non_blocking:
            return self.fd.accept()
        fd = self.fd
        while True:
            res = socket_accept(fd)
            if res is not None:
                client, addr = res
                set_nonblocking(client)
                return type(self)(client), addr
            trampoline(fd, read=True, timeout=self.gettimeout(),
                           timeout_exc=socket.timeout("timed out"))

    def connect(self, address):
        if self.act_non_blocking:
            return self.fd.connect(address)
        fd = self.fd
        if self.gettimeout() is None:
            while not socket_connect(fd, address):
                trampoline(fd, write=True)
                socket_checkerr(fd)
        else:
            end = time.time() + self.gettimeout()
            while True:
                if socket_connect(fd, address):
                    return
                if time.time() >= end:
                    raise socket.timeout("timed out")
                trampoline(fd, write=True, timeout=end-time.time(),
                        timeout_exc=socket.timeout("timed out"))
                socket_checkerr(fd)

    def connect_ex(self, address):
        if self.act_non_blocking:
            return self.fd.connect_ex(address)
        fd = self.fd
        if self.gettimeout() is None:
            while not socket_connect(fd, address):
                try:
                    trampoline(fd, write=True)
                    socket_checkerr(fd)
                except socket.error, ex:
                    return get_errno(ex)
        else:
            end = time.time() + self.gettimeout()
            while True:
                try:
                    if socket_connect(fd, address):
                        return 0
                    if time.time() >= end:
                        raise socket.timeout(errno.EAGAIN)
                    trampoline(fd, write=True, timeout=end-time.time(),
                            timeout_exc=socket.timeout(errno.EAGAIN))
                    socket_checkerr(fd)
                except socket.error, ex:
                    return get_errno(ex)

    def dup(self, *args, **kw):
        sock = self.fd.dup(*args, **kw)
        set_nonblocking(sock)
        newsock = type(self)(sock)
        newsock.settimeout(self.gettimeout())
        return newsock

    def makefile(self, *args, **kw):
        return _fileobject(self.dup(), *args, **kw)

    def makeGreenFile(self, *args, **kw):
        warnings.warn("makeGreenFile has been deprecated, please use "
            "makefile instead", DeprecationWarning, stacklevel=2)
        return self.makefile(*args, **kw)

    def recv(self, buflen, flags=0):
        fd = self.fd
        if self.act_non_blocking:
            return fd.recv(buflen, flags)
        while True:
            try:
                return fd.recv(buflen, flags)
            except socket.error, e:
                if get_errno(e) in SOCKET_BLOCKING:
                    pass
                elif get_errno(e) in SOCKET_CLOSED:
                    return ''
                else:
                    raise
            trampoline(fd, 
                read=True, 
                timeout=self.gettimeout(), 
                timeout_exc=socket.timeout("timed out"))

    def recvfrom(self, *args):
        if not self.act_non_blocking:
            trampoline(self.fd, read=True, timeout=self.gettimeout(),
                    timeout_exc=socket.timeout("timed out"))
        return self.fd.recvfrom(*args)

    def recvfrom_into(self, *args):
        if not self.act_non_blocking:
            trampoline(self.fd, read=True, timeout=self.gettimeout(),
                    timeout_exc=socket.timeout("timed out"))
        return self.fd.recvfrom_into(*args)

    def recv_into(self, *args):
        if not self.act_non_blocking:
            trampoline(self.fd, read=True, timeout=self.gettimeout(),
                    timeout_exc=socket.timeout("timed out"))
        return self.fd.recv_into(*args)

    def send(self, data, flags=0):
        fd = self.fd
        if self.act_non_blocking:
            return fd.send(data, flags)

        # blocking socket behavior - sends all, blocks if the buffer is full
        total_sent = 0
        len_data = len(data)

        while 1:
            try:
                total_sent += fd.send(data[total_sent:], flags)
            except socket.error, e:
                if get_errno(e) not in SOCKET_BLOCKING and get_errno(e) not in SOCKET_CLOSED:
                    raise

            if total_sent == len_data:
                break

            trampoline(self.fd, write=True, timeout=self.gettimeout(),
                    timeout_exc=socket.timeout("timed out"))

        return total_sent

    def sendall(self, data, flags=0):
        tail = self.send(data, flags)
        len_data = len(data)
        while tail < len_data:
            tail += self.send(data[tail:], flags)

    def sendto(self, *args):
        trampoline(self.fd, write=True)
        return self.fd.sendto(*args)

    def setblocking(self, flag):
        if flag:
            self.act_non_blocking = False
            self._timeout = None
        else:
            self.act_non_blocking = True
            self._timeout = 0.0

    def settimeout(self, howlong):
        if howlong is None or howlong == _GLOBAL_DEFAULT_TIMEOUT:
            self.setblocking(True)
            return
        try:
            f = howlong.__float__
        except AttributeError:
            raise TypeError('a float is required')
        howlong = f()
        if howlong < 0.0:
            raise ValueError('Timeout value out of range')
        if howlong == 0.0:
            self.setblocking(howlong)
        else:
            self._timeout = howlong

    def gettimeout(self):
        return self._timeout

class _SocketDuckForFd(object):
    """ Class implementing all socket method used by _fileobject in cooperative manner using low level os I/O calls."""
    def __init__(self, fileno):
        self._fileno = fileno

    @property
    def _sock(self):
        return self

    def fileno(self):
        return self._fileno

    def recv(self, buflen):
        while True:
            try:
                data = os.read(self._fileno, buflen)
                return data
            except OSError, e:
                if get_errno(e) != errno.EAGAIN:
                    raise IOError(*e.args)
            trampoline(self, read=True)

    def sendall(self, data):
        len_data = len(data)
        os_write = os.write
        fileno = self._fileno
        try:
            total_sent = os_write(fileno, data)
        except OSError, e:
            if get_errno(e) != errno.EAGAIN:
                raise IOError(*e.args)
            total_sent = 0
        while total_sent <len_data:
            trampoline(self, write=True)
            try:
                total_sent += os_write(fileno, data[total_sent:])
            except OSError, e:
                if get_errno(e) != errno. EAGAIN:
                    raise IOError(*e.args)

    def __del__(self):
        try:
            os.close(self._fileno)
        except:
            # os.close may fail if __init__ didn't complete (i.e file dscriptor passed to popen was invalid
            pass

    def __repr__(self):  
        return "%s:%d" % (self.__class__.__name__, self._fileno)

def _operationOnClosedFile(*args, **kwargs):
    raise ValueError("I/O operation on closed file")

class GreenPipe(_fileobject):
    """
    GreenPipe is a cooperative replacement for file class.
    It will cooperate on pipes. It will block on regular file.
    Differneces from file class:
    - mode is r/w property. Should re r/o
    - encoding property not implemented
    - write/writelines will not raise TypeError exception when non-string data is written
      it will write str(data) instead
    - Universal new lines are not supported and newlines property not implementeded
    - file argument can be descriptor, file name or file object.
    """
    def __init__(self, f, mode='r', bufsize=-1):
        if not isinstance(f, (basestring, int, file)):
            raise TypeError('f(ile) should be int, str, unicode or file, not %r' % f)

        if isinstance(f, basestring):
            f = open(f, mode, 0)
 
        if isinstance(f, int):
            fileno = f
            self._name = "<fd:%d>" % fileno
        else:
            fileno = os.dup(f.fileno())
            self._name = f.name
            if f.mode != mode:
                raise ValueError('file.mode %r does not match mode parameter %r' % (f.mode, mode))
            self._name = f.name
            f.close()

        super(GreenPipe, self).__init__(_SocketDuckForFd(fileno), mode, bufsize)
        set_nonblocking(self)
        self.softspace = 0

    @property
    def name(self): return self._name

    def __repr__(self):
        return "<%s %s %r, mode %r at 0x%x>" % (
            self.closed and 'closed' or 'open',
            self.__class__.__name__,
            self.name,
            self.mode,
            (id(self) < 0) and (sys.maxint +id(self)) or id(self))

    def close(self):
        super(GreenPipe, self).close()
        for method in ['fileno', 'flush', 'isatty', 'next', 'read', 'readinto',
                   'readline', 'readlines', 'seek', 'tell', 'truncate',
                   'write', 'xreadlines', '__iter__', 'writelines']:
            setattr(self, method, _operationOnClosedFile)

    if getattr(file, '__enter__', None):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    def xreadlines(self, buffer):
        return iterator(self)

    def readinto(self, buf):
        data = self.read(len(buf)) #FIXME could it be done without allocating intermediate?
        n = len(data)
        try:
            buf[:n] = data
        except TypeError, err:
            if not isinstance(buf, array.array):
                raise err
            buf[:n] = array.array('c', data)
        return n

    def _get_readahead_len(self):
        try:
            return len(self._rbuf.getvalue()) # StringIO in 2.5
        except AttributeError:
            return len(self._rbuf) # str in 2.4

    def _clear_readahead_buf(self):
        len = self._get_readahead_len()
        if len>0:
            self.read(len)

    def tell(self):
        self.flush()
        try:
            return os.lseek(self.fileno(), 0, 1) - self._get_readahead_len()
        except OSError, e:
            raise IOError(*e.args)

    def seek(self, offset, whence=0):
        self.flush()
        if whence == 1 and offset==0: # tell synonym
            return self.tell()
        if whence == 1: # adjust offset by what is read ahead
            offset -= self.get_readahead_len()
        try:
            rv = os.lseek(self.fileno(), offset, whence)
        except OSError, e:
            raise IOError(*e.args)
        else:
            self._clear_readahead_buf()
            return rv

    if getattr(file, "truncate", None): # not all OSes implement truncate
        def truncate(self, size=-1):
            self.flush()
            if size ==-1:
                size = self.tell()
            try:
                rv = os.ftruncate(self.fileno(), size)
            except OSError, e:
                raise IOError(*e.args)
            else:
                self.seek(size) # move position&clear buffer
                return rv

    def isatty(self):
        try:
            return os.isatty(self.fileno())
        except OSError, e:
            raise IOError(*e.args)


# import SSL module here so we can refer to greenio.SSL.exceptionclass
try:
    from OpenSSL import SSL
except ImportError:
    # pyOpenSSL not installed, define exceptions anyway for convenience
    class SSL(object):
        class WantWriteError(object):
            pass

        class WantReadError(object):
            pass

        class ZeroReturnError(object):
            pass

        class SysCallError(object):
            pass


def shutdown_safe(sock):
    """ Shuts down the socket. This is a convenience method for
    code that wants to gracefully handle regular sockets, SSL.Connection
    sockets from PyOpenSSL and ssl.SSLSocket objects from Python 2.6
    interchangeably.  Both types of ssl socket require a shutdown() before
    close, but they have different arity on their shutdown method.

    Regular sockets don't need a shutdown before close, but it doesn't hurt.
    """
    try:
        try:
            # socket, ssl.SSLSocket
            return sock.shutdown(socket.SHUT_RDWR)
        except TypeError:
            # SSL.Connection
            return sock.shutdown()
    except socket.error, e:
        # we don't care if the socket is already closed;
        # this will often be the case in an http server context
        if get_errno(e) != errno.ENOTCONN:
            raise

