#
# Module providing the `Process` class which emulates `threading.Thread`
#
# processing/process.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = [
    'Process', 'currentProcess', 'activeChildren'
    ]

#
# Imports
#

import os
import sys
import time
import signal
import atexit
import weakref
import copy_reg
import itertools

#
# Public functions
#

def currentProcess():
    '''
    Return process object representing the current process
    '''
    return _current_process

def activeChildren():
    '''
    Return list of process objects corresponding to live child processes
    '''
    _cleanup()
    return list(_current_process._children)
    
#
#
#

def _cleanup():
    '''
    Purge `_children` of dead processes
    '''
    for p in list(_current_process._children):
        if p._popen.poll() is not None:
            _current_process._children.discard(p)

#
# The `Process` class
#

class Process(object):
    '''
    Process objects represent activity that is run in a separate process

    The class is analagous to `threading.Thread`
    '''
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        counter = _current_process._counter.next()

        self._identity = _current_process._identity + (counter,)
        self._authkey = _current_process._authkey
        self._daemonic = _current_process._daemonic
        self._parent_pid = os.getpid()
        self._popen = None
        self._exiting = False

        self._target = target
        self._args = tuple(args)
        self._kwargs = kwargs.copy()
        self._name = name or 'Process-' + ':'.join(map(str, self._identity))

    def run(self):
        '''
        Method to be run in sub-process; can be overridden in sub-class
        '''
        if self._target:
            self._target(*self._args, **self._kwargs)
            
    def start(self):
        '''
        Start child process
        '''
        from processing.forking import Popen
        assert self._popen is None, 'cannot start a process twice'
        assert self._parent_pid == os.getpid(), \
               'can only start a process object created by current process'
        _cleanup()
        self._popen = Popen(self)
        _current_process._children.add(self)

    def terminate(self):
        '''
        Terminate process; sends `SIGTERM` signal or uses `TerminateProcess()`
        '''
        self._popen.terminate()
        
    def join(self, timeout=None):
        '''
        Wait until child process terminates
        '''
        assert self._parent_pid == os.getpid(), 'can only join a child process'
        assert self._popen is not None, 'can only join a started process'
        if timeout == 0:
            res = self._popen.poll()
        elif timeout is None:
            res = self._popen.wait()
        else:
            res = self._popen.waitTimeout(timeout)
        if res is not None:
            _current_process._children.discard(self)

    def isAlive(self):
        '''
        Return whether child process is alive
        '''
        if self is _current_process:
            return True
        assert self._parent_pid == os.getpid(), 'can only test a child process'
        if self._popen is None:
            return False
        self._popen.poll()
        return self._popen.returncode is None

    def getName(self):
        '''
        Return name of process
        '''
        return self._name

    def setName(self, name):
        '''
        Set name of process
        '''
        assert type(name) is str, 'name must be a string'
        self._name = name

    def isDaemon(self):
        '''
        Return whether process is a daemon
        '''
        return self._daemonic

    def setDaemon(self, daemonic):
        '''
        Set whether process is a daemon
        '''
        assert self._popen is None, 'process has already started'
        self._daemonic = daemonic

    def getAuthKey(self):
        '''
        Return authorization key of process
        '''
        return self._authkey

    def setAuthKey(self, authkey):
        '''
        Set authorization key of process
        '''
        assert type(authkey) is str, 'value must be a string'
        self._authkey = authkey

    def getExitCode(self):
        '''
        Return exit code of process or `None` if it has yet to stop
        '''
        if self._popen is None:
            return self._popen
        return self._popen.poll()

    def getPid(self):
        '''
        Return PID of process or `None` if it has yet to start
        '''
        if self is _current_process:
            return os.getpid()
        else:
            assert self._parent_pid == os.getpid(), 'not a child process'
            return self._popen and self._popen.pid

    def __repr__(self):
        if self is _current_process:
            status = 'started'
        elif self._parent_pid != os.getpid():
            status = 'unknown'
        elif self._popen is None:
            status = 'initial'
        else:
            if self._popen.poll() is not None:
                status = self.getExitCode()
            else:
                status = 'started'

        if type(status) is int:
            if status == 0:
                status = 'stopped'
            else:
                status = 'stopped[%s]' % _exitcode_to_name.get(status, status)

        return '<%s(%s, %s%s)>' % (type(self).__name__, self._name,
                                   status, self._daemonic and ' daemon' or '')

    ##

    def _bootstrap(self):
        from processing.finalize import _registry
        from processing.logger import info
        
        global _current_process
        try:
            self._children = set()
            self._counter = itertools.count(1)
            sys.stdin.close()
            _registry.clear()
            _current_process = self
            _runAfterForkers()
            info('child process calling self.run()')
            try:
                self.run()
                exitcode = 0
            finally:
                _exitFunction()
        except SystemExit, e:
            if not e.args:
                exitcode = 1
            elif type(e.args[0]) is int:
                exitcode = e.args[0]
            else:
                print >>sys.stderr, e.args[0]
                exitcode = 1
        except:
            exitcode = 1
            import traceback
            print >>sys.stderr, 'Process %s:' % self.getName()
            traceback.print_exc()

        info('process exiting with exitcode %d' % exitcode)
        return exitcode

#
# Create object representing the main process
#

class _MainProcess(Process):

    def __init__(self):
        self._identity = ()
        self._daemonic = False
        self._name = 'MainProcess'
        self._parent_pid = None
        self._popen = None
        self._counter = itertools.count(1)
        self._children = set()
        self._authkey = ''.join('%02x' % ord(c) for c in os.urandom(16))


_current_process = _MainProcess()
del _MainProcess

#
# Give names to some return codes
#

_exitcode_to_name = {}

for name, signum in signal.__dict__.items():
    if name[:3]=='SIG' and '_' not in name:
        _exitcode_to_name[-signum] = name

#
# Make bound and unbound instance methods and class methods picklable
#

def _reduceMethod(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(type(_current_process.start), _reduceMethod)

#
# Support for reinitialization of objects when bootstrapping a child process
#

_afterfork_registry = weakref.WeakValueDictionary()
_afterForkerId = itertools.count().next

def _runAfterForkers():
    # execute in order of registration
    for (index, ident, func), obj in sorted(_afterfork_registry.items()):
        func(obj)
        
def _registerAfterFork(obj, func):
    _afterfork_registry[(_afterForkerId(), id(obj), func)] = obj
    
#
# Clean up on exit
#

def _exitFunction():
    from processing.finalize import _runFinalizers
    from processing.logger import info
    
    _current_process._exiting = True

    info('running all "atexit" finalizers with priority >= 0')
    _runFinalizers(0)

    for p in activeChildren():
        if p._daemonic:
            info('calling `terminate()` for daemon %s', p.getName())
            p._popen.terminate()

    for p in activeChildren():
        info('calling `join()` for process %s', p.getName())
        p.join()

    info('running the remaining "atexit" finalizers')
    _runFinalizers()

atexit.register(_exitFunction)
