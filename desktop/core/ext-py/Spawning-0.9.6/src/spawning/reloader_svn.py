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

"""Watch the svn revision returned from svn info and send a SIGHUP
to a process when the revision changes.
"""


import commands, optparse, os, signal, sys, tempfile, time

try:
    from procname import setprocname
except ImportError, e:
    setprocname = lambda n: None


def get_revision(directory):
    cmd = 'svn info'
    if directory is not None:
        cmd = '%s %s' % (cmd, directory)

    try:
        out = commands.getoutput(cmd).split('\n')
    except IOError:
        return

    for line in out:
        if line.startswith('Revision: '):
            return int(line[len('Revision: '):])


def watch_forever(directories, pid, interval):
    setprocname("spawn: svn reloader")
    if directories is None:
        directories = ['.']
    ## Look for externals
    all_svn_repos = set(directories)

    def visit(parent, subdirname, children):
        if '.svn' in children:
            children.remove('.svn')
        status, out = commands.getstatusoutput('svn propget svn:externals %s' % (subdirname, ))
        if status:
            return

        for line in out.split('\n'):
            line = line.strip()
            if not line:
                continue
            name, _external_url = line.split()
            fulldir = os.path.join(parent, subdirname, name)
            ## Don't keep going into the external in the walk()
            try:
                children.remove(name)
            except ValueError:
                print "*** An entry in svn externals doesn't exist, ignoring:", name
            else:
                directories.append(fulldir)
                all_svn_repos.add(fulldir)

    while directories:
        dirname = directories.pop(0)
        os.path.walk(dirname, visit, dirname)

    revisions = {}
    for dirname in all_svn_repos:
        revisions[dirname] = get_revision(dirname)

    print "(%s) svn watcher watching directories: %s" % (
        os.getpid(), list(all_svn_repos))

    while True:
        if pid:
            ## Check to see if our controller is still alive; if not, just exit.
            try:
                os.getpgid(pid)
            except OSError:
                print "(%s) reloader_svn is orphaned; controller %s no longer running. Exiting." % (
                    os.getpid(), pid)
                os._exit(0)

        for dirname in all_svn_repos:
            new_revision = get_revision(dirname)

            if new_revision is not None and new_revision != revisions[dirname]:
                revisions[dirname] = new_revision
                if pid:
                    print "(%s) * SVN revision changed on %s to %s; Sending SIGHUP to %s at %s" % (
                        os.getpid(), dirname, new_revision, pid, time.asctime())
                    os.kill(pid, signal.SIGHUP)
                    os._exit(0)
                else:
                    print "(%s) Revision changed, dying at %s" % (
                        os.getpid(), time.asctime())
                    os._exit(5)

        time.sleep(interval)


def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--dir", dest='dirs', action="append",
        help="The directories to do svn info in. If not given, use cwd.")
    parser.add_option("-p", "--pid",
        type="int", dest="pid",
        help="A pid to SIGHUP when the svn revision changes. "
        "If not given, just print a message to stdout and kill this process instead.")
    parser.add_option("-i", "--interval",
        type="int", dest="interval",
        help="The time to wait between scans, in seconds.", default=10)
    options, args = parser.parse_args()

    print "(%s) svn watcher running, controller pid %s" % (os.getpid(), options.pid)
    if options.pid is None:
        options.pid = os.getpid()
    try:
        watch_forever(options.dirs, int(options.pid), options.interval)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

