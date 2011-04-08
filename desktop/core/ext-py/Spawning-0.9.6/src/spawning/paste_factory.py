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

import os
import sys

from paste.deploy import loadwsgi

from spawning import spawning_controller


def config_factory(args):
    if 'config_url' in args:
        config_url = args['config_url']
        relative_to = args['relative_to']
        global_conf = args['global_conf']
    else:
        config_file = os.path.abspath(args['args'][0])
        config_url = 'config:%s' % (os.path.basename(config_file), )
        relative_to = os.path.dirname(config_file)
        global_conf = {}
        for arg in args['args'][1:]:
            key, value = arg.split('=')
            global_conf[key] = value

    ctx = loadwsgi.loadcontext(
        loadwsgi.SERVER,
        config_url,
        relative_to=relative_to,
        global_conf=global_conf)

    watch = args.get('watch', None)
    if watch is None:
        watch = []
    if ctx.global_conf['__file__'] not in watch:
        watch.append(ctx.global_conf['__file__'])
    args['watch'] = watch

    args['app_factory'] = 'spawning.paste_factory.app_factory'
    args['config_url'] = config_url
    args['relative_to'] = relative_to
    args['source_directories'] = [relative_to]
    args['global_conf'] = ctx.global_conf

    debug = ctx.global_conf.get('debug', None)
    if debug is not None:
        args['dev'] = (debug == 'true')
    host = ctx.local_conf.get('host', None)
    if host is not None:
        args['host'] = host
    port = ctx.local_conf.get('port', None)
    if port is not None:
        args['port'] = int(port)
    num_processes = ctx.local_conf.get('num_processes', None)
    if num_processes is not None:
        args['num_processes'] = int(num_processes)
    threadpool_workers = ctx.local_conf.get('threadpool_workers', None)
    if threadpool_workers is not None:
        args['threadpool_workers'] = int(threadpool_workers)

    return args


def app_factory(config):
    return loadwsgi.loadapp(
        config['config_url'],
        relative_to=config['relative_to'],
        global_conf=config['global_conf'])


def server_factory(global_conf, host, port, *args, **kw):
    config_url = 'config:' + os.path.split(global_conf['__file__'])[1]
    relative_to = global_conf['here']

    def run(app):
        args = spawning_controller.DEFAULTS.copy()
        args.update(
            {'config_url': config_url, 'relative_to': relative_to, 'global_conf': global_conf})

        spawning_controller.run_controller(
            'spawning.paste_factory.config_factory', args)

    return run
