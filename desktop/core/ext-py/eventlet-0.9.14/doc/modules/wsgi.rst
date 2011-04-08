:mod:`wsgi` -- WSGI server
===========================

The wsgi module provides a simple and easy way to start an event-driven 
`WSGI <http://wsgi.org/wsgi/>`_ server.  This can serve as an embedded
web server in an application, or as the basis for a more full-featured web
server package.  One such package is `Spawning <http://pypi.python.org/pypi/Spawning/>`_.

To launch a wsgi server, simply create a socket and call :func:`eventlet.wsgi.server` with it::

    from eventlet import wsgi
    import eventlet
    
    def hello_world(env, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, World!\r\n']
    
    wsgi.server(eventlet.listen(('', 8090)), hello_world)


You can find a slightly more elaborate version of this code in the file
``examples/wsgi.py``.

.. automodule:: eventlet.wsgi
	:members:

.. _wsgi_ssl:

SSL
---

Creating a secure server is only slightly more involved than the base example.  All that's needed is to pass an SSL-wrapped socket to the :func:`~eventlet.wsgi.server` method::

    wsgi.server(eventlet.wrap_ssl(eventlet.listen(('', 8090)),
                                  certfile='cert.crt',
                                  keyfile='private.key',
                                  server_side=True),
                hello_world)

Applications can detect whether they are inside a secure server by the value of the ``env['wsgi.url_scheme']`` environment variable.


Non-Standard Extension to Support Post Hooks
--------------------------------------------
Eventlet's WSGI server supports a non-standard extension to the WSGI
specification where :samp:`env['eventlet.posthooks']` contains an array of
`post hooks` that will be called after fully sending a response. Each post hook
is a tuple of :samp:`(func, args, kwargs)` and the `func` will be called with
the WSGI environment dictionary, followed by the `args` and then the `kwargs`
in the post hook.

For example::

    from eventlet import wsgi
    import eventlet

    def hook(env, arg1, arg2, kwarg3=None, kwarg4=None):
        print 'Hook called: %s %s %s %s %s' % (env, arg1, arg2, kwarg3, kwarg4)
    
    def hello_world(env, start_response):
        env['eventlet.posthooks'].append(
            (hook, ('arg1', 'arg2'), {'kwarg3': 3, 'kwarg4': 4}))
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, World!\r\n']
    
    wsgi.server(eventlet.listen(('', 8090)), hello_world)

The above code will print the WSGI environment and the other passed function
arguments for every request processed.

Post hooks are useful when code needs to be executed after a response has been
fully sent to the client (or when the client disconnects early). One example is
for more accurate logging of bandwidth used, as client disconnects use less
bandwidth than the actual Content-Length.
