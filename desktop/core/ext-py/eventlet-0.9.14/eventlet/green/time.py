__time = __import__('time')
globals().update(dict([(var, getattr(__time, var))
                       for var in dir(__time) 
                       if not var.startswith('__')]))
__patched__ = ['sleep']
from eventlet.greenthread import sleep
sleep # silence pyflakes
