from eventlet import patcher
from eventlet.green import SimpleHTTPServer

patcher.inject(
    'test.test_SimpleHTTPServer',
    globals(),
    ('SimpleHTTPServer', SimpleHTTPServer))

if __name__ == "__main__":
    test_main()
