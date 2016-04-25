#!/usr/local/bin/thrift -java

/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#
# Thrift Service that the MetaStore is built on
#

# include "share/fb303/if/fb303.thrift"
include "sentry_common_service.thrift"
include "sentry_policy_service.thrift"

namespace java org.apache.sentry.provider.db.generic.service.thrift
namespace php sentry.provider.db.service.db.generic.serivce.thrift
namespace cpp Apache.Sentry.Provider.Db.Generic.Service.Thrift

typedef sentry_common_service.TSentryResponseStatus TSentryResponseStatus

# Represents a new generic model privilege for solr or other component in transport 
# from the client to the server
enum TSentryGrantOption {
  TRUE = 1,
  FALSE = 0,
  UNSET = -1
}

# Represents a authorizable resource in the privilege
# like DATABASE=db1 in the hive, COLLECTION=collection1 in the solr
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

# CREATE ROLE r1
struct TCreateSentryRoleRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName,
4: required string component # The request is issued to which component
}

struct TCreateSentryRoleResponse {
1: required TSentryResponseStatus status
}

# DROP ROLE r1
struct TDropSentryRoleRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName,
4: required string component # The request is issued to which component
}

struct TDropSentryRoleResponse {
1: required TSentryResponseStatus status
}

# GRANT ROLE r1 TO GROUP g1
struct TAlterSentryRoleAddGroupsRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName,
4: required string component, # The request is issued to which component
5: required set<string> groups
}
struct TAlterSentryRoleAddGroupsResponse {
1: required TSentryResponseStatus status
}

# REVOLE ROLE r1 FROM GROUP g1
struct TAlterSentryRoleDeleteGroupsRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName,
4: required string component, # The request is issued to which component
5: required set<string> groups
}
struct TAlterSentryRoleDeleteGroupsResponse {
1: required TSentryResponseStatus status
}

# GRANT ... ON ... TO ROLE ...
struct TAlterSentryRoleGrantPrivilegeRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName,
4: required string component, # The request is issued to which component
5: required TSentryPrivilege privilege
}
struct TAlterSentryRoleGrantPrivilegeResponse {
1: required TSentryResponseStatus status
}

# REVOKE ... ON ... FROM ROLE ...
struct TAlterSentryRoleRevokePrivilegeRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName,
4: required string component, # The request is issued to which component
5: required TSentryPrivilege privilege
}
struct TAlterSentryRoleRevokePrivilegeResponse {
1: required TSentryResponseStatus status
}

# SHOW ROLE GRANT
struct TListSentryRolesRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: optional string groupName, # for this group, or all roles for all groups if null
4: required string component # The request is issued to which component
}
# used only for TListSentryRolesResponse
struct TSentryRole {
1: required string roleName,
2: required set<string> groups
}

struct TListSentryRolesResponse {
1: required TSentryResponseStatus status
2: optional set<TSentryRole> roles
}
# SHOW GRANT
struct TListSentryPrivilegesRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string roleName, # get privileges assigned for this role
4: required string component, # The request is issued to which component
5: required string serviceName, # The privilege belongs to which service
6: optional list<TAuthorizable> authorizables # get privileges assigned for this authorizable hierarchys
}

struct TListSentryPrivilegesResponse {
1: required TSentryResponseStatus status
2: optional set<TSentryPrivilege> privileges
}

# Drop privilege
struct TDropPrivilegesRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required TSentryPrivilege privilege
4: required string component, # The request is issued to which component
}

struct TDropPrivilegesResponse {
1: required TSentryResponseStatus status
}

# Rename privilege
struct TRenamePrivilegesRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string requestorUserName, # user on whose behalf the request is issued
3: required string component, # The request is issued to which component
4: required string serviceName, # The privilege belongs to which service
5: required list<TAuthorizable>  oldAuthorizables, # get old privileges assigned for this authorizable hierarchys
6: required list<TAuthorizable>  newAuthorizables # change to new authorizable hierarchys
}

