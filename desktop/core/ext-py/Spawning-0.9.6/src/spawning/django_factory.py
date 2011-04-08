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


import inspect
import os
import django.core.handlers.wsgi
from django.core.servers.basehttp import AdminMediaHandler

import spawning.util

def config_factory(args):
    args['django_settings_module'] = args.get('args', [None])[0]
    args['app_factory'] = 'spawning.django_factory.app_factory'

    ## TODO More directories
    ## INSTALLED_APPS (list of quals)
    ## ROOT_URL_CONF (qual)
    ## MIDDLEWARE_CLASSES (list of quals)
    ## TEMPLATE_CONTEXT_PROCESSORS (list of quals)
    settings_module = spawning.util.named(args['django_settings_module'])

    dirs = [os.path.split(
        inspect.getfile(
            inspect.getmodule(
                settings_module)))[0]]
    args['source_directories'] = dirs

    return args


def app_factory(config):
    os.environ['DJANGO_SETTINGS_MODULE'] = config['django_settings_module']

    app = django.core.handlers.wsgi.WSGIHandler()
    if config.get('dev'):
        app = AdminMediaHandler(app)
    return app

