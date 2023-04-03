from eventlet import patcher
from eventlet.green import socket
from eventlet.green import urllib2

patcher.inject(
    'test.test_urllib2',
    globals(),
    ('socket', socket),
    ('urllib2', urllib2))

HandlerTests.test_file = patcher.patch_function(HandlerTests.test_file, ('socket', socket))
HandlerTests.test_cookie_redirect = patcher.patch_function(
    HandlerTests.test_cookie_redirect, ('urllib2', urllib2))
OpenerDirectorTests.test_badly_named_methods = patcher.patch_function(
    OpenerDirectorTests.test_badly_named_methods, ('urllib2', urllib2))

if __name__ == "__main__":
    test_main()
