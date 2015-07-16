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

from thrift import Thrift
from thrift.transport.TSocket import TSocket
from thrift.transport.TTransport import TBufferedTransport
from thrift.protocol import TBinaryProtocol

from hbased import Hbase as thrift_hbase
from hbased import ttypes


LOG = logging.getLogger(__name__)


def get_client_type():
  return thrift_hbase.Client

def get_thrift_type(name):
  if not hasattr(ttypes,name):
    return False
  return getattr(ttypes,name)

def get_thrift_attributes(name):
  thrift_type = get_thrift_type(name)
  attrs = {}
  for spec in thrift_type.thrift_spec:
    if spec is not None:
      attrs[spec[2]] = spec[1]
  return attrs
