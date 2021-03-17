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

from jobbrowser import views as jobbrowser_views
from jobbrowser import api2 as jobbrowser_api2

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  # "Default"
  re_path(r'^$', jobbrowser_views.jobs),
  re_path(r'^jobs/?$', jobbrowser_views.jobs, name='jobs'),
  re_path(r'^jobs/(?P<job>\w+)$', jobbrowser_views.single_job, name='jobbrowser.views.single_job'),
  re_path(r'^jobs/(?P<job>\w+)/counters$', jobbrowser_views.job_counters, name='job_counters'),
  re_path(r'^jobs/(?P<job>\w+)/kill$', jobbrowser_views.kill_job, name='kill_job'),
  re_path(r'^jobs/(?P<job>\w+)/single_logs$', jobbrowser_views.job_single_logs, name='jobbrowser.views.job_single_logs'),
  re_path(r'^jobs/(?P<job>\w+)/tasks$', jobbrowser_views.tasks, name='jobbrowser.views.tasks'),
  re_path(
    r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)$', jobbrowser_views.single_task, name='jobbrowser.views.single_task'
  ),                                                                                                                 # TODO s/single// ?
  re_path(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)/attempts/(?P<attemptid>\w+)$',
  jobbrowser_views.single_task_attempt, name='single_task_attempt'),
  re_path(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)/attempts/(?P<attemptid>\w+)/counters$',
  jobbrowser_views.task_attempt_counters, name='task_attempt_counters'),
  re_path(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)/attempts/(?P<attemptid>\w+)/logs$',
  jobbrowser_views.single_task_attempt_logs, name='single_task_attempt_logs'),
  re_path(r'^jobs/(\w+)/tasks/(\w+)/attempts/(?P<attemptid>\w+)/kill$', jobbrowser_views.kill_task_attempt, name='kill_task_attempt'),
  re_path(r'^trackers/(?P<trackerid>.+)$', jobbrowser_views.single_tracker, name='single_tracker'),
  re_path(
    r'^container/(?P<node_manager_http_address>.+)/(?P<containerid>.+)$', jobbrowser_views.container, name='jobbrowser.views.container'
  ),

  # MR2 specific
  re_path(r'^jobs/(?P<job>\w+)/job_attempt_logs/(?P<attempt_index>\d+)$', jobbrowser_views.job_attempt_logs, name='job_attempt_logs'),
  re_path(r'^jobs/(?P<job>\w+)/job_attempt_logs_json/(?P<attempt_index>\d+)(?:/(?P<name>\w+))?(?:/(?P<offset>[\d-]+))?/?$',
  jobbrowser_views.job_attempt_logs_json, name='job_attempt_logs_json'),
  re_path(r'^jobs/(?P<jobid>\w+)/job_not_assigned/(?P<path>.+)$', jobbrowser_views.job_not_assigned, name='job_not_assigned'),

  # Unused
  re_path(r'^jobs/(?P<job>\w+)/setpriority$', jobbrowser_views.set_job_priority, name='set_job_priority'),
  re_path(r'^trackers$', jobbrowser_views.trackers, name='trackers'),
  re_path(r'^clusterstatus$', jobbrowser_views.clusterstatus, name='clusterstatus'),
  re_path(r'^queues$', jobbrowser_views.queues, name='queues'),
  re_path(r'^jobbrowser$', jobbrowser_views.jobbrowser, name='jobbrowser'),
  re_path(r'^dock_jobs/?$', jobbrowser_views.dock_jobs, name='dock_jobs'),
]

# V2
urlpatterns += [
  re_path(r'apps$', jobbrowser_views.apps, name='jobbrowser.views.apps'),
]

urlpatterns += [
  re_path(r'api/jobs(?:/(?P<interface>.+))?/?', jobbrowser_api2.jobs, name='jobs'),
  re_path(r'api/job/logs', jobbrowser_api2.logs, name='logs'),
  re_path(r'api/job/profile', jobbrowser_api2.profile, name='profile'),
  re_path(r'api/job/action(?:/(?P<interface>.+))?(?:/(?P<action>.+))?/?', jobbrowser_api2.action, name='action'),
  re_path(r'api/job(?:/(?P<interface>.+))?/?', jobbrowser_api2.job, name='job'),
]

urlpatterns += [
  re_path(r'^query-store/data-bundle/(?P<id>.*)$', jobbrowser_api2.query_store_download_bundle),
  re_path(r'^query-store/(?P<path>.*)$', jobbrowser_api2.query_store_api),
]
