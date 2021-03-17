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

from security import views as security_views
from security.api import hdfs as security_api_hdfs
from security.api import hive as security_api_hive
from security.api import sentry as security_api_sentry 

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^$', security_views.hive, name='index'),
  re_path(r'^hive$', security_views.hive, name='hive'),
  re_path(r'^hive2$', security_views.hive2, name='hive2'),
  re_path(r'^solr$', security_views.solr, name='solr'),
  re_path(r'^hdfs$', security_views.hdfs, name='hdfs'),
]


urlpatterns += [
  re_path(r'^api/hdfs/list(?P<path>/.*)$', security_api_hdfs.list_hdfs, name='list_hdfs'),
  re_path(r'^api/hdfs/get_acls$', security_api_hdfs.get_acls, name='get_acls'),
  re_path(r'^api/hdfs/update_acls', security_api_hdfs.update_acls, name='update_acls'),
  re_path(r'^api/hdfs/bulk_delete_acls', security_api_hdfs.bulk_delete_acls, name='bulk_delete_acls'),
  re_path(r'^api/hdfs/bulk_add_acls', security_api_hdfs.bulk_add_acls, name='bulk_add_acls'),
  re_path(r'^api/hdfs/bulk_sync_acls', security_api_hdfs.bulk_sync_acls, name='bulk_sync_acls'),
]


urlpatterns += [
  re_path(r'^api/hive/fetch_hive_path', security_api_hive.fetch_hive_path, name='fetch_hive_path'),

  re_path(r'^api/hive/list_sentry_roles_by_group', security_api_hive.list_sentry_roles_by_group, name='list_sentry_roles_by_group'),
  re_path(
    r'^api/hive/list_sentry_privileges_by_role', security_api_hive.list_sentry_privileges_by_role, name='list_sentry_privileges_by_role'
  ),
  re_path(
    r'^api/hive/list_sentry_privileges_for_provider$',
    security_api_hive.list_sentry_privileges_for_provider,
    name='list_sentry_privileges_for_provider'
  ),
  re_path(
    r'^api/hive/list_sentry_privileges_by_authorizable',
    security_api_hive.list_sentry_privileges_by_authorizable,
    name='list_sentry_privileges_by_authorizable'
  ),
  re_path(r'^api/hive/create_sentry_role', security_api_hive.create_sentry_role, name='create_sentry_role'),
  re_path(r'^api/hive/update_role_groups', security_api_hive.update_role_groups, name='update_role_groups'),
  re_path(r'^api/hive/drop_sentry_role', security_api_hive.drop_sentry_role, name='drop_sentry_role'),
  re_path(r'^api/hive/create_role$', security_api_hive.create_role, name='create_role'),
  re_path(r'^api/hive/save_privileges$', security_api_hive.save_privileges, name='save_privileges'),
  re_path(r'^api/hive/bulk_delete_privileges', security_api_hive.bulk_delete_privileges, name='bulk_delete_privileges'),
  re_path(r'^api/hive/bulk_add_privileges', security_api_hive.bulk_add_privileges, name='bulk_add_privileges'),
  re_path(r'^api/hive/grant_privilege', security_api_hive.grant_privilege, name='grant_privilege'),

  # Unused: API is for blind bulk operations
  re_path(r'^api/hive/rename_sentry_privilege', security_api_hive.rename_sentry_privilege, name='rename_sentry_privilege'),
]


# Generic API V2
urlpatterns += [
  re_path(r'^api/sentry/fetch_authorizables', security_api_sentry.fetch_authorizables, name='fetch_authorizables'),

  re_path(r'^api/sentry/list_sentry_roles_by_group', security_api_sentry.list_sentry_roles_by_group, name='list_sentry_roles_by_group'),
  re_path(
    r'^api/sentry/list_sentry_privileges_by_role',
    security_api_sentry.list_sentry_privileges_by_role,
    name='list_sentry_privileges_by_role'
  ),
  re_path(
    r'^api/sentry/list_sentry_privileges_for_provider$',
    security_api_sentry.list_sentry_privileges_for_provider,
    name='list_sentry_privileges_for_provider'
  ),
  re_path(
    r'^api/sentry/list_sentry_privileges_by_authorizable',
    security_api_sentry.list_sentry_privileges_by_authorizable,
    name='list_sentry_privileges_by_authorizable'
  ),
  re_path(r'^api/sentry/create_sentry_role', security_api_sentry.create_sentry_role, name='create_sentry_role'),
  re_path(r'^api/sentry/update_role_groups', security_api_sentry.update_role_groups, name='update_role_groups'),
  re_path(r'^api/sentry/drop_sentry_role', security_api_sentry.drop_sentry_role, name='drop_sentry_role'),
  re_path(r'^api/sentry/create_role$', security_api_sentry.create_role, name='create_role'),
  re_path(r'^api/sentry/save_privileges$', security_api_sentry.save_privileges, name='save_privileges'),
  re_path(r'^api/sentry/bulk_delete_privileges', security_api_sentry.bulk_delete_privileges, name='bulk_delete_privileges'),
  re_path(r'^api/sentry/bulk_add_privileges', security_api_sentry.bulk_add_privileges, name='bulk_add_privileges'),
  re_path(r'^api/sentry/grant_privilege', security_api_sentry.grant_privilege, name='grant_privilege'),

  # Unused: API is for blind bulk operations
  re_path(r'^api/sentry/rename_sentry_privilege', security_api_sentry.rename_sentry_privilege, name='rename_sentry_privilege'),
]
