from eventlet import patcher
from eventlet.green import subprocess
from eventlet.green import time

patcher.inject(
    'test.test_subprocess',
    globals(),
    ('subprocess', subprocess),
    ('time', time))

if __name__ == "__main__":
    test_main()
