#
# Support for the API of the processing package using threads
#
# processing/dummy/__init__.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = [
    'Process', 'currentProcess', 'activeChildren', 'freezeSupport',
    'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
    'Event', 'Queue', 'Manager', 'Pipe'
    ]

#
# Imports
#

import threading
import sys
import weakref
import array

from processing.dummy.connection import Pipe
from threading import Lock, RLock, Semaphore, BoundedSemaphore, \
         Condition, Event
from Queue import Queue

#
#
#

class DummyProcess(threading.Thread):

    _count = 1

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        if name is None:
            name = 'Thread-%s' % Process._count
        Process._count += 1
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._pid = None
        self._children = weakref.WeakKeyDictionary()
        self._parent = currentProcess()
        self._start_called = False

    def start(self):
        assert self._parent is currentProcess()
        self._start_called = True
        self._parent._children[self] = None
        threading.Thread.start(self)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        if not self.isAlive():
            self._parent._children.pop(self, None)

    def getExitCode(self):
        if self._start_called and not self.isAlive():
            return 0
        else:
            return None

#
#
#

Process = DummyProcess
currentProcess = threading.currentThread
currentProcess()._children = weakref.WeakKeyDictionary()

def activeChildren():
    children = currentProcess()._children
    for p in list(children):
        if not p.isAlive():
            children.pop(p, None)
    return list(children)

def freezeSupport():
    pass

#
#
#

class Namespace(object):
    def __repr__(self):
        items = self.__dict__.items()
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))
        temp.sort()
        return 'Namespace(%s)' % str.join(', ', temp)

dict = dict
list = list

def Array(typecode, sequence, lock=True):
    return array.array(typecode, sequence)

class Value(object):
    def __init__(self, typecode, value, lock=True):
        self._typecode = typecode
        self._value = value
    def _get(self):
        return self._value
    def _set(self, value):
        self._value = value
    value = property(_get, _set)
    def __repr__(self):
        return '<%r(%r, %r)>'%(type(self).__name__,self._typecode,self._value)

def Manager():
    return sys.modules[__name__]

def shutdown():
    pass
