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
from desktop.lib import security_util

from libsentry.conf import SENTRY_CONF_DIR, HOSTNAME


LOG = logging.getLogger(__name__)


_SENTRY_SITE_PATH = None
_SENTRY_SITE_DICT = None

_CONF_HIVE_PROVIDER = 'hive.sentry.provider'
_CONF_SENTRY_SERVER_PRINCIPAL = 'sentry.service.server.principal'
_CONF_SENTRY_SERVER_SECURITY_MODE = 'sentry.service.security.mode'


def reset():
  global _SENTRY_SITE_DICT
  _SENTRY_SITE_DICT = None


def get_conf():
  if _SENTRY_SITE_DICT is None:
    _parse_site()
  return _SENTRY_SITE_DICT



def get_hive_sentry_provider():
  return get_conf().get(_CONF_HIVE_PROVIDER, 'default')

def get_sentry_server_principal():  
  # Get kerberos principal and replace host pattern
  principal = get_conf().get(_CONF_SENTRY_SERVER_PRINCIPAL, None)
  if principal:
    fqdn = security_util.get_fqdn(HOSTNAME.get())
    return security_util.get_kerberos_principal(principal, fqdn)
  else:
    return None

def get_sentry_server_authentication():
  return get_conf().get(_CONF_SENTRY_SERVER_SECURITY_MODE, 'NOSASL').upper()


def _parse_site():
  global _SENTRY_SITE_DICT
  global _SENTRY_SITE_PATH

  _SENTRY_SITE_PATH = os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')
  try:
    data = file(_SENTRY_SITE_PATH, 'r').read()
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (_SENTRY_SITE_PATH, err))
      return
    data = ""

  _SENTRY_SITE_DICT = confparse.ConfParse(data)
