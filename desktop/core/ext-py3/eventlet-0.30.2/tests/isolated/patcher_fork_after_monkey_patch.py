# Monkey patching interferes with threading in Python 3.7
# https://github.com/eventlet/eventlet/issues/592
__test__ = False


def check(n, mod, tag):
    assert len(mod._active) == n, 'Expected {} {} threads, got {}'.format(n, tag, mod._active)


if __name__ == '__main__':
    import eventlet
    import eventlet.patcher
    eventlet.monkey_patch()
    import os
    import sys
    import threading
    _threading = eventlet.patcher.original('threading')
    import eventlet.green.threading

    def target():
        eventlet.sleep(0.1)

    threads = [
        threading.Thread(target=target, name='patched'),
        _threading.Thread(target=target, name='original-1'),
        _threading.Thread(target=target, name='original-2'),
        eventlet.green.threading.Thread(target=target, name='green-1'),
        eventlet.green.threading.Thread(target=target, name='green-2'),
        eventlet.green.threading.Thread(target=target, name='green-3'),
    ]
    for t in threads:
        t.start()

    check(2, threading, 'pre-fork patched')
    check(3, _threading, 'pre-fork original')
    check(4, eventlet.green.threading, 'pre-fork green')

    if os.fork() == 0:
        # Inside the child, we should only have a main thread,
        # but old pythons make it difficult to ensure
        if sys.version_info >= (3, 7):
            check(1, threading, 'child post-fork patched')
            check(1, _threading, 'child post-fork original')
        check(1, eventlet.green.threading, 'child post-fork green')
        sys.exit()
    else:
        os.wait()

    check(2, threading, 'post-fork patched')
    check(3, _threading, 'post-fork original')
    check(4, eventlet.green.threading, 'post-fork green')

    for t in threads:
        t.join()

    check(1, threading, 'post-join patched')
    check(1, _threading, 'post-join original')
    check(1, eventlet.green.threading, 'post-join green')
    print('pass')
