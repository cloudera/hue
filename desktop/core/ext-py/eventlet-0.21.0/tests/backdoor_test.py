import os
import os.path

import eventlet

from eventlet import backdoor
from eventlet.green import socket

from tests import LimitedTestCase, main


class BackdoorTest(LimitedTestCase):
    def test_server(self):
        listener = socket.socket()
        listener.bind(('localhost', 0))
        listener.listen(50)
        serv = eventlet.spawn(backdoor.backdoor_server, listener)
        client = socket.socket()
        client.connect(('localhost', listener.getsockname()[1]))
        self._run_test_on_client_and_server(client, serv)

    def _run_test_on_client_and_server(self, client, server_thread):
        f = client.makefile('rw')
        assert 'Python' in f.readline()
        f.readline()  # build info
        f.readline()  # help info
        assert 'InteractiveConsole' in f.readline()
        self.assertEqual('>>> ', f.read(4))
        f.write('print("hi")\n')
        f.flush()
        self.assertEqual('hi\n', f.readline())
        self.assertEqual('>>> ', f.read(4))
        f.close()
        client.close()
        server_thread.kill()
        # wait for the console to discover that it's dead
        eventlet.sleep(0.1)

    def test_server_on_ipv6_socket(self):
        listener = socket.socket(socket.AF_INET6)
        listener.bind(('::1', 0))
        listener.listen(5)
        serv = eventlet.spawn(backdoor.backdoor_server, listener)
        client = socket.socket(socket.AF_INET6)
        client.connect(listener.getsockname())
        self._run_test_on_client_and_server(client, serv)

    def test_server_on_unix_socket(self):
        SOCKET_PATH = '/tmp/eventlet_backdoor_test.socket'
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        listener = socket.socket(socket.AF_UNIX)
        listener.bind(SOCKET_PATH)
        listener.listen(5)
        serv = eventlet.spawn(backdoor.backdoor_server, listener)
        client = socket.socket(socket.AF_UNIX)
        client.connect(SOCKET_PATH)
        self._run_test_on_client_and_server(client, serv)


if __name__ == '__main__':
    main()
