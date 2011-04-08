#!/usr/bin/env python
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
import eventlet

import commands
import datetime
import errno
import logging
import optparse
import pprint
import signal
from eventlet.green import socket
import sys
from eventlet.green import time
import traceback

try:
    import simplejson as json
except ImportError:
    import json


import eventlet.backdoor
from eventlet.green import os

import spawning
import spawning.util

KEEP_GOING = True
RESTART_CONTROLLER = False
PANIC = False


DEFAULTS = {
    'num_processes': 4,
    'threadpool_workers': 4,
    'watch': [],
    'dev': True,
    'host': '',
    'port': 8080,
    'max_memory': None,
}

def print_exc(msg="Exception occured!"):
    print >>sys.stderr, "(%d) %s" % (os.getpid(), msg)
    traceback.print_exc()

def environ():
    env = os.environ.copy()
    # to avoid duplicates in the new sys.path
    revised_paths = set()
    new_path = list()
    for path in sys.path:
        if os.path.exists(path) and path not in revised_paths:
            revised_paths.add(path)
            new_path.append(path)
    current_directory = os.path.realpath('.')
    if current_directory not in revised_paths:
        new_path.append(current_directory)

    env['PYTHONPATH'] = ':'.join(new_path)
    return env

class Child(object):
    def __init__(self, pid, kill_pipe):
        self.pid = pid
        self.kill_pipe = kill_pipe
        self.active = True
        self.forked_at = datetime.datetime.now()

class Controller(object):
    sock = None
    factory = None
    args = None
    config = None
    children = None
    keep_going = True
    panic = False
    log = None
    controller_pid = None
    num_processes = 0

    def __init__(self, sock, factory, args, **kwargs):
        self.sock = sock
        self.factory = factory
        self.config = spawning.util.named(factory)(args)
        self.args = args
        self.children = {}
        self.log = logging.getLogger('Spawning')
        if not kwargs.get('log_handler'):
            self.log.addHandler(logging.StreamHandler())
        self.log.setLevel(logging.DEBUG)
        self.controller_pid = os.getpid()
        self.num_processes = int(self.config.get('num_processes', 0))
        self.started_at = datetime.datetime.now()

    def spawn_children(self, number=1):
        parent_pid = os.getpid()
        self.log.debug('Controller.spawn_children(number=%d)' % number)

        for i in range(number):
            child_side, parent_side = os.pipe()
            try:
                child_pid = os.fork()
            except:
                print_exc('Could not fork child! Panic!')
                ### TODO: restart

            if not child_pid:      # child process
                os.close(parent_side)
                command = [sys.executable, '-c',
                    'import sys; from spawning import spawning_child; spawning_child.main()',
                    str(parent_pid),
                    str(self.sock.fileno()),
                    str(child_side),
                    self.factory,
                    json.dumps(self.args)]
                if self.args['reload'] == 'dev':
                    command.append('--reload')
		if self.args.get('ssl_private_key') and self.args.get('ssl_certificate'):
                    command.append('--ssl-private-key')
                    command.append(self.args.get('ssl_private_key'))
                    command.append('--ssl-certificate')
                    command.append(self.args.get('ssl_certificate'))
                env = environ()
                tpool_size = int(self.config.get('threadpool_workers', 0))
                assert tpool_size >= 0, (tpool_size, 'Cannot have a negative --threads argument')
                if not tpool_size in (0, 1):
                    env['EVENTLET_THREADPOOL_SIZE'] = str(tpool_size)
                os.execve(sys.executable, command, env)

            # controller process
            os.close(child_side)
            self.children[child_pid] = Child(child_pid, parent_side)

    def children_count(self):
        return len(self.children)

    def runloop(self):
        while self.keep_going:
            eventlet.sleep(0.1)
            ## Only start the number of children we need
            number = self.num_processes - self.children_count()
            if number > 0:
                self.log.debug('Should start %d new children', number)
                self.spawn_children(number=number)
                continue

            if not self.children:
                ## If we don't yet have children, let's loop
                continue

            pid, result = None, None
            try:
                pid, result = os.wait()
            except OSError, e:
                if e.errno != errno.EINTR:
                    raise

            if pid and self.children.get(pid):
                try:
                    child = self.children.pop(pid)
                    os.close(child.kill_pipe)
                except (IOError, OSError):
                    pass

            if result:
                signum = os.WTERMSIG(result)
                exitcode = os.WEXITSTATUS(result)
                self.log.info('(%s) Child died from signal %s with code %s',
                              pid, signum, exitcode)

    def handle_sighup(self, *args, **kwargs):
        ''' Pass `no_restart` to prevent restarting the run loop '''
        self.kill_children()
        self.spawn_children(number=self.num_processes)
        # TODO: nothing seems to use no_restart, can it be removed?
        if not kwargs.get('no_restart', True):
            self.runloop()

    def kill_children(self):
        for pid, child in self.children.items():
            try:
                os.write(child.kill_pipe, 'k')
                child.active = False
                # all maintenance of children's membership happens in runloop()
                # as children die and os.wait() gets results
            except OSError, e:
                if e.errno != errno.EPIPE:
                    raise

    def handle_deadlychild(self, *args, **kwargs):
        if self.keep_going:
            self.log.debug('A child intends to die, starting replacement before it dies')
            self.spawn_children(number=1)

    def run(self):
        self.log.info('(%s) *** Controller starting at %s' % (self.controller_pid,
                time.asctime()))

        if self.config.get('pidfile'):
            fd = open(self.config.get('pidfile'), 'w')
            try:
                fd.write('%s\n' % self.controller_pid)
            finally:
                fd.close()

        spawning.setproctitle("spawn: controller " + self.args.get('argv_str', ''))

        if self.sock is None:
            self.sock = bind_socket(self.config)

        signal.signal(signal.SIGHUP, self.handle_sighup)
        signal.signal(signal.SIGUSR1, self.handle_deadlychild)

        if self.config.get('status_port'):
            from spawning.util import status
            eventlet.spawn(status.Server, self,
                self.config['status_host'], self.config['status_port'])

        try:
            self.runloop()
        except KeyboardInterrupt:
            self.keep_going = False
            self.kill_children()
        self.log.info('(%s) *** Controller exiting' % (self.controller_pid))

