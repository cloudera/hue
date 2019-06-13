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

import json
import logging
import posixpath
import threading
import urlparse

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource
from django.utils.translation import ugettext as _
from hadoop import cluster
from hadoop.yarn.clients import get_log_client

from lxml import html


LOG = logging.getLogger(__name__)

_API_VERSION = 'v1'
_JSON_CONTENT_TYPE = 'application/json'

API_CACHE = None
API_CACHE_LOCK = threading.Lock()


def get_history_server_api():
  # TODO: Spark History Server does not yet support setuser, implement when it does
  global API_CACHE

  if API_CACHE is None:
    API_CACHE_LOCK.acquire()
    try:
      if API_CACHE is None:
        yarn_cluster = cluster.get_cluster_conf_for_job_submission()
        if yarn_cluster is None:
          raise PopupException(_('No Spark History Server is available.'))
        API_CACHE = SparkHistoryServerApi(yarn_cluster.SPARK_HISTORY_SERVER_URL.get(), yarn_cluster.SPARK_HISTORY_SERVER_SECURITY_ENABLED.get(), yarn_cluster.SSL_CERT_CA_VERIFY.get())
    finally:
      API_CACHE_LOCK.release()

  return API_CACHE


class SparkHistoryServerApi(object):

  def __init__(self, spark_hs_url, security_enabled=False, ssl_cert_ca_verify=False):
    self._ui_url = spark_hs_url
    self._url = posixpath.join(spark_hs_url, 'api/%s/' % _API_VERSION)
    self._client = HttpClient(self._url, logger=LOG)
    self._root = Resource(self._client)
    self._security_enabled = security_enabled

    if self._security_enabled:
      self._client.set_kerberos_auth()

    self._client.set_verify(ssl_cert_ca_verify)

  def __str__(self):
    return "Spark History Server API at %s" % (self._url,)

  @property
  def url(self):
    return self._url

  @property
  def ui_url(self):
    return self._ui_url

  @property
  def headers(self):
    return {'Accept': _JSON_CONTENT_TYPE}

  def applications(self):
    return self._root.get('applications', headers=self.headers)

  def application(self, app_id):
    return self._root.get('applications/%(app_id)s' % {'app_id': app_id}, headers=self.headers)

  def jobs(self, app_id):
    return self._root.get('applications/%(app_id)s/jobs' % {'app_id': app_id}, headers=self.headers)

  def stages(self, app_id):
    return self._root.get('applications/%(app_id)s/stages' % {'app_id': app_id}, headers=self.headers)

  def executors(self, job):
    LOG.debug("Getting executors for Spark job %s" % job.jobId)
    app_id = self.get_real_app_id(job)
    if not app_id:
      return []

    return self._root.get('applications/%(app_id)s/executors' % {'app_id': app_id}, headers=self.headers)

  def stage_attempts(self, app_id, stage_id):
    return self._root.get('applications/%(app_id)s/stages/%(stage_id)s' % {'app_id': app_id, 'stage_id': stage_id}, headers=self.headers)

  def stage_attempt(self, app_id, stage_id, stage_attempt_id):
    return self._root.get('applications/%(app_id)s/stages/%(stage_id)s/%(stage_attempt_id)s' % {'app_id': app_id, 'stage_id': stage_id, 'stage_attempt_id': stage_attempt_id}, headers=self.headers)

  def task_summary(self, app_id, stage_id, stage_attempt_id):
    return self._root.get('applications/%(app_id)s/stages/%(stage_id)s/%(stage_attempt_id)s/taskSummary' % {'app_id': app_id, 'stage_id': stage_id, 'stage_attempt_id': stage_attempt_id}, headers=self.headers)

  def task_list(self, app_id, stage_id, stage_attempt_id):
    return self._root.get('applications/%(app_id)s/stages/%(stage_id)s/%(stage_attempt_id)s/taskList' % {'app_id': app_id, 'stage_id': stage_id, 'stage_attempt_id': stage_attempt_id}, headers=self.headers)

  def storages(self, app_id):
    return self._root.get('applications/%(app_id)s/storage/rdd' % {'app_id': app_id}, headers=self.headers)

  def storage(self, app_id, rdd_id):
    return self._root.get('applications/%(app_id)s/storage/rdd/%(rdd_id)s' % {'app_id': app_id, 'rdd_id': rdd_id}, headers=self.headers)

  def download_logs(self, app_id):
    return self._root.get('applications/%(app_id)s/logs' % {'app_id': app_id}, headers=self.headers)

  def download_attempt_logs(self, app_id, attempt_id):
    return self._root.get('applications/%(app_id)s/%(attempt_id)s/logs' % {'app_id': app_id, 'attempt_id': attempt_id}, headers=self.headers)

  def download_executors_logs(self, request, job, name, offset):
    log_links = self.get_executors_loglinks(job)

    return self.retrieve_log_content(log_links, name, request.user.username, offset)

  def download_executor_logs(self, user, executor, name, offset):
    return self.retrieve_log_content(executor['logs'], name, user.username, offset)

  def retrieve_log_content(self, log_links, log_name, username, offset):
    params = {
      'doAs': username
    }

    if offset != 0:
      params['start'] = offset

    if not log_name or not log_name == 'stderr':
      log_name = 'stdout'

    log = ''
    if log_links and log_name in log_links:
      log_link = log_links[log_name]

      root = Resource(get_log_client(log_link), urlparse.urlsplit(log_link)[2], urlencode=False)
      response = root.get('', params=params)
      log = html.fromstring(response, parser=html.HTMLParser()).xpath('/html/body/table/tbody/tr/td[2]')[0].text_content()
    return log

  def get_executors_loglinks(self, job):
    executor = None
    if job.metrics and 'executors' in job.metrics and job.metrics['executors']:
      executors = [executor for executor in job.metrics['executors'] if executor[0] == 'driver']  # look up driver executor
      if not executors:
        executor = job.metrics['executors'][0]
      else:
        executor = executors[0]

    return None if not executor else executor[12]

  def get_real_app_id(self, job):
    # https://spark.apache.org/docs/1.6.0/monitoring.html and https://spark.apache.org/docs/2.0.0/monitoring.html
    # When running on Yarn, each application has multiple attempts, so [app-id] is actually [app-id]/[attempt-id] in all cases.
    # When running job as cluster mode, an attempt number is part of application ID, but proxy URL can't be resolved to match
    # Spark history URL. In the applications list, each job's attampt list shows if attempt ID is used and how many attempts.

    try:
      jobs_json = self.applications()
      job_filtered_json = [x for x in jobs_json if x['id'] == job.jobId]

      if not job_filtered_json:
        return {}

      attempts = job_filtered_json[0]['attempts']

      if len(attempts) == 1:
        app_id = job.jobId if 'attemptId' not in attempts[0] else job.jobId + '/' + attempts[0]['attemptId']
      else:
        app_id = job.jobId + '/%d' % len(attempts)

      LOG.debug("Getting real spark app id %s for Spark job %s" % (app_id, job.jobId))
    except Exception as e:
      LOG.error('Cannot get real app id %s: %s' % (job.jobId, e))
      app_id = None

    return app_id
