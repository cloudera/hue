__test__ = False

if __name__ == '__main__':
    import eventlet
    import eventlet.tpool
    import socket

    def do():
        eventlet.sleep(0.2)
        return True

    socket.setdefaulttimeout(0.05)
    result = eventlet.tpool.execute(do)
    assert result
    print('pass')
