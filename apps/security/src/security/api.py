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

from django.http import HttpResponse
from libsentry.api import get_api


# HDFS

def get_acls(request):  
  path = request.GET.get('path')
  acls = request.fs.get_acl_status(path)
  return HttpResponse(json.dumps(acls['AclStatus']), mimetype="application/json")


# Hive

def list_sentry_roles_by_group(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roles = get_api(request.user).list_sentry_roles_by_group()
    result['roles'] = roles
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
    result['sentry_privileges'] = sentry_privileges
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def hive_edit_role(request):  
  result = {'status': -1, 'message': 'Error'}

  try:
    role = json.loads(request.POST['role'])
    
    api = get_api(request.user)
    
    try:
      api.create_sentry_role(role['name'])
    except Exception, e:
      print e
    for priviledge in role['priviledges']:
      api.alter_sentry_role_grant_privilege(role['name'], {
          'privilegeScope': priviledge['privilegeScope'],
          'serverName': priviledge['serverName'],
          'dbName': priviledge['dbName'],
          'tableName': priviledge['tableName'],
          'URI': priviledge['URI'],
          'action': priviledge['action']
      })
    api.alter_sentry_role_add_groups(role['name'], role['groups'])

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
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")


def drop_sentry_role(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    roleName = request.POST['roleName']

    get_api(request.user).drop_sentry_role(roleName)
    result['message'] = ''
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return HttpResponse(json.dumps(result), mimetype="application/json")
