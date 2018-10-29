__test__ = False


def aaa(lock, e1, e2):
    e1.set()
    with lock:
        e2.wait()


def bbb(lock, e1, e2):
    e1.wait()
    e2.set()
    with lock:
        pass


if __name__ == '__main__':
    import threading
    import eventlet
    eventlet.monkey_patch()
    test_lock = threading.RLock()

    e1, e2 = threading.Event(), threading.Event()
    a = eventlet.spawn(aaa, test_lock, e1, e2)
    b = eventlet.spawn(bbb, test_lock, e1, e2)
    a.wait()
    b.wait()
    print('pass')
