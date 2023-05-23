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
import atexit
import desktop.log
import gunicorn.app.base
import logging
import logging.config
import os
import pkg_resources
import ssl
import sys
import tempfile

from OpenSSL import crypto
from multiprocessing.util import _exit_function
from desktop import conf
from desktop.lib.paths import get_desktop_root
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from django.utils.translation import gettext as _
from django.db import connection
from gunicorn import util
from six import iteritems

GUNICORN_SERVER_HELP = r"""
  Run Hue using the Gunicorn WSGI server in asynchronous mode.
"""

PID_FILE = None

class Command(BaseCommand):
  help = _("Gunicorn Web server for Hue.")

  def add_arguments(self, parser):
    parser.add_argument('--bind', help=_("Bind Address"), action='store', default=None)

  def handle(self, *args, **options):
    start_server(args, options)

  def usage(self, subcommand):
    return GUNICORN_SERVER_HELP

def activate_translation():
  from django.conf import settings
  from django.utils import translation

  # Activate the current language, because it won't get activated later.
  try:
    translation.activate(settings.LANGUAGE_CODE)
  except AttributeError:
    pass

def number_of_workers():
  return (multiprocessing.cpu_count() * 2) + 1

def handler_app(environ, start_response):
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desktop.settings")
  return get_wsgi_application()

def post_fork(server, worker):
  global PID_FILE
  with open(PID_FILE, "a") as f:
    f.write("%s\n"%worker.pid)

def post_worker_init(worker):
  connection.connect()

def worker_int(worker):
  connection.close()

def enable_logging(args, options):
  HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
  # Start basic logging as soon as possible.
  if "HUE_PROCESS_NAME" not in os.environ:
    _proc = os.path.basename(len(sys.argv) > 1 and sys.argv[1] or sys.argv[0])
    os.environ["HUE_PROCESS_NAME"] = _proc

  desktop.log.basic_logging(os.environ["HUE_PROCESS_NAME"])
  logging.info("Welcome to Hue from Gunicorn server " + HUE_DESKTOP_VERSION)

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

def argprocessing(args=[], options={}):
  global PID_FILE
  if options['bind']:
    http_port = "8888"
    bind_addr = options['bind']
    if ":" in bind_addr:
      http_port = bind_addr.split(":")[1]
    PID_FILE = "/tmp/hue_%s.pid" % (http_port)
  else:
    bind_addr = conf.HTTP_HOST.get() + ":" + str(conf.HTTP_PORT.get())
    PID_FILE = "/tmp/hue_%s.pid" % (conf.HTTP_PORT.get())
  options['bind_addr'] = bind_addr

  # Currently gunicorn does not support passphrase suppored SSL Keyfile
  # https://github.com/benoitc/gunicorn/issues/2410
  ssl_keyfile = None
  worker_tmp_dir = os.environ.get("HUE_CONF_DIR", get_desktop_root("conf"))
  if not worker_tmp_dir:
    worker_tmp_dir = "/tmp"
  options['worker_tmp_dir'] = worker_tmp_dir
  if conf.SSL_CERTIFICATE.get() and conf.SSL_PRIVATE_KEY.get():
    ssl_password = str.encode(conf.get_ssl_password()) if conf.get_ssl_password() is not None else None
    if ssl_password:
      with open(conf.SSL_PRIVATE_KEY.get(), 'r') as f:
        with tempfile.NamedTemporaryFile(dir=worker_tmp_dir, delete=False) as tf:
          tf.write(crypto.dump_privatekey(crypto.FILETYPE_PEM,
                                          crypto.load_privatekey(crypto.FILETYPE_PEM,
                                                                 f.read(), ssl_password)))
          ssl_keyfile = tf.name
    else:
      ssl_keyfile = conf.SSL_PRIVATE_KEY.get()
  options['ssl_keyfile'] = ssl_keyfile

def rungunicornserver(args=[], options={}):
  gunicorn_options = {
      'accesslog': "-",
      'backlog': 2048,
      'bind': [options['bind_addr']],
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
      'keyfile': options['ssl_keyfile'],      # SSL key file
      'limit_request_field_size': conf.LIMIT_REQUEST_FIELD_SIZE.get(),
      'limit_request_fields': conf.LIMIT_REQUEST_FIELDS.get(),
      'limit_request_line': conf.LIMIT_REQUEST_LINE.get(),
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
      'sendfile': True,
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
      'worker_tmp_dir': options['worker_tmp_dir'],
      'workers': conf.GUNICORN_NUMBER_OF_WORKERS.get() if conf.GUNICORN_NUMBER_OF_WORKERS.get() is not None else 5,
      'post_fork': post_fork,
      'post_worker_init': post_worker_init,
      'worker_int': worker_int
  }
  StandaloneApplication(handler_app, gunicorn_options).run()

def start_server(args, options):
  global PID_FILE
  argprocessing(args, options)

  # Hide the Server software version in the response body
  gunicorn.SERVER_SOFTWARE = "apache"
  os.environ["SERVER_SOFTWARE"] = gunicorn.SERVER_SOFTWARE

  # Activate django translation
  activate_translation()
  enable_logging(args, options)
  atexit.unregister(_exit_function)
  with open(PID_FILE, "a") as f:
    f.write("%s\n"%os.getpid())
  rungunicornserver(args, options)

if __name__ == '__main__':
  start_server(args=sys.argv[1:], options={})
