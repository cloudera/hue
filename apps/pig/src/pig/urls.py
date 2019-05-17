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
from pig import views as pig_views

urlpatterns = [
  url(r'^$', pig_views.app, name='index'),

  url(r'^app/?$', pig_views.app, name='app'),

  # Ajax
  url(r'^scripts/?$', pig_views.scripts, name='scripts'),
  url(r'^dashboard/?$', pig_views.dashboard, name='dashboard'),
  url(r'^save/?$', pig_views.save, name='save'),
  url(r'^run/?$', pig_views.run, name='run'),
  url(r'^copy/?$', pig_views.copy, name='copy'),
  url(r'^delete/?$', pig_views.delete, name='delete'),
  url(r'^watch/(?P<job_id>[-\w]+)$', pig_views.watch, name='watch'),
  url(r'^stop/?$', pig_views.stop, name='stop'),
  url(r'^install_examples$', pig_views.install_examples, name='install_examples'),
]
