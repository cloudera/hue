:mod:`websocket` -- Websocket Server
=====================================

This module provides a simple way to create a `websocket
<http://dev.w3.org/html5/websockets/>`_ server.  It works with a few
tweaks in the :mod:`~eventlet.wsgi` module that allow websockets to
coexist with other WSGI applications.

To create a websocket server, simply decorate a handler method with
:class:`WebSocketWSGI` and use it as a wsgi application::

    from eventlet import wsgi, websocket
    import eventlet
    
    @websocket.WebSocketWSGI
    def hello_world(ws):
        ws.send("hello world")
    
    wsgi.server(eventlet.listen(('', 8090)), hello_world)

.. note::

    Please see graceful termination warning in :func:`~eventlet.wsgi.server`
    documentation


You can find a slightly more elaborate version of this code in the file
``examples/websocket.py``.

As of version 0.9.13, eventlet.websocket supports SSL websockets; all that's necessary is to use an :ref:`SSL wsgi server <wsgi_ssl>`.

.. note :: The web socket spec is still under development, and it will be necessary to change the way that this module works in response to spec changes.


.. automodule:: eventlet.websocket
	:members:
