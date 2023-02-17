#!/usr/bin/env python3.8
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
import argparse
import logging
import logging.config
import os
import pickle
import re
import select
import signal
import socket
import stat
import struct
import sys
import threading

from io import StringIO as string_io
from socketserver import ThreadingTCPServer, StreamRequestHandler
#
#   The following code implements a socket listener for on-the-fly
#   reconfiguration of logging.
#
#   _listener holds the server object doing the listening
_udslistener = None
def udslisten(server_address='/tmp/hue.uds', verify=None):
  """
  Start up a socket server on the specified unix domain socket, and listen for new
  configurations.
  """
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
      while True:
        chunk = self.connection.recv(4)
        if len(chunk) < 4:
          break
        slen = struct.unpack('>L', chunk)[0]
        chunk = self.connection.recv(slen)
        while len(chunk) < slen:
          chunk = chunk + self.connection.recv(slen - len(chunk))
        obj = self.unPickle(chunk)
        record = logging.makeLogRecord(obj)
        self.handleLogRecord(record)

    def unPickle(self, data):
      return pickle.loads(data)

    def handleLogRecord(self, record):
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

    def __init__(self, server_address='/tmp/hue.uds', handler=None,
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
      # Create a UDS socket
      self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      self.socket.bind(self.server_address)
      st = os.stat(self.server_address)
      os.chmod(self.server_address, st.st_mode | stat.S_IWOTH)

    def server_activate(self):
      self.socket.listen(self.request_queue_size)

    def serve_until_stopped(self):
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

  class Server(threading.Thread):
    def __init__(self, rcvr, hdlr, server_address, verify):
      super(Server, self).__init__()
      self.rcvr = rcvr
      self.hdlr = hdlr
      self.server_address = server_address
      self.verify = verify
      self.ready = threading.Event()

    def run(self):
      server = self.rcvr(server_address='/tmp/hue.uds', handler=self.hdlr,
                         ready=self.ready, verify=self.verify)
      self.ready.set()
      global _udslistener
      logging._acquireLock()
      _udslistener = server
      logging._releaseLock()
      server.serve_until_stopped()

  return Server(ConfigSocketReceiver, ConfigStreamHandler, server_address, verify)

def udsstopListening():
  """
  Stop the listening server which was created with a call to listen().
  """
  global _udslistener
  logging._acquireLock()
  try:
    if _udslistener:
      _udslistener.abort = 1
      _udslistener = None
  finally:
    logging._releaseLock()

def argprocessing(args=[], options={}):
  parser = argparse.ArgumentParser(prog='runloglistener', description='What this program does', epilog='Text at the bottom of help')
  parser.add_argument('-s', '--socket', dest='socket', action='store', default='/tmp/hue.uds')

  opts = parser.parse_args()
  if opts.socket:
    options['socket'] = opts.socket

def enable_logging(args, options):
  CONF_RE = re.compile('%LOG_DIR%')
  CONF_FILE = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                           '..', '..', 'conf', 'gunicorn_log.conf'))
  if os.path.exists(CONF_FILE):
    log_dir = os.getenv("DESKTOP_LOG_DIR", "/var/log/hue")
    raw = open(CONF_FILE).read()
    def _repl(match):
      if match.group(0) == '%LOG_DIR%':
        return log_dir
    sio = string_io(CONF_RE.sub(_repl, raw))
    logging.config.fileConfig(sio)
  root_logger = logging.getLogger()
  root_logger.info("Welcome to Hue from Listener server ")

class LogException(Exception):
  def __init__(self, e):
    super(LogException, self).__init__(e)
    self.message = e.status.message

  def __str__(self):
    return self.message

rt = None
def signal_handler(sig, frame):
  print("Received %s" % sig)
  global rt
  udsstopListening()
  rt.join()

def start_listener(args, options):
  global rt
  try:
    os.unlink(options["socket"])
  except OSError:
    if os.path.exists(options["socket"]):
      raise
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGHUP, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGQUIT, signal_handler)
  enable_logging(args, options)
  rt = udslisten(options["socket"], verify=False)
  rt.start()

if __name__ == '__main__':
  args = sys.argv[1:]
  options = {}
  argprocessing(args=args, options=options)
  start_listener(args, options)
