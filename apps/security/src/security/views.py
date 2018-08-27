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

from desktop.lib.django_util import render

from libsentry.sentry_site import get_hive_sentry_provider, get_sentry_server_admin_groups, get_solr_sentry_provider
from desktop.auth.backend import is_admin


def hive(request):

  return render("hive.mako", request, {
      'initial': json.dumps({
          'user': request.user.username,
          'sentry_provider': get_hive_sentry_provider(),
          'is_sentry_admin': request.user.groups.filter(name__in=get_sentry_server_admin_groups()).exists()
      }),
      'is_embeddable': request.GET.get('is_embeddable', False),
      'has_impersonation_perm': _has_impersonation_perm(request.user),
  })


def hive2(request):
  return _sentry(request, component='hive')


def solr(request):
  return _sentry(request, component='solr')


def _sentry(request, component):
  return render("sentry.mako", request, {
      'initial': json.dumps({
          'component': component,
          'user': request.user.username,
          'sentry_provider': get_solr_sentry_provider() if component == 'solr' else get_hive_sentry_provider(),
          'is_sentry_admin': request.user.groups.filter(name__in=get_sentry_server_admin_groups()).exists()
      }),
      'is_embeddable': request.GET.get('is_embeddable', False),
      'has_impersonation_perm': _has_impersonation_perm(request.user) and component == 'hive',
      'component': component
  })


def hdfs(request):

  return render("hdfs.mako", request, {
      'initial': json.dumps({'user': request.user.username}),
      'is_embeddable': request.GET.get('is_embeddable', False),
      'has_impersonation_perm': _has_impersonation_perm(request.user)
  })


def _has_impersonation_perm(user):
  return is_admin(user) or user.has_hue_permission(action="impersonate", app="security")
