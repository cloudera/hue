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

from django.urls import re_path

from zookeeper import views as zookeeper_views

urlpatterns = [
  re_path(r'^$', zookeeper_views.index, name='index'),
  re_path(r'view/(?P<id>\w+)$', zookeeper_views.view, name='view'),
  re_path(r'clients/(?P<id>\w+)/(?P<host>.+)$', zookeeper_views.clients, name='clients'),
  re_path(r'tree/(?P<id>\w+)/(?P<path>.+)$', zookeeper_views.tree, name='tree'),
  re_path(r'create/(?P<id>\w+)/(?P<path>.*)$', zookeeper_views.create, name='create'),
  re_path(r'delete/(?P<id>\w+)/(?P<path>.*)$', zookeeper_views.delete, name='delete'),
  re_path(r'edit/base64/(?P<id>\w+)/(?P<path>.*)$', zookeeper_views.edit_as_base64, name='edit_as_base64'),
  re_path(r'edit/text/(?P<id>\w+)/(?P<path>.*)$', zookeeper_views.edit_as_text, name='edit_as_text'),
]
