Examples
========

Here are a bunch of small example programs that use Eventlet.  All of these examples can be found in the ``examples`` directory of a source copy of Eventlet.

.. _web_crawler_example:

Web Crawler
------------
``examples/webcrawler.py``

.. literalinclude:: ../examples/webcrawler.py

.. _wsgi_server_example:

WSGI Server
------------
``examples/wsgi.py``

.. literalinclude:: ../examples/wsgi.py

.. _echo_server_example:

Echo Server
-----------
``examples/echoserver.py``

.. literalinclude:: ../examples/echoserver.py

.. _socket_connect_example:

Socket Connect
--------------
``examples/connect.py``

.. literalinclude:: ../examples/connect.py

.. _chat_server_example:

Multi-User Chat Server
-----------------------
``examples/chat_server.py``

This is a little different from the echo server, in that it broadcasts the 
messages to all participants, not just the sender.
        
.. literalinclude:: ../examples/chat_server.py

.. _feed_scraper_example:

Feed Scraper
-----------------------
``examples/feedscraper.py``

This example requires `Feedparser <http://www.feedparser.org/>`_ to be installed or on the PYTHONPATH.

.. literalinclude:: ../examples/feedscraper.py

.. _forwarder_example:

Port Forwarder
-----------------------
``examples/forwarder.py``

.. literalinclude:: ../examples/forwarder.py

.. _recursive_crawler_example:

Recursive Web Crawler
-----------------------------------------
``examples/recursive_crawler.py``

This is an example recursive web crawler that fetches linked pages from a seed url.

.. literalinclude:: ../examples/recursive_crawler.py

.. _producer_consumer_example:

Producer Consumer Web Crawler
-----------------------------------------
``examples/producer_consumer.py``

This is an example implementation of the producer/consumer pattern as well as being identical in functionality to the recursive web crawler.

.. literalinclude:: ../examples/producer_consumer.py

.. _websocket_example:

Websocket Server Example
--------------------------
``examples/websocket.py``

This exercises some of the features of the websocket server
implementation.

.. literalinclude:: ../examples/websocket.py

.. _websocket_chat_example:

Websocket Multi-User Chat Example
-----------------------------------
``examples/websocket_chat.py``

This is a mashup of the websocket example and the multi-user chat example, showing how you can do the same sorts of things with websockets that you can do with regular sockets.

.. literalinclude:: ../examples/websocket_chat.py
