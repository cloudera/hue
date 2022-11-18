import errno
import os

from eventlet.greenio.base import (
    _operation_on_closed_file,
    greenpipe_doc,
    set_nonblocking,
    socket,
    SOCKET_BLOCKING,
)
from eventlet.hubs import trampoline, notify_close, notify_opened, IOClosed
from eventlet.support import get_errno
import six

__all__ = ['_fileobject', 'GreenPipe']

_fileobject = socket._fileobject


class GreenPipe(_fileobject):

    __doc__ = greenpipe_doc

    def __init__(self, f, mode='r', bufsize=-1):
        if not isinstance(f, six.string_types + (int, file)):
            raise TypeError('f(ile) should be int, str, unicode or file, not %r' % f)

        if isinstance(f, six.string_types):
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
    def name(self):
        return self._name

    def __repr__(self):
        return "<%s %s %r, mode %r at 0x%x>" % (
            self.closed and 'closed' or 'open',
            self.__class__.__name__,
            self.name,
            self.mode,
            (id(self) < 0) and (sys.maxint + id(self)) or id(self))

    def close(self):
        super(GreenPipe, self).close()
        for method in [
                'fileno', 'flush', 'isatty', 'next', 'read', 'readinto',
                'readline', 'readlines', 'seek', 'tell', 'truncate',
                'write', 'xreadlines', '__iter__', '__next__', 'writelines']:
            setattr(self, method, _operation_on_closed_file)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _get_readahead_len(self):
        return len(self._rbuf.getvalue())

    def _clear_readahead_buf(self):
        len = self._get_readahead_len()
        if len > 0:
            self.read(len)

    def tell(self):
        self.flush()
        try:
            return os.lseek(self.fileno(), 0, 1) - self._get_readahead_len()
        except OSError as e:
            raise IOError(*e.args)

    def seek(self, offset, whence=0):
        self.flush()
        if whence == 1 and offset == 0:  # tell synonym
            return self.tell()
        if whence == 1:  # adjust offset by what is read ahead
            offset -= self._get_readahead_len()
        try:
            rv = os.lseek(self.fileno(), offset, whence)
        except OSError as e:
            raise IOError(*e.args)
        else:
            self._clear_readahead_buf()
            return rv

    if getattr(file, "truncate", None):  # not all OSes implement truncate
        def truncate(self, size=-1):
            self.flush()
            if size == -1:
                size = self.tell()
            try:
                rv = os.ftruncate(self.fileno(), size)
            except OSError as e:
                raise IOError(*e.args)
            else:
                self.seek(size)  # move position&clear buffer
                return rv

    def isatty(self):
        try:
            return os.isatty(self.fileno())
        except OSError as e:
            raise IOError(*e.args)


class _SocketDuckForFd(object):
    """Class implementing all socket method used by _fileobject
    in cooperative manner using low level os I/O calls.
    """
    _refcount = 0

    def __init__(self, fileno):
        self._fileno = fileno
        notify_opened(fileno)
        self._closed = False

    def _trampoline(self, fd, read=False, write=False, timeout=None, timeout_exc=None):
        if self._closed:
            # Don't trampoline if we're already closed.
            raise IOClosed()
        try:
            return trampoline(fd, read=read, write=write, timeout=timeout,
                              timeout_exc=timeout_exc,
                              mark_as_closed=self._mark_as_closed)
        except IOClosed:
            # Our fileno has been obsoleted. Defang ourselves to
            # prevent spurious closes.
            self._mark_as_closed()
            raise

    def _mark_as_closed(self):
        current = self._closed
        self._closed = True
        return current

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
            except OSError as e:
                if get_errno(e) not in SOCKET_BLOCKING:
                    raise IOError(*e.args)
            self._trampoline(self, read=True)

    def recv_into(self, buf, nbytes=0, flags=0):
        if nbytes == 0:
            nbytes = len(buf)
        data = self.recv(nbytes)
        buf[:nbytes] = data
        return len(data)

    def send(self, data):
        while True:
            try:
                return os.write(self._fileno, data)
            except OSError as e:
                if get_errno(e) not in SOCKET_BLOCKING:
                    raise IOError(*e.args)
                else:
                    trampoline(self, write=True)

    def sendall(self, data):
        len_data = len(data)
        os_write = os.write
        fileno = self._fileno
        try:
            total_sent = os_write(fileno, data)
        except OSError as e:
            if get_errno(e) != errno.EAGAIN:
                raise IOError(*e.args)
            total_sent = 0
        while total_sent < len_data:
            self._trampoline(self, write=True)
            try:
                total_sent += os_write(fileno, data[total_sent:])
            except OSError as e:
                if get_errno(e) != errno. EAGAIN:
                    raise IOError(*e.args)

    def __del__(self):
        self._close()

    def _close(self):
        was_closed = self._mark_as_closed()
        if was_closed:
            return
        if notify_close:
            # If closing from __del__, notify_close may have
            # already been cleaned up and set to None
            notify_close(self._fileno)
        try:
            os.close(self._fileno)
        except:
            # os.close may fail if __init__ didn't complete
            # (i.e file dscriptor passed to popen was invalid
            pass

    def __repr__(self):
        return "%s:%d" % (self.__class__.__name__, self._fileno)

    def _reuse(self):
        self._refcount += 1

    def _drop(self):
        self._refcount -= 1
        if self._refcount == 0:
            self._close()
