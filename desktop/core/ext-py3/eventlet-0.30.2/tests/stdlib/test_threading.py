from eventlet import patcher
from eventlet.green import threading
from eventlet.green import thread
from eventlet.green import time

# *NOTE: doesn't test as much of the threading api as we'd like because many of
# the tests are launched via subprocess and therefore don't get patched

patcher.inject('test.test_threading',
               globals())

# "PyThreadState_SetAsyncExc() is a CPython-only gimmick, not (currently)
# exposed at the Python level.  This test relies on ctypes to get at it."
# Therefore it's also disabled when testing eventlet, as it's not emulated.
try:
    ThreadTests.test_PyThreadState_SetAsyncExc = lambda s: None
except (AttributeError, NameError):
    pass

# disabling this test because it fails when run in Hudson even though it always
# succeeds when run manually
try:
    ThreadJoinOnShutdown.test_3_join_in_forked_from_thread = lambda *a, **kw: None
except (AttributeError, NameError):
    pass

# disabling this test because it relies on dorking with the hidden
# innards of the threading module in a way that doesn't appear to work
# when patched
try:
    ThreadTests.test_limbo_cleanup = lambda *a, **kw: None
except (AttributeError, NameError):
    pass

# this test has nothing to do with Eventlet; if it fails it's not
# because of patching (which it does, grump grump)
try:
    ThreadTests.test_finalize_runnning_thread = lambda *a, **kw: None
    # it's misspelled in the stdlib, silencing this version as well because
    # inevitably someone will correct the error
    ThreadTests.test_finalize_running_thread = lambda *a, **kw: None
except (AttributeError, NameError):
    pass

if __name__ == "__main__":
    test_main()
