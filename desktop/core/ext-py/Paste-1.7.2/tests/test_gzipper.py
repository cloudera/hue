from paste.fixture import TestApp
from paste.gzipper import middleware
import gzip, cStringIO

def simple_app(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    return 'this is a test'

wsgi_app = middleware(simple_app)
app = TestApp(wsgi_app)

def test_gzip():
    res = app.get(
        '/', extra_environ=dict(HTTP_ACCEPT_ENCODING='gzip'))
    assert int(res.header('content-length')) == len(res.body)
    assert res.body != 'this is a test'
    actual = gzip.GzipFile(fileobj=cStringIO.StringIO(res.body)).read()
    assert actual == 'this is a test'
