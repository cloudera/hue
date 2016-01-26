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

# Navigator API
urlpatterns = patterns('metadata.navigator_api',
  url(r'^api/navigator/find_entity/?$', 'find_entity', name='find_entity'),
  url(r'^api/navigator/get_entity/?$', 'get_entity', name='get_entity'),
  url(r'^api/navigator/add_tags/?$', 'add_tags', name='add_tags'),
  url(r'^api/navigator/delete_tags/?$', 'delete_tags', name='delete_tags'),
  url(r'^api/navigator/update_properties/?$', 'update_properties', name='update_properties'),
  url(r'^api/navigator/delete_properties/?$', 'delete_properties', name='delete_properties'),
)


# Optimizer API
urlpatterns = patterns('metadata.optimizer_api',
  url(r'^api/optimizer_api/top_tables/?$', 'top_tables', name='top_tables'),
  url(r'^api/optimizer_api/table_details/?$', 'table_details', name='table_details'),
  url(r'^api/optimizer_api/upload_history/?$', 'upload_history', name='upload_history'),
)
