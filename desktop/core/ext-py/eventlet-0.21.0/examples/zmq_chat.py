import eventlet
import sys
from eventlet.green import socket, zmq
from eventlet.hubs import use_hub
use_hub('zeromq')

ADDR = 'ipc:///tmp/chat'

ctx = zmq.Context()


def publish(writer):

    print("connected")
    socket = ctx.socket(zmq.SUB)

    socket.setsockopt(zmq.SUBSCRIBE, "")
    socket.connect(ADDR)
    eventlet.sleep(0.1)

    while True:
        msg = socket.recv_pyobj()
        str_msg = "%s: %s" % msg
        writer.write(str_msg)
        writer.flush()


PORT = 3001


def read_chat_forever(reader, pub_socket):

    line = reader.readline()
    who = 'someone'
    while line:
        print("Chat:", line.strip())
        if line.startswith('name:'):
            who = line.split(':')[-1].strip()

        try:
            pub_socket.send_pyobj((who, line))
        except socket.error as e:
            # ignore broken pipes, they just mean the participant
            # closed its connection already
            if e[0] != 32:
                raise
        line = reader.readline()
    print("Participant left chat.")

try:
    print("ChatServer starting up on port %s" % PORT)
    server = eventlet.listen(('0.0.0.0', PORT))
    pub_socket = ctx.socket(zmq.PUB)
    pub_socket.bind(ADDR)
    eventlet.spawn_n(publish,
                     sys.stdout)
    while True:
        new_connection, address = server.accept()

        print("Participant joined chat.")
        eventlet.spawn_n(publish,
                         new_connection.makefile('w'))
        eventlet.spawn_n(read_chat_forever,
                         new_connection.makefile('r'),
                         pub_socket)
except (KeyboardInterrupt, SystemExit):
    print("ChatServer exiting.")
