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

import errno
import logging
import os.path
import re

from desktop.lib import security_util

import beeswax.conf
from hadoop import confparse


LOG = logging.getLogger(__name__)

_HIVE_SITE_PATH = None                  # Path to hive-site.xml
_HIVE_SITE_DICT = None                  # A dictionary of name/value config options
_METASTORE_LOC_CACHE = None

_CNF_HIVESERVER2_KERBEROS_PRINCIPAL = 'hive.server2.authentication.kerberos.principal'
_CNF_HIVESERVER2_AUTHENTICATION = 'hive.server2.authentication'
_CNF_HIVESERVER2_IMPERSONATION = 'hive.server2.enable.impersonation'

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

def get_hiveserver2_authentication():
  return get_conf().get(_CNF_HIVESERVER2_AUTHENTICATION, 'NONE').upper() # NONE == PLAIN SASL

def hiveserver2_impersonation_enabled():
  return get_conf().get(_CNF_HIVESERVER2_IMPERSONATION, 'FALSE').upper() == 'TRUE'

def _parse_hive_site():
  """
  Parse hive-site.xml and store in _HIVE_SITE_DICT
  """
  global _HIVE_SITE_DICT
  global _HIVE_SITE_PATH

  _HIVE_SITE_PATH = os.path.join(beeswax.conf.HIVE_CONF_DIR.get(), 'hive-site.xml')
  try:
    data = file(_HIVE_SITE_PATH, 'r').read()
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (_HIVE_SITE_PATH, err))
      return
    # Keep going and make an empty ConfParse
    data = ""

  _HIVE_SITE_DICT = confparse.ConfParse(data)
