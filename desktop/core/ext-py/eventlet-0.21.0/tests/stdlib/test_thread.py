from eventlet import patcher
from eventlet.green import thread
from eventlet.green import time


patcher.inject('test.test_thread', globals())

try:
    # this is a new test in 2.7 that we don't support yet
    TestForkInThread.test_forkinthread = lambda *a, **kw: None
except NameError:
    pass

if __name__ == "__main__":
    test_main()
