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
import json
import random
import threading
import time

from desktop.lib.exceptions_renderable import PopupException
from django.utils.translation import ugettext as _

from kazoo.client import KazooClient

from libsentry.client import SentryClient
from libsentry.conf import HOSTNAME, PORT
from libsentry.sentry_site import get_sentry_server_ha_enabled, get_sentry_server_ha_has_security, get_sentry_server_ha_zookeeper_quorum, get_sentry_server_ha_zookeeper_namespace


LOG = logging.getLogger(__name__)


_api_cache = None
_api_cache_lock = threading.Lock()


def ha_error_handler(func):
  def decorator(*args, **kwargs):
    retries = 15

    while retries > 0:
      try:
        return func(*args, **kwargs)
      except SentryException, e:
        raise e
      except Exception, e:
        retries -= 1
        if not get_sentry_server_ha_enabled() or retries == 0:
          raise e
        else:
          # Right now retries on any error and pull a fresh list of servers from ZooKeeper
          LOG.info('Retrying fetching an available client in ZooKeeper.')
          global _api_cache
          _api_cache = None
          time.sleep(1)
          args[0].client = _get_client(args[0].client.username)
          LOG.info('Picked %s' % args[0].client)

  return decorator


def get_api(user):
  client = _get_client(user.username)

  return SentryApi(client)


class SentryApi(object):

  def __init__(self, client):
    self.client = client

  @ha_error_handler
  def create_sentry_role(self, roleName):
    response = self.client.create_sentry_role(roleName)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def drop_sentry_role(self, roleName):
    response = self.client.drop_sentry_role(roleName)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def alter_sentry_role_grant_privilege(self, roleName, tSentryPrivilege):
    response = self.client.alter_sentry_role_grant_privilege(roleName, tSentryPrivilege)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def alter_sentry_role_revoke_privilege(self, roleName, tSentryPrivilege):
    response = self.client.alter_sentry_role_revoke_privilege(roleName, tSentryPrivilege)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def alter_sentry_role_add_groups(self, roleName, groups):
    response = self.client.alter_sentry_role_add_groups(roleName, groups)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def alter_sentry_role_delete_groups(self, roleName, groups):
    response = self.client.alter_sentry_role_delete_groups(roleName, groups)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def list_sentry_roles_by_group(self, groupName=None):
    response = self.client.list_sentry_roles_by_group(groupName)

    if response.status.value == 0:
      roles = []
      for role in response.roles:
        roles.append({
          'name': role.roleName,
          'groups': [group.groupName for group in role.groups]
        })
      return roles
    else:
      raise SentryException(response)

  @ha_error_handler
  def list_sentry_privileges_by_role(self, roleName, authorizableHierarchy=None):
    response = self.client.list_sentry_privileges_by_role(roleName, authorizableHierarchy)

    if response.status.value == 0:
      return [self._massage_priviledge(privilege) for privilege in response.privileges]
    else:
      raise SentryException(response)

  @ha_error_handler
  def list_sentry_privileges_for_provider(self, groups, roleSet=None, authorizableHierarchy=None):
    response = self.client.list_sentry_privileges_for_provider(groups, roleSet, authorizableHierarchy)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def list_sentry_privileges_by_authorizable(self, authorizableSet, groups=None, roleSet=None):
    response = self.client.list_sentry_privileges_by_authorizable(authorizableSet, groups, roleSet)

    _privileges = []

    for authorizable, roles in response.privilegesMapByAuth.iteritems():
      _roles = {}
      for role, privileges in roles.privilegeMap.iteritems():
        _roles[role] = [self._massage_priviledge(privilege) for privilege in privileges]
      _privileges.append((self._massage_authorizable(authorizable), _roles))

    if response.status.value == 0:
      return _privileges
    else:
      raise SentryException(response)

  @ha_error_handler
  def drop_sentry_privileges(self, authorizableHierarchy):
    response = self.client.drop_sentry_privilege(authorizableHierarchy)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def rename_sentry_privileges(self, oldAuthorizable, newAuthorizable):
    response = self.client.rename_sentry_privilege(oldAuthorizable, newAuthorizable)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)


  def _massage_priviledge(self, privilege):
    return {
        'scope': privilege.privilegeScope,
        'server': privilege.serverName,
        'database': privilege.dbName,
        'table': privilege.tableName,
        'URI': privilege.URI,
        'action': 'ALL' if privilege.action == '*' else privilege.action.upper(),
        'timestamp': privilege.createTime,
        'grantOption': privilege.grantOption == 1,
    }


  def _massage_authorizable(self, authorizable):
    return {
        'server': authorizable.server,
        'database': authorizable.db,
        'table': authorizable.table,
        'URI': authorizable.uri,
    }


class SentryException(Exception):
  def __init__(self, e):
    super(SentryException, self).__init__(e)
    self.message = e.status.message

  def __str__(self):
    return self.message


def _get_client(username):
  if get_sentry_server_ha_enabled():
    servers = _get_server_properties()
    if servers:
      server = random.choice(servers)
    else:
      raise PopupException(_('No Sentry servers are available.'))
  else:
    server = {
        'hostname': HOSTNAME.get(),
        'port': PORT.get()
    }

  return SentryClient(server['hostname'], server['port'], username)


# To move to a libzookeeper with decorator


def _get_server_properties():
  global _api_cache

  if _api_cache is None:
    _api_cache_lock.acquire()

    try:
      if _api_cache is None:

        if get_sentry_server_ha_has_security():
          try:
            from zookeeper.conf import CLUSTERS
            sasl_server_principal = CLUSTERS.get()['default'].PRINCIPAL_NAME.get()
          except Exception, e:
            LOG.error("Could not get principal name from ZooKeeper app config: %s. Using 'zookeeper' as principal name." % e)
            sasl_server_principal = 'zookeeper'
        else:
          sasl_server_principal = None

        zk = KazooClient(hosts=get_sentry_server_ha_zookeeper_quorum(), read_only=True, sasl_server_principal=sasl_server_principal)

        zk.start()

        servers = []
        namespace = get_sentry_server_ha_zookeeper_namespace()

        children = zk.get_children("/%s/sentry-service/sentry-service/" % namespace)
        for node in children:
          data, stat = zk.get("/%s/sentry-service/sentry-service/%s" % (namespace, node))
          server = json.loads(data.decode("utf-8"))
          servers.append({'hostname': server['address'], 'port': server['sslPort'] if server['sslPort'] else server['port']})

        zk.stop()

        _api_cache = servers
    finally:
      _api_cache_lock.release()

  return _api_cache
