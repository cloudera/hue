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

import datetime
import logging
import functools
import re

from django.urls import reverse
from desktop.conf import REST_CONN_TIMEOUT
from desktop.lib.view_util import format_duration_in_millis
from desktop.lib import i18n
from django.utils.html import escape
from django.utils.translation import ugettext as _

from desktop.lib.view_util import location_to_url

from jobbrowser.conf import DISABLE_KILLING_JOBS
from desktop.auth.backend import is_admin


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

  if is_admin(user):
    return True

  if can_modify_job(user.username, self):
    return True

  return user.username == self.user


class LinkJobLogs(object):

  @classmethod
  def _make_hdfs_links(cls, log, is_embeddable=False):
    escaped_logs = escape(log)
    return re.sub('((?<= |;)/|hdfs://)[^ <&\t;,\n]+', functools.partial(LinkJobLogs._replace_hdfs_link, is_embeddable), escaped_logs)

  @classmethod
  def _make_mr_links(cls, log):
    escaped_logs = escape(log)
    return re.sub('(job_[0-9]{12,}_[0-9]+)', LinkJobLogs._replace_mr_link, escaped_logs)

  @classmethod
  def _make_links(cls, log, is_embeddable=False):
    escaped_logs = escape(log)
    hdfs_links = re.sub('((?<= |;)/|hdfs://)[^ <&\t;,\n]+', functools.partial(LinkJobLogs._replace_hdfs_link, is_embeddable), escaped_logs)
    return re.sub('(job_[0-9]{12,}_[0-9]+)', LinkJobLogs._replace_mr_link, hdfs_links)

  @classmethod
  def _replace_hdfs_link(self, is_embeddable=False, match=None):
    try:
      return '<a href="%s">%s</a>' % (location_to_url(match.group(0), strict=False, is_embeddable=is_embeddable), match.group(0))
    except:
      LOG.exception('failed to replace hdfs links: %s' % (match.groups(),))
      return match.group(0)

  @classmethod
  def _replace_mr_link(self, match):
    try:
      return '<a href="/hue%s">%s</a>' % (reverse('jobbrowser.views.single_job', kwargs={'job': match.group(0)}), match.group(0))
    except:
      LOG.exception('failed to replace mr links: %s' % (match.groups(),))
      return match.group(0)


def format_unixtime_ms(unixtime):
  """
  Format a unix timestamp in ms to a human readable string
  """
  if unixtime:
    return str(datetime.datetime.fromtimestamp(unixtime/1000).strftime("%x %X %Z"))
  else:
    return ""
