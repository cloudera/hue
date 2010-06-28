import re
import os

from beaker.middleware import SessionMiddleware
from webtest import TestApp

loc = os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), 'sessions'])

def no_save_app(environ, start_response):
    session = environ['beaker.session']
    sess_id = environ.get('SESSION_ID')
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %s, session id is %s' % (session.get('value'),
                                                            session.id)]
    
def simple_app(environ, start_response):
    session = environ['beaker.session']
    sess_id = environ.get('SESSION_ID')
    if sess_id:
        session = session.get_by_id(sess_id)
    if not session:
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ["No session id of %s found." % sess_id]
    if not session.has_key('value'):
        session['value'] = 0
    session['value'] += 1
    if not environ['PATH_INFO'].startswith('/nosave'):
        session.save()
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %d, session id is %s' % (session['value'],
                                                            session.id)]

def simple_auto_app(environ, start_response):
    """Like the simple_app, but assume that sessions auto-save"""
    session = environ['beaker.session']
    sess_id = environ.get('SESSION_ID')
    if sess_id:
        session = session.get_by_id(sess_id)
    if not session:
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ["No session id of %s found." % sess_id]
    if not session.has_key('value'):
        session['value'] = 0
    session['value'] += 1
    if environ['PATH_INFO'].startswith('/nosave'):
        session.revert()
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %d, session id is %s' % (session.get('value', 0),
                                                            session.id)]

def test_no_save():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(no_save_app, **options))
    res = app.get('/')
    assert 'current value is: None' in res
    assert [] == res.headers.getall('Set-Cookie')


def test_increment():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res

def test_increment_auto():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(simple_auto_app, auto=True, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res


def test_different_sessions():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
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

def test_different_sessions_auto():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(simple_auto_app, auto=True, **options))
    app2 = TestApp(SessionMiddleware(simple_auto_app, auto=True, **options))
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
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/nosave')
    assert 'current value is: 1' in res
    res = app.get('/nosave')
    assert 'current value is: 1' in res
    
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res

def test_revert():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(simple_auto_app, auto=True, **options))
    res = app.get('/nosave')
    assert 'current value is: 0' in res
    res = app.get('/nosave')
    assert 'current value is: 0' in res
    
    res = app.get('/')
    assert 'current value is: 1' in res
    assert [] == res.headers.getall('Set-Cookie')
    res = app.get('/')
    assert [] == res.headers.getall('Set-Cookie')
    assert 'current value is: 2' in res
    
    # Finally, ensure that reverting shows the proper one
    res = app.get('/nosave')
    assert [] == res.headers.getall('Set-Cookie')
    assert 'current value is: 2' in res

def test_load_session_by_id():
    options = {'session.data_dir':loc, 'session.secret':'blah'}
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    res = app.get('/')
    res = app.get('/')
    assert 'current value is: 3' in res
    old_id = re.sub(r'^.*?session id is (\S+)$', r'\1', res.body, re.M)
    
    # Clear the cookies and do a new request
    app = TestApp(SessionMiddleware(simple_app, **options))
    res = app.get('/')
    assert 'current value is: 1' in res
    
    # Load a bogus session to see that its not there
    res = app.get('/', extra_environ={'SESSION_ID':'jil2j34il2j34ilj23'})
    assert 'No session id of' in res
    
    # Saved session was at 3, now it'll be 4
    res = app.get('/', extra_environ={'SESSION_ID':old_id})
    assert 'current value is: 4' in res
    
    # Prior request is now up to 2
    res = app.get('/')
    assert 'current value is: 2' in res


if __name__ == '__main__':
    from paste import httpserver
    wsgi_app = SessionMiddleware(simple_app, {})
    httpserver.serve(wsgi_app, host='127.0.0.1', port=8080)
