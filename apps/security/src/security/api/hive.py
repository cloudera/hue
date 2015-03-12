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
import logging
import time

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from libsentry.api import get_api
from libsentry.sentry_site import get_sentry_server_admin_groups
from hadoop.cluster import get_defaultfs

from beeswax.api import autocomplete


LOG = logging.getLogger(__name__)


def fetch_hive_path(request):
  path = request.GET['path']

  database = None
  table = None
  if path:
    database = path
  if '/' in path:
    database, table = path.split('/')

  resp = autocomplete(request, database, table)

  if database and request.GET['doas'] != request.user.username:
    request.GET = request.GET.copy()
    request.GET['doas'] = request.GET['doas']

    resp = autocomplete(request, database, table)

  return resp


def list_sentry_roles_by_group(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    if request.POST['groupName']:
      groupName = request.POST['groupName']
    else:
      # Admins can see everything, other only the groups they belong too
      groupName = None if request.user.groups.filter(name__in=get_sentry_server_admin_groups()).exists() else '*'
    roles = get_api(request.user).list_sentry_roles_by_group(groupName)
    result['roles'] = sorted(roles, key=lambda role: role['name'])
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not retrieve roles")

    if "couldn't be retrieved." in str(e):
      result['roles'] = []
      result['status'] = 0
    else:
      result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def list_sentry_privileges_by_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']
    sentry_privileges = get_api(request.user).list_sentry_privileges_by_role(roleName)
    result['sentry_privileges'] = sorted(sentry_privileges, key=lambda privilege: '%s.%s.%s.%s' % (privilege['server'], privilege['database'], privilege['table'], privilege['URI']))
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not list sentry privileges")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def _to_sentry_privilege(privilege):
  return {
      'privilegeScope': privilege['privilegeScope'],
      'serverName': privilege['serverName'],
      'dbName': privilege['dbName'],
      'tableName': privilege['tableName'],
      'URI': _massage_uri(privilege['URI']),
      'action': privilege['action'],
      'createTime': privilege['timestamp'],
      'grantOption': 1 if privilege['grantOption'] else 0,
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
            'database': privilege.get('dbName'),
            'action': privilege.get('action'),
            'scope': privilege.get('privilegeScope'),
            'table': privilege.get('tableName'),
            'URI': privilege.get('URI'),
            'server': privilege.get('serverName'),
            'grantOption': privilege.get('grantOption') == 1
        })

    return _privileges


def _massage_uri(uri):
  if uri:
    if uri.startswith('hdfs:///'):
      uri = uri.replace('hdfs://', get_defaultfs())
    elif uri.startswith('/'):
      uri = get_defaultfs() + uri

  return uri


def _drop_sentry_privilege(user, role, authorizable):
  return get_api(user).alter_sentry_role_revoke_privilege(role['name'], _to_sentry_privilege(authorizable))


def create_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    role = json.loads(request.POST['role'])

    api = get_api(request.user)

    api.create_sentry_role(role['name'])

    privileges = [privilege for privilege in role['privileges'] if privilege['status'] != 'deleted']
    result['privileges'] = _hive_add_privileges(request.user, role, privileges)
    api.alter_sentry_role_add_groups(role['name'], role['groups'])

    result['role'] = {"name": role['name'], "groups": role['groups']}

    result['message'] = _('Role created!')
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not create role")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


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
    LOG.exception("could not update role groups")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


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

    result['message'] = _('Privileges updated')
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not save privileges")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def grant_privilege(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = json.loads(request.POST['roleName'])
    privilege = json.loads(request.POST['privilege'])

    result['privileges'] = _hive_add_privileges(request.user, {'name': roleName}, [privilege])

    result['message'] = _('Privilege granted successfully to %s.') % roleName
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not grant privileges")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def create_sentry_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']

    get_api(request.user).create_sentry_role(roleName)
    result['message'] = _('Role and privileges created.')
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not create role")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def drop_sentry_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']

    get_api(request.user).drop_sentry_role(roleName)
    result['message'] = _('Role and privileges deleted.')
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not drop role")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def list_sentry_privileges_by_authorizable(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    groups = [request.POST['groupName']] if request.POST['groupName'] else None
    authorizableSet = [json.loads(request.POST['authorizableHierarchy'])]

    _privileges = []

    for authorizable, roles in get_api(request.user).list_sentry_privileges_by_authorizable(authorizableSet=authorizableSet, groups=groups):
      for role, privileges in roles.iteritems():
        for privilege in privileges:
          privilege['roleName'] = role
          _privileges.append(privilege)

    result['privileges'] = sorted(_privileges, key=lambda privilege: privilege['roleName'])

    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not list privileges by authorizable")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


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
    LOG.exception("could not bulk delete privileges")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


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
    LOG.exception("could not bulk add privileges")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def rename_sentry_privilege(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    oldAuthorizable = json.loads(request.POST['oldAuthorizable'])
    newAuthorizable = json.loads(request.POST['newAuthorizable'])

    get_api(request.user).rename_sentry_privilege(oldAuthorizable, newAuthorizable)
    result['message'] = _('Privilege deleted.')
    result['status'] = 0
  except Exception, e:
    LOG.exception("could not rename privilege")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


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
    LOG.exception("could not list privileges for provider")

    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)
