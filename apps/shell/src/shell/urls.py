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

urlpatterns = patterns('shell',
  url(r'^$', 'views.index'),
  url(r'^process_command/?$', 'views.process_command'),
  url(r'^restore_shell/?$', 'views.restore_shell'),
  url(r'^kill_shell/?$', 'views.kill_shell'),
  url(r'^create/?$', 'views.create'),
  url(r'^retrieve_output/?$', 'views.retrieve_output'),
  url(r'^add_to_output/?$', 'views.add_to_output'),
)
