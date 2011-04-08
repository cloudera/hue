import os
import os.path
import socket
from unittest import TestCase, main
import warnings

import eventlet
warnings.simplefilter('ignore', DeprecationWarning)
from eventlet import api
warnings.simplefilter('default', DeprecationWarning)
from eventlet import greenio, util, hubs, greenthread, spawn

def check_hub():
    # Clear through the descriptor queue
    api.sleep(0)
    api.sleep(0)
    hub = hubs.get_hub()
    for nm in 'get_readers', 'get_writers':
        dct = getattr(hub, nm)()
        assert not dct, "hub.%s not empty: %s" % (nm, dct)
    # Stop the runloop (unless it's twistedhub which does not support that)
    if not getattr(hub, 'uses_twisted_reactor', None):
        hub.abort(True)
        assert not hub.running


class TestApi(TestCase):

    certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
    private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')

    def test_tcp_listener(self):
        socket = eventlet.listen(('0.0.0.0', 0))
        assert socket.getsockname()[0] == '0.0.0.0'
        socket.close()

        check_hub()

    def test_connect_tcp(self):
        def accept_once(listenfd):
            try:
                conn, addr = listenfd.accept()
                fd = conn.makefile(mode='w')
                conn.close()
                fd.write('hello\n')
                fd.close()
            finally:
                listenfd.close()

        server = eventlet.listen(('0.0.0.0', 0))
        api.spawn(accept_once, server)

        client = eventlet.connect(('127.0.0.1', server.getsockname()[1]))
        fd = client.makefile()
        client.close()
        assert fd.readline() == 'hello\n'

        assert fd.read() == ''
        fd.close()

        check_hub()

    def test_connect_ssl(self):
        def accept_once(listenfd):
            try:
                conn, addr = listenfd.accept()
                conn.write('hello\r\n')
                greenio.shutdown_safe(conn)
                conn.close()
            finally:
                greenio.shutdown_safe(listenfd)
                listenfd.close()

        server = api.ssl_listener(('0.0.0.0', 0),
                                  self.certificate_file,
                                  self.private_key_file)
        api.spawn(accept_once, server)

        raw_client = eventlet.connect(('127.0.0.1', server.getsockname()[1]))
        client = util.wrap_ssl(raw_client)
        fd = socket._fileobject(client, 'rb', 8192)

        assert fd.readline() == 'hello\r\n'
        try:
            self.assertEquals('', fd.read(10))
        except greenio.SSL.ZeroReturnError:
            # if it's a GreenSSL object it'll do this
            pass
        greenio.shutdown_safe(client)
        client.close()
        
        check_hub()

    def test_001_trampoline_timeout(self):
        from eventlet import coros
        server_sock = eventlet.listen(('127.0.0.1', 0))
        bound_port = server_sock.getsockname()[1]
        def server(sock):
            client, addr = sock.accept()
            api.sleep(0.1)
        server_evt = spawn(server, server_sock)
        api.sleep(0)
        try:
            desc = eventlet.connect(('127.0.0.1', bound_port))
            api.trampoline(desc, read=True, write=False, timeout=0.001)
        except api.TimeoutError:
            pass # test passed
        else:
            assert False, "Didn't timeout"

        server_evt.wait()
        check_hub()

    def test_timeout_cancel(self):
        server = eventlet.listen(('0.0.0.0', 0))
        bound_port = server.getsockname()[1]

        done = [False]
        def client_closer(sock):
            while True:
                (conn, addr) = sock.accept()
                conn.close()

        def go():
            desc = eventlet.connect(('127.0.0.1', bound_port))
            try:
                api.trampoline(desc, read=True, timeout=0.1)
            except api.TimeoutError:
                assert False, "Timed out"

            server.close()
            desc.close()
            done[0] = True

        greenthread.spawn_after_local(0, go)

        server_coro = api.spawn(client_closer, server)
        while not done[0]:
            api.sleep(0)
        api.kill(server_coro)

        check_hub()

    def test_named(self):
        named_foo = api.named('tests.api_test.Foo')
        self.assertEquals(
            named_foo.__name__,
            "Foo")

    def test_naming_missing_class(self):
        self.assertRaises(
            ImportError, api.named, 'this_name_should_hopefully_not_exist.Foo')
        
        
    def test_killing_dormant(self):
        DELAY = 0.1
        state = []
        def test():
            try:
                state.append('start')
                api.sleep(DELAY)
            except:
                state.append('except')
                # catching GreenletExit
                pass
            # when switching to hub, hub makes itself the parent of this greenlet,
            # thus after the function's done, the control will go to the parent
            api.sleep(0)
            state.append('finished')
        g = api.spawn(test)
        api.sleep(DELAY/2)
        self.assertEquals(state, ['start'])
        api.kill(g)
        # will not get there, unless switching is explicitly scheduled by kill
        self.assertEquals(state,['start', 'except'])
        api.sleep(DELAY)
        self.assertEquals(state, ['start', 'except', 'finished'])

    def test_nested_with_timeout(self):
        def func():
            return api.with_timeout(0.2, api.sleep, 2, timeout_value=1)
        self.assertRaises(api.TimeoutError, api.with_timeout, 0.1, func)


class Foo(object):
    pass


if __name__ == '__main__':
    main()

