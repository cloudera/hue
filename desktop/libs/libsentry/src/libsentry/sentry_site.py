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
import random

from django.utils.translation import ugettext as _

from hadoop import confparse

from desktop.lib import security_util
from desktop.lib.exceptions_renderable import PopupException

from libsentry.conf import SENTRY_CONF_DIR, HOSTNAME, PORT


LOG = logging.getLogger(__name__)


_SITE_DICT = None

_CONF_HIVE_PROVIDER = 'hive.sentry.server'

_CONF_SENTRY_SERVER_PRINCIPAL = 'sentry.service.server.principal'
_CONF_SENTRY_SERVER_SECURITY_MODE = 'sentry.service.security.mode'
_CONF_SENTRY_SERVER_ADMIN_GROUP = 'sentry.service.admin.group'

_CONF_SENTRY_SERVER_RPC_ADDRESSES = 'sentry.service.client.server.rpc-address'
_CONF_SENTRY_SERVER_RPC_PORT = 'sentry.service.client.server.rpc-port'


def reset():
  global _SITE_DICT
  _SITE_DICT = None


def get_conf(name='sentry'):
  if _SITE_DICT is None:
    _parse_sites()
  return _SITE_DICT[name]


def get_hive_sentry_provider():
  return get_conf(name='hive').get(_CONF_HIVE_PROVIDER, 'server1')


def get_solr_sentry_provider():
  return 'service1'


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


def get_sentry_server_rpc_addresses():
  hosts = None
  servers = get_conf().get(_CONF_SENTRY_SERVER_RPC_ADDRESSES)
  if servers:
    hosts = servers.split(',')
  return hosts


def get_sentry_server_rpc_port():
  return int(get_conf().get(_CONF_SENTRY_SERVER_RPC_PORT, '8038'))


def is_ha_enabled():
  return get_sentry_server_rpc_addresses() is not None


def get_sentry_client(username, client_class, exempt_host=None, component=None):
  server = None
  if is_ha_enabled():
    servers = _get_server_properties(exempt_host=exempt_host)
    if servers:
      server = random.choice(servers)

  if server is None:
    if HOSTNAME.get() and PORT.get():
      LOG.info('No Sentry servers configured in %s, falling back to libsentry configured host: %s:%s' %
               (_CONF_SENTRY_SERVER_RPC_ADDRESSES, HOSTNAME.get(), PORT.get()))
      server = {
          'hostname': HOSTNAME.get(),
          'port': PORT.get()
      }
    else:
      raise PopupException(_('No Sentry servers are configured.'))

  if component:
    client = client_class(server['hostname'], server['port'], username, component=component)
  else:
    client = client_class(server['hostname'], server['port'], username)

  return client


def _get_server_properties(exempt_host=None):
  try:
    servers = []
    sentry_servers = get_sentry_server_rpc_addresses()
    for server in sentry_servers:
      host = server
      if ':' in server:
        host, port = server.split(':')
      elif get_sentry_server_rpc_port():
        port = get_sentry_server_rpc_port()
      else:
        port = PORT.get()
      if host != exempt_host:
        servers.append({'hostname': host, 'port': int(port)})
  except Exception, e:
    raise PopupException(_('Error in retrieving Sentry server properties.'), detail=e)

  return servers


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
