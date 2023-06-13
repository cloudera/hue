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

"""
Helper for reading hive-site.xml
"""

from builtins import str
import errno
import logging
import os.path
import re
import socket
import sys

from desktop.lib import security_util
from hadoop import confparse
from hadoop.ssl_client_site import get_trustore_location, get_trustore_password

import beeswax.conf

if sys.version_info[0] > 2:
  open_file = open
else:
  open_file = file

LOG = logging.getLogger()

_HIVE_SITE_PATH = None                  # Path to hive-site.xml
_HIVE_SITE_DICT = None                  # A dictionary of name/value config options
_METASTORE_LOC_CACHE = None

_CNF_METASTORE_SASL = 'hive.metastore.sasl.enabled'
_CNF_METASTORE_URIS = 'hive.metastore.uris'
_CNF_METASTORE_KERBEROS_PRINCIPAL = 'hive.metastore.kerberos.principal'
_CNF_METASTORE_WAREHOUSE_DIR = 'hive.metastore.warehouse.dir'

_CNF_HIVESERVER2_KERBEROS_PRINCIPAL = 'hive.server2.authentication.kerberos.principal'
_CNF_HIVESERVER2_AUTHENTICATION = 'hive.server2.authentication'
_CNF_HIVESERVER2_IMPERSONATION = 'hive.server2.enable.doAs'

_CNF_HIVESERVER2_USE_SSL = 'hive.server2.use.SSL'
_CNF_HIVESERVER2_TRUSTSTORE_PATH = 'hive.server2.truststore.path'
_CNF_HIVESERVER2_TRUSTSTORE_PASSWORD = 'hive.server2.truststore.password'

_CNF_HIVESERVER2_TRANSPORT_MODE = 'hive.server2.transport.mode'
_CNF_HIVESERVER2_THRIFT_BINARY_PORT = 'hive.server2.thrift.port'
_CNF_HIVESERVER2_THRIFT_HTTP_PORT = 'hive.server2.thrift.http.port'
_CNF_HIVESERVER2_THRIFT_HTTP_PATH = 'hive.server2.thrift.http.path'
_CNF_HIVESERVER2_THRIFT_SASL_QOP = 'hive.server2.thrift.sasl.qop'

_CNF_HIVESERVER2_USE_SASL = 'hive.metastore.sasl.enabled'

_CNF_HIVE_SUPPORT_CONCURRENCY = 'hive.support.concurrency'
_CNF_HIVE_HOOK_PROTO_BASE_DIR = 'hive.hook.proto.base-directory'
_CNF_HIVE_EXECUTION_MODE = 'hive.execution.mode'
_CNF_HIVE_EXECUTION_ENGINE = 'hive.execution.engine'


# Host is whatever up to the colon. Allow and ignore a trailing slash.
_THRIFT_URI_RE = re.compile("^thrift://([^:]+):(\d+)[/]?$")


class MalformedHiveSiteException(Exception):
  """Parsing error class used internally"""
  pass

def reset():
  """Reset the cached conf"""
  global _HIVE_SITE_DICT
  global _METASTORE_LOC_CACHE
  _HIVE_SITE_DICT = None
  _METASTORE_LOC_CACHE = None


def get_conf():
  """get_conf() ->  ConfParse object for hive-site.xml"""
  if _HIVE_SITE_DICT is None:
    _parse_hive_site()
  return _HIVE_SITE_DICT


def get_metastore():
  """
  Get first metastore information from local hive-site.xml.
  """
  global _METASTORE_LOC_CACHE
  if not _METASTORE_LOC_CACHE:
    thrift_uris = get_conf().get(_CNF_METASTORE_URIS)
    is_local = thrift_uris is None or thrift_uris == ''

    if not is_local:
      use_sasl = str(get_conf().get(_CNF_METASTORE_SASL, 'false')).lower() == 'true'
      thrift_uri = thrift_uris.split(",")[0] # First URI
      host = socket.getfqdn()
      match = _THRIFT_URI_RE.match(thrift_uri)
      if not match:
        LOG.error('Cannot understand remote metastore uri "%s"' % thrift_uri)
      else:
        host, port = match.groups()
      kerberos_principal = security_util.get_kerberos_principal(get_conf().get(_CNF_METASTORE_KERBEROS_PRINCIPAL, None), host)

      _METASTORE_LOC_CACHE = {
          'use_sasl': use_sasl,
          'thrift_uri': thrift_uri,
          'kerberos_principal': kerberos_principal
      }
    else:
      LOG.error('Hue requires a remote metastore configuration')
  return _METASTORE_LOC_CACHE


def get_hiveserver2_kerberos_principal(hostname_or_ip):
  """
  Retrieves principal for HiveServer 2.

  Raises socket.herror
  """
  fqdn = security_util.get_fqdn(hostname_or_ip)
  # Get kerberos principal and replace host pattern
  principal = get_conf().get(_CNF_HIVESERVER2_KERBEROS_PRINCIPAL, None)
  if principal:
    return security_util.get_kerberos_principal(principal, fqdn)
  else:
    return None

