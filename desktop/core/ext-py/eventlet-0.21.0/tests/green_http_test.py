import eventlet
from eventlet.support import six
import tests

__test__ = six.PY3


def test_green_http_doesnt_change_original_module():
    tests.run_isolated('green_http_doesnt_change_original_module.py')


def test_green_httplib_doesnt_change_original_module():
    tests.run_isolated('green_httplib_doesnt_change_original_module.py')


def test_http_request_encode_chunked_kwarg():
    # https://bugs.python.org/issue12319
    # As of 2017-01 this test only verifies encode_chunked kwarg is properly accepted.
    # Stdlib http.client code was copied partially, chunked encoding may not work.
    from eventlet.green.http import client
    server_sock = eventlet.listen(('127.0.0.1', 0))
    addr = server_sock.getsockname()
    h = client.HTTPConnection(host=addr[0], port=addr[1])
    h.request('GET', '/', encode_chunked=True)
