#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

import os
import sys

import multiprocessing

import gunicorn.app.base

from desktop import conf
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from django.utils.translation import ugettext as _

from gunicorn import util
from gunicorn.six import iteritems

GUNICORN_SERVER_HELP = r"""
  Run Hue using the Gunicorn WSGI server in asynchronous mode.
"""


class Command(BaseCommand):
  help = _("Gunicorn Web server for Hue.")

  def handle(self, *args, **options):
    rungunicornserver()

  def usage(self, subcommand):
    return GUNICORN_SERVER_HELP

def number_of_workers():
  return (multiprocessing.cpu_count() * 2) + 1


def handler_app(environ, start_response):
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desktop.settings")
  return get_wsgi_application()


class StandaloneApplication(gunicorn.app.base.BaseApplication):

  def __init__(self, app, options=None):
    self.options = options or {}
    self.app_uri = 'desktop.wsgi:application'
    super(StandaloneApplication, self).__init__()

  def load_config(self):
    config = dict([(key, value) for key, value in iteritems(self.options)
                    if key in self.cfg.settings and value is not None])
    for key, value in iteritems(config):
      self.cfg.set(key.lower(), value)

  def chdir(self):
    # chdir to the configured path before loading,
    # default is the current dir
    os.chdir(self.cfg.chdir)

    # add the path to sys.path
    sys.path.insert(0, self.cfg.chdir)

  def load_wsgiapp(self):
    self.chdir()

    # load the app
    return util.import_app(self.app_uri)

  def load(self):
    return self.load_wsgiapp()


def rungunicornserver():
  bind_addr = conf.HTTP_HOST.get() + ":" + str(conf.HTTP_PORT.get())

  options = {
      'access_log_format': None,
      'accesslog': '-',
      'backlog': None,
      'bind': [bind_addr],
      'ca_certs': None,
      'capture_output': None,
      'cert_reqs': None,
      'certfile': None,
      'chdir': None,
      'check_config': None,
      'ciphers': None,
      'config': None,
      'daemon': None,
      'do_handshake_on_connect': None,
      'enable_stdio_inheritance': None,
      'errorlog': '-',
      'forwarded_allow_ips': None,
      'graceful_timeout': None,
      'group': None,
      'initgroups': None,
      'keepalive': None,
      'keyfile': None,
      'limit_request_field_size': None,
      'limit_request_fields': None,
      'limit_request_line': None,
      'logconfig': None,
      'logger_class': None,
      'loglevel': 'debug',
      'max_requests': None,
      'max_requests_jitter': None,
      'paste': None,
      'pidfile': None,
      'preload_app': None,
      'proc_name': None,
      'proxy_allow_ips': None,
      'proxy_protocol': None,
      'pythonpath': None,
      'raw_env': None,
      'raw_paste_global_conf': None,
      'reload': None,
      'reload_engine': None,
      'sendfile': None,
      'spew': None,
      'ssl_version': None,
      'statsd_host': None,
      'statsd_prefix': None,
      'suppress_ragged_eofs': None,
      'syslog': None,
      'syslog_addr': None,
      'syslog_facility': None,
      'syslog_prefix': None,
      'threads': conf.CHERRYPY_SERVER_THREADS.get(),
      'timeout': None,
      'umask': None,
      'user': None,
      'worker_class': conf.GUNICORN_WORKER_CLASS.get(),
      'worker_connections': None,
      'worker_tmp_dir': None,
      'workers': conf.GUNICORN_NUMBER_OF_WORKERS.get() if conf.GUNICORN_NUMBER_OF_WORKERS.get() is not None else number_of_workers()
  }
  StandaloneApplication(handler_app, options).run()

if __name__ == '__main__':
    rungunicornserver()
