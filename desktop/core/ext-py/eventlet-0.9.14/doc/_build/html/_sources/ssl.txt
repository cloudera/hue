Using SSL With Eventlet
========================

Eventlet makes it easy to use non-blocking SSL sockets.  If you're using Python 2.6 or later, you're all set, eventlet wraps the built-in ssl module.  If on Python 2.5 or 2.4, you have to install pyOpenSSL_ to use eventlet.

In either case, the the ``green`` modules handle SSL sockets transparently, just like their standard counterparts.  As an example, :mod:`eventlet.green.urllib2` can be used to fetch https urls in as non-blocking a fashion as you please::

    from eventlet.green import urllib2
    from eventlet import coros
    bodies = [coros.execute(urllib2.urlopen, url)
         for url in ("https://secondlife.com","https://google.com")]
    for b in bodies:
        print b.wait().read()
 
 
With Python 2.6
----------------

To use ssl sockets directly in Python 2.6, use :mod:`eventlet.green.ssl`, which is a non-blocking wrapper around the standard Python :mod:`ssl` module, and which has the same interface.  See the standard documentation for instructions on use.

With Python 2.5 or Earlier
---------------------------

Prior to Python 2.6, there is no :mod:`ssl`, so SSL support is much weaker.  Eventlet relies on pyOpenSSL to implement its SSL support on these older versions, so be sure to install pyOpenSSL, or you'll get an ImportError whenever your system tries to make an SSL connection.

Once pyOpenSSL is installed, you can then use the ``eventlet.green`` modules, like :mod:`eventlet.green.httplib` to fetch https urls.  You can also use :func:`eventlet.green.socket.ssl`, which is a nonblocking wrapper for :func:`socket.ssl`.

PyOpenSSL
----------

:mod:`eventlet.green.OpenSSL` has exactly the same interface as pyOpenSSL_ `(docs) <http://pyopenssl.sourceforge.net/pyOpenSSL.html/>`_, and works in all versions of Python.  This module is much more powerful than :func:`socket.ssl`, and may have some advantages over :mod:`ssl`, depending on your needs.

Here's an example of a server::

    from eventlet.green import socket
    from eventlet.green.OpenSSL import SSL
    
    # insecure context, only for example purposes
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.set_verify(SSL.VERIFY_NONE, lambda *x: True))

    # create underlying green socket and wrap it in ssl
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = SSL.Connection(context, sock)
    
    # configure as server
    connection.set_accept_state()
    connection.bind(('127.0.0.1', 80443))
    connection.listen(50)
    
    # accept one client connection then close up shop
    client_conn, addr = connection.accept()
    print client_conn.read(100)
    client_conn.shutdown()
    client_conn.close()
    connection.close()

.. _pyOpenSSL: https://launchpad.net/pyopenssl