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

from desktop.lib import thrift_util

from sentry_policy_service import SentryPolicyService
from sentry_policy_service.ttypes import TListSentryRolesRequest, TListSentryPrivilegesRequest, TSentryAuthorizable, TCreateSentryRoleRequest, \
    TDropSentryRoleRequest, TAlterSentryRoleGrantPrivilegeRequest, TSentryPrivilege, TAlterSentryRoleGrantPrivilegeResponse, \
    TAlterSentryRoleRevokePrivilegeRequest, TAlterSentryRoleAddGroupsRequest, TSentryGroup, TAlterSentryRoleDeleteGroupsRequest, \
    TListSentryPrivilegesForProviderRequest, TSentryActiveRoleSet, TSentryAuthorizable, TDropPrivilegesRequest, TRenamePrivilegesRequest, \
    TListSentryPrivilegesByAuthRequest, TSentryConfigValueRequest

from libsentry.sentry_site import get_sentry_server_authentication,\
  get_sentry_server_principal


LOG = logging.getLogger(__name__)


"""
struct TSentryPrivilege {
1: required string privilegeScope, # Valid values are SERVER, DATABASE, TABLE
3: required string serverName,
4: optional string dbName = "",
5: optional string tableName = "",
6: optional string URI = "",
7: required string action = "",
8: optional i64 createTime, # Set on server side
9: optional TSentryGrantOption grantOption = TSentryGrantOption.FALSE
}

struct TSentryAuthorizable {
1: required string server,
2: optional string uri,
3: optional string db,
4: optional string table,
}
"""

