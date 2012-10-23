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
  'jobsub',

  # The base view is the "list" view, which we alias as /
  url(r'^$', 'views.list_designs'),

  url(r'^list_designs$', 'views.list_designs'),
  url(r'^new_design/(?P<action_type>\w+)$', 'views.new_design'),
  url(r'^delete_design/(?P<design_id>\d+)$', 'views.delete_design'),
  url(r'^edit_design/(?P<design_id>\d+)$', 'views.edit_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', 'views.clone_design'),
  url(r'^submit_design/(?P<design_id>\d+)$', 'views.submit_design'),
  url(r'^design_parameters/(?P<design_id>\d+)$', 'views.get_design_params'),

  url(r'^job/(?P<jobid>[-\w]+)$', 'views.oozie_job'),
  url(r'^list_history$', 'views.list_history'),

  # Setup
  url(r'^setup/$', 'views.setup'),

  # Jasmine
  url(r'^jasmine', 'views.jasmine'),
)
