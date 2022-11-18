from __future__ import print_function
__test__ = False


class Foo(object):
    pass

if __name__ == '__main__':
    import eventlet.hubs
    eventlet.hubs.use_hub(Foo)
    hub = eventlet.hubs.get_hub()
    assert isinstance(hub, Foo), repr(hub)
    print('pass')
