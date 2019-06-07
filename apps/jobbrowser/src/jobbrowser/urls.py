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

from jobbrowser import views as jobbrowser_views
from jobbrowser import api2 as jobbrowser_api2

urlpatterns = [
  # "Default"
  url(r'^$', jobbrowser_views.jobs),
  url(r'^jobs/?$', jobbrowser_views.jobs, name='jobs'),
  url(r'^jobs/(?P<job>\w+)$', jobbrowser_views.single_job, name='jobbrowser.views.single_job'),
  url(r'^jobs/(?P<job>\w+)/counters$', jobbrowser_views.job_counters, name='job_counters'),
  url(r'^jobs/(?P<job>\w+)/kill$', jobbrowser_views.kill_job, name='kill_job'),
  url(r'^jobs/(?P<job>\w+)/single_logs$', jobbrowser_views.job_single_logs, name='jobbrowser.views.job_single_logs'),
  url(r'^jobs/(?P<job>\w+)/tasks$', jobbrowser_views.tasks, name='jobbrowser.views.tasks'),
  url(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)$', jobbrowser_views.single_task, name='jobbrowser.views.single_task'), # TODO s/single// ?
  url(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)/attempts/(?P<attemptid>\w+)$', jobbrowser_views.single_task_attempt, name='single_task_attempt'),
  url(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)/attempts/(?P<attemptid>\w+)/counters$', jobbrowser_views.task_attempt_counters, name='task_attempt_counters'),
  url(r'^jobs/(?P<job>\w+)/tasks/(?P<taskid>\w+)/attempts/(?P<attemptid>\w+)/logs$', jobbrowser_views.single_task_attempt_logs, name='single_task_attempt_logs'),
  url(r'^jobs/(\w+)/tasks/(\w+)/attempts/(?P<attemptid>\w+)/kill$', jobbrowser_views.kill_task_attempt, name='kill_task_attempt'),
  url(r'^trackers/(?P<trackerid>.+)$', jobbrowser_views.single_tracker, name='single_tracker'),
  url(r'^container/(?P<node_manager_http_address>.+)/(?P<containerid>.+)$', jobbrowser_views.container, name='jobbrowser.views.container'),

  # MR2 specific
  url(r'^jobs/(?P<job>\w+)/job_attempt_logs/(?P<attempt_index>\d+)$', jobbrowser_views.job_attempt_logs, name='job_attempt_logs'),
  url(r'^jobs/(?P<job>\w+)/job_attempt_logs_json/(?P<attempt_index>\d+)(?:/(?P<name>\w+))?(?:/(?P<offset>[\d-]+))?/?$', jobbrowser_views.job_attempt_logs_json, name='job_attempt_logs_json'),
  url(r'^jobs/(?P<jobid>\w+)/job_not_assigned/(?P<path>.+)$', jobbrowser_views.job_not_assigned, name='job_not_assigned'),

  # Unused
  url(r'^jobs/(?P<job>\w+)/setpriority$', jobbrowser_views.set_job_priority, name='set_job_priority'),
  url(r'^trackers$', jobbrowser_views.trackers, name='trackers'),
  url(r'^clusterstatus$', jobbrowser_views.clusterstatus, name='clusterstatus'),
  url(r'^queues$', jobbrowser_views.queues, name='queues'),
  url(r'^jobbrowser$', jobbrowser_views.jobbrowser, name='jobbrowser'),
  url(r'^dock_jobs/?$', jobbrowser_views.dock_jobs, name='dock_jobs'),
]

# V2
urlpatterns += [
  url(r'apps$', jobbrowser_views.apps, name='jobbrowser.views.apps'),
]

urlpatterns += [
  url(r'api/jobs(?:/(?P<interface>.+))?/?', jobbrowser_api2.jobs, name='jobs'),
  url(r'api/job/logs', jobbrowser_api2.logs, name='logs'),
  url(r'api/job/profile', jobbrowser_api2.profile, name='profile'),
  url(r'api/job/action(?:/(?P<interface>.+))?(?:/(?P<action>.+))?/?', jobbrowser_api2.action, name='action'),
  url(r'api/job(?:/(?P<interface>.+))?/?', jobbrowser_api2.job, name='job'),
]
