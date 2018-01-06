.. _design-patterns:

Design Patterns
=================

There are a bunch of basic patterns that Eventlet usage falls into.  Here are a few examples that show their basic structure.

Client Pattern
--------------------

The canonical client-side example is a web crawler.  This use case is given a list of urls and wants to retrieve their bodies for later processing.  Here is a very simple example::

    import eventlet
    from eventlet.green import urllib2

    urls = ["http://www.google.com/intl/en_ALL/images/logo.gif",
           "https://www.python.org/static/img/python-logo.png",
           "http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif"]

    def fetch(url):
        return urllib2.urlopen(url).read()

    pool = eventlet.GreenPool()
    for body in pool.imap(fetch, urls):
        print("got body", len(body))

There is a slightly more complex version of this in the :ref:`web crawler example <web_crawler_example>`.  Here's a tour of the interesting lines in this crawler.

``from eventlet.green import urllib2`` is how you import a cooperatively-yielding version of urllib2.  It is the same in all respects to the standard version, except that it uses green sockets for its communication.  This is an example of the :ref:`import-green` pattern.

``pool = eventlet.GreenPool()`` constructs a :class:`GreenPool <eventlet.greenpool.GreenPool>` of a thousand green threads.  Using a pool is good practice because it provides an upper limit on the amount of work that this crawler will be doing simultaneously, which comes in handy when the input data changes dramatically.

``for body in pool.imap(fetch, urls):`` iterates over the results of calling the fetch function in parallel.  :meth:`imap <eventlet.greenpool.GreenPool.imap>` makes the function calls in parallel, and the results are returned in the order that they were executed.

The key aspect of the client pattern is that it involves collecting the results of each function call; the fact that each fetch is done concurrently is essentially an invisible optimization.  Note also that imap is memory-bounded and won't consume gigabytes of memory if the list of urls grows to the tens of thousands (yes, we had that problem in production once!).


Server Pattern
--------------------

Here's a simple server-side example, a simple echo server::

    import eventlet

    def handle(client):
        while True:
            c = client.recv(1)
            if not c: break
            client.sendall(c)

    server = eventlet.listen(('0.0.0.0', 6000))
    pool = eventlet.GreenPool(10000)
    while True:
        new_sock, address = server.accept()
        pool.spawn_n(handle, new_sock)

The file :ref:`echo server example <echo_server_example>` contains a somewhat more robust and complex version of this example.

``server = eventlet.listen(('0.0.0.0', 6000))`` uses a convenience function to create a listening socket.

``pool = eventlet.GreenPool(10000)`` creates a pool of green threads that could handle ten thousand clients.

``pool.spawn_n(handle, new_sock)`` launches a green thread to handle the new client.  The accept loop doesn't care about the return value of the ``handle`` function, so it uses :meth:`spawn_n <eventlet.greenpool.GreenPool.spawn_n>`, instead of :meth:`spawn <eventlet.greenpool.GreenPool.spawn>`.

The difference between the server and the client patterns boils down to the fact that the server has a ``while`` loop calling ``accept()`` repeatedly, and that it hands off the client socket completely to the handle() method, rather than collecting the results.

Dispatch Pattern
-------------------

One common use case that Linden Lab runs into all the time is a "dispatch" design pattern.  This is a server that is also a client of some other services.  Proxies, aggregators, job workers, and so on are all terms that apply here.  This is the use case that the :class:`GreenPile <eventlet.greenpool.GreenPile>` was designed for.

Here's a somewhat contrived example: a server that receives POSTs from clients that contain a list of urls of RSS feeds.  The server fetches all the feeds concurrently and responds with a list of their titles to the client.  It's easy to imagine it doing something more complex than this, and this could be easily modified to become a Reader-style application::

    import eventlet
    feedparser = eventlet.import_patched('feedparser')

    pool = eventlet.GreenPool()

    def fetch_title(url):
        d = feedparser.parse(url)
        return d.feed.get('title', '')

    def app(environ, start_response):
        pile = eventlet.GreenPile(pool)
        for url in environ['wsgi.input'].readlines():
            pile.spawn(fetch_title, url)
        titles = '\n'.join(pile)
        start_response('200 OK', [('Content-type', 'text/plain')])
        return [titles]

The full version of this example is in the :ref:`feed_scraper_example`, which includes code to start the WSGI server on a particular port.

This example uses a global (gasp) :class:`GreenPool <eventlet.greenpool.GreenPool>` to control concurrency.  If we didn't have a global limit on the number of outgoing requests, then a client could cause the server to open tens of thousands of concurrent connections to external servers, thereby getting feedscraper's IP banned, or various other accidental-or-on-purpose bad behavior.  The pool isn't a complete DoS protection, but it's the bare minimum.

.. highlight:: python
    :linenothreshold: 1

The interesting lines are in the app function::

    pile = eventlet.GreenPile(pool)
    for url in environ['wsgi.input'].readlines():
        pile.spawn(fetch_title, url)
    titles = '\n'.join(pile)

.. highlight:: python
    :linenothreshold: 1000

Note that in line 1, the Pile is constructed using the global pool as its argument.  That ties the Pile's concurrency to the global's.  If there are already 1000 concurrent fetches from other clients of feedscraper, this one will block until some of those complete.  Limitations are good!

Line 3 is just a spawn, but note that we don't store any return value from it.  This is because the return value is kept in the Pile itself.  This becomes evident in the next line...

Line 4 is where we use the fact that the Pile is an iterator.  Each element in the iterator is one of the return values from the fetch_title function, which are strings.  We can use a normal Python idiom (:func:`join`) to concatenate these incrementally as they happen.
