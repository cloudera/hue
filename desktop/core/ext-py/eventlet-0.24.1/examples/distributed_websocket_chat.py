"""This is a websocket chat example with many servers. A client can connect to
any of the servers and their messages will be received by all clients connected
to any of the servers.

Run the examples like this:

$ python examples/chat_bridge.py tcp://127.0.0.1:12345 tcp://127.0.0.1:12346

and the servers like this (changing the port for each one obviously):

$ python examples/distributed_websocket_chat.py -p tcp://127.0.0.1:12345 -s tcp://127.0.0.1:12346 7000

So all messages are published to port 12345 and the device forwards all the
messages to 12346 where they are subscribed to
"""
import os
import sys
import eventlet
from collections import defaultdict
from eventlet import spawn_n, sleep
from eventlet import wsgi
from eventlet import websocket
from eventlet.green import zmq
from eventlet.hubs import get_hub, use_hub
from uuid import uuid1

use_hub('zeromq')
ctx = zmq.Context()


class IDName(object):

    def __init__(self):
        self.id = uuid1()
        self.name = None

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.id)

    def pack_message(self, msg):
        return self, msg

    def unpack_message(self, msg):
        sender, message = msg
        sender_name = 'you said' if sender.id == self.id \
            else '%s says' % sender
        return "%s: %s" % (sender_name, message)


participants = defaultdict(IDName)


def subscribe_and_distribute(sub_socket):
    global participants
    while True:
        msg = sub_socket.recv_pyobj()
        for ws, name_id in participants.items():
            to_send = name_id.unpack_message(msg)
            if to_send:
                try:
                    ws.send(to_send)
                except:
                    del participants[ws]


@websocket.WebSocketWSGI
def handle(ws):
    global pub_socket
    name_id = participants[ws]
    ws.send("Connected as %s, change name with 'name: new_name'" % name_id)
    try:
        while True:
            m = ws.wait()
            if m is None:
                break
            if m.startswith('name:'):
                old_name = str(name_id)
                new_name = m.split(':', 1)[1].strip()
                name_id.name = new_name
                m = 'Changed name from %s' % old_name
            pub_socket.send_pyobj(name_id.pack_message(m))
            sleep()
    finally:
        del participants[ws]


def dispatch(environ, start_response):
    """Resolves to the web page or the websocket depending on the path."""
    global port
    if environ['PATH_INFO'] == '/chat':
        return handle(environ, start_response)
    else:
        start_response('200 OK', [('content-type', 'text/html')])
        return [open(os.path.join(
                     os.path.dirname(__file__),
                     'websocket_chat.html')).read() % dict(port=port)]

port = None

if __name__ == "__main__":
    usage = 'usage: websocket_chat -p pub address -s sub address port number'
    if len(sys.argv) != 6:
        print(usage)
        sys.exit(1)

    pub_addr = sys.argv[2]
    sub_addr = sys.argv[4]
    try:
        port = int(sys.argv[5])
    except ValueError:
        print("Error port supplied couldn't be converted to int\n", usage)
        sys.exit(1)

    try:
        pub_socket = ctx.socket(zmq.PUB)
        pub_socket.connect(pub_addr)
        print("Publishing to %s" % pub_addr)
        sub_socket = ctx.socket(zmq.SUB)
        sub_socket.connect(sub_addr)
        sub_socket.setsockopt(zmq.SUBSCRIBE, "")
        print("Subscribing to %s" % sub_addr)
    except:
        print("Couldn't create sockets\n", usage)
        sys.exit(1)

    spawn_n(subscribe_and_distribute, sub_socket)
    listener = eventlet.listen(('127.0.0.1', port))
    print("\nVisit http://localhost:%s/ in your websocket-capable browser.\n" % port)
    wsgi.server(listener, dispatch)
