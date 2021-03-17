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

from sqoop import views as sqoop_views
from sqoop import api as sqoop_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^$', sqoop_views.app, name='index')
]

urlpatterns += [
  re_path(r'^api/autocomplete/databases/?$', sqoop_api.autocomplete, name='autocomplete_databases'),
  re_path(r'^api/autocomplete/databases/(?P<database>.+)/tables/?$', sqoop_api.autocomplete, name='autocomplete_tables'),
  re_path(
    r'^api/autocomplete/databases/(?P<database>.+)/tables/(?P<table>.+)/columns/?$', sqoop_api.autocomplete, name='autocomplete_fields'
  ),
  re_path(r'^api/driver/?$', sqoop_api.driver, name='driver'),
  re_path(r'^api/connectors', sqoop_api.connectors, name='connectors'),
  re_path(r'^api/connectors/(?P<connector_id>\d+)/?$', sqoop_api.connector, name='connector'),
  re_path(r'^api/links/?$', sqoop_api.links, name='links'),
  re_path(r'^api/links/(?P<link_id>\d+)/?$', sqoop_api.link, name='link'),
  re_path(r'^api/links/(?P<link_id>\d+)/clone/?$', sqoop_api.link_clone, name='link_clone'),
  re_path(r'^api/links/(?P<link_id>\d+)/delete/?$', sqoop_api.link_delete, name='link_delete'),
  re_path(r'^api/jobs/?$', sqoop_api.jobs, name='jobs'),
  re_path(r'^api/jobs/(?P<job_id>\d+)/?$', sqoop_api.job, name='job'),
  re_path(r'^api/jobs/(?P<job_id>\d+)/clone/?$', sqoop_api.job_clone, name='job_clone'),
  re_path(r'^api/jobs/(?P<job_id>\d+)/delete/?$', sqoop_api.job_delete, name='job_delete'),
  re_path(r'^api/jobs/(?P<job_id>\d+)/start/?$', sqoop_api.job_start, name='job_start'),
  re_path(r'^api/jobs/(?P<job_id>\d+)/stop/?$', sqoop_api.job_stop, name='job_stop'),
  re_path(r'^api/jobs/(?P<job_id>\d+)/status/?$', sqoop_api.job_status, name='job_status'),
  re_path(r'^api/submissions/?$', sqoop_api.submissions, name='submissions')
]
