from eventlet import patcher
from eventlet.green import httplib
from eventlet.green import urllib

patcher.inject(
    'test.test_urllib',
    globals(),
    ('httplib', httplib),
    ('urllib', urllib))

if __name__ == "__main__":
    test_main()
