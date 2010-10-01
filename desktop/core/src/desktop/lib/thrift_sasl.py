#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys

from cStringIO import StringIO
from thrift.transport import TTransport
from thrift.transport.TTransport import *
from thrift.protocol import TBinaryProtocol
import sasl
import struct

class TSaslClientTransport(TTransportBase):
  START = 1
  OK = 2
  BAD = 3
  ERROR = 4
  COMPLETE = 5

  def __init__(self, sasl_client, mechanism, trans):
    self._trans = trans
    self.sasl = sasl_client
    self.mechanism = mechanism
    self.__wbuf = StringIO()
    self.__rbuf = StringIO()

  def isOpen(self):
    return self._trans.isOpen()

  def open(self):
    if not self._trans.isOpen():
      self._trans.open()
    ret, chosen_mech, initial_response = self.sasl.start(self.mechanism)
    if not ret:
      raise TTransportException(type=TTransportException.NOT_OPEN,
        message=("Could not start SASL: %s" % self.sasl.getError()))

    # Send initial response
    self._send_message(self.START, chosen_mech)
    self._send_message(self.OK, initial_response)

    # SASL negotiation loop
    while True:
      status, payload = self._recv_sasl_message()
      if status not in (self.OK, self.COMPLETE):
        raise TTransportException(type=TTransportException.NOT_OPEN,
          message=("Bad status: %d (%s)" % (status, payload)))
      if status == self.COMPLETE:
        break
      ret, response = self.sasl.step(payload)
      if not ret:
        raise TTransportException(type=TTransportException.NOT_OPEN,
          message=("Bad SASL result: %s" % (self.sasl.getError())))
      self._send_message(self.OK, response)

  def _send_message(self, status, body):
    header = struct.pack(">BI", status, len(body))
    self._trans.write(header)
    self._trans.write(body)
    self._trans.flush()

  def _recv_sasl_message(self):
    header = self._trans.read(5)
    status, length = struct.unpack(">BI", header)
    if length > 0:
      payload = self._trans.read(length)
    else:
      payload = ""
    return status, payload

  def write(self, data):
    self.__wbuf.write(data)

  def flush(self):
    success, encoded = self.sasl.encode(self.__wbuf.getvalue())
    if not success:
      raise TTransportException(type=TTransportException.UNKNOWN,
                                message=self.sasl.getError())
    self._trans.write(struct.pack(">I", len(encoded)))
    self._trans.write(encoded)
    self._trans.flush()
    self.__wbuf = StringIO()

  def read(self, sz):
    ret = self.__rbuf.read(sz)
    if len(ret) != 0:
      return ret

    self._read_frame()
    return self.__rbuf.read(sz)

  def _read_frame(self):
    header = self._trans.readAll(4)
    (length,) = struct.unpack(">I", header)
    print "reading frame len: %d" % length
    self.__rbuf = StringIO(self._trans.readAll(length))


  def close(self):
    return self._trans.close()
