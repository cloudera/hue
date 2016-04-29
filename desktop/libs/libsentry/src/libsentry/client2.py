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

from sentry_generic_policy_service import SentryGenericPolicyService
from sentry_generic_policy_service.ttypes import TListSentryRolesRequest, TListSentryPrivilegesRequest, TAuthorizable, TCreateSentryRoleRequest, \
    TDropSentryRoleRequest, TAlterSentryRoleGrantPrivilegeRequest, TSentryPrivilege, TAlterSentryRoleGrantPrivilegeResponse, \
    TAlterSentryRoleRevokePrivilegeRequest, TAlterSentryRoleAddGroupsRequest, TAlterSentryRoleDeleteGroupsRequest, \
    TListSentryPrivilegesForProviderRequest, TSentryActiveRoleSet, TDropPrivilegesRequest, TRenamePrivilegesRequest, \
    TListSentryPrivilegesByAuthRequest

from libsentry.sentry_site import get_sentry_server_authentication,\
  get_sentry_server_principal


LOG = logging.getLogger(__name__)


"""
struct TAuthorizable {
1: required string type,
2: required string name
}

struct TSentryPrivilege {
1: required string component,
2: required string serviceName,
3: required list<TAuthorizable> authorizables,
4: required string action,
5: optional i64 createTime, # Set on server side
6: optional string grantorPrincipal, # Set on server side
7: optional TSentryGrantOption grantOption = sentry_policy_service.TSentryGrantOption.FALSE
}
"""

class SentryClient(object):
  SENTRY_MECHANISMS = {'KERBEROS': 'GSSAPI', 'NOSASL': 'NOSASL', 'NONE': 'NONE'}

  def __init__(self, host, port, username, component='hive'):
    self.username = username
    self.host = host
    self.port = port
    self.security = self._get_security()
    self.component = component

    self.client = thrift_util.get_client(
        SentryGenericPolicyService.Client,
        host,
        port,
        service_name="SentryGenericPolicyService",
        username=self.username,
        timeout_seconds=30,
        multiple=True,
        kerberos_principal=self.security['kerberos_principal_short_name'],
        use_sasl=self.security['use_sasl'],
        mechanism=self.security['mechanism']
    )

  def __str__(self):
    return ', '.join(map(str, [self.host, self.port, self.component, self.username, self.security]))


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
    request = TCreateSentryRoleRequest(requestorUserName=self.username, component=self.component, roleName=roleName)
    return self.client.create_sentry_role(request)


  def drop_sentry_role(self, roleName):
    request = TDropSentryRoleRequest(requestorUserName=self.username, component=self.component, roleName=roleName)
    return self.client.drop_sentry_role(request)


  def alter_sentry_role_grant_privilege(self, roleName, tSentryPrivilege):
    tSentryPrivilege['authorizables'] = [TAuthorizable(type=_auth['type'], name=_auth['name']) for _auth in tSentryPrivilege['authorizables']]
    tSentryPrivilege = TSentryPrivilege(**tSentryPrivilege)

    request = TAlterSentryRoleGrantPrivilegeRequest(requestorUserName=self.username, component=self.component, roleName=roleName, privilege=tSentryPrivilege)
    return self.client.alter_sentry_role_grant_privilege(request)


  def alter_sentry_role_revoke_privilege(self, roleName, tSentryPrivilege):
    if tSentryPrivilege is not None:
      tSentryPrivilege['authorizables'] = [TAuthorizable(type=_auth['type'], name=_auth['name']) for _auth in tSentryPrivilege['authorizables']]
      tSentryPrivilege = TSentryPrivilege(**tSentryPrivilege)

    request = TAlterSentryRoleRevokePrivilegeRequest(requestorUserName=self.username, component=self.component, roleName=roleName, privilege=tSentryPrivilege)
    return self.client.alter_sentry_role_revoke_privilege(request)


  def alter_sentry_role_add_groups(self, roleName, groups):
    request = TAlterSentryRoleAddGroupsRequest(requestorUserName=self.username, component=self.component, roleName=roleName, groups=groups)
    return self.client.alter_sentry_role_add_groups(request)


  def alter_sentry_role_delete_groups(self, roleName, groups):
    request = TAlterSentryRoleDeleteGroupsRequest(requestorUserName=self.username, component=self.component, roleName=roleName, groups=groups)
    return self.client.alter_sentry_role_delete_groups(request)


  def list_sentry_roles_by_group(self, groupName=None):
    request = TListSentryRolesRequest(requestorUserName=self.username, component=self.component, groupName=groupName)
    return self.client.list_sentry_roles_by_group(request)


  def list_sentry_privileges_by_role(self, serviceName, roleName, authorizables=None):
    if authorizables is not None:
      authorizables = TAuthorizable(**authorizables)
    request = TListSentryPrivilegesRequest(requestorUserName=self.username, component=self.component, roleName=roleName, serviceName=serviceName, authorizables=authorizables)
    return self.client.list_sentry_privileges_by_role(request)


  def drop_sentry_privilege(self, authorizable):
    authorizable = TAuthorizable(**authorizable)
    request = TDropPrivilegesRequest(requestorUserName=self.username, component=self.component, authorizable=authorizable)
    return self.client.drop_sentry_privilege(request)


  def rename_sentry_privilege(self, oldAuthorizable, newAuthorizable):
    oldAuthorizable = TAuthorizable(**oldAuthorizable)
    newAuthorizable = TAuthorizable(**newAuthorizable)
    request = TRenamePrivilegesRequest(requestorUserName=self.username, component=self.component, oldAuthorizable=oldAuthorizable, newAuthorizable=newAuthorizable)
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
      authorizableHierarchy = TAuthorizable(**authorizableHierarchy)
    request = TListSentryPrivilegesForProviderRequest(component=self.component, groups=groups, roleSet=roleSet, authorizableHierarchy=authorizableHierarchy)
    return self.client.list_sentry_privileges_for_provider(request)


  def list_sentry_privileges_by_authorizable(self, serviceName, authorizableSet, groups=None, roleSet=None):
    authorizableSet = ['%s=%s' % (_auth['type'], _auth['name']) for _authSet in authorizableSet for _auth in _authSet['authorizables']]

    if roleSet is not None:
      roleSet = TSentryActiveRoleSet(**roleSet)

    request = TListSentryPrivilegesByAuthRequest(requestorUserName=self.username, component=self.component, serviceName=serviceName, authorizablesSet=set(authorizableSet), groups=groups, roleSet=roleSet)
    return self.client.list_sentry_privileges_by_authorizable(request)
