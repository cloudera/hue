from tests import skipped, LimitedTestCase, skip_unless, certificate_file, private_key_file
from unittest import main
import eventlet
from eventlet import util, coros, greenio
import socket
import os

def listen_ssl_socket(address=('127.0.0.1', 0)):
    sock = util.wrap_ssl(socket.socket(), certificate_file,
          private_key_file, True)
    sock.bind(address)
    sock.listen(50)

    return sock
   

class SSLTest(LimitedTestCase):
    def test_duplex_response(self):
        def serve(listener):
            sock, addr = listener.accept()
            stuff = sock.read(8192)
            sock.write('response')

        sock = listen_ssl_socket()

        server_coro = eventlet.spawn(serve, sock)
        
        client = util.wrap_ssl(eventlet.connect(('127.0.0.1', sock.getsockname()[1])))
        client.write('line 1\r\nline 2\r\n\r\n')
        self.assertEquals(client.read(8192), 'response')
        server_coro.wait()
        
    def test_ssl_close(self):
        def serve(listener):
            sock, addr = listener.accept()
            stuff = sock.read(8192)
            try:
                self.assertEquals("", sock.read(8192))
            except greenio.SSL.ZeroReturnError:
                pass
  
        sock = listen_ssl_socket()

        server_coro = eventlet.spawn(serve, sock)
        
        raw_client = eventlet.connect(('127.0.0.1', sock.getsockname()[1]))
        client = util.wrap_ssl(raw_client)
        client.write('X')
        greenio.shutdown_safe(client)
        client.close()
        server_coro.wait()
        
    def test_ssl_connect(self):
        def serve(listener):
            sock, addr = listener.accept()
            stuff = sock.read(8192)
        sock = listen_ssl_socket()
        server_coro = eventlet.spawn(serve, sock)
        
        raw_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_client = util.wrap_ssl(raw_client)
        ssl_client.connect(('127.0.0.1', sock.getsockname()[1]))
        ssl_client.write('abc')
        greenio.shutdown_safe(ssl_client)
        ssl_client.close()
        server_coro.wait()


class SocketSSLTest(LimitedTestCase):
    @skip_unless(hasattr(socket, 'ssl'))
    def test_greensslobject(self):
        import warnings
        # disabling socket.ssl warnings because we're testing it here
        warnings.filterwarnings(action = 'ignore',
                        message='.*socket.ssl.*',
                        category=DeprecationWarning)

        def serve(listener):
            sock, addr = listener.accept()
            sock.write('content')
            greenio.shutdown_safe(sock)
            sock.close()
        listener = listen_ssl_socket(('', 0))
        killer = eventlet.spawn(serve, listener)
        from eventlet.green.socket import ssl
        client = ssl(eventlet.connect(('localhost', listener.getsockname()[1])))
        self.assertEquals(client.read(1024), 'content')
        self.assertEquals(client.read(1024), '')

        
if __name__ == '__main__':
    main()
