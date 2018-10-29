# Copyright 2009-2014 Jason Stitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import threading
from Queue import Queue
from tidylib import tidy_document

error_queue = Queue()

DOC = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title></title>
  </head>
  <body>
    hello, world
  </body>
</html>
'''

SAMPLE = "hello, world"

NUM_THREADS = 100
NUM_TRIES = 100


class TidyingThread(threading.Thread):
    def run(self):
        for x in xrange(NUM_TRIES):
            output, errors = tidy_document(SAMPLE, keep_doc=True)
            if output != DOC:
                error_queue.put(output)


def run_test():
    threads = []
    for i in xrange(NUM_THREADS):
        t = TidyingThread()
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    run_test()
    if not error_queue.empty():
        print("About %s errors out of %s" % (error_queue.qsize(), NUM_THREADS * NUM_TRIES))
        print(error_queue.get())
