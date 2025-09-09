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
Gunicorn Log Listener Utilities

This module contains the integrated log listener functionality for handling
multiprocess logging in Gunicorn environments.
"""

import logging
import os
import pickle
import re
import select
import socket
import stat
import struct
import threading
from io import StringIO as string_io
from socketserver import StreamRequestHandler, ThreadingTCPServer

from desktop import conf

# Global variables for integrated log listener
LOG_LISTENER_THREAD = None
LOG_LISTENER_SERVER = None
LOG_LISTENER_SOCKET_PATH = None


class ConfigStreamHandler(StreamRequestHandler):
  """
  Handler for a streaming logging request.
  This basically logs the record using whatever logging policy is
  configured locally.
  """
  def handle(self):
    """
    Handle multiple requests - each expected to be a 4-byte length,
    followed by the LogRecord in pickle format. Logs the record
    according to whatever policy is configured locally.
    """
    while self.server.ready:
      try:
        chunk = self.connection.recv(4)
        if len(chunk) < 4:
          break
        slen = struct.unpack('>L', chunk)[0]
        chunk = self.connection.recv(slen)
        while len(chunk) < slen:
          chunk = chunk + self.connection.recv(slen - len(chunk))
        obj = pickle.loads(chunk)
        record = logging.makeLogRecord(obj)
        self.handleLogRecord(record)
      except Exception as e:
        logging.debug(f"Error handling log record: {e}")
        break

  def handleLogRecord(self, record):
    """Handle a single log record"""
    # if a name is specified, we use the named logger rather than the one
    # implied by the record.
    if self.server.logname is not None:
      name = self.server.logname
    else:
      name = record.name
    logger = logging.getLogger(name)
    logger.handle(record)


class ConfigSocketReceiver(ThreadingTCPServer):
  """
  A simple TCP socket-based logging config receiver.
  """
  request_queue_size = 1

  def __init__(self, server_address='hue.uds', handler=None,
         ready=None, verify=None):
    ThreadingTCPServer.__init__(self, server_address, handler)
    logging._acquireLock()
    self.abort = 0
    logging._releaseLock()
    self.timeout = 1
    self.ready = ready
    self.verify = verify
    self.logname = None
    self.server_address = server_address

  def server_bind(self):
    """Create and bind Unix Domain Socket"""
    self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    self.socket.bind(self.server_address)
    st = os.stat(self.server_address)
    os.chmod(self.server_address, st.st_mode | stat.S_IWOTH)

  def server_activate(self):
    """Activate the server"""
    self.socket.listen(self.request_queue_size)

  def serve_until_stopped(self):
    """Serve requests until stopped"""
    abort = 0
    while not abort:
      rd, wr, ex = select.select([self.socket.fileno()],
              [], [],
              self.timeout)
      if rd:
        self.handle_request()
      logging._acquireLock()
      abort = self.abort
      logging._releaseLock()
    self.server_close()


class LogListenerThread(threading.Thread):
  """
  Thread that runs the log listener server
  """
  def __init__(self, server_address, verify=None):
    super(LogListenerThread, self).__init__()
    self.server_address = server_address
    self.verify = verify
    self.ready = threading.Event()
    self.daemon = True  # Daemon thread will be killed when main process exits

  def run(self):
    """Run the log listener server"""
    global LOG_LISTENER_SERVER
    server = ConfigSocketReceiver(server_address=self.server_address,
                   handler=ConfigStreamHandler,
                   ready=self.ready, verify=self.verify)
    self.ready.set()
    logging._acquireLock()
    LOG_LISTENER_SERVER = server
    logging._releaseLock()
    server.serve_until_stopped()

  def stop(self):
    """Stop the log listener"""
    stop_log_listener()
    self.ready.clear()

  def stopped(self):
    """Check if the listener is stopped"""
    return not self.ready.is_set()


def stop_log_listener():
  """
  Stop the listening server which was created with start_log_listener().
  """
  global LOG_LISTENER_SERVER
  logging._acquireLock()
  try:
    if LOG_LISTENER_SERVER:
      LOG_LISTENER_SERVER.abort = 1
      LOG_LISTENER_SERVER = None
  finally:
    logging._releaseLock()


def start_log_listener(socket_path=None):
  """
  Start up a socket server on the specified unix domain socket, and listen for new
  configurations from gunicorn worker processes.
  """
  global LOG_LISTENER_THREAD, LOG_LISTENER_SOCKET_PATH

  if not socket_path:
    socket_dir = os.getenv("DESKTOP_LOG_DIR", "/var/log/hue")
    socket_name = conf.LOG_LISTENER_SOCKET_NAME.get()
    socket_path = os.path.join(socket_dir, socket_name)

  # Store socket path globally for signal handler access
  LOG_LISTENER_SOCKET_PATH = socket_path

  # Remove existing socket file if it exists
  try:
    os.unlink(socket_path)
  except OSError:
    if os.path.exists(socket_path):
      logging.warning(f"Could not remove existing socket file: {socket_path}")

  # Ensure the directory exists
  socket_dir = os.path.dirname(socket_path)
  if not os.path.exists(socket_dir):
    try:
      os.makedirs(socket_dir)
      logging.info(f"Created log directory: {socket_dir}")
    except OSError as e:
      logging.error(f"Failed to create log directory {socket_dir}: {e}")
      raise

  # Configure logging for the listener
  enable_log_listener_logging(socket_path)

  # Start the listener thread
  LOG_LISTENER_THREAD = LogListenerThread(server_address=socket_path, verify=None)
  LOG_LISTENER_THREAD.start()

  # Wait for the thread to be ready
  LOG_LISTENER_THREAD.ready.wait()

  logging.info(f"Log listener started on socket: {socket_path}")
  return LOG_LISTENER_THREAD


def enable_log_listener_logging(socket_path):
  """
  Configure logging for the log listener functionality
  """
  CONF_RE = re.compile('%LOG_DIR%')
  CONF_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       '..', '..', '..', 'conf', 'gunicorn_log.conf'))
  if os.path.exists(CONF_FILE):
    log_dir = os.getenv("DESKTOP_LOG_DIR", "/var/log/hue")
    raw = open(CONF_FILE).read()

    def _repl(match):
      if match.group(0) == '%LOG_DIR%':
        return log_dir
    sio = string_io(CONF_RE.sub(_repl, raw))
    logging.config.fileConfig(sio)

  root_logger = logging.getLogger()
  root_logger.info("Starting integrated Hue Log Listener using socket file %s" % socket_path)
  root_logger.info("Using logging.conf file %s" % CONF_FILE)
