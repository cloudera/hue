from eventlet import patcher
from eventlet.green import thread
from eventlet.green import threading
from eventlet.green import time

# hub requires initialization before test can run
from eventlet import hubs
hubs.get_hub()

patcher.inject(
    'test.test_threading_local',
    globals(),
    ('time', time),
    ('thread', thread),
    ('threading', threading))

if __name__ == '__main__':
    test_main()
