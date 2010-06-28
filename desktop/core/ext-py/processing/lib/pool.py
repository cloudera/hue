#
# Module providing the `Pool` class for managing a process pool
#
# processing/pool.py
#
# Copyright (c) 2007-2008, R Oudkerk --- see COPYING.txt
#

__all__ = ['Pool']

#
# Imports
#

import processing
import threading
import Queue
import itertools
import collections
import time

from processing import Process
from processing.logger import debug
from processing.finalize import Finalize
from processing.queue import SimpleQueue

#
# Constants representing the state of a pool
#

RUN = 0
CLOSE = 1
TERMINATE = 2

#
# Miscellaneous
#

newJobId = itertools.count().next

def mapstar(args):
    return map(*args)

#
# Code run by worker processes
#

def worker(inqueue, outqueue, initializer=None, initargs=()):
    put = outqueue.put

    if initializer is not None:
        initializer(*initargs)

    for job, i, func, args, kwds in iter(inqueue.get, None):
        try:
            result = (True, func(*args, **kwds))
        except Exception, e:
            result = (False, e)
        put((job, i, result))

    debug('worker got sentinel -- exiting')
    
#
# Class representing a process pool
#

class Pool(object):
    '''
    Class which supports an async version of the `apply()` builtin
    '''
    def __init__(self, processes=None, initializer=None, initargs=()):
        self._inqueue = SimpleQueue()
        self._outqueue = SimpleQueue()
        self._taskqueue = Queue.Queue()
        self._cache = {}
        self._state = RUN

        if processes is None:
            try:
                processes = processing.cpuCount()
            except NotImplementedError:
                processes = 1
            
        self._pool = [
            Process(target=worker, args=(self._inqueue, self._outqueue,
                                         initializer, initargs))
            for i in range(processes)
            ]
        
        for i, w in enumerate(self._pool):
            w.setName('PoolWorker-' + ':'.join(map(str, w._identity)))
            w.start()
                    
        self._task_handler = threading.Thread(
            target=Pool._handleTasks,
            args=(self._taskqueue, self._inqueue, self._outqueue, self._pool)
            )
        self._task_handler.setDaemon(True)
        self._task_handler._state = RUN
        self._task_handler.start()

        self._result_handler = threading.Thread(
            target=Pool._handleResults,
            args=(self._outqueue, self._cache)
            )
        self._result_handler.setDaemon(True)
        self._result_handler._state = RUN
        self._result_handler.start()

        self._terminate = Finalize(
            self, Pool._terminatePool,
            args=(self._taskqueue, self._inqueue, self._outqueue,
                  self._cache, self._pool, self._task_handler,
                  self._result_handler),
            exitpriority=5
            )

    def apply(self, func, args=(), kwds={}):
        '''
        Equivalent of `apply()` builtin
        '''
        assert self._state == RUN
        return self.applyAsync(func, args, kwds).get()

    def map(self, func, iterable, chunksize=None):
        '''
        Equivalent of `map()` builtin
        '''
        assert self._state == RUN
        return self.mapAsync(func, iterable, chunksize).get()

    def imap(self, func, iterable, chunksize=1):
        '''
        Equivalent of `itertool.imap()` -- can be MUCH slower than `Pool.map()`
        '''
        assert self._state == RUN
        if chunksize == 1:
            result = IMapIterator(self._cache)
            self._taskqueue.put((((result._job, i, func, (x,), {})
                          for i, x in enumerate(iterable)), result._setLength))
            return result
        else:
            assert chunksize > 1
            task_batches = Pool._getTasks(func, iterable, chunksize)
            result = IMapIterator(self._cache)
            self._taskqueue.put((((result._job, i, mapstar, (x,), {})
                      for i, x in enumerate(task_batches)), result._setLength))
            return (item for chunk in result for item in chunk)

    def imapUnordered(self, func, iterable, chunksize=1):
        '''
        Like `imap()` method but ordering of results is arbitrary
        '''
        assert self._state == RUN
        if chunksize == 1:
            result = IMapUnorderedIterator(self._cache)
            self._taskqueue.put((((result._job, i, func, (x,), {})
                          for i, x in enumerate(iterable)), result._setLength))
            return result
        else:
            assert chunksize > 1
            task_batches = Pool._getTasks(func, iterable, chunksize)
            result = IMapUnorderedIterator(self._cache)
            self._taskqueue.put((((result._job, i, mapstar, (x,), {})
                      for i, x in enumerate(task_batches)), result._setLength))
            return (item for chunk in result for item in chunk)
            
    def applyAsync(self, func, args=(), kwds={}, callback=None):
        '''
        Asynchronous equivalent of `apply()` builtin
        '''
        assert self._state == RUN
        result = ApplyResult(self._cache, callback)
        self._taskqueue.put(([(result._job, None, func, args, kwds)], None))
        return result

    def mapAsync(self, func, iterable, chunksize=None, callback=None):
        '''
        Asynchronous equivalent of `map()` builtin
        '''
        assert self._state == RUN
        if not hasattr(iterable, '__len__'):
            iterable = list(iterable)
        
        if chunksize is None:
            chunksize, extra = divmod(len(iterable), len(self._pool) * 4)
            if extra:
                chunksize += 1
                
        task_batches = Pool._getTasks(func, iterable, chunksize)
        result = MapResult(self._cache, chunksize, len(iterable), callback)
        self._taskqueue.put((((result._job, i, mapstar, (x,), {})
                              for i, x in enumerate(task_batches)), None))
        return result

    @staticmethod
    def _handleTasks(taskqueue, inqueue, outqueue, pool):
        thread = threading.currentThread()
        put = inqueue._writer.send

        for taskseq, setLength in iter(taskqueue.get, None):
            i = -1
            for i, task in enumerate(taskseq):
                if thread._state:
                    debug('task handler found thread._state != RUN')
                    break
                put(task)
            else:
                if setLength:
                    debug('doing setLength()')
                    setLength(i+1)
                continue
            break
        else:
            debug('task handler got sentinel')
            
        # tell result handler to finish when cache is empty
        outqueue.put(None)

        # tell workers there is no more work
        debug('task handler sending sentinel to workers')
        for p in pool:
            put(None)

        debug('task handler exiting')

    @staticmethod
    def _handleResults(outqueue, cache):
        thread = threading.currentThread()
        get = outqueue._reader.recv

        for job, i, obj in iter(get, None):
            if thread._state:
                assert thread._state == TERMINATE
                debug('result handler found thread._state=TERMINATE')
                return
            try:
                cache[job]._set(i, obj)
            except KeyError:
                pass
        else:
            debug('result handler got sentinel')

        while cache and thread._state != TERMINATE:
            item = get()
            if item is None:
                debug('result handler ignoring extra sentinel')
                continue
            job, i, obj = item
            try:
                cache[job]._set(i, obj)
            except KeyError:
                pass

        debug('result handler exiting: len(cache)=%s, thread._state=%s',
              len(cache), thread._state)

    @staticmethod
    def _getTasks(func, it, size):
        it = iter(it)
        while 1:
            x = tuple(itertools.islice(it, size))
            if not x:
                return
            yield (func, x)

    def __reduce__(self):
        raise NotImplementedError, \
              'pool objects cannot be passed between processes or pickled'
    
    def close(self):
        debug('closing pool')
        self._state = CLOSE
        self._taskqueue.put(None)

    def terminate(self):
        debug('terminating pool')
        self._state = TERMINATE
        self._terminate()

    def join(self):
        debug('joining pool')
        assert self._state in (CLOSE, TERMINATE)
        self._task_handler.join()
        self._result_handler.join()
        for p in self._pool:
            p.join()

    @staticmethod
    def _terminatePool(taskqueue, inqueue, outqueue, cache, pool,
                        task_handler, result_handler):
        debug('finalizing pool')
        
        if not result_handler.isAlive():
            debug('result handler already finished -- no need to terminate')
            return
        
        cache = {}
        task_handler._state = TERMINATE
        result_handler._state = TERMINATE

        debug('sending sentinels')
        taskqueue.put(None)
        outqueue.put(None)
        
        debug('getting read lock on inqueue')
        inqueue._rlock.acquire()

        debug('terminating workers')
        for p in pool:
            p.terminate()

        if task_handler.isAlive():
            debug('removing tasks from inqueue until task handler finished')
            while task_handler.isAlive() and inqueue._reader.poll():
                inqueue._reader.recv()
                time.sleep(0)

        debug('joining result handler')
        result_handler.join()
        debug('joining task handler')
        task_handler.join()
        debug('joining pool workers')
        for p in pool:
            p.join()
        debug('closing connections')
        inqueue._reader.close()
        outqueue._reader.close()
        inqueue._writer.close()
        outqueue._writer.close()

    # deprecated
    apply_async = applyAsync
    map_async = mapAsync
    imap_unordered = imapUnordered