class SentryClient(object):
  SENTRY_MECHANISMS = {'KERBEROS': 'GSSAPI', 'NOSASL': 'NOSASL', 'NONE': 'NONE'}

  def __init__(self, host, port, username):
    self.username = username
    self.host = host
    self.port = port
    self.security = self._get_security()

    self.client = thrift_util.get_client(
        SentryPolicyService.Client,
        host,
        port,
        service_name="SentryPolicyService",
        username=self.username,
        timeout_seconds=30,
        multiple=True,
        kerberos_principal=self.security['kerberos_principal_short_name'],
        use_sasl=self.security['use_sasl'],
        mechanism=self.security['mechanism']
    )

  def __str__(self):
    return ', '.join(map(str, [self.host, self.port, self.username, self.security]))


  def _get_security(self):
    principal = get_sentry_server_principal()
    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None
    use_sasl = get_sentry_server_authentication() == 'KERBEROS'
    mechanism = SentryClient.SENTRY_MECHANISMS[get_sentry_server_authentication()]

    return {
        'kerberos_principal_short_name': kerberos_principal_short_name,
        'use_sasl': use_sasl,
        'mechanism': mechanism
    }


  def create_sentry_role(self, roleName):
    request = TCreateSentryRoleRequest(requestorUserName=self.username, roleName=roleName)
    return self.client.create_sentry_role(request)


  def drop_sentry_role(self, roleName):
    request = TDropSentryRoleRequest(requestorUserName=self.username, roleName=roleName, )
    return self.client.drop_sentry_role(request)


  def alter_sentry_role_grant_privilege(self, roleName, tSentryPrivilege, tSentryPrivileges):
    if tSentryPrivilege is not None:
      tSentryPrivilege = TSentryPrivilege(**tSentryPrivilege)

    if tSentryPrivileges is not None:
      tSentryPrivileges = [TSentryPrivilege(**tSentryPrivilege) for tSentryPrivilege in tSentryPrivileges]

    request = TAlterSentryRoleGrantPrivilegeRequest(requestorUserName=self.username, roleName=roleName, privilege=tSentryPrivilege, privileges=tSentryPrivileges)
    return self.client.alter_sentry_role_grant_privilege(request)


  def alter_sentry_role_revoke_privilege(self, roleName, tSentryPrivilege, tSentryPrivileges):
    if tSentryPrivilege is not None:
      tSentryPrivilege = TSentryPrivilege(**tSentryPrivilege)

    if tSentryPrivileges is not None:
      tSentryPrivileges = [TSentryPrivilege(**tSentryPrivilege) for tSentryPrivilege in tSentryPrivileges]

    request = TAlterSentryRoleRevokePrivilegeRequest(requestorUserName=self.username, roleName=roleName, privilege=tSentryPrivilege, privileges=tSentryPrivileges)
    return self.client.alter_sentry_role_revoke_privilege(request)


  def alter_sentry_role_add_groups(self, roleName, groups):
    groups = [TSentryGroup(name) for name in groups]
    request = TAlterSentryRoleAddGroupsRequest(requestorUserName=self.username, roleName=roleName, groups=groups)
    return self.client.alter_sentry_role_add_groups(request)


  def alter_sentry_role_delete_groups(self, roleName, groups):
    groups = [TSentryGroup(name) for name in groups]
    request = TAlterSentryRoleDeleteGroupsRequest(requestorUserName=self.username, roleName=roleName, groups=groups)
    return self.client.alter_sentry_role_delete_groups(request)


  def list_sentry_roles_by_group(self, groupName=None):
    request = TListSentryRolesRequest(requestorUserName=self.username, groupName=groupName)
    return self.client.list_sentry_roles_by_group(request)


  def list_sentry_privileges_by_role(self, roleName, authorizableHierarchy=None):
    if authorizableHierarchy is not None:
      authorizableHierarchy = TSentryAuthorizable(**authorizableHierarchy)
    request = TListSentryPrivilegesRequest(requestorUserName=self.username, roleName=roleName, authorizableHierarchy=authorizableHierarchy)
    return self.client.list_sentry_privileges_by_role(request)


  def drop_sentry_privilege(self, authorizable):
    authorizable = TSentryAuthorizable(**authorizable)
    request = TDropPrivilegesRequest(requestorUserName=self.username, authorizable=authorizable)
    return self.client.drop_sentry_privilege(request)


  def rename_sentry_privilege(self, oldAuthorizable, newAuthorizable):
    oldAuthorizable = TSentryAuthorizable(**oldAuthorizable)
    newAuthorizable = TSentryAuthorizable(**newAuthorizable)
    request = TRenamePrivilegesRequest(requestorUserName=self.username, oldAuthorizable=oldAuthorizable, newAuthorizable=newAuthorizable)
    return self.client.rename_sentry_privilege(request)


  def list_sentry_privileges_for_provider(self, groups, roleSet=None, authorizableHierarchy=None):
    """
    struct TSentryActiveRoleSet {
      1: required bool all,
      2: required set<string> roles,
    }

    struct TListSentryPrivilegesForProviderResponse {
      1: required sentry_common_service.TSentryResponseStatus status
      2: required set<string> privileges
    }
    """
    if roleSet is not None:
      roleSet = TSentryActiveRoleSet(**roleSet)
    if authorizableHierarchy is not None:
      authorizableHierarchy = TSentryAuthorizable(**authorizableHierarchy)
    request = TListSentryPrivilegesForProviderRequest(groups=groups, roleSet=roleSet, authorizableHierarchy=authorizableHierarchy)
    return self.client.list_sentry_privileges_for_provider(request)


  def list_sentry_privileges_by_authorizable(self, authorizableSet, groups=None, roleSet=None):
    authorizableSet = [TSentryAuthorizable(**authorizable) for authorizable in authorizableSet]
    if roleSet is not None:
      roleSet = TSentryActiveRoleSet(**roleSet)

    request = TListSentryPrivilegesByAuthRequest(requestorUserName=self.username, authorizableSet=authorizableSet, groups=groups, roleSet=roleSet)
    return self.client.list_sentry_privileges_by_authorizable(request)


  def get_sentry_config_value(self, propertyName, defaultValue=None):
    # Note there is no requestorUserName in Sentry API

    request = TSentryConfigValueRequest(propertyName=propertyName, defaultValue=defaultValue)
    return self.client.get_sentry_config_value(request)
