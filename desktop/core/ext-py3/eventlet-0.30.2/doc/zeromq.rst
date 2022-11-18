Zeromq
######

What is ØMQ?
============

"A ØMQ socket is what you get when you take a normal TCP socket, inject it with a mix of radioactive isotopes stolen
from a secret Soviet atomic research project, bombard it with 1950-era cosmic rays, and put it into the hands of a drug-addled
comic book author with a badly-disguised fetish for bulging muscles clad in spandex."

Key differences to conventional sockets
Generally speaking, conventional sockets present a synchronous interface to either connection-oriented reliable byte streams (SOCK_STREAM),
or connection-less unreliable datagrams (SOCK_DGRAM). In comparison, 0MQ sockets present an abstraction of an asynchronous message queue,
with the exact queueing semantics depending on the socket type in use. Where conventional sockets transfer streams of bytes or discrete datagrams,
0MQ sockets transfer discrete messages.

0MQ sockets being asynchronous means that the timings of the physical connection setup and teardown,
reconnect and effective delivery are transparent to the user and organized by 0MQ itself.
Further, messages may be queued in the event that a peer is unavailable to receive them.

Conventional sockets allow only strict one-to-one (two peers), many-to-one (many clients, one server),
or in some cases one-to-many (multicast) relationships. With the exception of ZMQ::PAIR,
0MQ sockets may be connected to multiple endpoints using connect(),
while simultaneously accepting incoming connections from multiple endpoints bound to the socket using bind(), thus allowing many-to-many relationships.

API documentation
=================

ØMQ support is provided in the :mod:`eventlet.green.zmq` module.
