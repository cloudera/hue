import errno
import new

import eventlet
from eventlet import greenio
from eventlet import patcher
from eventlet.green import os
from eventlet.green import select

patcher.inject('subprocess', globals(), ('select', select))
subprocess_orig = __import__("subprocess")

# This is the meat of this module, the green version of Popen.
class Popen(subprocess_orig.Popen):
    """eventlet-friendly version of subprocess.Popen"""
    # We do not believe that Windows pipes support non-blocking I/O. At least,
    # the Python file objects stored on our base-class object have no
    # setblocking() method, and the Python fcntl module doesn't exist on
    # Windows. (see eventlet.greenio.set_nonblocking()) As the sole purpose of
    # this __init__() override is to wrap the pipes for eventlet-friendly
    # non-blocking I/O, don't even bother overriding it on Windows.
    if not subprocess_orig.mswindows:
        def __init__(self, args, bufsize=0, *argss, **kwds):
            # Forward the call to base-class constructor
            subprocess_orig.Popen.__init__(self, args, 0, *argss, **kwds)
            # Now wrap the pipes, if any. This logic is loosely borrowed from 
            # eventlet.processes.Process.run() method.
            for attr in "stdin", "stdout", "stderr":
                pipe = getattr(self, attr)
                if pipe is not None:
                    wrapped_pipe = greenio.GreenPipe(pipe, pipe.mode, bufsize)
                    setattr(self, attr, wrapped_pipe)
        __init__.__doc__ = subprocess_orig.Popen.__init__.__doc__

    def wait(self, check_interval=0.01):
        # Instead of a blocking OS call, this version of wait() uses logic
        # borrowed from the eventlet 0.2 processes.Process.wait() method.
        try:
            while True:
                status = self.poll()
                if status is not None:
                    return status
                eventlet.sleep(check_interval)
        except OSError, e:
            if e.errno == errno.ECHILD:
                # no child process, this happens if the child process
                # already died and has been cleaned up
                return -1
            else:
                raise
    wait.__doc__ = subprocess_orig.Popen.wait.__doc__

    if not subprocess_orig.mswindows:
        # don't want to rewrite the original _communicate() method, we
        # just want a version that uses eventlet.green.select.select() 
        # instead of select.select().
        try:
            _communicate = new.function(subprocess_orig.Popen._communicate.im_func.func_code,
                                        globals())
        except AttributeError:
            # 2.4 only has communicate
            _communicate = new.function(subprocess_orig.Popen.communicate.im_func.func_code,
                                        globals())
            def communicate(self, input=None):
                return self._communicate(input)

# Borrow subprocess.call() and check_call(), but patch them so they reference
# OUR Popen class rather than subprocess.Popen.
call = new.function(subprocess_orig.call.func_code, globals())
try:
    check_call = new.function(subprocess_orig.check_call.func_code, globals())
except AttributeError:
    pass  # check_call added in 2.5
