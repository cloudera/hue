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

from OpenSSL import crypto

import atexit
import os
import sys
import ssl
import multiprocessing
import tempfile

import gunicorn.app.base

from desktop import conf
from desktop import supervisor, metrics
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from gunicorn import util
from multiprocessing.util import _exit_function
from six import iteritems

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


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

def post_worker_init(worker):
  atexit.unregister(_exit_function)


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

  # Currently gunicorn does not support passphrase suppored SSL Keyfile
  # https://github.com/benoitc/gunicorn/issues/2410
  ssl_keyfile = None
  if conf.SSL_CERTIFICATE.get() and conf.SSL_PRIVATE_KEY.get():
    ssl_password = str.encode(conf.get_ssl_password()) if conf.get_ssl_password() is not None else None
    if ssl_password:
      with open(conf.SSL_PRIVATE_KEY.get(), 'r') as f:
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(
                                          conf.SSL_CERTIFICATE.get()), delete=False) as tf:
          tf.write(crypto.dump_privatekey(crypto.FILETYPE_PEM,
                                          crypto.load_privatekey(crypto.FILETYPE_PEM,
                                                                 f.read(), ssl_password)))
          ssl_keyfile = tf.name
    else:
      ssl_keyfile = conf.SSL_PRIVATE_KEY.get()

  options = {
      'accesslog': "-",
      'backlog': 2048,
      'bind': [bind_addr],
      'ca_certs': conf.SSL_CACERTS.get(),     # CA certificates file
      'capture_output': True,
      'cert_reqs': None,                      # Whether client certificate is required (see stdlib ssl module)
      'certfile': conf.SSL_CERTIFICATE.get(), # SSL certificate file
      'chdir': None,
      'check_config': None,
      'ciphers': conf.SSL_CIPHER_LIST.get(),  # Ciphers to use (see stdlib ssl module)
      'config': None,
      'daemon': None,
      'do_handshake_on_connect': False,       # Whether to perform SSL handshake on socket connect.
      'enable_stdio_inheritance': None,
      'errorlog': "-",
      'forwarded_allow_ips': None,
      'graceful_timeout': 900,                # Timeout for graceful workers restart.
      'group': conf.SERVER_GROUP.get(),
      'initgroups': None,
      'keepalive': 120,                       # seconds to wait for requests on a keep-alive connection.
      'keyfile': ssl_keyfile,                 # SSL key file
      'limit_request_field_size': None,
      'limit_request_fields': None,
      'limit_request_line': None,
      'logconfig': None,
      'loglevel': 'info',
      'max_requests': 1200,                   # The maximum number of requests a worker will process before restarting.
      'max_requests_jitter': 0,
      'paste': None,
      'pidfile': None,
      'preload_app': False,
      'proc_name': "hue",
      'proxy_allow_ips': None,
      'proxy_protocol': None,
      'pythonpath': None,
      'raw_env': None,
      'raw_paste_global_conf': None,
      'reload': None,
      'reload_engine': None,
      'sendfile': None,
      'spew': None,
      'ssl_version': ssl.PROTOCOL_TLSv1_2,    # SSL version to use
      'statsd_host': None,
      'statsd_prefix': None,
      'suppress_ragged_eofs': None,           # Suppress ragged EOFs (see stdlib ssl module)
      'syslog': None,
      'syslog_addr': None,
      'syslog_facility': None,
      'syslog_prefix': None,
      'threads': conf.CHERRYPY_SERVER_THREADS.get(),
      'timeout': 900,                         # Workers silent for more than this many seconds are killed and restarted.
      'umask': None,
      'user': conf.SERVER_USER.get(),
      'worker_class': conf.GUNICORN_WORKER_CLASS.get(),
      'worker_connections': 1000,
      'worker_tmp_dir': None,
      'workers': conf.GUNICORN_NUMBER_OF_WORKERS.get() if conf.GUNICORN_NUMBER_OF_WORKERS.get() is not None else number_of_workers(),
      'post_worker_init': post_worker_init
  }
  StandaloneApplication(handler_app, options).run()

if __name__ == '__main__':
  rungunicornserver()
