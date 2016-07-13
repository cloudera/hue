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

from django.contrib.auth.models import User, Group

from desktop.decorators import check_superuser_permission
from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import smart_unicode


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    response = {}
    try:
      return view_fn(*args, **kwargs)
    except Exception, e:
      LOG.exception('Error running %s' % view_fn)
      response['status'] = -1
      response['message'] = smart_unicode(e)
    return JsonResponse(response)
  return decorator


@error_handler
@check_superuser_permission
def get_users(request):
  """
  Returns all users with username, ID, groups, active and superuser status by default.
  Optional params:
    username=<username> - Filter by username
    groups=<groupnames> - List of group names to filter on (additive "OR" search)
    is_active=true         - Only return active users (defaults to all users)
  """
  response = {
    'users': []
  }

  username = request.GET.get('username', '').lower()
  groups = request.GET.getlist('groups')
  is_active = request.GET.get('is_active', '').lower()

  users = User.objects

  if is_active and is_active == 'true':
    users = users.filter(is_active=True)

  if username:
    users = users.filter(username=username)

  if groups:
    group_ids = []
    for groupname in groups:
      groupname = groupname.lower()
      try:
        group = Group.objects.get(name=groupname)
        group_ids.append(group.id)
      except Group.DoesNotExist, e:
        LOG.exception("Failed to filter by group, group with name %s not found." % groupname)
    users = users.filter(groups__in=group_ids)

  users = users.order_by('username')

  for user in users:
    user = {
      'id': user.id,
      'username': user.username,
      'groups': [group.name for group in user.groups.all()],
      'is_active': user.is_active,
      'superuser': user.is_superuser
    }
    response['users'].append(user)

  response['status'] = 0

  return JsonResponse(response)
