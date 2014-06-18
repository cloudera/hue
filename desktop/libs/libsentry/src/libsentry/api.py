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

from libsentry.client import SentryClient
from libsentry.conf import HOSTNAME, PORT

import logging


LOG = logging.getLogger(__name__)


class SentryException(Exception):
  def __init__(self, e, message=''):
    super(SentryException, self).__init__(e)
    self.message = message


def get_api(user):
  return SentryApi(SentryClient(HOSTNAME.get(), PORT.get(), user.username))


class SentryApi(object):

  def __init__(self, client):
    self.client = client


  def create_sentry_role(self, roleName):
    response = self.client.create_sentry_role(roleName)
    
    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)  


  def drop_sentry_role(self, roleName):
    response = self.client.drop_sentry_role(roleName)
    
    if response.status.value == 0:
      return response
    else:
      raise SentryException(response) 


  def alter_sentry_role_grant_privilege(self, roleName, tSentryPrivilege):
    response = self.client.alter_sentry_role_grant_privilege(roleName, tSentryPrivilege)
    
    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)
    

  def alter_sentry_role_revoke_privilege(self, roleName, tSentryPrivilege):
    response = self.client.alter_sentry_role_revoke_privilege(roleName, tSentryPrivilege)
    
    if response.status.value == 0:
      return response
    else:
      raise SentryException(response) 
    
    
  def alter_sentry_role_add_groups(self, roleName, groups):
    response = self.client.alter_sentry_role_add_groups(roleName, groups)
    
    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)
        
        
  def alter_sentry_role_delete_groups(self, roleName, groups):
    response = self.client.alter_sentry_role_delete_groups(roleName, groups)
    
    if response.status.value == 0:
      return response
    else:
      raise SentryException(response)        
        
    
  def list_sentry_roles_by_group(self, groupName=None):
    response = self.client.list_sentry_roles_by_group()
    
    if response.status.value == 0:
      roles = {}
      for role in response.roles:
        roles[role.roleName] = {
          'grantorPrincipal': role.grantorPrincipal,
          'groups': [group.groupName for group in role.groups]
        }
      return roles
    else:
      raise SentryException(response)  


  def list_sentry_privileges_by_role(self, roleName, authorizableHierarchy=None):
    response = self.client.list_sentry_privileges_by_role(roleName, authorizableHierarchy)
    
    if response.status.value == 0:
      return [self._massage_priviledges(privilige) for privilige in response.privileges]
    else:
      raise SentryException(response)
    
    
  def list_sentry_privileges_for_provider(self, groups, roleSet=None, authorizableHierarchy=None):
    response = self.client.list_sentry_privileges_for_provider(groups, roleSet, authorizableHierarchy)
    
    if response.status.value == 0:
      return  [self._massage_priviledges(privilige) for privilige in response.privileges]
    else:
      raise SentryException(response)
    
    
  def _massage_priviledges(self, privilige):
    return {
        'scope': privilige.privilegeScope,
        'name': privilige.privilegeName,
        'server': privilige.serverName,
        'database': privilige.dbName,
        'table': privilige.tableName,
        'URI': privilige.URI,
        'action': privilige.action,
        'timestamp': privilige.createTime,
        'grantor': privilige.grantorPrincipal
    }     