struct TRenamePrivilegesResponse {
1: required TSentryResponseStatus status
}

# This API was created specifically for ProviderBackend.getPrivileges
# and is not mean for general purpose privilege retrieval.
# This request/response pair are created specifically so we can
# efficiently obtain the specific privilges for a user query
struct TSentryActiveRoleSet {
1: required bool all,
2: required set<string> roles,
}

struct TListSentryPrivilegesForProviderRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,
2: required string component, # The request is issued to which component
3: required string serviceName, # The privilege belongs to which service
4: required set<string> groups,
5: required TSentryActiveRoleSet roleSet,
6: optional list<TAuthorizable>  authorizables # authorizable hierarchys
}

struct TListSentryPrivilegesForProviderResponse {
1: required TSentryResponseStatus status
2: required set<string> privileges
}

# Map of role:set<privileges> for the given authorizable
# Optionally use the set of groups to filter the roles
struct TSentryPrivilegeMap {
1: required map<string, set<TSentryPrivilege>> privilegeMap
}

struct TListSentryPrivilegesByAuthRequest {
1: required i32 protocol_version = sentry_common_service.TSENTRY_SERVICE_V2,

# User on whose behalf the request is issued
2: required string requestorUserName,

# The request is issued to which component
3: required string component,

# The privilege belongs to which service
4: required string serviceName,

# The authorizable hierarchys, it is represented as a string. e.g
# resourceType1=resourceName1->resourceType2=resourceName2->resourceType3=resourceName3
5: required set<string> authorizablesSet,

# The requested groups. For admin, the requested groups can be empty, if so it is
# treated as a wildcard query. Otherwise, it is a query on this specifc groups.
# For non-admin user, the requested groups must be the groups they are part of.
6: optional set<string> groups,

# The active role set.
7: optional TSentryActiveRoleSet roleSet
}

struct TListSentryPrivilegesByAuthResponse {
1: required sentry_common_service.TSentryResponseStatus status,

# Will not be set in case of an error. Otherwise it will be a
# <Authorizables, <Role, Set<Privileges>>> mapping. For non-admin
# requestor, the roles are intersection of active roles and granted roles.
# For admin requestor, the roles are filtered based on the active roles
# and requested group from TListSentryPrivilegesByAuthRequest.
# The authorizable hierarchys is represented as a string in the form
# of the request.
2: optional map<string, TSentryPrivilegeMap> privilegesMapByAuth
}

service SentryGenericPolicyService
{
  TCreateSentryRoleResponse create_sentry_role(1:TCreateSentryRoleRequest request)
  TDropSentryRoleResponse drop_sentry_role(1:TDropSentryRoleRequest request)

  TAlterSentryRoleGrantPrivilegeResponse alter_sentry_role_grant_privilege(1:TAlterSentryRoleGrantPrivilegeRequest request)
  TAlterSentryRoleRevokePrivilegeResponse alter_sentry_role_revoke_privilege(1:TAlterSentryRoleRevokePrivilegeRequest request)

  TAlterSentryRoleAddGroupsResponse alter_sentry_role_add_groups(1:TAlterSentryRoleAddGroupsRequest request)
  TAlterSentryRoleDeleteGroupsResponse alter_sentry_role_delete_groups(1:TAlterSentryRoleDeleteGroupsRequest request)

  TListSentryRolesResponse list_sentry_roles_by_group(1:TListSentryRolesRequest request)

  TListSentryPrivilegesResponse list_sentry_privileges_by_role(1:TListSentryPrivilegesRequest request)

  TListSentryPrivilegesForProviderResponse list_sentry_privileges_for_provider(1:TListSentryPrivilegesForProviderRequest request)

  TListSentryPrivilegesByAuthResponse list_sentry_privileges_by_authorizable(1:TListSentryPrivilegesByAuthRequest request);

  TDropPrivilegesResponse drop_sentry_privilege(1:TDropPrivilegesRequest request);

  TRenamePrivilegesResponse rename_sentry_privilege(1:TRenamePrivilegesRequest request);
}
