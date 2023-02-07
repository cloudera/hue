# Issue #508: test ThreadPoolExecutor with monkey-patching
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()

    import sys

    # Futures is only included in 3.2 or later
    if sys.version_info >= (3, 2):
        from concurrent import futures

        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(pow, 2, 3)
            res = future.result()
        assert res == 8, '2^3 should be 8, not %s' % res
    print('pass')
