import eventlet
from eventlet import greenio
import os


__test__ = False
_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0 * 1024.0,
          'KB': 1024.0, 'MB': 1024.0 * 1024.0}


def _VmB(VmKey):
    '''Private.
    '''
    global _proc_status, _scale
    # get pseudo file  /proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?
    # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace
    if len(v) < 3:
        return 0.0  # invalid format?
    # convert Vm value to bytes
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''Return memory usage in bytes.
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.
    '''
    return _VmB('VmStk:') - since


def test_pipe_writes_large_messages():
    r, w = os.pipe()

    r = greenio.GreenPipe(r)
    w = greenio.GreenPipe(w, 'w')

    large_message = b"".join([1024 * chr(i) for i in range(65)])

    def writer():
        w.write(large_message)
        w.close()

    gt = eventlet.spawn(writer)

    for i in range(65):
        buf = r.read(1024)
        expected = 1024 * chr(i)
        if buf != expected:
            print(
                "expected=%r..%r, found=%r..%r iter=%d"
                % (expected[:4], expected[-4:], buf[:4], buf[-4:], i))
    gt.wait()


if __name__ == "__main__":
    _iter = 1
    while True:
        test_pipe_writes_large_messages()

        _iter += 1
        if _iter % 10 == 0:
            print("_iter = %d, VmSize: %d, VmRSS = %d, VmStk = %d" %
                  (_iter, memory(), resident(), stacksize()))