#
# Class whose instances are returned by `Pool.applyAsync()`
#

class ApplyResult(object):

    def __init__(self, cache, callback):
        self._cond = threading.Condition(threading.Lock())
        self._job = newJobId()
        self._cache = cache
        self._ready = False
        self._callback = callback
        cache[self._job] = self
        
    def ready(self):
        return self._ready
    
    def successful(self):
        assert self._ready
        return self._success
    
    def wait(self, timeout=None):
        self._cond.acquire()
        try:
            if not self._ready:
                self._cond.wait(timeout)
        finally:
            self._cond.release()

    def get(self, timeout=None):
        self.wait(timeout)
        if not self._ready:
            raise processing.TimeoutError
        if self._success:
            return self._value
        else:
            raise self._value

    def _set(self, i, obj):
        self._success, self._value = obj
        if self._callback and self._success:
            self._callback(self._value)
        self._cond.acquire()
        try:
            self._ready = True
            self._cond.notify()
        finally:
            self._cond.release()
        del self._cache[self._job]

#
# Class whose instances are returned by `Pool.mapAsync()`
#

class MapResult(ApplyResult):
    
    def __init__(self, cache, chunksize, length, callback):
        ApplyResult.__init__(self, cache, callback)
        self._success = True
        self._value = [None] * length
        self._chunksize = chunksize
        if chunksize <= 0:
            self._number_left = 0
            self._ready = True
        else:
            self._number_left = length//chunksize + bool(length % chunksize)
        
    def _set(self, i, (success, result)):
        if success:
            self._value[i*self._chunksize:(i+1)*self._chunksize] = result
            self._number_left -= 1
            if self._number_left == 0:
                if self._callback:
                    self._callback(self._value)
                del self._cache[self._job]
                self._cond.acquire()
                try:
                    self._ready = True
                    self._cond.notify()
                finally:
                    self._cond.release()

        else:
            self._success = False
            self._value = result
            del self._cache[self._job]
            self._cond.acquire()
            try:
                self._ready = True
                self._cond.notify()
            finally:
                self._cond.release()

