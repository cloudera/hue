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

import logging

from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.translation import ugettext as _

from filebrowser.views import location_to_url

from jobbrowser.conf import DISABLE_KILLING_JOBS


LOG = logging.getLogger(__name__)


def can_view_job(username, job):
  acl = get_acls(job).get('mapreduce.job.acl-view-job', '')
  return acl == '*' or username in acl.split(',')

def can_modify_job(username, job):
  acl = get_acls(job).get('mapreduce.job.acl-modify-job', '')
  return acl == '*' or username in acl.split(',')

def get_acls(job):
  if job.is_mr2:
    return job.acls
  else:
    return job.full_job_conf

def can_kill_job(self, user):
  if DISABLE_KILLING_JOBS.get():
    return False

  if self.status.lower() not in ('running', 'pending', 'accepted'):
    return False

  if user.is_superuser:
    return True

  if can_modify_job(user.username, self):
    return True

  return user.username == self.user
