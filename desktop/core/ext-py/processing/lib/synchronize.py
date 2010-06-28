#
# Module implementing synchronization primitives
#
# processing/synchronize.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

__all__ = [ 'Lock', 'RLock', 'Semaphore', 'BoundedSemaphore', 'Condition',
            'Event']

import threading
import os
import sys

from struct import pack as _pack, unpack as _unpack, calcsize as _calcsize
from time import time as _time, sleep as _sleep

from processing import _processing
from processing.process import currentProcess, _registerAfterFork
from processing.logger import debug
from processing.finalize import Finalize
from processing.forking import assertSpawning

#
# Constants to describe the kind of blocker (normal lock is a bounded sem)
#

RECURSIVE_MUTEX, SEMAPHORE, BOUNDED_SEMAPHORE = range(3)

#
# Base class for semaphores and mutexes; wraps `_processing.SemLock`
#

class SemLock(object):

    def __init__(self, kind, value):
        sl = self._semlock = _processing.SemLock(kind, value)
        debug('created semlock with handle %s' % sl.handle)
        self.__setstate__((sl.handle, sl.kind, sl.maxvalue))

        if sys.platform != 'win32':
            def _afterFork(obj):
                obj._semlock._afterFork()
            _registerAfterFork(self, _afterFork)

    def __getstate__(self):
        assertSpawning(self)
        return self._state

    def __setstate__(self, state):
        self._state = state
        if not hasattr(self, '_semlock'):
            self._semlock = _processing.SemLock._rebuild(*state)
            debug('recreated blocker with handle %r' % state[0])

        self.acquire = self._semlock.acquire
        self.release = self._semlock.release
        self.__enter__ = self._semlock.__enter__
        self.__exit__ = self._semlock.__exit__

#
# Semaphore
#

class Semaphore(SemLock):

    def __init__(self, value=1):
        SemLock.__init__(self, SEMAPHORE, value)

    def getValue(self):
        return self._semlock._getValue()

    def __repr__(self):
        try:
            value = self._semlock._getValue()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            value = 'unknown'
        return '<Semaphore(value=%s)>' % value

#
# Bounded semaphore
#

class BoundedSemaphore(Semaphore):

    def __init__(self, value=1):
        SemLock.__init__(self, BOUNDED_SEMAPHORE, value)

    def __repr__(self):
        try:
            value = self._semlock._getValue()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            value = 'unknown'
        return '<BoundedSemaphore(value=%s, maxvalue=%s)>' % \
               (value, self._semlock.maxvalue)

#
# Non-recursive lock
#

class Lock(SemLock):

    def __init__(self):
        SemLock.__init__(self, BOUNDED_SEMAPHORE, 1)

    def __repr__(self):
        try:
            if self._semlock._isMine():
                name = currentProcess().getName()
                if threading.currentThread().getName() != 'MainThread':
                    name += '|' + threading.currentThread().getName()
            elif self._semlock._getValue() == 1:
                name = 'None'
            elif self._semlock._count() > 0:
                name = 'SomeOtherThread'
            else:
                name = 'SomeOtherProcess'
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            name = 'unknown'
        return '<Lock(owner=%s)>' % name

#
# Recursive lock
#

class RLock(SemLock):

    def __init__(self):
        SemLock.__init__(self, RECURSIVE_MUTEX, 1)

    def __repr__(self):
        try:
            if self._semlock._isMine():
                name = currentProcess().getName()
                if threading.currentThread().getName() != 'MainThread':
                    name += '|' + threading.currentThread().getName()
                count = self._semlock._count()
            elif self._semlock._getValue() == 1:
                name, count = 'None', 0
            elif self._semlock._count() > 0:
                name, count = 'SomeOtherThread', 'nonzero'
            else:
                name, count = 'SomeOtherProcess', 'nonzero'
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            name, count = 'unknown', 'unknown'
        return '<RLock(%s, %s)>' % (name, count)

#
# Condition variable
#

class Condition(object):

    def __init__(self, lock=None):
        state = (lock or RLock(), Semaphore(0), Semaphore(0), Semaphore(0))
        self.__setstate__(state)

    def __getstate__(self):
        assertSpawning(self)
        return self._state

    def __setstate__(self, state):
        (self._lock, self._sleeping_count,
         self._woken_count, self._wait_semaphore) = self._state = state
        self.acquire = self._lock.acquire
        self.release = self._lock.release
        self.__enter__ = self._lock.__enter__
        self.__exit__ = self._lock.__exit__

    def __repr__(self):
        try:
            num_waiters = (self._sleeping_count._semlock._getValue() -
                           self._woken_count._semlock._getValue())
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            num_waiters = 'unkown'
        return '<Condition(%s, %s)>' % (self._lock, num_waiters)

    def wait(self, timeout=None):
        assert self._lock._semlock._isMine(), \
               'must acquire() condition before using wait()'

        # indicate that this thread is going to sleep
        self._sleeping_count.release()

        # release lock
        count = self._lock._semlock._count()
        for i in xrange(count):
            self._lock.release()

        try:
            # wait for notification or timeout
            self._wait_semaphore.acquire(True, timeout)
        finally:
            # indicate that this thread has woken
            self._woken_count.release()

            # reacquire lock
            for i in xrange(count):
                self._lock.acquire()

    def notify(self):
        assert self._lock._semlock._isMine(), 'lock is not owned'
        assert not self._wait_semaphore.acquire(False)
        
        # to take account of timeouts since last notify() we subtract
        # woken_count from sleeping_count and rezero woken_count
        while self._woken_count.acquire(False):
            res = self._sleeping_count.acquire(False)
            assert res
            
        if self._sleeping_count.acquire(False): # try grabbing a sleeper
            self._wait_semaphore.release()      # wake up one sleeper
            self._woken_count.acquire()         # wait for the sleeper to wake
            
            # rezero _wait_semaphore in case a timeout just happened
            self._wait_semaphore.acquire(False)

    def notifyAll(self):
        assert self._lock._semlock._isMine(), 'lock is not owned'
        assert not self._wait_semaphore.acquire(False)

        # to take account of timeouts since last notify*() we subtract
        # woken_count from sleeping_count and rezero woken_count
        while self._woken_count.acquire(False):
            res = self._sleeping_count.acquire(False)
            assert res
            
        sleepers = 0
        while self._sleeping_count.acquire(False):
            self._wait_semaphore.release()        # wake up one sleeper
            sleepers += 1

        if sleepers:
            for i in xrange(sleepers):
                self._woken_count.acquire()       # wait for a sleeper to wake

            # rezero wait_semaphore in case some timeouts just happened
            while self._wait_semaphore.acquire(False):
                pass

#
# Event
#

class Event(object):

    def __init__(self):
        self._cond = Condition(Lock())
        self._flag = Semaphore(0)

    def isSet(self):
        self._cond.acquire()
        try:
            if self._flag.acquire(False):
                self._flag.release()
                return True
            return False
        finally:
            self._cond.release()
    
    def set(self):
        self._cond.acquire()
        try:
            self._flag.acquire(False)
            self._flag.release()
            self._cond.notifyAll()
        finally:
            self._cond.release()

    def clear(self):
        self._cond.acquire()
        try:
            self._flag.acquire(False)
        finally:
            self._cond.release()

    def wait(self, timeout=None):
        self._cond.acquire()
        try:
            if self._flag.acquire(False):
                self._flag.release()
            else:
                self._cond.wait(timeout)
        finally:
            self._cond.release()
