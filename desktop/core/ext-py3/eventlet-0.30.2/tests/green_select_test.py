import eventlet
from eventlet import hubs
from eventlet.green import select
import tests
original_socket = eventlet.patcher.original('socket')


def test_select_mark_file_as_reopened():
    # https://github.com/eventlet/eventlet/pull/294
    # Fix API inconsistency in select and Hub.
    # mark_as_closed takes one argument, but called without arguments.
    # on_error takes file descriptor, but called with an exception object.
    s = original_socket.socket()
    s.setblocking(0)
    s.bind(('127.0.0.1', 0))
    s.listen(5)

    gt = eventlet.spawn(select.select, [s], [s], [s])
    eventlet.sleep(0.01)

    with eventlet.Timeout(0.5) as t:
        with tests.assert_raises(hubs.IOClosed):
            hubs.get_hub().mark_as_reopened(s.fileno())
            gt.wait()
        t.cancel()