def bind_socket(config):
    sleeptime = 0.5
    host = config.get('host', '')
    port = config.get('port', 8080)
    for x in range(8):
        try:
            sock = eventlet.listen((host, port))
            break
        except socket.error, e:
            if e[0] != errno.EADDRINUSE:
                raise
            print "(%s) socket %s:%s already in use, retrying after %s seconds..." % (
                os.getpid(), host, port, sleeptime)
            eventlet.sleep(sleeptime)
            sleeptime *= 2
    else:
        print "(%s) could not bind socket %s:%s, dying." % (
            os.getpid(), host, port)
        sys.exit(1)
    return sock

def set_process_owner(spec):
    import pwd, grp
    if ":" in spec:
        user, group = spec.split(":", 1)
    else:
        user, group = spec, None
    if group:
        os.setgid(grp.getgrnam(group).gr_gid)
    if user:
        os.setuid(pwd.getpwnam(user).pw_uid)
    return user, group

def start_controller(sock, factory, factory_args):
    c = Controller(sock, factory, factory_args)
    installGlobal(c)
    c.run()

def main():
    current_directory = os.path.realpath('.')
    if current_directory not in sys.path:
        sys.path.append(current_directory)

    parser = optparse.OptionParser(description="Spawning is an easy-to-use and flexible wsgi server. It supports graceful restarting so that your site finishes serving any old requests while starting new processes to handle new requests with the new code. For the simplest usage, simply pass the dotted path to your wsgi application: 'spawn my_module.my_wsgi_app'", version=spawning.__version__)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', help='Display verbose configuration '
        'information when starting up or restarting.')
    parser.add_option("-f", "--factory", dest='factory', default='spawning.wsgi_factory.config_factory',
        help="""Dotted path (eg mypackage.mymodule.myfunc) to a callable which takes a dictionary containing the command line arguments and figures out what needs to be done to start the wsgi application. Current valid values are: spawning.wsgi_factory.config_factory, spawning.paste_factory.config_factory, and spawning.django_factory.config_factory. The factory used determines what the required positional command line arguments will be. See the spawning.wsgi_factory module for documentation on how to write a new factory.
        """)
    parser.add_option("-i", "--host",
        dest='host', default=DEFAULTS['host'],
        help='The local ip address to bind.')
    parser.add_option("-p", "--port",
        dest='port', type='int', default=DEFAULTS['port'],
        help='The local port address to bind.')
    parser.add_option("-s", "--processes",
        dest='processes', type='int', default=DEFAULTS['num_processes'],
        help='The number of unix processes to start to use for handling web i/o.')
    parser.add_option("-t", "--threads",
        dest='threads', type='int', default=DEFAULTS['threadpool_workers'],
        help="The number of posix threads to use for handling web requests. "
            "If threads is 0, do not use threads but instead use eventlet's cooperative "
            "greenlet-based microthreads, monkeypatching the socket and pipe operations which normally block "
            "to cooperate instead. Note that most blocking database api modules will not "
            "automatically cooperate.")
    parser.add_option('-d', '--daemonize', dest='daemonize', action='store_true',
        help="Daemonize after starting children.")
    parser.add_option('-u', '--chuid', dest='chuid', metavar="ID",
        help="Change user ID in daemon mode (and group ID if given, "
             "separate with colon.)")
    parser.add_option('--pidfile', dest='pidfile', metavar="FILE",
        help="Write own process ID to FILE in daemon mode.")
    parser.add_option('--stdout', dest='stdout', metavar="FILE",
        help="Redirect stdout to FILE in daemon mode.")
    parser.add_option('--stderr', dest='stderr', metavar="FILE",
        help="Redirect stderr to FILE in daemon mode.")
    parser.add_option('-w', '--watch', dest='watch', action='append',
        help="Watch the given file's modification time. If the file changes, the web server will "
            'restart gracefully, allowing old requests to complete in the old processes '
            'while starting new processes with the latest code or configuration.')
    ## TODO Hook up the svn reloader again
    parser.add_option("-r", "--reload",
        type='str', dest='reload',
        help='If --reload=dev is passed, reload any time '
        'a loaded module or configuration file changes.')
    parser.add_option('-l', '--access-log-file', dest='access_log_file', default=None,
        help='The file to log access log lines to. If not given, log to stdout. Pass /dev/null to discard logs.')
    parser.add_option('-c', '--coverage', dest='coverage', action='store_true',
        help='If given, gather coverage data from the running program and make the '
            'coverage report available from the /_coverage url. See the figleaf docs '
            'for more info: http://darcs.idyll.org/~t/projects/figleaf/doc/')
    parser.add_option('--sysinfo', dest='sysinfo', action='store_true',
        help='If given, gather system information data and make the '
            'report available from the /_sysinfo url.')
    parser.add_option('-m', '--max-memory', dest='max_memory', type='int', default=0,
        help='If given, the maximum amount of memory this instance of Spawning '
            'is allowed to use. If all of the processes started by this Spawning controller '
            'use more than this amount of memory, send a SIGHUP to the controller '
            'to get the children to restart.')
    parser.add_option('--backdoor', dest='backdoor', action='store_true',
            help='Start a backdoor bound to localhost:3000')
    parser.add_option('-a', '--max-age', dest='max_age', type='int',
        help='If given, the maximum amount of time (in seconds) an instance of spawning_child '
            'is allowed to run. Once this time limit has expired the child will'
            'gracefully kill itself while the server starts a replacement.')
    parser.add_option('--no-keepalive', dest='no_keepalive', action='store_true',
            help='Disable HTTP/1.1 KeepAlive')
    parser.add_option('-z', '--z-restart-args', dest='restart_args',
        help='For internal use only')
    parser.add_option('--status-port', dest='status_port', type='int', default=0,
        help='If given, hosts a server status page at that port.  Two pages are served: a human-readable HTML version at http://host:status_port/status, and a machine-readable version at http://host:status_port/status.json')
    parser.add_option('--status-host', dest='status_host', type='string', default='',
        help='If given, binds the server status page to the specified local ip address.  Defaults to the same value as --host.  If --status-port is not supplied, the status page will not be activated.')
    parser.add_option('--ssl-certificate', dest='ssl_certificate', type='string', default='',
        help='Absolute path to SSL certificate file.')
    parser.add_option('--ssl-private-key', dest='ssl_private_key', type='string', default='',
        help='Absolute path to SSL private key.')

    options, positional_args = parser.parse_args()

    if len(positional_args) < 1 and not options.restart_args:
        parser.error("At least one argument is required. "
            "For the default factory, it is the dotted path to the wsgi application "
            "(eg my_package.my_module.my_wsgi_application). For the paste factory, it "
            "is the ini file to load. Pass --help for detailed information about available options.")

    if options.backdoor:
        try:
            eventlet.spawn(eventlet.backdoor.backdoor_server, eventlet.listen(('localhost', 3000)))
        except Exception, ex:
            sys.stderr.write('**> Error opening backdoor: %s\n' % ex)

    sock = None

    if options.restart_args:
        restart_args = json.loads(options.restart_args)
        factory = restart_args['factory']
        factory_args = restart_args['factory_args']

        start_delay = restart_args.get('start_delay')
        if start_delay is not None:
            factory_args['start_delay'] = start_delay
            print "(%s) delaying startup by %s" % (os.getpid(), start_delay)
            time.sleep(start_delay)

        fd = restart_args.get('fd')
        if fd is not None:
            sock = socket.fromfd(restart_args['fd'], socket.AF_INET, socket.SOCK_STREAM)
            ## socket.fromfd doesn't result in a socket object that has the same fd.
            ## The old fd is still open however, so we close it so we don't leak.
            os.close(restart_args['fd'])
        return start_controller(sock, factory, factory_args)

    ## We're starting up for the first time.
    if options.daemonize:
        # Do the daemon dance. Note that this isn't what is considered good
        # daemonization, because frankly it's convenient to keep the file
        # descriptiors open (especially when there are prints scattered all
        # over the codebase.)
        # What we do instead is fork off, create a new session, fork again.
        # This leaves the process group in a state without a session
        # leader.
        pid = os.fork()
        if not pid:
            os.setsid()
            pid = os.fork()
            if pid:
                os._exit(0)
        else:
            os._exit(0)
        print "(%s) now daemonized" % (os.getpid(),)
        # Close _all_ open (and othewise!) files.
        import resource
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            maxfd = 4096
        for fdnum in xrange(maxfd):
            try:
                os.close(fdnum)
            except OSError, e:
                if e.errno != errno.EBADF:
                    raise
        # Remap std{in,out,err}
        devnull = os.open(os.path.devnull, os.O_RDWR)
        oflags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        if devnull != 0:  # stdin
            os.dup2(devnull, 0)
        if options.stdout:
            stdout_fd = os.open(options.stdout, oflags)
            if stdout_fd != 1:
                os.dup2(stdout_fd, 1)
                os.close(stdout_fd)
        else:
            os.dup2(devnull, 1)
        if options.stderr:
            stderr_fd = os.open(options.stderr, oflags)
            if stderr_fd != 2:
                os.dup2(stderr_fd, 2)
                os.close(stderr_fd)
        else:
            os.dup2(devnull, 2)
        # Change user & group ID.
        if options.chuid:
            user, group = set_process_owner(options.chuid)
            print "(%s) set user=%s group=%s" % (os.getpid(), user, group)
    else:
        # Become a process group leader only if not daemonizing.
        os.setpgrp()

    ## Fork off the thing that watches memory for this process group.
    controller_pid = os.getpid()
    if options.max_memory and not os.fork():
        env = environ()
        from spawning import memory_watcher
        basedir, cmdname = os.path.split(memory_watcher.__file__)
        if cmdname.endswith('.pyc'):
            cmdname = cmdname[:-1]

        os.chdir(basedir)
        command = [
            sys.executable,
            cmdname,
            '--max-age', str(options.max_age),
            str(controller_pid),
            str(options.max_memory)]
        os.execve(sys.executable, command, env)

    factory = options.factory

    # If you tell me to watch something, I'm going to reload then
    if options.watch:
        options.reload = True

    if options.status_port == options.port:
        options.status_port = None
        sys.stderr.write('**> Status port cannot be the same as the service port, disabling status.\n')


    factory_args = {
        'verbose': options.verbose,
        'host': options.host,
        'port': options.port,
        'num_processes': options.processes,
        'threadpool_workers': options.threads,
        'watch': options.watch,
        'reload': options.reload,
        'access_log_file': options.access_log_file,
        'pidfile': options.pidfile,
        'coverage': options.coverage,
        'sysinfo': options.sysinfo,
        'no_keepalive' : options.no_keepalive,
        'max_age' : options.max_age,
        'argv_str': " ".join(sys.argv[1:]),
        'args': positional_args,
        'status_port': options.status_port,
        'status_host': options.status_host or options.host,
	'ssl_private_key': options.ssl_private_key,
	'ssl_certificate': options.ssl_certificate
    }
    start_controller(sock, factory, factory_args)

_global_attr_name_ = '_spawning_controller_'
def installGlobal(controller):
    setattr(sys, _global_attr_name_, controller)

def globalController():
    return getattr(sys, _global_attr_name_, None)


if __name__ == '__main__':
    main()



