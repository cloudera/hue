"""A simple web server that accepts POSTS containing a list of feed urls,
and returns the titles of those feeds.
"""
import eventlet
feedparser = eventlet.import_patched('feedparser')

# the pool provides a safety limit on our concurrency
pool = eventlet.GreenPool()


def fetch_title(url):
    d = feedparser.parse(url)
    return d.feed.get('title', '')


def app(environ, start_response):
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('403 Forbidden', [])
        return []

    # the pile collects the result of a concurrent operation -- in this case,
    # the collection of feed titles
    pile = eventlet.GreenPile(pool)
    for line in environ['wsgi.input'].readlines():
        url = line.strip()
        if url:
            pile.spawn(fetch_title, url)
    # since the pile is an iterator over the results,
    # you can use it in all sorts of great Pythonic ways
    titles = '\n'.join(pile)
    start_response('200 OK', [('Content-type', 'text/plain')])
    return [titles]


if __name__ == '__main__':
    from eventlet import wsgi
    wsgi.server(eventlet.listen(('localhost', 9010)), app)
