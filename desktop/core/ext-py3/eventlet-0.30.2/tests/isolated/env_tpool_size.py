__test__ = False

if __name__ == '__main__':
    import sys
    import time
    from eventlet import tpool
    import eventlet

    current = [0]
    highwater = [0]

    def count():
        current[0] += 1
        time.sleep(0.01)
        if current[0] > highwater[0]:
            highwater[0] = current[0]
        current[0] -= 1

    expected = int(sys.argv[1])
    normal = int(sys.argv[2])
    p = eventlet.GreenPool()
    for i in range(expected * 2):
        p.spawn(tpool.execute, count)
    p.waitall()
    assert highwater[0] > normal, "Highwater %s <= %s" % (highwater[0], normal)
    print('pass')
