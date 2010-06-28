import os
import sys
import py.test
from paste.cgiapp import CGIApplication, CGIError
from paste.fixture import *

data_dir = os.path.join(os.path.dirname(__file__), 'cgiapp_data')

if sys.platform != 'win32': # these CGI scripts can't work on Windows
    def test_ok():
        app = TestApp(CGIApplication({}, script='ok.cgi', path=[data_dir]))
        res = app.get('')
        assert res.header('content-type') == 'text/html; charset=UTF-8'
        assert res.full_status == '200 Okay'
        assert 'This is the body' in res

    def test_form():
        app = TestApp(CGIApplication({}, script='form.cgi', path=[data_dir]))
        res = app.post('', params={'name': 'joe'},
                       upload_files=[('up', 'file.txt', 'x'*10000)])
        assert 'file.txt' in res
        assert 'joe' in res
        assert 'x'*10000 in res

    def test_error():
        app = TestApp(CGIApplication({}, script='error.cgi', path=[data_dir]))
        py.test.raises(CGIError, "app.get('', status=500)")

    def test_stderr():
        app = TestApp(CGIApplication({}, script='stderr.cgi', path=[data_dir]))
        res = app.get('', expect_errors=True)
        assert res.status == 500
        assert 'error' in res
        assert 'some data' in res.errors

