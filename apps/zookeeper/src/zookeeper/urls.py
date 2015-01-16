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


urlpatterns = patterns('zookeeper.views',
  url(r'^$', 'index', name='index'),
  url(r'view/(?P<id>\w+)$', 'view', name='view'),
  url(r'clients/(?P<id>\w+)/(?P<host>.+)$', 'clients', name='clients'),
  url(r'tree/(?P<id>\w+)/(?P<path>.+)$', 'tree', name='tree'),
  url(r'create/(?P<id>\w+)/(?P<path>.*)$', 'create', name='create'),
  url(r'delete/(?P<id>\w+)/(?P<path>.*)$', 'delete', name='delete'),
  url(r'edit/base64/(?P<id>\w+)/(?P<path>.*)$', 'edit_as_base64', name='edit_as_base64'),
  url(r'edit/text/(?P<id>\w+)/(?P<path>.*)$', 'edit_as_text', name='edit_as_text'),
)
