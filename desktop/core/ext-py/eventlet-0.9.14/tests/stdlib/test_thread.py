from eventlet import patcher
from eventlet.green import thread
from eventlet.green import time

# necessary to initialize the hub before running on 2.5
from eventlet import hubs
hubs.get_hub()

patcher.inject('test.test_thread', globals())

try:
    # this is a new test in 2.7 that we don't support yet
    TestForkInThread.test_forkinthread = lambda *a, **kw: None
except NameError:
    pass

if __name__ == "__main__":
    try:
        test_main()
    except NameError:
        pass  # 2.5