def get_metastore_warehouse_dir():
  return get_conf().get(_CNF_METASTORE_WAREHOUSE_DIR, '/user/hive/warehouse')

def get_hiveserver2_authentication():
  return get_conf().get(_CNF_HIVESERVER2_AUTHENTICATION, 'NONE').upper() # NONE == PLAIN SASL

def get_hiveserver2_thrift_sasl_qop():
  return get_conf().get(_CNF_HIVESERVER2_THRIFT_SASL_QOP, 'NONE').lower()

def hiveserver2_impersonation_enabled():
  return get_conf().get(_CNF_HIVESERVER2_IMPERSONATION, 'TRUE').upper() == 'TRUE'

def hiveserver2_jdbc_url():
  is_transport_mode_http = hiveserver2_transport_mode() == 'HTTP'
  urlbase = 'jdbc:hive2://%s:%s/default' % (
      beeswax.conf.HIVE_SERVER_HOST.get(),
      beeswax.conf.HIVE_HTTP_THRIFT_PORT.get() if is_transport_mode_http else beeswax.conf.HIVE_SERVER_PORT.get()
  )

  if get_conf().get(_CNF_HIVESERVER2_USE_SSL, 'FALSE').upper() == 'TRUE':
    urlbase += ';ssl=true'

    if get_conf().get(_CNF_HIVESERVER2_TRUSTSTORE_PATH):
      urlbase += ';sslTrustStore=%s' % get_conf().get(_CNF_HIVESERVER2_TRUSTSTORE_PATH)
    elif get_trustore_location():
      urlbase += ';sslTrustStore=%s' % get_trustore_location()

    if get_conf().get(_CNF_HIVESERVER2_TRUSTSTORE_PASSWORD):
      urlbase += ';trustStorePassword=%s' % get_conf().get(_CNF_HIVESERVER2_TRUSTSTORE_PASSWORD)
    elif get_trustore_password():
      urlbase += ';trustStorePassword=%s' % get_trustore_password()

  if is_transport_mode_http:
    urlbase += ';transportMode=http'
    urlbase += ';httpPath=%s' % hiveserver2_thrift_http_path()

  return urlbase


def hiveserver2_use_ssl():
  return get_conf().get(_CNF_HIVESERVER2_USE_SSL, 'FALSE').upper() == 'TRUE'

def hiveserver2_transport_mode():
  return get_conf().get(_CNF_HIVESERVER2_TRANSPORT_MODE, 'TCP').upper()

def hiveserver2_thrift_binary_port():
  return get_conf().get(_CNF_HIVESERVER2_THRIFT_BINARY_PORT)

def hiveserver2_thrift_http_port():
  return get_conf().get(_CNF_HIVESERVER2_THRIFT_HTTP_PORT)

def hiveserver2_thrift_http_path():
  return get_conf().get(_CNF_HIVESERVER2_THRIFT_HTTP_PATH, 'cliservice')


def get_use_sasl():
  return get_conf().get(_CNF_HIVESERVER2_USE_SASL)


def has_concurrency_support():
  '''For SQL transactions like INSERT, DELETE, UPDATE since Hive 3. '''
  ''''Possibly use set -v in future to obtain properties hive.create.as.acid=true & hive.create.as.insert.only=true'''
  return get_conf().get(_CNF_HIVE_SUPPORT_CONCURRENCY, 'TRUE').upper() == 'TRUE'

def get_hive_hook_proto_base_directory():
  return get_conf().get(_CNF_HIVE_HOOK_PROTO_BASE_DIR)

def get_hive_execution_mode():
  return get_conf().get(_CNF_HIVE_EXECUTION_MODE)

def get_hive_execution_engine():
  return get_conf().get(_CNF_HIVE_EXECUTION_ENGINE)

def _parse_hive_site():
  """
  Parse hive-site.xml and store in _HIVE_SITE_DICT
  """
  global _HIVE_SITE_DICT
  global _HIVE_SITE_PATH

  _HIVE_SITE_PATH = os.path.join(beeswax.conf.HIVE_CONF_DIR.get(), 'hive-site.xml')
  try:
    data = open_file(_HIVE_SITE_PATH, 'r').read()
  except IOError as err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (_HIVE_SITE_PATH, err))
      return
    # Keep going and make an empty ConfParse
    data = ""

  _HIVE_SITE_DICT = confparse.ConfParse(data)

def get_hive_site_content():
  hive_site_path = os.path.join(beeswax.conf.HIVE_CONF_DIR.get(), 'hive-site.xml')
  if not os.path.exists(hive_site_path):
    return ''
  else:
    return open_file(hive_site_path, 'r').read()
