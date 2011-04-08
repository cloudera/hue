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

"""The config_factory takes a dictionary containing the command line arguments
and should return the same dictionary after modifying any of the settings it wishes.
At the very least the config_factory must set the 'app_factory' key in the returned
argument dictionary, which should be the dotted path to the function which will be
called to actually return the wsgi application which will be served.  Also, the
config_factory can look at the 'args' key for any additional positional command-line
arguments that were passed to spawn, and modify the configuration dictionary
based on it's contents.

Return value of config_factory should be a dict containing:
    app_factory: The dotted path to the wsgi application factory.
        Will be called with the result of factory_qual as the argument.
    host: The local ip to bind to.
    port: The local port to bind to.
    num_processes: The number of processes to spawn.
    num_threads: The number of threads to use in the threadpool in each process.
        If 0, install the eventlet monkeypatching and do not use the threadpool.
        Code which blocks instead of cooperating will block the process, possibly
        causing stalls. (TODO sigalrm?)
    dev: If True, watch all files in sys.modules, easy-install.pth, and any additional
        file paths in the 'watch' list for changes and restart child
        processes on change. If False, only reload if the svn revision of the
        current directory changes.
    watch: List of additional files to watch for changes and reload when changed.
"""
import inspect
import os
import time

import spawning.util

def config_factory(args):
    args['app_factory'] = 'spawning.wsgi_factory.app_factory'
    args['app'] = args['args'][0]
    args['middleware'] = args['args'][1:]

    args['source_directories'] = [os.path.split(
        inspect.getfile(
            inspect.getmodule(
                spawning.util.named(args['app']))))[0]]
    return args


def app_factory(config):
    app = spawning.util.named(config['app'])
    for mid in config['middleware']:
        app = spawning.util.named(mid)(app)
    return app


def hello_world(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Hello, World!\r\n']


def really_long(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    time.sleep(180)
    return ['Goodbye, World!\r\n']

