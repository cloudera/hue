#! /usr/bin/env python
"""\
Simple server that listens on port 6000 and echos back every input to
the client.  To try out the server, start it up by running this file.

Connect to it with:
  telnet localhost 6000

You terminate your connection by terminating telnet (typically Ctrl-]
and then 'quit')
"""
from __future__ import print_function

import eventlet


def handle(fd):
    print("client connected")
    while True:
        # pass through every non-eof line
        x = fd.readline()
        if not x:
            break
        fd.write(x)
        fd.flush()
        print("echoed", x, end=' ')
    print("client disconnected")

print("server socket listening on port 6000")
server = eventlet.listen(('0.0.0.0', 6000))
pool = eventlet.GreenPool()
while True:
    try:
        new_sock, address = server.accept()
        print("accepted", address)
        pool.spawn_n(handle, new_sock.makefile('rw'))
    except (SystemExit, KeyboardInterrupt):
        break
