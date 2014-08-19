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

import json
import time

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from libsentry.api import get_api


def list_sentry_roles_by_group(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    groupName = request.POST['groupName'] if request.POST['groupName'] else None
    roles = get_api(request.user).list_sentry_roles_by_group(groupName)
    result['roles'] = sorted(roles, key= lambda role: role['name'])
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def list_sentry_privileges_by_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']
    sentry_privileges = get_api(request.user).list_sentry_privileges_by_role(roleName)
    result['sentry_privileges'] = sorted(sentry_privileges, key=lambda privilege: '%s.%s' % (privilege['database'], privilege['table']))
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def _to_sentry_privilege(privilege):
  return {
      'privilegeScope': privilege['privilegeScope'],
      'serverName': privilege['serverName'],
      'dbName': privilege['dbName'],
      'tableName': privilege['tableName'],
      'URI': privilege['URI'],
      'action': privilege['action'],
      'createTime': privilege['timestamp']
  }  


def _hive_add_privileges(user, role, privileges):
    api = get_api(user)

    _privileges = []

    for privilege in privileges:
      if privilege['status'] not in ('deleted',):
        api.alter_sentry_role_grant_privilege(role['name'], _to_sentry_privilege(privilege))
        # Mocked until Sentry API returns the info. Not used currently as we refresh the whole role.
        _privileges.append({
            'timestamp': int(time.time()),
            'grantor': user.username,
            'database': privilege.get('dbName'),
            'action': privilege.get('action'),
            'scope': privilege.get('privilegeScope'),
            'table': privilege.get('tableName'),
            'URI': privilege.get('URI'),            
            'server': privilege.get('serverName')
        })

    return _privileges


def _drop_sentry_privilege(user, role, authorizable):
  return get_api(user).alter_sentry_role_revoke_privilege(role['name'], _to_sentry_privilege(authorizable))


def create_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    role = json.loads(request.POST['role'])

    api = get_api(request.user)

    api.create_sentry_role(role['name'])
    result['privileges'] = _hive_add_privileges(request.user, role, role['privileges'])
    api.alter_sentry_role_add_groups(role['name'], role['groups'])

    result['role'] = {"name": role['name'], "groups": role['groups'], "grantorPrincipal": request.user.username}

    result['message'] = _('Role created!')
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def update_role_groups(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    role = json.loads(request.POST['role'])
    
    new_groups = set(role['groups']) - set(role['originalGroups'])
    deleted_groups = set(role['originalGroups']) - set(role['groups'])

    api = get_api(request.user)
    
    if new_groups:
      api.alter_sentry_role_add_groups(role['name'], new_groups)
    if deleted_groups:
      api.alter_sentry_role_delete_groups(role['name'], deleted_groups)

    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def save_privileges(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    role = json.loads(request.POST['role'])

    new_privileges = [privilege for privilege in role['privilegesChanged'] if privilege['status'] == 'new']
    result['privileges'] = _hive_add_privileges(request.user, role, new_privileges)
    
    deleted_privileges = [privilege for privilege in role['privilegesChanged'] if privilege['status'] == 'deleted']
    for privilege in deleted_privileges:
      _drop_sentry_privilege(request.user, role, privilege)

    modified_privileges = [privilege for privilege in role['privilegesChanged'] if privilege['status'] == 'modified']
    old_privileges_ids = [privilege['id'] for privilege in modified_privileges]
    _hive_add_privileges(request.user, role, modified_privileges)
    for privilege in role['originalPrivileges']:
      if privilege['id'] in old_privileges_ids:      
        _drop_sentry_privilege(request.user, role, privilege)

    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def create_sentry_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']

    get_api(request.user).create_sentry_role(roleName)
    result['message'] = _('Role and privileges created.')
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def drop_sentry_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']

    get_api(request.user).drop_sentry_role(roleName)
    result['message'] = _('Role and privileges deleted.')
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


# Mocked until Sentry API returns the info!
def list_sentry_privileges_by_authorizable(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    groupName = request.POST['groupName'] if request.POST['groupName'] else None
    roleSet = json.loads(request.POST['roleSet'])
    authorizableHierarchy = json.loads(request.POST['authorizableHierarchy'])

    privileges = []
    roles = get_api(request.user).list_sentry_roles_by_group(groupName=groupName)

    for role in roles:
      for privilege in get_api(request.user).list_sentry_privileges_by_role(role['name'], authorizableHierarchy=authorizableHierarchy):
        privilege['roleName'] = role['name']
        privileges.append(privilege)

    result['privileges'] = privileges

    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def bulk_delete_privileges(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    checkedPaths = json.loads(request.POST['checkedPaths'])
    authorizableHierarchy = json.loads(request.POST['authorizableHierarchy'])

    for path in [path['path'] for path in checkedPaths]:
      if '.' in path:
        db, table = path.split('.')
      else:
        db, table = path, ''
      authorizableHierarchy.update({
        'db': db,
        'table': table,
      })
      get_api(request.user).drop_sentry_privileges(authorizableHierarchy)
    result['message'] = _('Privileges deleted.')
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def bulk_add_privileges(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    privileges = json.loads(request.POST['privileges'])
    checkedPaths = json.loads(request.POST['checkedPaths'])
    authorizableHierarchy = json.loads(request.POST['authorizableHierarchy'])

    privileges = [privilege for privilege in privileges if privilege['status'] == '']

    for path in [path['path'] for path in checkedPaths]:
      if '.' in path:
        db, table = path.split('.')
      else:
        db, table = path, ''
      privilegeScope = 'TABLE' if table else 'DATABASE' if db else 'SERVER'
      authorizableHierarchy.update({
        'db': db,
        'table': table, 
      })

      for privilege in privileges:
        privilege['dbName'] = db
        privilege['tableName'] = table
        privilege['privilegeScope'] = privilegeScope        
        _hive_add_privileges(request.user, {'name': privilege['roleName']}, [privilege])      

    result['message'] = _('Privileges added.')
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def rename_sentry_privilege(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    oldAuthorizable = json.loads(request.POST['oldAuthorizable'])
    newAuthorizable = json.loads(request.POST['newAuthorizable'])

    get_api(request.user).rename_sentry_privilege(oldAuthorizable, newAuthorizable)
    result['message'] = _('Privilege deleted.')
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def list_sentry_privileges_for_provider(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    groups = json.loads(request.POST['groups'])
    roleSet = json.loads(request.POST['roleSet'])
    authorizableHierarchy = json.loads(request.POST['authorizableHierarchy'])

    sentry_privileges = get_api(request.user).list_sentry_privileges_for_provider(groups=groups, roleSet=roleSet, authorizableHierarchy=authorizableHierarchy)
    result['sentry_privileges'] = sentry_privileges
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")
