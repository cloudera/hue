from __future__ import print_function
__test__ = False


def delattr_silent(x, name):
    try:
        delattr(x, name)
    except AttributeError:
        pass


if __name__ == '__main__':
    # Simulate absence of kqueue even on platforms that support it.
    import select
    delattr_silent(select, 'kqueue')
    delattr_silent(select, 'KQ_FILTER_READ')
    # patcher.original used in hub may reimport and return deleted kqueue attribute
    import eventlet.patcher
    select_original = eventlet.patcher.original('select')
    delattr_silent(select_original, 'kqueue')
    delattr_silent(select_original, 'KQ_FILTER_READ')

    import eventlet.hubs
    default = eventlet.hubs.get_default_hub()
    assert not default.__name__.endswith('kqueue')
    import eventlet.hubs.kqueue
    assert not eventlet.hubs.kqueue.is_available()
    print('pass')
