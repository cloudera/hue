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

from desktop.lib.connectors import views, api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path


urlpatterns = [
  re_path(r'^$', views.index, name='desktop.lib.connectors.views.index'),

  re_path(r'^api/types/?$', api.get_connector_types, name='connectors.api.get_connector_types'),
  re_path(r'^api/instances/?$', api.get_connectors_instances, name='connectors.api.get_connectors_instances'),

  re_path(r'^api/instance/new/(?P<dialect>[\w\-]+)/(?P<interface>[\w\-]+)$', api.new_connector, name='connectors.api.new_connector'),
  re_path(r'^api/instance/get/(?P<id>\d+)$', api.get_connector, name='connectors.api.get_connector'),
  re_path(r'^api/instance/delete/?$', api.delete_connector, name='connectors.api.delete_connector'),
  re_path(r'^api/instance/update/?$', api.update_connector, name='connectors.api.update_connector'),
  re_path(r'^api/instance/test/?$', api.test_connector, name='connectors.api.test_connector'),

  re_path(r'^api/examples/install/?$', api.install_connector_examples, name='connectors.api.install_connector_examples'),
]
