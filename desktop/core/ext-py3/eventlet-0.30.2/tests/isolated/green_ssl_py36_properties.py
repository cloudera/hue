__test__ = False


if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()

    try:
        eventlet.wrap_ssl(
            eventlet.listen(('localhost', 0)),
            certfile='does-not-exist',
            keyfile='does-not-exist',
            server_side=True)
    except IOError as ex:
        assert ex.errno == 2
        print('pass')
