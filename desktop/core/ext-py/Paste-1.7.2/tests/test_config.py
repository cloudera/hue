# (c) 2007 Philip Jenvey; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
from py.test import raises
from paste.config import CONFIG, ConfigMiddleware
from paste.fixture import TestApp

test_key = 'test key'

def app_with_config(environ, start_response):
    start_response('200 OK', [('Content-type','text/plain')])
    return ['Variable is: %s\n' % CONFIG[test_key],
            'Variable is (in environ): %s' % environ['paste.config'][test_key]]

class NestingAppWithConfig(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        response = self.app(environ, start_response)
        assert isinstance(response, list)
        supplement = ['Nesting variable is: %s' % CONFIG[test_key],
                      'Nesting variable is (in environ): %s' % \
                          environ['paste.config'][test_key]]
        response.extend(supplement)
        return response

def test_request_config():
    config = {test_key: 'test value'}
    app = ConfigMiddleware(app_with_config, config)
    res = TestApp(app).get('/')
    assert 'Variable is: test value' in res
    assert 'Variable is (in environ): test value' in res

def test_request_config_multi():
    config = {test_key: 'test value'}
    app = ConfigMiddleware(app_with_config, config)
    config = {test_key: 'nesting value'}
    app = ConfigMiddleware(NestingAppWithConfig(app), config)
    res = TestApp(app).get('/')
    assert 'Variable is: test value' in res
    assert 'Variable is (in environ): test value' in res
    assert 'Nesting variable is: nesting value' in res
    print res
    assert 'Nesting variable is (in environ): nesting value' in res

def test_process_config(request_app=test_request_config):
    process_config = {test_key: 'bar', 'process_var': 'foo'}
    CONFIG.push_process_config(process_config)

    assert CONFIG[test_key] == 'bar'
    assert CONFIG['process_var'] == 'foo'

    request_app()

    assert CONFIG[test_key] == 'bar'
    assert CONFIG['process_var'] == 'foo'
    CONFIG.pop_process_config()
    
    raises(AttributeError, lambda: 'process_var' not in CONFIG)
    raises(IndexError, CONFIG.pop_process_config)

def test_process_config_multi():
    test_process_config(test_request_config_multi)
