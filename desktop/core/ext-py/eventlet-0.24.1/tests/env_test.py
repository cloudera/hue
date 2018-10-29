import tests


def test_hub_selects():
    code = 'from eventlet import hubs\nprint(hubs.get_hub())'
    output = tests.run_python(
        path=None,
        env={'EVENTLET_HUB': 'selects'},
        args=['-c', code],
    )
    assert output.count(b'\n') == 1
    assert b'eventlet.hubs.selects.Hub' in output


def test_tpool_dns():
    code = '''\
from eventlet.green import socket
socket.gethostbyname('localhost')
socket.getaddrinfo('localhost', 80)
print('pass')
'''
    tests.run_python(
        path=None,
        env={'EVENTLET_TPOOL_DNS': 'yes'},
        args=['-c', code],
        expect_pass=True,
    )


@tests.skip_with_pyevent
def test_tpool_size():
    expected = '40'
    normal = '20'
    tests.run_isolated(
        path='env_tpool_size.py',
        env={'EVENTLET_THREADPOOL_SIZE': expected},
        args=[expected, normal],
    )


def test_tpool_negative():
    tests.run_isolated('env_tpool_negative.py', env={'EVENTLET_THREADPOOL_SIZE': '-1'})


def test_tpool_zero():
    tests.run_isolated('env_tpool_zero.py', env={'EVENTLET_THREADPOOL_SIZE': '0'})
