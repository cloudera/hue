__test__ = False

if __name__ == '__main__':
    import MySQLdb as m
    from eventlet import patcher
    from eventlet.green import MySQLdb as gm
    patcher.monkey_patch(all=True, MySQLdb=True)
    patched_set = set(patcher.already_patched) - set(['psycopg'])
    assert patched_set == frozenset([
        'MySQLdb',
        'os',
        'select',
        'socket',
        'subprocess',
        'thread',
        'time',
    ])
    assert m.connect == gm.connect
    print('pass')
