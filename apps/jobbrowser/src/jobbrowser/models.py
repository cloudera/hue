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

from __future__ import division
from builtins import str
from builtins import object
import datetime
import logging
import math
import functools
import re

from django.db import connection, models
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import ugettext as _

from desktop.auth.backend import is_admin
from desktop.conf import REST_CONN_TIMEOUT
from desktop.lib import i18n
from desktop.lib.view_util import format_duration_in_millis, location_to_url

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
    try:
      acls = job.acls
    except:
      LOG.exception('failed to get acls')
      acls = {}
    return acls
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


# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

class HiveQuery(models.Model):
  # (mysql.E001) MySQL does not allow unique CharFields to have a max_length > 255.
  # query_id = models.CharField(unique=True, max_length=512, blank=True, null=True)
  id = models.IntegerField(unique=True, blank=True, null=False, primary_key=True)
  query_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
  query = models.TextField(blank=True, null=True)
  query_fts = models.TextField(blank=True, null=True)  # This field type is a guess.
  start_time = models.BigIntegerField(blank=True, null=True)
  end_time = models.BigIntegerField(blank=True, null=True)
  elapsed_time = models.BigIntegerField(blank=True, null=True)
  status = models.CharField(max_length=32, blank=True, null=True)
  queue_name = models.CharField(max_length=767, blank=True, null=True)
  user_id = models.CharField(max_length=256, blank=True, null=True)
  request_user = models.CharField(max_length=256, blank=True, null=True)
  cpu_time = models.BigIntegerField(blank=True, null=True)
  physical_memory = models.BigIntegerField(blank=True, null=True)
  virtual_memory = models.BigIntegerField(blank=True, null=True)
  data_read = models.BigIntegerField(blank=True, null=True)
  data_written = models.BigIntegerField(blank=True, null=True)
  operation_id = models.CharField(max_length=512, blank=True, null=True)
  client_ip_address = models.CharField(max_length=64, blank=True, null=True)
  hive_instance_address = models.CharField(max_length=512, blank=True, null=True)
  hive_instance_type = models.CharField(max_length=512, blank=True, null=True)
  session_id = models.CharField(max_length=512, blank=True, null=True)
  log_id = models.CharField(max_length=512, blank=True, null=True)
  thread_id = models.CharField(max_length=512, blank=True, null=True)
  execution_mode = models.CharField(max_length=16, blank=True, null=True)
  databases_used = models.TextField(blank=True, null=True)  # This field type is a guess.
  tables_read = models.TextField(blank=True, null=True)  # This field type is a guess.
  tables_written = models.TextField(blank=True, null=True)  # This field type is a guess.
  domain_id = models.CharField(max_length=512, blank=True, null=True)
  llap_app_id = models.CharField(max_length=512, blank=True, null=True)
  used_cbo = models.CharField(max_length=16, blank=True, null=True)
  first_task_started_time = models.BigIntegerField(blank=True, null=True)
  waiting_time = models.BigIntegerField(blank=True, null=True)
  resource_utilization = models.BigIntegerField(blank=True, null=True)
  version = models.SmallIntegerField(blank=True, null=True)
  created_at = models.DateTimeField(blank=True, null=True)

  class Meta:
    managed = False
    db_table = 'hive_query'


class QueryDetails(models.Model):
  hive_query = models.ForeignKey(HiveQuery, HiveQuery, unique=True, blank=True, null=True)
  explain_plan_raw = models.TextField(blank=True, null=True)  # This field type is a guess.
  configuration_raw = models.TextField(blank=True, null=True)  # This field type is a guess.
  perf = models.TextField(blank=True, null=True)  # This field type is a guess.
  configuration_compressed = models.BinaryField(blank=True, null=True)
  explain_plan_compressed = models.BinaryField(blank=True, null=True)

  class Meta:
    managed = False
    db_table = 'query_details'


class DagInfo(models.Model):
  # (mysql.E001) MySQL does not allow unique CharFields to have a max_length > 255.
  # dag_id = models.CharField(unique=True, max_length=512, blank=True, null=True)
  dag_id = models.CharField(unique=True, max_length=255, blank=True, null=True)
  dag_name = models.CharField(max_length=512, blank=True, null=True)
  application_id = models.CharField(max_length=512, blank=True, null=True)
  init_time = models.BigIntegerField(blank=True, null=True)
  start_time = models.BigIntegerField(blank=True, null=True)
  end_time = models.BigIntegerField(blank=True, null=True)
  time_taken = models.BigIntegerField(blank=True, null=True)
  status = models.CharField(max_length=64, blank=True, null=True)
  am_webservice_ver = models.CharField(max_length=16, blank=True, null=True)
  am_log_url = models.CharField(max_length=512, blank=True, null=True)
  queue_name = models.CharField(max_length=64, blank=True, null=True)
  caller_id = models.CharField(max_length=512, blank=True, null=True)
  caller_type = models.CharField(max_length=128, blank=True, null=True)
  hive_query = models.ForeignKey('HiveQuery', HiveQuery, blank=True, null=True)
  created_at = models.DateTimeField(blank=True, null=True)
  source_file = models.TextField(blank=True, null=True)

  class Meta:
    managed = False
    db_table = 'dag_info'


class DagDetails(models.Model):
  dag_info = models.ForeignKey('DagInfo', DagInfo, unique=True, blank=True, null=True)
  hive_query = models.ForeignKey('HiveQuery', HiveQuery, blank=True, null=True)
  dag_plan_raw = models.TextField(blank=True, null=True)  # This field type is a guess.
  vertex_name_id_mapping_raw = models.TextField(blank=True, null=True)  # This field type is a guess.
  diagnostics = models.TextField(blank=True, null=True)
  counters_raw = models.TextField(blank=True, null=True)  # This field type is a guess.
  dag_plan_compressed = models.BinaryField(blank=True, null=True)
  vertex_name_id_mapping_compressed = models.BinaryField(blank=True, null=True)
  counters_compressed = models.BinaryField(blank=True, null=True)

  class Meta:
    managed = False
    db_table = 'dag_details'


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
      return '<a href="/hue%s">%s</a>' % (reverse('jobbrowser:jobbrowser.views.single_job', kwargs={'job': match.group(0)}), match.group(0))
    except:
      LOG.exception('failed to replace mr links: %s' % (match.groups(),))
      return match.group(0)


def format_unixtime_ms(unixtime):
  """
  Format a unix timestamp in ms to a human readable string
  """
  if unixtime:
    return str(datetime.datetime.fromtimestamp(math.floor(unixtime / 1000)).strftime("%x %X %Z"))
  else:
    return ""
