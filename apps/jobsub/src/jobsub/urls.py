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

urlpatterns = patterns(
  'jobsub.views',

  # The base view is the "list" view, which we alias as /
  url(r'^$', 'list_designs'),

  # Actions: get, save, clone, delete, submit, new.
  url(r'^designs$', 'list_designs'),
  url(r'^designs/(?P<design_id>\d+)$', 'get_design'),
  url(r'^designs/(?P<node_type>\w+)/new$', 'new_design'),
  url(r'^designs/(?P<design_id>\d+)/save$', 'save_design'),
  url(r'^designs/(?P<design_id>\d+)/clone$', 'clone_design'),
  url(r'^designs/(?P<design_id>\d+)/delete$', 'delete_design'),
  url(r'^designs/(?P<design_id>\d+)/restore$', 'restore_design'),

  # Jasmine - Skip until rewritten
  url(r'^jasmine', 'jasmine'),
)
