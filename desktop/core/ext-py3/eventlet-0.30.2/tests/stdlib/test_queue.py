from eventlet import patcher
from eventlet.green import Queue
from eventlet.green import threading
from eventlet.green import time

patcher.inject(
    'test.test_queue',
    globals(),
    ('Queue', Queue),
    ('threading', threading),
    ('time', time))

if __name__ == "__main__":
    test_main()
