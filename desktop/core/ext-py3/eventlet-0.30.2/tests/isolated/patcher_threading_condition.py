# Issue #185: test threading.Condition with monkey-patching
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()

    import threading

    def func(c):
        with c:
            c.notify()

    c = threading.Condition()
    with c:
        t = threading.Thread(target=func, args=(c,))
        t.start()
        c.wait()

    print('pass')
