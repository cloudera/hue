import sys, time, threading, thread, os, traceback, threadframe, pprint
# daemon thread that spouts Monty Pythonesque nonsense
class T(threading.Thread):
  def run(self):
    while 1:
      time.sleep(1)
      print '[%d] Spam spam spam spam. Lovely spam! Wonderful spam!' % ( thread.get_ident(), )
# thread that cause a deliberate deadlock with itself
U_lock = threading.Lock()
class U(threading.Thread):
  def run(self):
    U_lock.acquire()
    U_lock.acquire()
# thread that will exit after the thread frames are extracted but before
# they are printed
V_event = threading.Event()
class V(threading.Thread):
  def run(self):
    V_event.clear()
    V_event.wait()
    
print 'ident of main thread is: %d' % (thread.get_ident(),)
print
print 'launching daemon thread...',
T().start()
print 'done'
print 'launching self-deadlocking thread...',
U().start()
print 'done'
print 'launching thread that will die before the end...',
v = V()
v.start()
print 'done'

time.sleep(5)

# Python 2.2 does not support threadframe.dict()
if sys.hexversion < 0x02030000:
  frames = threadframe.threadframe()
else:
  frames = threadframe.dict()

# signal the thread V to die, then wait for it to oblige
V_event.set()
v.join()

if sys.hexversion < 0x02030000:
  for frame in frames:
    print '-' * 72
    print 'frame ref count = %d' % sys.getrefcount(frame)
    traceback.print_stack(frame)
else:
  for thread_id, frame in frames.iteritems():
    print '-' * 72
    print '[%s] %d' % (thread_id, sys.getrefcount(frame))
    traceback.print_stack(frame)
os._exit(0)
