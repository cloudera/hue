__test__ = False


def take(lock, e1, e2):
    with lock:
        e1.set()
        e2.wait()


if __name__ == '__main__':
    import sys
    import threading
    lock = threading.RLock()
    import eventlet
    eventlet.monkey_patch()

    lock.acquire()
    lock.release()

    e1, e2 = threading.Event(), threading.Event()
    eventlet.spawn(take, lock, e1, e2)
    e1.wait()
    assert not lock.acquire(blocking=0)
    e2.set()
    print('pass')
