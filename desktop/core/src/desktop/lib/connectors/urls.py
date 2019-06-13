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

from django.conf.urls import url

from desktop.lib.connectors import views, api


urlpatterns = [
  url(r'^$', views.index, name='desktop.lib.connectors.views.index'),

  url(r'^api/types/?$', api.get_connector_classes, name='connectors.api.get_connector_classes'),
  url(r'^api/instances/?$', api.get_installed_connectors, name='connectors.api.get_installed_connectors'),

  url(r'^api/instance/new/(?P<type>[\w\-]+)$', api.new_connector, name='connectors.api.new_connector'),
  url(r'^api/instance/get/(?P<id>\d+)$', api.get_connector, name='connectors.api.get_connector'),
  url(r'^api/instance/delete/?$', api.delete_connector, name='connectors.api.delete_connector'),
  url(r'^api/instance/update/?$', api.update_connector, name='connectors.api.update_connector'),
]
