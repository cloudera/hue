#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Gunicorn Server Utilities

This module contains utilities for configuring and running the Gunicorn server
with proper SSL, worker management, and process handling.
"""

import logging
import multiprocessing
import os
import ssl
import sys
import tempfile
import time

import gunicorn.app.base
import pkg_resources
import psutil
import redis
from django.core.wsgi import get_wsgi_application
from django.db import connection
from gunicorn import util
from OpenSSL import crypto
from six import iteritems

import desktop.log
from desktop import conf
from desktop.lib.ip_utils import fetch_ipv6_bind_address
from desktop.lib.paths import get_desktop_root
from desktop.lib.tls_utils import get_tls_settings
from filebrowser.utils import parse_broker_url


def activate_translation():
  """Activate Django translation"""
  from django.conf import settings
  from django.utils import translation

  # Activate the current language, because it won't get activated later.
  try:
    translation.activate(settings.LANGUAGE_CODE)
  except AttributeError:
    pass


def number_of_workers():
  """Calculate the number of workers for Gunicorn"""
  return (multiprocessing.cpu_count() * 2) + 1


def handler_app(environ, start_response):
  """WSGI application handler"""
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desktop.settings")
  return get_wsgi_application()


def post_fork(server, worker):
  """Post-fork worker initialization"""
  global PID_FILE
  with open(PID_FILE, "a") as f:
    f.write("%s\n" % worker.pid)


def post_worker_init(worker):
  """Initialize worker after fork"""
  connection.connect()


def worker_int(worker):
  """Worker interrupt handler"""
  connection.close()


def enable_logging(args, options):
  """Enable basic logging for the process"""
  HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
  # Start basic logging as soon as possible.
  if "HUE_PROCESS_NAME" not in os.environ:
    _proc = os.path.basename(len(sys.argv) > 1 and sys.argv[1] or sys.argv[0])
    os.environ["HUE_PROCESS_NAME"] = _proc

  desktop.log.basic_logging(os.environ["HUE_PROCESS_NAME"])
  logging.info("Welcome to Hue from Gunicorn server " + HUE_DESKTOP_VERSION)


def initialize_free_disk_space_in_redis():
  """Initialize free disk space tracking in Redis"""
  conn_success = False
  for retries in range(5):
    try:
      redis_client = parse_broker_url(desktop.conf.TASK_SERVER_V2.BROKER_URL.get())
      free_space = psutil.disk_usage('/tmp').free
      available_space = redis_client.get('upload_available_space')
      if available_space is None:
        available_space = free_space
      else:
        available_space = int(available_space)
      upload_keys_exist = any(redis_client.scan_iter('upload__*'))
      redis_client.delete('upload_available_space')
      if not upload_keys_exist:
        redis_client.setnx('upload_available_space', free_space)
      else:
        redis_client.setnx('upload_available_space', min(free_space, available_space))
      logging.info("Successfully initialized free disk space in Redis.")
      conn_success = True
      break
    except redis.ConnectionError as e:
      logging.error(f"Redis connection error: {e}")
      time.sleep(10)
    except Exception as e:
      logging.error(f"Error while initializing free disk space in Redis: {e}")
      time.sleep(10)
  if not conn_success:
    logging.error("Failed to initialize free disk space in Redis after 5 retries.")


class StandaloneApplication(gunicorn.app.base.BaseApplication):
  """Standalone Gunicorn application"""

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


def process_arguments(args=[], options={}):
  """Process command line arguments and options"""
  global PID_FILE

  ipv6_enabled = conf.ENABLE_IPV6.get()  # This is already a bool

  if options.get('bind'):
    http_port = "8888"
    bind_addr = options['bind']
    if ":" in bind_addr:
      http_port = bind_addr.split(":")[-1]  # Use last part in case of IPv6
    PID_FILE = f"/tmp/hue_{http_port}.pid"
  else:
    http_host = conf.HTTP_HOST.get()
    http_port = str(conf.HTTP_PORT.get())

    if ipv6_enabled:
      bind_addr = fetch_ipv6_bind_address(http_host, http_port)
    else:
      bind_addr = f"{http_host}:{http_port}"
      logging.info(f"IPv6 disabled, using standard format: {bind_addr}")

    PID_FILE = f"/tmp/hue_{http_port}.pid"

  options['bind_addr'] = bind_addr
  options['pid_file'] = PID_FILE  # Store PID file in options for return

  # Currently gunicorn does not support passphrase suppored SSL Keyfile
  # https://github.com/benoitc/gunicorn/issues/2410
  ssl_keyfile = None

  # HUE_RUN_DIR is set for env variable. If unset, fall back to previous behaviour (for base).
  worker_tmp_dir = os.environ.get("HUE_RUN_DIR")
  if not worker_tmp_dir:
    worker_tmp_dir = os.environ.get("HUE_CONF_DIR", get_desktop_root("conf"))
    if not worker_tmp_dir:
      worker_tmp_dir = "/tmp"
  options['worker_tmp_dir'] = worker_tmp_dir

  # Gunicorn needs chown privileges if the OS user/group does not match Gunicorn's user/group.
  # This can happen when the OS user is not in our control to set (OpenShift).
  if not os.environ.get("GUNICORN_USE_OS_USER"):
    options['user'] = conf.SERVER_USER.get()
    options['group'] = conf.SERVER_GROUP.get()

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

  return options


def create_gunicorn_options(options):
  """Create Gunicorn configuration options"""
  # Get TLS configuration
  tls_settings = get_tls_settings()

  def gunicorn_ssl_context(conf, default_ssl_context_factory):
    """
    Create and configure SSL context for Gunicorn based on TLS settings.
    """
    context = default_ssl_context_factory()

    try:
      # Validate TLS settings before applying
      if "error" in tls_settings:
        logging.warning(f"TLS configuration error: {tls_settings['error']}")
        return context

      # Configure maximum TLS version
      max_version = tls_settings.get("tls_maximum_version")
      if max_version == "TLSv1.3":
        if hasattr(ssl, "HAS_TLSv1_3") and ssl.HAS_TLSv1_3 and hasattr(ssl, "TLSVersion"):
          context.maximum_version = ssl.TLSVersion.TLSv1_3
          logging.info("Set maximum TLS version to TLSv1.3")
        else:
          logging.warning("TLS 1.3 requested but not supported by system, falling back to TLS 1.2")
          if hasattr(ssl, "TLSVersion"):
            context.maximum_version = ssl.TLSVersion.TLSv1_2
      elif max_version == "TLSv1.2":
        if hasattr(ssl, "TLSVersion"):
          context.maximum_version = ssl.TLSVersion.TLSv1_2
          logging.info("Set maximum TLS version to TLSv1.2")

      # Configure minimum TLS version
      min_version = tls_settings.get("tls_minimum_version")
      if min_version == "TLSv1.3":
        if hasattr(ssl, "HAS_TLSv1_3") and ssl.HAS_TLSv1_3 and hasattr(ssl, "TLSVersion"):
          context.minimum_version = ssl.TLSVersion.TLSv1_3
          logging.info("Set minimum TLS version to TLSv1.3")
        else:
          logging.warning("TLS 1.3 minimum requested but not supported, falling back to TLS 1.2")
          if hasattr(ssl, "TLSVersion"):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
      elif min_version == "TLSv1.2":
        if hasattr(ssl, "TLSVersion"):
          context.minimum_version = ssl.TLSVersion.TLSv1_2
          logging.info("Set minimum TLS version to TLSv1.2")

      # Configure ciphers (only for TLS 1.2)
      ciphers = tls_settings.get("ciphers", "")
      if ciphers and ciphers.strip():  # Only set if ciphers is not empty
        try:
          context.set_ciphers(ciphers)
          logging.info(f"Successfully configured ciphers: {ciphers}")
        except ssl.SSLError as e:
          logging.error(f"Invalid cipher configuration '{ciphers}': {e}")
        except Exception as e:
          logging.error(f"Unexpected error setting ciphers '{ciphers}': {e}")
      elif max_version == "TLSv1.3":
        logging.info("TLS 1.3 enabled - cipher configuration handled automatically")
      else:
        logging.info("No custom ciphers configured, using system defaults")

    except Exception as e:
      logging.error(f"Error configuring SSL context: {e}")
      logging.info("Using default SSL context configuration")

    return context

  gunicorn_options = {
    'accesslog': "-",
    'access_log_format': "%({x-forwarded-for}i)s %(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s'",
    'backlog': 2048,
    'bind': [options['bind_addr']],
    'ca_certs': conf.SSL_CACERTS.get(),   # CA certificates file
    'capture_output': True,
    'cert_reqs': None,           # Whether client certificate is required (see stdlib ssl module)
    'certfile': conf.SSL_CERTIFICATE.get(),  # SSL certificate file
    'chdir': None,
    'check_config': None,
    'config': None,
    'daemon': None,
    'do_handshake_on_connect': False,    # Whether to perform SSL handshake on socket connect.
    'enable_stdio_inheritance': None,
    'errorlog': "-",
    'forwarded_allow_ips': None,
    'graceful_timeout': conf.GUNICORN_WORKER_GRACEFUL_TIMEOUT.get(),
    'group': options.get('group'),
    'initgroups': None,
    'keepalive': 120,            # seconds to wait for requests on a keep-alive connection.
    'keyfile': options['ssl_keyfile'],   # SSL key file
    'limit_request_field_size': conf.LIMIT_REQUEST_FIELD_SIZE.get(),
    'limit_request_fields': conf.LIMIT_REQUEST_FIELDS.get(),
    'limit_request_line': conf.LIMIT_REQUEST_LINE.get(),
    'loglevel': 'DEBUG' if conf.DJANGO_DEBUG_MODE.get() else 'INFO',
    'max_requests': 1200,          # The maximum number of requests a worker will process before restarting.
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
    'ssl_context': gunicorn_ssl_context,
    'statsd_host': None,
    'statsd_prefix': None,
    'suppress_ragged_eofs': None,      # Suppress ragged EOFs (see stdlib ssl module)
    'syslog': None,
    'syslog_addr': None,
    'syslog_facility': None,
    'syslog_prefix': None,
    'threads': conf.CHERRYPY_SERVER_THREADS.get(),
    'timeout': conf.GUNICORN_WORKER_TIMEOUT.get(),
    'umask': None,
    'user': options.get('user'),
    'worker_class': conf.GUNICORN_WORKER_CLASS.get(),
    'worker_connections': 1000,
    'worker_tmp_dir': options['worker_tmp_dir'],
    'workers': conf.GUNICORN_NUMBER_OF_WORKERS.get() if conf.GUNICORN_NUMBER_OF_WORKERS.get() is not None else 5,
    'post_fork': post_fork,
    'post_worker_init': post_worker_init,
    'worker_int': worker_int
  }

  return gunicorn_options


def run_gunicorn_server(args=[], options={}):
  """Run the Gunicorn server with the given options"""
  gunicorn_options = create_gunicorn_options(options)
  StandaloneApplication(handler_app, gunicorn_options).run()


# Global variable for PID file (used by post_fork)
PID_FILE = None
