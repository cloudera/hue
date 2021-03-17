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

import sys

from desktop.lib.django_util import get_username_re_rule, get_groupname_re_rule

from useradmin import views as useradmin_views
from useradmin import api as useradmin_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

username_re = get_username_re_rule()
groupname_re = get_groupname_re_rule()


urlpatterns = [
  re_path(r'^$', useradmin_views.list_users, name="useradmin.views.list_users"),
  re_path(r'^users/?$', useradmin_views.list_users, name="useradmin.views.list_users"),
  re_path(r'^groups/?$', useradmin_views.list_groups, name="useradmin.views.list_groups"),
  re_path(r'^permissions/?$', useradmin_views.list_permissions, name="useradmin.views.list_permissions"),
  re_path(r'^configurations/?$', useradmin_views.list_configurations, name="useradmin.views.list_configurations"),
  re_path(r'^organizations/?$', useradmin_views.list_organizations, name="useradmin.views.list_organizations"),
  re_path(r'^users/edit/(?P<username>%s)$' % (username_re,), useradmin_views.edit_user, name="useradmin.views.edit_user"),
  re_path(r'^users/add_ldap_users$', useradmin_views.add_ldap_users, name="useradmin.views.add_ldap_users"),
  re_path(r'^users/add_ldap_groups$', useradmin_views.add_ldap_groups, name="useradmin.views.add_ldap_groups"),
  re_path(r'^users/sync_ldap_users_groups$', useradmin_views.sync_ldap_users_groups, name="useradmin_views_sync_ldap_users_groups"),
  re_path(r'^groups/edit/(?P<name>%s)$' % (groupname_re,), useradmin_views.edit_group, name="useradmin.views.edit_group"),
  re_path(r'^permissions/edit/(?P<app>.+?)/(?P<priv>.+?)/?$', useradmin_views.edit_permission, name="useradmin.views.edit_permission"),
  re_path(r'^users/new$', useradmin_views.edit_user, name="useradmin.views.edit_user"),
  re_path(r'^groups/new$', useradmin_views.edit_group, name="useradmin.views.edit_group"),
  re_path(r'^users/delete', useradmin_views.delete_user, name="useradmin.views.delete_user"),
  re_path(r'^groups/delete$', useradmin_views.delete_group, name="useradmin.views.delete_group"),
]

urlpatterns += [
  re_path(r'^api/get_users/?', useradmin_api.get_users, name='api_get_users'),
]
