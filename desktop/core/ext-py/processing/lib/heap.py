#
# Module which supports allocation of memory from an mmap
#
# processing/heap.py
#
# Copyright (c) 2007-2008, R Oudkerk --- see COPYING.txt
#

import bisect
import mmap
import tempfile
import os
import sys
import thread
import itertools

from processing import _processing
from processing.finalize import Finalize
from processing.logger import info
from processing.forking import assertSpawning

__all__ = ['BufferWrapper']

#
# Inheirtable class which wraps an mmap, and from which blocks can be allocated
#

if sys.platform == 'win32':

    from processing._processing import win32

    class Arena(object):

        _nextid = itertools.count().next

        def __init__(self, size):
            self.size = size
            self.name = 'pym-%d-%d' % (os.getpid(), Arena._nextid())
            self.buffer = mmap.mmap(0, self.size, tagname=self.name)
            assert win32.GetLastError() == 0, 'tagname already in use'
            self._state = (self.size, self.name)

        def __getstate__(self):
            assertSpawning(self)
            return self._state

        def __setstate__(self, state):
            self.size, self.name = self._state = state
            self.buffer = mmap.mmap(0, self.size, tagname=self.name)
            assert win32.GetLastError() == win32.ERROR_ALREADY_EXISTS

else:

    class Arena(object):

        def __init__(self, size):
            if sys.version_info >= (2, 5, 0):
                self.buffer = mmap.mmap(-1, size)
                self.size = size
                self.name = None
            else:
                fd, self.name = tempfile.mkstemp(prefix='pym-')
                self.size = remaining = size
                while remaining > 0:
                    remaining -= os.write(fd, '\0' * remaining)
                self.buffer = mmap.mmap(fd, size)
                os.close(fd)

                if sys.platform == 'cygwin':
                    # cannot unlink file until it is no longer in use
                    def _finalize_heap(mmap, unlink, name):
                        mmap.close()
                        unlink(name)
                    Finalize(
                        self, _finalize_heap,
                        args=(self.buffer, os.unlink, name),
                        exitpriority=-10
                        )
                else:
                    os.unlink(self.name)

        def __getstate__(self):
            assertSpawning(self)     # will fail

#
# Class allowing allocation of chunks of memory from arenas
#

class Heap(object):

    _alignment = 8

    def __init__(self, size=4096):
        self._lastpid = os.getpid()
        self._lock = thread.allocate_lock()
        self._size = size
        self._lengths = []
        self._len_to_seq = {}
        self._start_to_block = {}
        self._stop_to_block = {}
        self._allocated_blocks = set()
        self._arenas = []

    def _roundUp(self, n):
        mask = self._alignment - 1
        return (max(1, n) + mask) & ~mask

    def _malloc(self, size):
        # returns a large enough block -- it might be much larger
        i = bisect.bisect_left(self._lengths, size)
        if i == len(self._lengths):
            length = max(self._size, size)
            self._size *= 2
            info('allocating a new mmap of length %d', length)
            arena = Arena(length)
            self._arenas.append(arena)
            return (arena, 0, length)
        else:
            length = self._lengths[i]
            seq = self._len_to_seq[length]
            block = seq.pop()
            if not seq:
                del self._len_to_seq[length], self._lengths[i]

        (arena, start, stop) = block
        del self._start_to_block[(arena, start)]
        del self._stop_to_block[(arena, stop)]
        return block

    def _free(self, block):
        # free location and try to merge with neighbours
        (arena, start, stop) = block

        try:
            prev_block = self._stop_to_block[(arena, start)]
        except KeyError:
            pass
        else:
            start, _ = self._absorb(prev_block)

        try:
            next_block = self._start_to_block[(arena, stop)]
        except KeyError:
            pass
        else:
            _, stop = self._absorb(next_block)

        block = (arena, start, stop)
        length = stop - start

        try:
            self._len_to_seq[length].append(block)
        except KeyError:
            self._len_to_seq[length] = [block]
            bisect.insort(self._lengths, length)

        self._start_to_block[(arena, start)] = block
        self._stop_to_block[(arena, stop)] = block

    def _absorb(self, block):
        # deregister this block so it can be merged with a neighbour
        (arena, start, stop) = block
        del self._start_to_block[(arena, start)]
        del self._stop_to_block[(arena, stop)]

        length = stop - start
        seq = self._len_to_seq[length]
        seq.remove(block)
        if not seq:
            del self._len_to_seq[length]
            self._lengths.remove(length)

        return start, stop

    def free(self, block):
        # free a block returned by malloc()
        assert os.getpid() == self._lastpid
        self._lock.acquire()
        try:
            self._allocated_blocks.remove(block)
            self._free(block)
        finally:
            self._lock.release()

    def malloc(self, size):
        # return a block of right size (possibly rounded up)
        if os.getpid() != self._lastpid:
            self.__init__()                     # reinitialize after fork
        self._lock.acquire()
        try:
            size = self._roundUp(size)
            (arena, start, stop) = self._malloc(size)
            new_stop = start + size
            if new_stop < stop:
                self._free((arena, new_stop, stop))
            block = (arena, start, new_stop)
            self._allocated_blocks.add(block)
            return block
        finally:
            self._lock.release()

#
# Class representing a chunk of an mmap -- can be inherited
#

class BufferWrapper(object):

    _heap = Heap()

    def __init__(self, size):
        assert 0 <= size <= sys.maxint
        block = BufferWrapper._heap.malloc(size)
        self._state = (block, size)
        Finalize(self, BufferWrapper._heap.free, args=(block,))

    def getAddress(self):
        (arena, start, stop), size = self._state
        address, length = _processing.addressOfBuffer(arena.buffer)
        assert size <= length
        return address + start

    def getView(self):
        (arena, start, stop), size = self._state
        return _processing.readWriteBuffer(arena.buffer, start, size)

    def getSize(self):
        return self._state[1]
