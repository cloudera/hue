# verify eventlet.listen() accepts in forked children
__test__ = False

if __name__ == '__main__':
    import os
    import sys
    import eventlet

    server = eventlet.listen(('127.0.0.1', 0))
    result = eventlet.with_timeout(0.01, server.accept, timeout_value=True)
    assert result is True, 'Expected timeout'

    pid = os.fork()
    if pid < 0:
        print('fork error')
        sys.exit(1)
    elif pid == 0:
        with eventlet.Timeout(1):
            sock, _ = server.accept()
            sock.sendall('ok {0}'.format(os.getpid()).encode())
            sock.close()
        sys.exit(0)
    elif pid > 0:
        with eventlet.Timeout(1):
            sock = eventlet.connect(server.getsockname())
            data = sock.recv(20).decode()
            assert data.startswith('ok ')
            spid = int(data[3:].strip())
            assert spid == pid
            kpid, status = os.wait()
            assert kpid == pid
            assert status == 0
            print('pass')
