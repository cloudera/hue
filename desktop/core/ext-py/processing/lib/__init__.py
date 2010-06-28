#
# Package analogous to 'threading.py' but using processes
#
# processing/__init__.py
#
# This package is intended to duplicate the functionality (and much of
# the API) of threading.py but uses processes instead of threads.  A
# subpackage 'processing.dummy' has the same API but is a simple
# wrapper for 'threading'.
#
# Try calling `processing.doc.main()` to read the html documentation in
# in a webbrowser.
#
#
# Copyright (c) 2006-2008, R Oudkerk
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of author nor the names of any contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#

__version__ = '0.52'

__all__ = [
    'Process', 'currentProcess', 'activeChildren', 'freezeSupport',
    'Manager', 'Pipe', 'cpuCount', 'getLogger', 'enableLogging',
    'BufferTooShort'
    ]

#
# Absolute imports
#

import os
import sys

#
# Relative imports - Python 2.4 does not have relative import syntax
#

import _processing
from process import Process, currentProcess, activeChildren
from logger import NOTSET, SUBDEBUG, DEBUG, INFO, SUBWARNING

#
#
#

HAVE_NATIVE_SEMAPHORE = hasattr(_processing, 'SemLock')
ORIGINAL_DIR = os.path.abspath(os.getcwd())

#
# Definitions not depending on native semaphores
#

ProcessError = _processing.ProcessError
BufferTooShort = _processing.BufferTooShort

def Manager():
    '''
    Returns a manager associated with a running server process

    The managers methods such as `Lock()`, `Condition()` and `Queue()`
    can be used to create shared objects.
    '''
    from processing.managers import SyncManager
    m = SyncManager()
    m.start()
    return m

def Pipe(duplex=True):
    '''
    Returns two connection object connected by a pipe
    '''
    from processing.connection import Pipe
    return Pipe(duplex)

def cpuCount():
    '''
    Returns the number of CPUs in the system
    '''
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            num = 0
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            num = 0
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            num = 0
        
    if num >= 1:
        return num
    else:
        raise NotImplementedError, 'cannot determine number of cpus'

def getLogger():
    '''
    Returns logger used by processing
    '''
    from processing.logger import getLogger
    return getLogger()

def enableLogging(level, HandlerType=None, handlerArgs=(), format=None):
    '''
    Enable logging using `level` as the debug level
    '''
    from processing.logger import enableLogging
    return enableLogging(level, HandlerType, handlerArgs, format)

def freezeSupport():
    '''
    Check whether this is a fake forked process in a frozen executable.
    If so then run code specified by commandline and exit.
    '''
    if sys.platform == 'win32' and getattr(sys, 'frozen', False):
        from processing.forking import freezeSupport
        freezeSupport()

def waitForAnyChild(block=True):
    '''
    Wait for a child process returning (pid, exitcode, process_object).

    Similar to os.wait() but plays nicely with `processing`:
    waitForAnyChild()[:2] is equivalent to os.wait().
    '''
    from processing.forking import waitForAnyChild
    return waitForAnyChild(block)

#
# Definitions depending on native semaphores
#

if HAVE_NATIVE_SEMAPHORE:
    
    __all__ += [
        'TimeoutError', 'Lock', 'RLock', 'Semaphore',
        'BoundedSemaphore', 'Condition', 'Event', 'Queue', 'Pool',
        'Value', 'Array'
        ]
    
    class TimeoutError(ProcessError):
        pass

    def Lock():
        '''
        Returns a non-recursive lock object
        '''
        from processing.synchronize import Lock
        return Lock()

    def RLock():
        '''
        Returns a recursive lock object
        '''
        from processing.synchronize import RLock
        return RLock()

    def Condition(lock=None):
        '''
        Returns a condition object
        '''
        from processing.synchronize import Condition
        return Condition(lock)

    def Semaphore(value=1):
        '''
        Returns a semaphore object
        '''
        from processing.synchronize import Semaphore
        return Semaphore(value)

    def BoundedSemaphore(value=1):
        '''
        Returns a bounded object
        '''
        from processing.synchronize import BoundedSemaphore
        return BoundedSemaphore(value)

    def Event():
        '''
        Returns an event object
        '''
        from processing.synchronize import Event
        return Event()

    def Queue(maxsize=0):
        '''
        Returns a queue object implemented using a pipe
        '''
        from processing.queue import Queue
        return Queue(maxsize)

    def Pool(processes=None, initializer=None, initargs=()):
        '''
        Returns a process pool object
        '''
        from processing.pool import Pool
        return Pool(processes, initializer, initargs)

    def Value(typecode_or_type, *args, **kwds):
        '''
        Returns a shared object
        '''
        from processing.sharedctypes import Value
        return Value(typecode_or_type, *args, **kwds)

    def Array(typecode_or_type, size_or_initializer, **kwds):
        '''
        Returns a shared array
        '''
        from processing.sharedctypes import Array
        return Array(typecode_or_type, size_or_initializer, **kwds)
