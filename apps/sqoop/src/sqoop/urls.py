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

from django.conf.urls import patterns, url

urlpatterns = patterns('sqoop.views',
  url(r'^$', 'app', name='index')
)

urlpatterns += patterns('sqoop.api',
  url(r'^api/autocomplete/databases/?$', 'autocomplete', name='autocomplete_databases'),
  url(r'^api/autocomplete/databases/(?P<database>.+)/tables/?$', 'autocomplete', name='autocomplete_tables'),
  url(r'^api/autocomplete/databases/(?P<database>.+)/tables/(?P<table>.+)/columns/?$', 'autocomplete', name='autocomplete_fields'),
  url(r'^api/driver/?$', 'driver', name='driver'),
  url(r'^api/connectors', 'connectors', name='connectors'),
  url(r'^api/connectors/(?P<connector_id>\d+)/?$', 'connector', name='connector'),
  url(r'^api/links/?$', 'links', name='links'),
  url(r'^api/links/(?P<link_id>\d+)/?$', 'link', name='link'),
  url(r'^api/links/(?P<link_id>\d+)/clone/?$', 'link_clone', name='link_clone'),
  url(r'^api/links/(?P<link_id>\d+)/delete/?$', 'link_delete', name='link_delete'),
  url(r'^api/jobs/?$', 'jobs', name='jobs'),
  url(r'^api/jobs/(?P<job_id>\d+)/?$', 'job', name='job'),
  url(r'^api/jobs/(?P<job_id>\d+)/clone/?$', 'job_clone', name='job_clone'),
  url(r'^api/jobs/(?P<job_id>\d+)/delete/?$', 'job_delete', name='job_delete'),
  url(r'^api/jobs/(?P<job_id>\d+)/start/?$', 'job_start', name='job_start'),
  url(r'^api/jobs/(?P<job_id>\d+)/stop/?$', 'job_stop', name='job_stop'),
  url(r'^api/jobs/(?P<job_id>\d+)/status/?$', 'job_status', name='job_status'),
  url(r'^api/submissions/?$', 'submissions', name='submissions')
)
