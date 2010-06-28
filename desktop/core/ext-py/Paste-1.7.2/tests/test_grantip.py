from paste.auth import grantip
from paste.fixture import *

def test_make_app():
    def application(environ, start_response):
        start_response('200 OK', [('content-type', 'text/plain')])
        return [
            str(environ.get('REMOTE_USER')),
            ':',
            str(environ.get('REMOTE_USER_TOKENS')),
            ]
    ip_map = {
        '127.0.0.1': (None, 'system'),
        '192.168.0.0/16': (None, 'worker'),
        '192.168.0.5<->192.168.0.8': ('bob', 'editor'),
        '192.168.0.8': ('__remove__', '-worker'),
        }
    app = grantip.GrantIPMiddleware(application, ip_map)
    app = TestApp(app)
    return app

def test_req():
    app = test_make_app()
    def doit(remote_addr):
        res = app.get('/', extra_environ={'REMOTE_ADDR': remote_addr})
        return res.body
    assert doit('127.0.0.1') == 'None:system'
    assert doit('192.168.15.12') == 'None:worker'
    assert doit('192.168.0.4') == 'None:worker'
    result = doit('192.168.0.5')
    assert result.startswith('bob:')
    assert 'editor' in result and 'worker' in result
    assert result.count(',') == 1
    assert doit('192.168.0.8') == 'None:editor'
