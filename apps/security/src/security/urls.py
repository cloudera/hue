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

from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('security.views',
  url(r'^$', 'hive', name='index'),
  url(r'^hive$', 'hive', name='hive'),
  url(r'^hdfs$', 'hdfs', name='hdfs'),
)


urlpatterns += patterns('security.api',
  url(r'^api/hdfs/get_acls$', 'get_acls', name='get_acls'),
)

urlpatterns += patterns('security.api',
  url(r'^api/hive/list_sentry_roles_by_group', 'list_sentry_roles_by_group', name='list_sentry_roles_by_group'),
  url(r'^api/hive/list_sentry_privileges_by_role', 'list_sentry_privileges_by_role', name='list_sentry_privileges_by_role'),
  url(r'^api/hive/list_sentry_privileges_for_provider$', 'list_sentry_privileges_for_provider', name='list_sentry_privileges_for_provider'),  
  url(r'^api/hive/create_sentry_role', 'create_sentry_role', name='create_sentry_role'),
  url(r'^api/hive/drop_sentry_role', 'drop_sentry_role', name='drop_sentry_role'),
  url(r'^api/hive/create_role$', 'hive_create_role', name='hive_create_role'),
  url(r'^api/hive/add_privileges$', 'hive_add_privileges', name='hive_add_privileges'),
)
