from eventlet import patcher
from eventlet.green import socket

to_patch = [('socket', socket)]

try:
    from eventlet.green import ssl
    to_patch.append(('ssl', ssl))
except ImportError:
    pass

patcher.inject('httplib',
    globals(),
    *to_patch)
        
if __name__ == '__main__':
    test()
