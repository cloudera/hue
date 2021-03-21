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

from desktop.lib.scheduler import api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path


urlpatterns = [
  re_path(r'^api/schedule/new/?$', api.get_schedule, name='scheduler.api.new_schedule'),
  re_path(r'^api/schedule/edit/?$', api.get_schedule, name='scheduler.api.edit_schedule'),
  re_path(r'^api/schedule/submit/(?P<doc_id>[-\w]+)?$', api.submit_schedule, name='scheduler.api.submit_schedule'),
  re_path(r'^api/schedule/list/?$', api.list_schedules, name='scheduler.api.list_schedules'),
]
