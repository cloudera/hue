from paste.session import SessionMiddleware
from paste.fixture import TestApp

info = []

def wsgi_app(environ, start_response):
    pi = environ.get('PATH_INFO', '')
    if pi in ('/get1', '/get2'):
        if pi == '/get1':
            sess = environ['paste.session.factory']()
        start_response('200 OK', [('content-type', 'text/plain')])
        if pi == '/get2':
            sess = environ['paste.session.factory']()
        if 'info' in sess:
            return [str(sess['info'])]
        else:
            return ['no-info']
    if pi in ('/put1', '/put2'):
        if pi == '/put1':
            sess = environ['paste.session.factory']()
            sess['info']  = info[0]
        start_response('200 OK', [('content-type', 'text/plain')])
        if pi == '/put2':
            sess = environ['paste.session.factory']()
            sess['info']  = info[0]
        return ['foo']

wsgi_app = SessionMiddleware(wsgi_app)
    
def test_app1():
    app = TestApp(wsgi_app)
    res = app.get('/get1')
    assert res.body == 'no-info'
    res = app.get('/get2')
    assert res.body == 'no-info'
    info[:] = ['test']
    res = app.get('/put1')
    res = app.get('/get1')
    assert res.body == 'test'
    res = app.get('/get2')
    assert res.body == 'test'

def test_app2():
    app = TestApp(wsgi_app)
    info[:] = ['fluff']
    res = app.get('/put2')
    res = app.get('/get1')
    assert res.body == 'fluff'
    res = app.get('/get2')
    assert res.body == 'fluff'
    
    
