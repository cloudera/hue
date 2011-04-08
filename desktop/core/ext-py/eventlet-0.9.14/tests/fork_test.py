from tests.patcher_test import ProcessBase


class ForkTest(ProcessBase):
    def test_simple(self):
        newmod = '''
import eventlet
import os
import sys
import signal
mydir = %r
signal_file = os.path.join(mydir, "output.txt")
pid = os.fork()
if (pid != 0):
  eventlet.Timeout(10)
  try:
    port = None
    while True:
      try:
        contents = open(signal_file, "rb").read()
        port = int(contents.split()[0])
        break
      except (IOError, IndexError, ValueError, TypeError):
        eventlet.sleep(0.1)
    eventlet.connect(('127.0.0.1', port))
    while True:
      try:
        contents = open(signal_file, "rb").read()
        result = contents.split()[1]
        break
      except (IOError, IndexError):
        eventlet.sleep(0.1)
    print 'result', result
  finally:
    os.kill(pid, signal.SIGTERM)
else:
  try:
    s = eventlet.listen(('', 0))
    fd = open(signal_file, "wb")
    fd.write(str(s.getsockname()[1]))
    fd.write("\\n")
    fd.flush()
    s.accept()
    fd.write("done")
    fd.flush()
  finally:
    fd.close()
'''
        self.write_to_tempfile("newmod", newmod % self.tempdir)
        output, lines = self.launch_subprocess('newmod.py')
        self.assertEqual(lines[0], "result done", output)
