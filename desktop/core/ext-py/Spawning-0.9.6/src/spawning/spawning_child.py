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

"""spawning_child.py
"""

import eventlet
import eventlet.event
import eventlet.greenio
import eventlet.greenthread
import eventlet.hubs
import eventlet.wsgi

import errno
import optparse
import os
import signal
import socket
import sys
import time

import spawning.util
from spawning import setproctitle, reloader_dev

try:
    import simplejson as json
except ImportError:
    import json


class URLInterceptor(object):
    """
    Intercepts one or more paths.
    """

    paths = []

    def __init__(self, app, paths=[]):
        """
        Creates an instance.

        :Parameters:
           - `app`: Application to fall through to
        """
        self.app = app

    def _intercept(self, env, start_response):
        """
        Executes business logic.

        :Parameters:
           - `env`: environment information
           - `start_response`: wsgi response function
        """
        raise NotImplementedError('_intercept must be overridden')

    def __call__(self, env, start_response):
        """
        Dispatches input to the proper method.

        :Parameters:
           - `env`: environment information
           - `start_response`: wsgi response function
        """
        if env['PATH_INFO'] in self.paths:
            return self._intercept(env, start_response)
        return self.app(env, start_response)


class FigleafCoverage(URLInterceptor):

    paths = ['/_coverage']

    def __init__(self, app):
        URLInterceptor.__init__(self, app)
        import figleaf
        figleaf.start()

    def _intercept(self, env, start_response):
        import figleaf
        try:
            import cPickle as pickle
        except ImportError:
            import pickle

        coverage = figleaf.get_info()
        s = pickle.dumps(coverage)
        start_response("200 OK", [('Content-type', 'application/x-pickle')])
        return [s]


class SystemInfo(URLInterceptor):
    """
    Intercepts /_sysinfo path and returns json data.
    """

    paths = ['/_sysinfo']

    def _intercept(self, env, start_response):
        """
        Executes business logic.

        :Parameters:
           - `env`: environment information
           - `start_response`: wsgi response function
        """
        import spawning.util.system
        start_response("200 OK", [('Content-type', 'application/json')])
        return [json.dumps(spawning.util.system.System())]


class ExitChild(Exception):
    pass

class ChildStatus(object):
    def __init__(self, controller_port):
        self.controller_url =  "http://127.0.0.1:%s/" % controller_port
        self.server = None
        
    def send_status_to_controller(self):
        try:
            child_status = {'pid':os.getpid()}
            if self.server: 
                child_status['concurrent_requests'] = \
                    self.server.outstanding_requests
            else:
                child_status['error'] = 'Starting...'
            body = json.dumps(child_status)
            import urllib2
            urllib2.urlopen(self.controller_url, body)
        except (KeyboardInterrupt, SystemExit,
             eventlet.greenthread.greenlet.GreenletExit):
            raise
        except Exception, e:  
            # we really don't want exceptions here to stop read_pipe_and_die
            pass

_g_status = None
def init_statusobj(status_port):
    global _g_status
    if status_port:
        _g_status = ChildStatus(status_port)
def get_statusobj():
    return _g_status


def read_pipe_and_die(the_pipe, server_coro):
    dying = False
    try:
        while True:
            eventlet.hubs.trampoline(the_pipe, read=True)
            c = os.read(the_pipe, 1)
            # this is how the controller tells the child to send a status update
            if c == 's' and get_statusobj():
                get_statusobj().send_status_to_controller()
            elif not dying:
                dying = True  # only send ExitChild once
                eventlet.greenthread.kill(server_coro, ExitChild)
                # continue to listen for status pings while dying
    except socket.error:
        pass
    # if here, perhaps the controller's process went down; we should die too if
    # we aren't already
    if not dying:
        eventlet.greenthread.kill(server_coro, KeyboardInterrupt)

def tpool_wsgi(app):
    from eventlet import tpool
    def tpooled_application(e, s):
        result = tpool.execute(app, e, s)
        # return builtins directly
        if isinstance(result, (basestring, list, tuple)):
            return result
        else:
            # iterators might execute code when iterating over them,
            # so we wrap them in a Proxy object so every call to
            # next() goes through tpool
            return tpool.Proxy(result)
    return tpooled_application


def warn_controller_of_imminent_death(controller_pid):
    # The controller responds to a SIGUSR1 by kicking off a new child process.
    try:
        os.kill(controller_pid, signal.SIGUSR1)
    except OSError, e:
        if not e.errno == errno.ESRCH:
            raise