#
# Class whose instances are returned by `Pool.imap()`
#

class IMapIterator(object):

    def __init__(self, cache):
        self._cond = threading.Condition(threading.Lock())
        self._job = newJobId()
        self._cache = cache
        self._items = collections.deque()
        self._index = 0
        self._length = None
        self._unsorted = {}
        cache[self._job] = self
        
    def __iter__(self):
        return self
    
    def next(self, timeout=None):
        self._cond.acquire()
        try:
            try:
                item = self._items.popleft()
            except IndexError:
                if self._index == self._length:
                    raise StopIteration
                self._cond.wait(timeout)
                try:
                    item = self._items.popleft()
                except IndexError:
                    if self._index == self._length:
                        raise StopIteration
                    raise processing.TimeoutError
        finally:
            self._cond.release()

        success, value = item
        if success:
            return value
        raise value
    
    def _set(self, i, obj):
        self._cond.acquire()
        try:
            if self._index == i:
                self._items.append(obj)
                self._index += 1
                while self._index in self._unsorted:
                    obj = self._unsorted.pop(self._index)
                    self._items.append(obj)
                    self._index += 1
                self._cond.notify()
            else:
                self._unsorted[i] = obj
                
            if self._index == self._length:
                del self._cache[self._job]
        finally:
            self._cond.release()
            
    def _setLength(self, length):
        self._cond.acquire()
        try:
            self._length = length
            if self._index == self._length:
                self._cond.notify()
                del self._cache[self._job]
        finally:
            self._cond.release()

#
# Class whose instances are returned by `Pool.imapUnordered()`
#

class IMapUnorderedIterator(IMapIterator):

    def _set(self, i, obj):
        self._cond.acquire()
        try:
            self._items.append(obj)
            self._index += 1
            self._cond.notify()
            if self._index == self._length:
                del self._cache[self._job]
        finally:
            self._cond.release()
