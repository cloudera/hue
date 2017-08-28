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
import threading

from django.utils.translation import ugettext as _

from desktop.lib.exceptions import StructuredThriftTransportException
from desktop.lib.exceptions_renderable import PopupException

from libsentry.client2 import SentryClient
from libsentry.sentry_ha import get_next_available_server, create_client
from libsentry.sentry_site import get_sentry_server, is_ha_enabled


LOG = logging.getLogger(__name__)

API_CACHE = None
API_CACHE_LOCK = threading.Lock()


def ha_error_handler(func):

  def decorator(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except StructuredThriftTransportException, e:
      if not is_ha_enabled():
        raise PopupException(_('Failed to connect to Sentry server %s, and Sentry HA is not enabled.') % args[0].client.host, detail=e)
      else:
        LOG.warn("Failed to connect to Sentry server %s, will attempt to find next available host." % args[0].client.host)
        server, attempts = get_next_available_server(client_class=SentryClient, username=args[0].client.username, failed_host=args[0].client.host, component=args[0].client.component)
        if server is not None:
          args[0].client = create_client(SentryClient, args[0].client.username, server, args[0].client.component)
          set_api_cache(server)
          return func(*args, **kwargs)
        else:
          raise PopupException(_('Failed to find an available Sentry server.'))
    except (SentryException, PopupException), e:
      raise e
    except Exception, e:
      raise PopupException(_('Encountered unexpected error in SentryApi.'), detail=e)

  return decorator


def clear_api_cache():
  global API_CACHE
  if API_CACHE is not None:
    LOG.info("Force resetting the currently cached Sentry server: %s:%s" % (API_CACHE['hostname'], API_CACHE['port']))
    API_CACHE = None


def set_api_cache(server):
  global API_CACHE
  global API_CACHE_LOCK
  API_CACHE_LOCK.acquire()
  try:
    API_CACHE = server
    LOG.info("Setting cached Sentry server: %s:%s" % (API_CACHE['hostname'], API_CACHE['port']))
  finally:
    API_CACHE_LOCK.release()
  return server


def get_cached_server(current_host=None):
  global API_CACHE
  if current_host and API_CACHE is not None:
    clear_api_cache()

  if API_CACHE is None:
    server = get_sentry_server(current_host)
    if server is not None:
      set_api_cache(server)
    else:
      raise PopupException(_('Failed to find an available Sentry server.'))
  else:
    LOG.debug("Returning cached Sentry server: %s:%s" % (API_CACHE['hostname'], API_CACHE['port']))

  return API_CACHE


def get_api(user, component='hive'):
  if component == 'solr':
    component = component.upper()

  server = get_cached_server()
  client = create_client(SentryClient, user.username, server, component)
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
  def alter_sentry_role_grant_privilege(self, roleName, tSentryPrivilege=None):
    response = self.client.alter_sentry_role_grant_privilege(roleName, tSentryPrivilege)

    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)

  @ha_error_handler
  def alter_sentry_role_revoke_privilege(self, roleName, tSentryPrivilege=None):
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
          'groups': list(role.groups)
        })
      return roles
    else:
      raise SentryException(response)

  @ha_error_handler
  def list_sentry_privileges_by_role(self, serviceName, roleName, authorizables=None):
    response = self.client.list_sentry_privileges_by_role(serviceName, roleName, authorizables)

    if response.status.value == 0:
      return [self._massage_privilege(privilege) for privilege in response.privileges]
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
  def list_sentry_privileges_by_authorizable(self, serviceName, authorizableSet, groups=None, roleSet=None):
    response = self.client.list_sentry_privileges_by_authorizable(serviceName, authorizableSet, groups, roleSet)

    if response.status.value != 0:
      raise SentryException(response)

    _privileges = []

    for authorizable, roles in response.privilegesMapByAuth.iteritems():
      _roles = {}
      for role, privileges in roles.privilegeMap.iteritems():
        _roles[role] = [self._massage_privilege(privilege) for privilege in privileges]
      _privileges.append((self._massage_string_authorizable(authorizable), _roles))

    return _privileges

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


  def _massage_privilege(self, privilege):
    return {
        'component': privilege.component,
        'serviceName': privilege.serviceName,
        'authorizables': self._massage_authorizable(privilege.authorizables),
        'action': 'ALL' if privilege.action == '*' else privilege.action.upper(),
        'timestamp': privilege.createTime,
        'grantorPrincipal': privilege.grantorPrincipal,
        'grantOption': privilege.grantOption == 1,
    }


  def _massage_authorizable(self, authorizables):
    return [{'type': auth.type, 'name': auth.name} for auth in authorizables]


  def _massage_string_authorizable(self, authorizables):
    return [{'type': auth.split('=')[0], 'name': auth.split('=')[1]} for auth in authorizables.split('->')]


class SentryException(Exception):
  def __init__(self, e):
    super(SentryException, self).__init__(e)
    self.message = e.status.message

  def __str__(self):
    return self.message
