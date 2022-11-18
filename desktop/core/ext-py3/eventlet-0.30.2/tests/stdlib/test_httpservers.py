from eventlet import patcher

from eventlet.green import BaseHTTPServer
from eventlet.green import SimpleHTTPServer
from eventlet.green import CGIHTTPServer
from eventlet.green import urllib
from eventlet.green import httplib
from eventlet.green import threading

patcher.inject(
    'test.test_httpservers',
    globals(),
    ('BaseHTTPServer', BaseHTTPServer),
    ('SimpleHTTPServer', SimpleHTTPServer),
    ('CGIHTTPServer', CGIHTTPServer),
    ('urllib', urllib),
    ('httplib', httplib),
    ('threading', threading))

if __name__ == "__main__":
    test_main()
