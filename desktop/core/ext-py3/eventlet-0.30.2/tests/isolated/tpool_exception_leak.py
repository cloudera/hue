__test__ = False

if __name__ == '__main__':
    import eventlet
    import eventlet.tpool
    import gc
    import pprint

    class RequiredException(Exception):
        pass

    class A(object):
        def ok(self):
            return 'ok'

        def err(self):
            raise RequiredException

    a = A()

    # case 1 no exception
    assert eventlet.tpool.Proxy(a).ok() == 'ok'
    # yield to tpool_trampoline(), otherwise e.send(rv) have a reference
    eventlet.sleep(0.1)
    gc.collect()
    refs = gc.get_referrers(a)
    assert len(refs) == 1, 'tpool.Proxy-ied object leaked: {}'.format(pprint.pformat(refs))

    # case 2 with exception
    def test_exception():
        try:
            eventlet.tpool.Proxy(a).err()
            assert False, 'expected exception'
        except RequiredException:
            pass
    test_exception()
    # yield to tpool_trampoline(), otherwise e.send(rv) have a reference
    eventlet.sleep(0.1)
    gc.collect()
    refs = gc.get_referrers(a)
    assert len(refs) == 1, 'tpool.Proxy-ied object leaked: {}'.format(pprint.pformat(refs))

    print('pass')
