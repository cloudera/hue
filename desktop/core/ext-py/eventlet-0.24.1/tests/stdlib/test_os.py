from eventlet import patcher
from eventlet.green import os

patcher.inject(
    'test.test_os',
    globals(),
    ('os', os))

if __name__ == "__main__":
    test_main()
