import warnings
warnings.warn("eventlet.processes is deprecated in favor of "
 "eventlet.green.subprocess, which is API-compatible with the standard "
 " library subprocess module.",
    DeprecationWarning, stacklevel=2)


import errno
import os
import popen2
import signal

from eventlet import api
from eventlet import pools
from eventlet import greenio


class DeadProcess(RuntimeError):
    pass

def cooperative_wait(pobj, check_interval=0.01):
    """ Waits for a child process to exit, returning the status
    code.

    Unlike ``os.wait``, :func:`cooperative_wait` does not block the entire
    process, only the calling coroutine.  If the child process does not die,
    :func:`cooperative_wait` could wait forever.

    The argument *check_interval* is the amount of time, in seconds, that
    :func:`cooperative_wait` will sleep between calls to ``os.waitpid``.
    """
    try:
        while True:
            status = pobj.poll()
            if status >= 0:
                return status
            api.sleep(check_interval)
    except OSError, e:
        if e.errno == errno.ECHILD:
            # no child process, this happens if the child process
            # already died and has been cleaned up, or if you just
            # called with a random pid value
            return -1
        else:
            raise


class Process(object):
    """Construct Process objects, then call read, and write on them."""
    process_number = 0
    def __init__(self, command, args, dead_callback=lambda:None):
        self.process_number = self.process_number + 1
        Process.process_number = self.process_number
        self.command = command
        self.args = args
        self._dead_callback = dead_callback
        self.run()

    def run(self):
        self.dead = False
        self.started = False
        self.popen4 = None

        ## We use popen4 so that read() will read from either stdout or stderr
        self.popen4 = popen2.Popen4([self.command] + self.args)
        child_stdout_stderr = self.popen4.fromchild
        child_stdin = self.popen4.tochild
        self.child_stdout_stderr = greenio.GreenPipe(child_stdout_stderr, child_stdout_stderr.mode, 0)
        self.child_stdin = greenio.GreenPipe(child_stdin, child_stdin.mode, 0)

        self.sendall = self.child_stdin.write
        self.send = self.child_stdin.write
        self.recv = self.child_stdout_stderr.read
        self.readline = self.child_stdout_stderr.readline
        self._read_first_result = False

    def wait(self):
        return cooperative_wait(self.popen4)

    def dead_callback(self):
        self.wait()
        self.dead = True
        if self._dead_callback:
            self._dead_callback()

    def makefile(self, mode, *arg):
        if mode.startswith('r'):
            return self.child_stdout_stderr
        if mode.startswith('w'):
            return self.child_stdin
        raise RuntimeError("Unknown mode", mode)

    def read(self, amount=None):
        """Reads from the stdout and stderr of the child process.
        The first call to read() will return a string; subsequent
        calls may raise a DeadProcess when EOF occurs on the pipe.
        """
        result = self.child_stdout_stderr.read(amount)
        if result == '' and self._read_first_result:
            # This process is dead.
            self.dead_callback()
            raise DeadProcess
        else:
            self._read_first_result = True
        return result

    def write(self, stuff):
        written = 0
        try:
            written = self.child_stdin.write(stuff)
            self.child_stdin.flush()
        except ValueError, e:
            ## File was closed
            assert str(e) == 'I/O operation on closed file'
        if written == 0:
            self.dead_callback()
            raise DeadProcess

    def flush(self):
        self.child_stdin.flush()

    def close(self):
        self.child_stdout_stderr.close()
        self.child_stdin.close()
        self.dead_callback()

    def close_stdin(self):
        self.child_stdin.close()

    def kill(self, sig=None):
        if sig == None:
            sig = signal.SIGTERM
        pid = self.getpid()
        os.kill(pid, sig)

    def getpid(self):
        return self.popen4.pid


class ProcessPool(pools.Pool):
    def __init__(self, command, args=None, min_size=0, max_size=4):
        """*command*
            the command to run
        """
        self.command = command
        if args is None:
            args = []
        self.args = args
        pools.Pool.__init__(self, min_size, max_size)

    def create(self):
        """Generate a process
        """
        def dead_callback():
            self.current_size -= 1
        return Process(self.command, self.args, dead_callback)

    def put(self, item):
        if not item.dead:
            if item.popen4.poll() != -1:
                item.dead_callback()
            else:
                pools.Pool.put(self, item)
