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
from jobsub import views as jobsub_views

urlpatterns = [
  # The base view is the "list" view, which we alias as /
  url(r'^$', jobsub_views.list_designs),

  # Not available on Hue 4
  url(r'^not_available$', jobsub_views.not_available),

  # Actions: get, save, clone, delete, submit, new.
  url(r'^designs$', jobsub_views.list_designs, name="jobsub.views.list_designs"),
  url(r'^designs/(?P<design_id>\d+)$', jobsub_views.get_design, name="jobsub.views.get_design"),
  url(r'^designs/(?P<node_type>\w+)/new$', jobsub_views.new_design, name="jobsub.views.new_design"),
  url(r'^designs/(?P<design_id>\d+)/save$', jobsub_views.save_design, name="jobsub.views.save_design"),
  url(r'^designs/(?P<design_id>\d+)/clone$', jobsub_views.clone_design, name="jobsub.views.clone_design"),
  url(r'^designs/(?P<design_id>\d+)/delete$', jobsub_views.delete_design, name="jobsub.views.delete_design"),
  url(r'^designs/(?P<design_id>\d+)/restore$', jobsub_views.restore_design, name="jobsub.views.restore_design"),
]
