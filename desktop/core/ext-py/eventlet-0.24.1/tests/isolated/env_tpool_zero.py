__test__ = False

if __name__ == '__main__':
    import warnings
    from eventlet import tpool
    g = [False]

    def do():
        g[0] = True

    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always')

        tpool.execute(do)

        assert len(ws) == 1
        msg = str(ws[0].message)
        assert 'Zero threads in tpool' in msg
        assert 'EVENTLET_THREADPOOL_SIZE' in msg

    assert g[0]
    print('pass')
