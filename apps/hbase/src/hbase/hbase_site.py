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

import errno
import logging
import os.path

from hadoop import confparse
from desktop.lib.security_util import get_components


LOG = logging.getLogger(__name__)


SITE_PATH = None
SITE_DICT = None

_CNF_HBASE_THRIFT_KERBEROS_PRINCIPAL = 'hbase.thrift.kerberos.principal'
_CNF_HBASE_AUTHENTICATION = 'hbase.security.authentication'
_CNF_HBASE_REGIONSERVER_THRIFT_FRAMED = 'hbase.regionserver.thrift.framed'

_CNF_HBASE_IMPERSONATION_ENABLED = 'hbase.thrift.support.proxyuser'
_CNF_HBASE_USE_THRIFT_HTTP = 'hbase.regionserver.thrift.http'
_CNF_HBASE_USE_THRIFT_SSL = 'hbase.thrift.ssl.enabled'



def reset():
  global SITE_DICT
  SITE_DICT = None


def get_conf():
  if SITE_DICT is None:
    _parse_site()
  return SITE_DICT


def get_server_principal():
  principal = get_conf().get(_CNF_HBASE_THRIFT_KERBEROS_PRINCIPAL, None)
  components = get_components(principal)
  if components is not None:
    return components[0]


def get_server_authentication():
  return get_conf().get(_CNF_HBASE_AUTHENTICATION, 'NOSASL').upper()

def get_thrift_transport():
  use_framed = get_conf().get(_CNF_HBASE_REGIONSERVER_THRIFT_FRAMED)
  if use_framed is not None:
    if use_framed.upper() == "TRUE":
      return "framed"
    else:
      return "buffered"
  else:
    #Avoid circular import
    from hbase.conf import THRIFT_TRANSPORT
    return THRIFT_TRANSPORT.get()

def is_impersonation_enabled():
  #Avoid circular import
  from hbase.conf import USE_DOAS
  return get_conf().get(_CNF_HBASE_IMPERSONATION_ENABLED, 'FALSE').upper() == 'TRUE' or USE_DOAS.get()

def is_using_thrift_http():
  #Avoid circular import
  from hbase.conf import USE_DOAS
  return get_conf().get(_CNF_HBASE_USE_THRIFT_HTTP, 'FALSE').upper() == 'TRUE' or USE_DOAS.get()

def is_using_thrift_ssl():
  return get_conf().get(_CNF_HBASE_USE_THRIFT_SSL, 'FALSE').upper() == 'TRUE'


def _parse_site():
  global SITE_DICT
  global SITE_PATH

  #Avoid circular import
  from hbase.conf import HBASE_CONF_DIR
  SITE_PATH = os.path.join(HBASE_CONF_DIR.get(), 'hbase-site.xml')
  try:
    data = file(SITE_PATH, 'r').read()
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (SITE_PATH, err))
      return
    data = ""

  SITE_DICT = confparse.ConfParse(data)

