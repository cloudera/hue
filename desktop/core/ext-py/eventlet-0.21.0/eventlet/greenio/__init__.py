from eventlet.support import six

from eventlet.greenio.base import *  # noqa

if six.PY2:
    from eventlet.greenio.py2 import *  # noqa
else:
    from eventlet.greenio.py3 import *  # noqa
