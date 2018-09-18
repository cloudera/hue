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
import logging
import multiprocessing

import gunicorn.app.base

from desktop import conf
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application
from django.utils.translation import ugettext as _

from gunicorn import util
from gunicorn.six import iteritems

LOG = logging.getLogger(__name__)


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
  LOG.info("calling handler app ...")
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
      'ca_certs': conf.SSL_CACERTS.get(),     # CA certificates file
      'capture_output': None,
      'cert_reqs': None,                      # Whether client certificate is required (see stdlib ssl module)
      'certfile': conf.SSL_CERTIFICATE.get(), # SSL certificate file
      'chdir': None,
      'check_config': None,
      'ciphers': conf.SSL_CIPHER_LIST.get(),  # Ciphers to use (see stdlib ssl module)
      'config': None,
      'daemon': None,
      'do_handshake_on_connect': None,        # Whether to perform SSL handshake on socket connect (see stdlib ssl module)
      'enable_stdio_inheritance': None,
      'errorlog': '-',
      'forwarded_allow_ips': None,
      'graceful_timeout': None,
      'group': None,
      'initgroups': None,
      'keepalive': None,
      'keyfile': conf.SSL_PRIVATE_KEY.get(),  # SSL key file
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
      'preload_app': None, #True if conf.GUNICORN_WORKER_CLASS.get() == 'gevent' else None,
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
      'ssl_version': None,                    # SSL version to use (see stdlib ssl module) [ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_TLSv1]
      'statsd_host': None,
      'statsd_prefix': None,
      'suppress_ragged_eofs': None,           # Suppress ragged EOFs (see stdlib ssl module)
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
  if conf.GUNICORN_WORKER_CLASS.get():
    patch_thread_ident()
  LOG.info("Patching gevent monkey!!!")
  StandaloneApplication(handler_app, options).run()

DB_SHARED_THREAD = """\
DatabaseWrapper objects created in a thread can only \
be used in that same thread.  The object with alias '{0}' \
was created in thread id {1} and this is thread id {2}.\
"""

def patch_thread_ident():
  # monkey patch django.
  # This patch make sure that we use real threads to get the ident which
  # is going to happen if we are using gevent or eventlet.
  # -- patch taken from gunicorn
  if getattr(patch_thread_ident, 'called', False):
    return

  try:
    # django >= 1.8
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.utils import DatabaseError
    LOG.info("patch_thread_ident step 1 ...")
  except ImportError:
    try:
      # django < 1.8
      from django.db.backends import BaseDatabaseWrapper, DatabaseError
    except ImportError:
      return

  if 'validate_thread_sharing' in BaseDatabaseWrapper.__dict__:
    try:
      import thread
    except ImportError:
      return

    LOG.info("patch_thread_ident step 2 ...")

    _get_ident = thread.get_ident

    __old__init__ = BaseDatabaseWrapper.__init__

    def _init(self, *args, **kwargs):
      __old__init__(self, *args, **kwargs)
      self._thread_ident = _get_ident()

    def _validate_thread_sharing(self):
      if (not self.allow_thread_sharing and self._thread_ident != _get_ident()):
        raise DatabaseError(
                    DB_SHARED_THREAD % (
                        self.alias, self._thread_ident, _get_ident()),
                )

    LOG.info("patch_thread_ident step 3 ...")

    BaseDatabaseWrapper.__init__ = _init
    BaseDatabaseWrapper.validate_thread_sharing = _validate_thread_sharing
    LOG.info("patch_thread_ident step 4 ...")

  patch_thread_ident.called = True

if __name__ == '__main__':
    rungunicornserver()
