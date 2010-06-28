from paste.urlmap import *
from paste.fixture import *

def make_app(response_text):
    def app(environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response('200 OK', headers)
        return [response_text % environ]
    return app

def test_map():
    mapper = URLMap({})
    app = TestApp(mapper)
    text = '%s script_name="%%(SCRIPT_NAME)s" path_info="%%(PATH_INFO)s"'
    mapper[''] = make_app(text % 'root')
    mapper['/foo'] = make_app(text % 'foo-only')
    mapper['/foo/bar'] = make_app(text % 'foo:bar')
    mapper['/f'] = make_app(text % 'f-only')
    res = app.get('/')
    res.mustcontain('root')
    res.mustcontain('script_name=""')
    res.mustcontain('path_info="/"')
    res = app.get('/blah')
    res.mustcontain('root')
    res.mustcontain('script_name=""')
    res.mustcontain('path_info="/blah"')
    res = app.get('/foo/and/more')
    res.mustcontain('script_name="/foo"')
    res.mustcontain('path_info="/and/more"')
    res.mustcontain('foo-only')
    res = app.get('/foo/bar/baz')
    res.mustcontain('foo:bar')
    res.mustcontain('script_name="/foo/bar"')
    res.mustcontain('path_info="/baz"')
    res = app.get('/fffzzz')
    res.mustcontain('root')
    res.mustcontain('path_info="/fffzzz"')
    res = app.get('/f/z/y')
    res.mustcontain('script_name="/f"')
    res.mustcontain('path_info="/z/y"')
    res.mustcontain('f-only')
    
