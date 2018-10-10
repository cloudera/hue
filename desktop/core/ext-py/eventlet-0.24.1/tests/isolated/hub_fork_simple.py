import os
import signal
import sys
import tempfile
__test__ = False


def parent(signal_path, pid):
    eventlet.Timeout(5)
    port = None
    while True:
        try:
            contents = open(signal_path, 'rb').read()
            port = int(contents.strip())
            break
        except Exception:
            eventlet.sleep(0.1)
    eventlet.connect(('127.0.0.1', port))
    while True:
        try:
            contents = open(signal_path, 'rb').read()
            result = contents.split()[1]
            break
        except Exception:
            eventlet.sleep(0.1)
    assert result == b'done', repr(result)
    print('pass')


def child(signal_path):
    eventlet.Timeout(5)
    s = eventlet.listen(('127.0.0.1', 0))
    with open(signal_path, 'wb') as f:
        f.write(str(s.getsockname()[1]).encode() + b'\n')
        f.flush()
        s.accept()
        f.write(b'done\n')
        f.flush()


if __name__ == '__main__':
    import eventlet

    with tempfile.NamedTemporaryFile() as signal_file:
        signal_path = signal_file.name

    pid = os.fork()
    if pid < 0:
        sys.stderr.write('fork error\n')
        sys.exit(1)
    elif pid == 0:
        child(signal_path)
        sys.exit(0)
    elif pid > 0:
        try:
            parent(signal_path, pid)
        except Exception:
            os.kill(pid, signal.SIGTERM)
