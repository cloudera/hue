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

import logging
import logging.config
import os
import os.path
import re
import sys

from cStringIO import StringIO
from logging import FileHandler
from logging.handlers import RotatingFileHandler

from desktop.lib.paths import get_desktop_root
from desktop.log import formatter
from desktop.log.formatter import MessageOnlyFormatter


DEFAULT_LOG_DIR = 'logs'
LOG_FORMAT = '[%(asctime)s] %(module)-12s %(levelname)-8s %(message)s'
DATE_FORMAT = '%d/%b/%Y %H:%M:%S %z'
FORCE_DEBUG = False
CONF_RE = re.compile('%LOG_DIR%|%PROC_NAME%')

_log_dir = None


def _read_log_conf(proc_name, log_dir):
  """
  _read_log_conf(proc_name, log_dir) -> StringIO or None

  This method also replaces the %LOG_DIR% and %PROC_NAME% occurrences.
  """
  def _repl(match):
    if match.group(0) == '%LOG_DIR%':
      return log_dir
    elif match.group(0) == '%PROC_NAME%':
      return proc_name

  log_conf = get_desktop_root('conf', 'log.conf')

  if not os.path.isfile(log_conf):
    return None

  try:
    raw = file(log_conf).read()
    sio = StringIO(CONF_RE.sub(_repl, raw))
    return sio
  except IOError, ex:
    print >> sys.stderr, "ERROR: Failed to open %s: %s" % (log_conf, ex)
    return None


def _find_console_stream_handler(logger):
  """Find a StreamHandler that is attached to the logger that prints to the console."""
  for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler) and handler.stream in (sys.stderr, sys.stdout):
      return logger
  return None


class AuditHandler(RotatingFileHandler):
  pass


def get_audit_logger():
  from desktop.conf import AUDIT_EVENT_LOG_DIR, AUDIT_LOG_MAX_FILE_SIZE

  audit_logger = logging.getLogger('audit')
  if not filter(lambda hclass: isinstance(hclass, AuditHandler), audit_logger.handlers): # Don't add handler twice
    size, unit = int(AUDIT_LOG_MAX_FILE_SIZE.get()[:-2]), AUDIT_LOG_MAX_FILE_SIZE.get()[-2:]
    maxBytes = size * 1024 ** (1 if unit == 'KB' else 2 if unit == 'MB' else 3)

    audit_handler = AuditHandler(AUDIT_EVENT_LOG_DIR.get(), maxBytes=maxBytes, backupCount=50)
    audit_handler.setFormatter(MessageOnlyFormatter())
    audit_logger.addHandler(audit_handler)

  return audit_logger


def chown_log_dir(uid, gid):
  """
  chown all files in the log dir to this user and group.
  Should only be called after logic has been setup.
  Return success
  """
  if _log_dir is None:
    return False

  try:
    os.chown(_log_dir, uid, gid)
    for entry in os.listdir(_log_dir):
      os.chown(os.path.join(_log_dir, entry), uid, gid)
    return True
  except OSError, ex:
    print >> sys.stderr, 'Failed to chown log directory %s: ex' % (_log_dir, ex)
    return False


def basic_logging(proc_name, log_dir=None):
  """
  Configure logging for the program ``proc_name``:
    - Apply log.conf in the config directory.
    - If DESKTOP_LOGLEVEL environment variable is specified, the root console
      handler (stdout/stderr) is set to that level. If there is no console handler,
      a new one is created.
    - Defining the environment variable DESKTOP_DEBUG is the same as setting
      DESKTOP_LOGLEVEL=DEBUG.

  The ``log_dir`` will replace the %LOG_DIR% in log.conf. If not specified, we look
  for the DESTKOP_LOG_DIR environment variable, and then default to the DEFAULT_LOG_DIR.

  This removes all previously installed logging handlers.
  """
  global FORCE_DEBUG

  # Setup log_dir
  if not log_dir:
    log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  if not os.path.exists(log_dir):
    try:
      os.makedirs(log_dir)
    except OSError, err:
      print >> sys.stderr, 'Failed to create log directory "%s": %s' % (log_dir, err)
      raise err

  # Remember where our log directory is
  global _log_dir
  _log_dir = log_dir

  log_conf = _read_log_conf(proc_name, log_dir)

  if log_conf is not None:
    logging.config.fileConfig(log_conf)
    root_logger = logging.getLogger()
  else:
    # Get rid of any preinstalled/default handlers
    root_logger = logging.getLogger()
    for h in root_logger.handlers:
      root_logger.removeHandler(h)

  # always keep DEBUG at the root, since we'll filter in the
  # handlers themselves - this allows the /logs endpoint
  # to always have all logs.
  root_logger.setLevel(logging.DEBUG)

  # Handle env variables
  env_loglevel = os.getenv("DESKTOP_LOGLEVEL")
  env_debug = os.getenv('DESKTOP_DEBUG') or FORCE_DEBUG
  if env_debug:
    env_loglevel = 'DEBUG'

  if env_loglevel:
    try:
      lvl = getattr(logging, env_loglevel.upper())
    except AttributeError:
      raise Exception("Invalid log level in DESKTOP_LOGLEVEL: %s" % (env_loglevel,))

    # Set the StreamHandler to the level (create one if necessary)
    handler = _find_console_stream_handler(root_logger)
    if not handler:
      handler = logging.StreamHandler()
      handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
      root_logger.addHandler(handler)
    handler.setLevel(lvl)

    # Set all loggers but error.log to the same logging level
    error_handler = logging.getLogger('handler_errorlog')
    for h in root_logger.handlers:
      if isinstance(h, (FileHandler, RotatingFileHandler)) and h != error_handler:
        h.setLevel(lvl)


def fancy_logging():
  """Configure logging into a buffer for /logs endpoint."""
  from log_buffer import FixedBufferHandler

  BUFFER_SIZE = 1500 * 200 # This is the size in characters, not bytes. Targets about 1500 rows.
  buffer_handler = FixedBufferHandler(BUFFER_SIZE)
  _formatter = formatter.Formatter(LOG_FORMAT, DATE_FORMAT)

  # We always want to catch all messages in our error report buffer
  buffer_handler.setLevel(logging.DEBUG)
  buffer_handler.setFormatter(_formatter)
  root_logger = logging.getLogger()
  root_logger.addHandler(buffer_handler)


def get_all_debug():
  global FORCE_DEBUG

  return FORCE_DEBUG


def set_all_debug():
  from desktop.settings import ENV_HUE_PROCESS_NAME # Circular dependency
  global FORCE_DEBUG

  FORCE_DEBUG = True
  basic_logging(os.environ[ENV_HUE_PROCESS_NAME])
  fancy_logging()


def reset_all_debug():
  from desktop.settings import ENV_HUE_PROCESS_NAME # Circular dependency
  global FORCE_DEBUG

  FORCE_DEBUG = False
  basic_logging(os.environ[ENV_HUE_PROCESS_NAME])
  fancy_logging()
