# Threading.current_thread does not change when using greenthreads?
# https://github.com/eventlet/eventlet/issues/172
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()

    import threading

    g = set()

    def fun():
        ct = threading.current_thread()
        g.add(ct.name)

    ts = tuple(threading.Thread(target=fun, name='t{}'.format(i)) for i in range(3))
    for t in ts:
        t.start()
    for t in ts:
        t.join()

    assert g == set(('t0', 't1', 't2')), repr(g)

    print('pass')
