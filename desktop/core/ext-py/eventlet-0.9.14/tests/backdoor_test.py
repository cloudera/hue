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
        f = client.makefile('rw')
        self.assert_('Python' in f.readline())
        f.readline()  # build info
        f.readline()  # help info
        self.assert_('InteractiveConsole' in f.readline())
        self.assertEquals('>>> ', f.read(4))
        f.write('print("hi")\n')
        f.flush()
        self.assertEquals('hi\n', f.readline())
        self.assertEquals('>>> ', f.read(4))
        f.close()
        client.close()
        serv.kill()
        # wait for the console to discover that it's dead
        eventlet.sleep(0.1)
        
        

if __name__ == '__main__':
    main()
