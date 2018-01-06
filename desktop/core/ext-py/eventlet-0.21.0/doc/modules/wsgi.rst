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
        print('Hook called: %s %s %s %s %s' % (env, arg1, arg2, kwarg3, kwarg4))

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


"100 Continue" Response Headers
-------------------------------

Eventlet's WSGI server supports sending (optional) headers with HTTP "100 Continue"
provisional responses.  This is useful in such cases where a WSGI server expects
to complete a PUT request as a single HTTP request/response pair, and also wants to
communicate back to client as part of the same HTTP transaction.  An example is
where the HTTP server wants to pass hints back to the client about characteristics
of data payload it can accept.  As an example, an HTTP server may pass a hint in a
header the accompanying "100 Continue" response to the client indicating it can or
cannot accept encrypted data payloads, and thus client can make the encrypted vs
unencrypted decision before starting to send the data).  

This works well for WSGI servers as the WSGI specification mandates HTTP
expect/continue mechanism (PEP333).

To define the "100 Continue" response headers, one may call
:func:`set_hundred_continue_response_header` on :samp:`env['wsgi.input']`
as shown in the following example::

    from eventlet import wsgi
    import eventlet

    def wsgi_app(env, start_response):
        # Define "100 Continue" response headers
        env['wsgi.input'].set_hundred_continue_response_headers(
            [('Hundred-Continue-Header-1', 'H1'),
             ('Hundred-Continue-Header-k', 'Hk')])
        # The following read() causes "100 Continue" response to
        # the client.  Headers 'Hundred-Continue-Header-1' and 
        # 'Hundred-Continue-Header-K' are sent with the response
        # following the "HTTP/1.1 100 Continue\r\n" status line
        text = env['wsgi.input'].read()
        start_response('200 OK', [('Content-Length', str(len(text)))])
        return [text]

You can find a more elaborate example in the file:
``tests/wsgi_test.py``, :func:`test_024a_expect_100_continue_with_headers`.


Per HTTP RFC 7231 (http://tools.ietf.org/html/rfc7231#section-6.2) a client is
required to be able to process one or more 100 continue responses.  A sample
use case might be a user protocol where the server may want to use a 100-continue
response to indicate to a client that it is working on a request and the 
client should not timeout.

To support multiple 100-continue responses, evenlet wsgi module exports
the API :func:`send_hundred_continue_response`.

Sample use cases for chunked and non-chunked HTTP scenarios are included
in the wsgi test case ``tests/wsgi_test.py``,
:func:`test_024b_expect_100_continue_with_headers_multiple_chunked` and
:func:`test_024c_expect_100_continue_with_headers_multiple_nonchunked`.

