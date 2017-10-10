"""
From gevent/hub.py
"""
PY3 = sys.version_info[0] >= 3

if PY3:
    string_types = str,
    integer_types = int,
else:
    string_types = basestring,
    integer_types = (int, long)


if sys.version_info[0] <= 2:
    import thread
else:
    import _thread as thread
