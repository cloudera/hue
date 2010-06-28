import re
import os

import beaker.session
from beaker.middleware import SessionMiddleware
from nose import SkipTest
from webtest import TestApp

if not beaker.session.crypto_ok:
    raise SkipTest("No usable crypto library found, can't test cookie-only "
                   "Sessions")

def simple_app(environ, start_response):
    session = environ['beaker.session']
    if not session.has_key('value'):
        session['value'] = 0
    session['value'] += 1
    if not environ['PATH_INFO'].startswith('/nosave'):
        session.save()
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %d and cookie is %s' % (session['value'], session)]

def test_increment():
    options = {'session.validate_key':'hoobermas', 'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res

def test_different_sessions():
    options = {'session.validate_key':'hoobermas', 'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    app2 = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app2.get('/')
    assert 'current value is: 1' in res
    res = app2.get('/')
    res = app2.get('/')
    res = app2.get('/')
    res2 = app.get('/')
    assert 'current value is: 2' in res2
    assert 'current value is: 4' in res

def test_nosave():
    options = {'session.validate_key':'hoobermas', 'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/nosave')
    assert 'current value is: 1' in res
    assert [] == res.headers.getall('Set-Cookie')
    res = app.get('/nosave')
    assert 'current value is: 1' in res
    
    res = app.get('/')
    assert 'current value is: 1' in res
    assert len(res.headers.getall('Set-Cookie')) > 0
    res = app.get('/')
    assert 'current value is: 2' in res

def test_increment_with_encryption():
    options = {'session.encrypt_key':'666a19cf7f61c64c', 'session.validate_key':'hoobermas',
               'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res

def test_different_sessions_with_encryption():
    options = {'session.encrypt_key':'666a19cf7f61c64c', 'session.validate_key':'hoobermas',
               'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    app2 = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app2.get('/')
    assert 'current value is: 1' in res
    res = app2.get('/')
    res = app2.get('/')
    res = app2.get('/')
    res2 = app.get('/')
    assert 'current value is: 2' in res2
    assert 'current value is: 4' in res

def test_nosave_with_encryption():
    options = {'session.encrypt_key':'666a19cf7f61c64c', 'session.validate_key':'hoobermas',
               'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/nosave')
    assert 'current value is: 1' in res
    assert [] == res.headers.getall('Set-Cookie')
    res = app.get('/nosave')
    assert 'current value is: 1' in res
    
    res = app.get('/')
    assert 'current value is: 1' in res
    assert len(res.headers.getall('Set-Cookie')) > 0
    res = app.get('/')
    assert 'current value is: 2' in res

def test_cookie_id():
    options = {'session.encrypt_key':'666a19cf7f61c64c', 'session.validate_key':'hoobermas',
               'session.type':'cookie'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert "_id':" in res
    sess_id = re.sub(r".*'_id': '(.*?)'.*", r'\1', res.body)
    res = app.get('/')
    new_id = re.sub(r".*'_id': '(.*?)'.*", r'\1', res.body)
    assert new_id == sess_id

if __name__ == '__main__':
    from paste import httpserver
    wsgi_app = SessionMiddleware(simple_app, {})
    httpserver.serve(wsgi_app, host='127.0.0.1', port=8080)
