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
#

from future import standard_library
standard_library.install_aliases()
import logging
import sys

from thrift.transport.TTransport import *

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

if sys.version_info[0] > 2:
  from io import BytesIO as buffer_writer
else:
  from cStringIO import StringIO as buffer_writer

LOG = logging.getLogger()


class THttpClient(TTransportBase):
  """
  HTTP transport mode for Thrift.

  HTTPS and Kerberos support with Request.

  e.g.
  mode = THttpClient('http://hbase-thrift-v1.com:9090')
  mode = THttpClient('http://hive-localhost:10001/cliservice')
  """

  def __init__(self, base_url):
    self._base_url = base_url
    self._client = HttpClient(self._base_url, logger=LOG)
    self._data = None
    self._headers = None
    self._wbuf = buffer_writer()

  def open(self):
    pass

  def set_kerberos_auth(self, service="HTTP"):
    self._client.set_kerberos_auth(service=service)

  def set_basic_auth(self, username, password):
    self._client.set_basic_auth(username, password)

  def set_bearer_auth(self, token):
    self._client.set_bearer_auth(token)

  def set_verify(self, verify=True):
    self._client.set_verify(verify)

  def close(self):
    self._headers = None
    # Close session too?

  def isOpen(self):
    return self._client is not None

  def setTimeout(self, ms):
    if not self._headers:
      self._headers = {}
    self._headers.update(timeout=str(int(ms / 1000)))

  def setCustomHeaders(self, headers):
    if self._headers:
      self._headers.update(headers)
    else:
      self._headers = headers

  def read(self, sz):
    return self._data

  def write(self, buf):
    self._wbuf.write(buf)

  def flush(self):
    data = self._wbuf.getvalue()
    self._wbuf = buffer_writer()

    # POST
    self._root = Resource(self._client)
    self._data = self._root.post('', data=data, headers=self._headers)
