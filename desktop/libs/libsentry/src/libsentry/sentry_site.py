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


_SITE_DICT = None

_CONF_HIVE_PROVIDER = 'hive.sentry.server'

_CONF_SENTRY_SERVER_PRINCIPAL = 'sentry.service.server.principal'
_CONF_SENTRY_SERVER_SECURITY_MODE = 'sentry.service.security.mode'
_CONF_SENTRY_SERVER_ADMIN_GROUP = 'sentry.service.admin.group'

_CONF_SENTRY_SERVER_HA_ENABLED = 'sentry.ha.enabled'
_CONF_SENTRY_SERVER_HA_HAS_SECURITY = 'sentry.ha.zookeeper.security'
_CONF_SENTRY_SERVER_HA_ZOOKEEPER_ADDRESSES = 'sentry.ha.zookeeper.security.quorum'
_CONF_SENTRY_SERVER_HA_ZOOKEEPER_NAMESPACE = 'sentry.ha.zookeeper.namespace'


def reset():
  global _SITE_DICT
  _SITE_DICT = None


def get_conf(name='sentry'):
  if _SITE_DICT is None:
    _parse_sites()
  return _SITE_DICT[name]



def get_hive_sentry_provider():
  return get_conf(name='hive').get(_CONF_HIVE_PROVIDER, 'server1')


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

def get_sentry_server_admin_groups():
  return get_conf().get(_CONF_SENTRY_SERVER_ADMIN_GROUP, '').split(',')


def get_sentry_server_ha_enabled():
  return get_conf().get(_CONF_SENTRY_SERVER_HA_ENABLED, 'FALSE').upper() == 'TRUE'

def get_sentry_server_ha_has_security():
  return get_conf().get(_CONF_SENTRY_SERVER_HA_HAS_SECURITY, 'FALSE').upper() == 'TRUE'

def get_sentry_server_ha_zookeeper_quorum():
  return get_conf().get(_CONF_SENTRY_SERVER_HA_ZOOKEEPER_ADDRESSES)

def get_sentry_server_ha_zookeeper_namespace():
  return get_conf().get(_CONF_SENTRY_SERVER_HA_ZOOKEEPER_NAMESPACE, 'sentry')


def _parse_sites():
  global _SITE_DICT
  _SITE_DICT ={}

  paths = [
    ('sentry', os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')),
  ]

  try:
    from beeswax.conf import HIVE_CONF_DIR
    paths.append(('hive', os.path.join(HIVE_CONF_DIR.get(), 'sentry-site.xml')))
  except Exception, e:
    LOG.error('Cannot read Hive sentry site: %s' % e)

  for name, path in paths:
    _SITE_DICT[name] = _parse_site(path)

def _parse_site(site_path):
  try:
    data = file(site_path, 'r').read()
  except IOError, err:
    if err.errno != errno.ENOENT:
      LOG.error('Cannot read from "%s": %s' % (site_path, err))
      return
    data = ""

  return confparse.ConfParse(data)
