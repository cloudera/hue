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

  # Manipulations of job designs:
  url(r'^list/$', 'views.list_designs', name="jobsub.list"),
  url(r'^delete/(?P<id>\d+)$', 'views.delete_design', name="jobsub.delete"),
  url(r'^edit/(?P<id>\d+)$', 'views.edit_design', name="jobsub.edit"),
  url(r'^clone/(?P<id>\d+)$', 'views.clone_design', name="jobsub.clone"),
  url(r'^new/(?P<type>[a-zA-Z]+)$', 'views.edit_design', name="jobsub.new"),
  url(r'^submit/(?P<id>\d+)$', 'views.submit_design', name="jobsub.submit"),

  # Submitted jobs
  url(r'^watch/$', 'views.watch'),
  url(r'^watch/(?P<id>\d+)$', 'views.watch_submission'),

  # Status Bar (typically invoked by /status_bar, not /jobsub/status_bar)
  url(r'^status_bar/$', 'views.status_bar'),

  # Setup
  url(r'^setup/$', 'views.setup'),
)
