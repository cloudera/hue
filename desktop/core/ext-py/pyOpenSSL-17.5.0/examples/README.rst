========
Examples
========


certgen.py -- Certificate generation module
===========================================

Example module with three functions:

createKeyPair
   Create a public/private key pair.

createCertRequest
   Create a certificate request.

createCertificate
   Create a certificate given a cert request.

In fact, I created the certificates and keys in the 'simple' directory with the script ``mk_simple_certs.py``.


simple -- Simple client/server example
======================================

Start the server with::

    python server.py PORT

and start clients with::

    python client.py HOST PORT

The server is a simple echo server, anything a client sends, it sends back.


proxy.py -- Example of an SSL-enabled proxy
===========================================

The proxy example demonstrate how to use set_connect_state to start talking SSL over an already connected socket.

Usage::

  python proxy.py server[:port] proxy[:port]

Contributed by Mihai Ibanescu


SecureXMLRPCServer.py -- SSL-enabled version of SimpleXMLRPCServer
==================================================================

Acts exactly like `SimpleXMLRPCServer <https://docs.python.org/3/library/xmlrpc.server.html>`_ from the Python standard library, but uses secure connections.
The technique and classes should work for any SocketServer style server.
However, the code has not been extensively tested.

Contributed by Michal Wallace
