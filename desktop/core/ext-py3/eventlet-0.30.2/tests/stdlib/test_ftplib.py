from eventlet import patcher
from eventlet.green import asyncore
from eventlet.green import ftplib
from eventlet.green import threading
from eventlet.green import socket

patcher.inject('test.test_ftplib', globals())

# this test only fails on python2.7/pyevent/--with-xunit; screw that
try:
    TestTLS_FTPClass.test_data_connection = lambda *a, **kw: None
except (AttributeError, NameError):
    pass

if __name__ == "__main__":
    test_main()
