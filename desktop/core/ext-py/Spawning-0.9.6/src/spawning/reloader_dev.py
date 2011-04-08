# Copyright (c) 2008, Donovan Preston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Watch files and send a SIGHUP signal to another process
if any of the files change.
"""

try:
	set
except NameError:
	import sets
	set = sets.Set

import optparse, os, signal, sys, tempfile, time
from os.path import join
from distutils import sysconfig

import eventlet

try:
    from procname import setprocname
except ImportError, e:
    setprocname = lambda n: None

def watch_forever(pid, interval, files=None):
    """
    """
    limiter = eventlet.GreenPool()
    module_mtimes = {}
    last_changed_time = None
    while True:
        uniques = set()

        uniques.add(join(sysconfig.get_python_lib(), 'easy-install.pth'))
        uniques.update(list(get_sys_modules_files()))

        if files:
            uniques.update(files)
        ##print uniques
        changed = False
        for filename in uniques:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
            if not module_mtimes.has_key(filename):
                module_mtimes[filename] = mtime
            elif module_mtimes[filename] < mtime:
                changed = True
                last_changed_time = mtime
                module_mtimes[filename] = mtime
                print "(%s) * File %r changed" % (os.getpid(), filename)

        if not changed and last_changed_time is not None:
            last_changed_time = None
            if pid:
                print "(%s) ** Sending SIGHUP to %s at %s" % (
                    os.getpid(), pid, time.asctime())
                os.kill(pid, signal.SIGHUP)
                return ## this process is going to die now, no need to keep watching
            else:
                print "EXIT??!!!"
                os._exit(5)

        eventlet.sleep(interval)


def get_sys_modules_files():
    for module in sys.modules.values():
        fn = getattr(module, '__file__', None)
        if fn is not None:
            yield os.path.abspath(fn)


def main():
    parser = optparse.OptionParser()
    parser.add_option("-p", "--pid",
        type="int", dest="pid",
        help="A pid to SIGHUP when a monitored file changes. "
        "If not given, just print a message to stdout and kill this process instead.")
    parser.add_option("-i", "--interval",
        type="int", dest="interval",
        help="The time to wait between scans, in seconds.", default=1)
    options, args = parser.parse_args()

    try:
        watch_forever(options.pid, options.interval)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

