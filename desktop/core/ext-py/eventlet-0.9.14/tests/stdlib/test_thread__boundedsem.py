"""Test that BoundedSemaphore with a very high bound is as good as unbounded one"""
from eventlet import coros
from eventlet.green import thread

def allocate_lock():
    return coros.semaphore(1, 9999)

original_allocate_lock = thread.allocate_lock
thread.allocate_lock = allocate_lock
original_LockType = thread.LockType
thread.LockType = coros.CappedSemaphore

try:
    import os.path
    execfile(os.path.join(os.path.dirname(__file__), 'test_thread.py'))
finally:
    thread.allocate_lock = original_allocate_lock
    thread.LockType = original_LockType