def serve_from_child(sock, config, controller_pid):
    threads = config.get('threadpool_workers', 0)
    wsgi_application = spawning.util.named(config['app_factory'])(config)

    if config.get('coverage'):
        wsgi_application = FigleafCoverage(wsgi_application)
    if config.get('sysinfo'):
        wsgi_application = SystemInfo(wsgi_application)

    if threads >= 1:
        # proxy calls of the application through tpool
        wsgi_application = tpool_wsgi(wsgi_application)
    elif threads != 1:
        from eventlet.green import socket

    host, port = sock.getsockname()

    access_log_file = config.get('access_log_file')
    if access_log_file is not None:
        access_log_file = open(access_log_file, 'a')

    max_age = 0
    if config.get('max_age'):
        max_age = int(config.get('max_age'))

    server_event = eventlet.event.Event()
    # the status object wants to have a reference to the server object
    if config.get('status_port'):
        def send_server_to_status(server_event):
            server = server_event.wait()
            get_statusobj().server = server
        eventlet.spawn(send_server_to_status, server_event)

    http_version = config.get('no_keepalive') and 'HTTP/1.0' or 'HTTP/1.1'
    try:
        wsgi_args = (sock, wsgi_application)
        wsgi_kwargs = {'log' : access_log_file, 'server_event' : server_event, 'max_http_version' : http_version}
        if config.get('no_keepalive'):
            wsgi_kwargs.update({'keepalive' : False})
        if max_age:
            wsgi_kwargs.update({'timeout_value' : True})
            eventlet.with_timeout(max_age, eventlet.wsgi.server, *wsgi_args,
                    **wsgi_kwargs)
            warn_controller_of_imminent_death(controller_pid)
        else:
            eventlet.wsgi.server(*wsgi_args, **wsgi_kwargs)
    except KeyboardInterrupt:
        # controller probably doesn't know that we got killed by a SIGINT
        warn_controller_of_imminent_death(controller_pid)
    except ExitChild:
        pass  # parent killed us, it already knows we're dying

    ## Once we get here, we should not accept any new sockets, so we should close the server socket.
    sock.close()
    
    server = server_event.wait()

    print "(%s) *** Child exiting" % (os.getpid(),)
    os.kill(os.getpid(), signal.SIGKILL)

def child_sighup(*args, **kwargs):
    exit(0)


def main():
    parser = optparse.OptionParser()
    parser.add_option("-r", "--reload",
        action='store_true', dest='reload',
        help='If --reload is passed, reload the server any time '
        'a loaded module changes.')
    parser.add_option('--ssl-certificate', dest='ssl_certificate', type='string', default='',
        help='Absolute path to SSL certificate file.')
    parser.add_option('--ssl-private-key', dest='ssl_private_key', type='string', default='',
        help='Absolute path to SSL private key.')

    options, args = parser.parse_args()

    if len(args) != 5:
        print "Usage: %s controller_pid httpd_fd death_fd factory_qual factory_args" % (
            sys.argv[0], )
        sys.exit(1)

    controller_pid, httpd_fd, death_fd, factory_qual, factory_args = args
    controller_pid = int(controller_pid)
    config = spawning.util.named(factory_qual)(json.loads(factory_args))

    setproctitle("spawn: child (%s)" % ", ".join(config.get("args")))
    
    ## Set up status reporter, if requested
    init_statusobj(config.get('status_port'))

    ## Set up the reloader
    if config.get('reload'):
        watch = config.get('watch', None)
        if watch:
            watching = ' and %s' % watch
        else:
            watching = ''
        print "(%s) reloader watching sys.modules%s" % (os.getpid(), watching)
        eventlet.spawn(
            reloader_dev.watch_forever, controller_pid, 1, watch)

    ## The parent will catch sigint and tell us to shut down
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    ## Expect a SIGHUP when we want the child to die
    signal.signal(signal.SIGHUP, child_sighup)
    eventlet.spawn(read_pipe_and_die, int(death_fd), eventlet.getcurrent())

    ## Make the socket object from the fd given to us by the controller
    sock = eventlet.greenio.GreenSocket(
        socket.fromfd(int(httpd_fd), socket.AF_INET, socket.SOCK_STREAM))

    if options.ssl_certificate and options.ssl_private_key:
        # The way spawning works is that there's a parent process which forks off long-lived
        # children, each of which can be multithreaded. What we're using is a single-threaded,
        # single-process server that does things asynchronously (using coroutines). Spawning creates
        # a socket and then calls fork() at least once. In the child process, it exec()'s something
        # else, so as a result the child loses all context. It puts the file descriptor for the
        # socket as a command-line argument to the child, which then uses the fromfd function of the
        # socket module to create a socket object. Unfortunately, the resulting object isn't quite
        # the same as the socket created by the parent. In particular, when we go to upgrade this
        # socket to ssl using eventlet's wrap_with_ssl(), it fails because it expects sock.fd to be
        # of type "socket._socketobject", but it's actually of type "_socket.socket". Patching
        # up the object in this way solves this problem.
        sock.fd = socket._socketobject(_sock=sock.fd)
        sock = eventlet.wrap_ssl(sock, certfile=options.ssl_certificate, keyfile=options.ssl_private_key, server_side=True)

    serve_from_child(sock, config, controller_pid)

if __name__ == '__main__':
    main()
