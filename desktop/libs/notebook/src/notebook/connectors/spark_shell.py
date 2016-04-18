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
import re
import time

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import RestException
from desktop.models import DefaultConfiguration

from notebook.data_export import download as spark_download
from notebook.connectors.base import Api, QueryError, SessionExpired, _get_snippet_session


LOG = logging.getLogger(__name__)


try:
  from spark.conf import LIVY_SERVER_SESSION_KIND
  from spark.job_server_api import get_api as get_spark_api
except ImportError, e:
  LOG.exception('Spark is not enabled')


class SparkConfiguration(object):

  APP_NAME = 'spark'

  PROPERTIES = [
    {
      "name": "jars",
      "nice_name": _("Jars"),
      "help_text": _("Add one or more JAR files to the list of resources."),
      "type": "csv-hdfs-files",
      "is_yarn": False,
      "multiple": True,
      "value": [],
    }, {
      "name": "files",
      "nice_name": _("Files"),
      "help_text": _("Files to be placed in the working directory of each executor."),
      "type": "csv-hdfs-files",
      "is_yarn": False,
      "multiple": True,
      "value": [],
    }, {
      "name": "pyFiles",
      "nice_name": _("pyFiles"),
      "help_text": _("Python files to be placed in the working directory of each executor."),
      "type": "csv-hdfs-files",
      "is_yarn": False,
      "multiple": True,
      "value": [],
    }, {
      "name": "driverMemory",
      "nice_name": _("Driver Memory"),
      "help_text": _("Amount of memory to use for the driver process in GB. (Default: 1). "),
      "type": "jvm",
      "is_yarn": False,
      "multiple": False,
      "value": '1',
    }, {
      "name": "totalExecutorCores",
      "nice_name": _("Total Executor Cores"),
      "help_text": _("number of cluster cores used by executor, only in standalone mode (Default: 1))"),
      "type": "number",
      "is_yarn": False,
      "multiple": False,
      "value": '1',
    },
    # YARN-only properties
    {
      "name": "driverCores",
      "nice_name": _("Driver Cores"),
      "help_text": _("Number of cores used by the driver, only in cluster mode (Default: 1)"),
      "type": "number",
      "is_yarn": True,
      "multiple": False,
      "value": '1',
    }, {
      "name": "numExecutors",
      "nice_name": _("Executors Number"),
      "help_text": _("Number of executors to launch, only in cluster mode (Default: 2)"),
      "type": "number",
      "is_yarn": True,
      "multiple": False,
      "value": '2',
    }, {
      "name": "executorMemory",
      "nice_name": _("Executor Memory"),
      "help_text": _("Amount of memory to use per executor process in GB. (Default: 1)"),
      "type": "jvm",
      "is_yarn": True,
      "multiple": False,
      "value": '1',
    }, {
      "name": "executorCores",
      "nice_name": _("Executor Cores"),
      "help_text": _("Number of cores used by the driver, only in cluster mode (Default: 1)"),
      "type": "number",
      "is_yarn": True,
      "multiple": False,
      "value": '1',
    }, {
      "name": "queue",
      "nice_name": _("Queue"),
      "help_text": _("The YARN queue to submit to, only in cluster mode (Default: default)"),
      "type": "string",
      "is_yarn": True,
      "multiple": False,
      "value": 'default',
    }, {
      "name": "archives",
      "nice_name": _("Archives"),
      "help_text": _("Archives to be extracted into the working directory of each executor, only in cluster mode."),
      "type": "csv-hdfs-files",
      "is_yarn": True,
      "multiple": True,
      "value": [],
    }
  ]


class SparkApi(Api):

  SPARK_UI_RE = re.compile("Started SparkUI at (http[s]?://([0-9a-zA-Z-_\.]+):(\d+))")
  YARN_JOB_RE = re.compile("tracking URL: (http[s]?://.+/)")
  STANDALONE_JOB_RE = re.compile("Got job (\d+)")

  @staticmethod
  def get_properties():
    return SparkConfiguration.PROPERTIES

  def create_session(self, lang='scala', properties=None):
    if not properties:
      config = DefaultConfiguration.objects.get_configuration_for_user(app='spark', user=self.user)
      if config is not None:
        properties = config.properties_list
      else:
        properties = self.get_properties()

    props = dict([(p['name'], p['value']) for p in properties]) if properties is not None else {}

    props['kind'] = lang

    api = get_spark_api(self.user)

    response = api.create_session(**props)

    status = api.get_session(response['id'])
    count = 0

    while status['state'] == 'starting' and count < 120:
      status = api.get_session(response['id'])
      count += 1
      time.sleep(1)

    if status['state'] != 'idle':
      info = '\n'.join(status['log']) if status['log'] else 'timeout'
      raise QueryError(_('The Spark session could not be created in the cluster: %s') % info)

    return {
        'type': lang,
        'id': response['id'],
        'properties': properties
    }

  def execute(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)

    try:
      response = api.submit_statement(session['id'], snippet['statement'])
      return {
          'id': response['id'],
          'has_result_set': True,
      }
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message or 'connection refused' in message or 'session is in state busy' in message:
        raise SessionExpired(e)
      else:
        raise e

  def check_status(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
      return {
          'status': response['state'],
      }
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

  def fetch_result(self, notebook, snippet, rows, start_over):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
    except Exception, e:
      message = force_unicode(str(e)).lower()
      if 'session not found' in message:
        raise SessionExpired(e)
      else:
        raise e

    content = response['output']

    if content['status'] == 'ok':
      data = content['data']
      images = []

      try:
        table = data['application/vnd.livy.table.v1+json']
      except KeyError:
        try:
          images = [data['image/png']]
        except KeyError:
          images = []
        data = [[data['text/plain']]]
        meta = [{'name': 'Header', 'type': 'STRING_TYPE', 'comment': ''}]
        type = 'text'
      else:
        data = table['data']
        headers = table['headers']
        meta = [{'name': h['name'], 'type': h['type'], 'comment': ''} for h in headers]
        type = 'table'

      # Non start_over not supported
      if not start_over:
        data = []

      return {
          'data': data,
          'images': images,
          'meta': meta,
          'type': type
      }
    elif content['status'] == 'error':
      tb = content.get('traceback', None)

      if tb is None:
        msg = content.get('ename', 'unknown error')

        evalue = content.get('evalue')
        if evalue is not None:
          msg = '%s: %s' % (msg, evalue)
      else:
        msg = ''.join(tb)

      raise QueryError(msg)

  def download(self, notebook, snippet, format):
    try:
      api = get_spark_api(self.user)
      session = _get_snippet_session(notebook, snippet)
      cell = snippet['result']['handle']['id']

      return spark_download(api, session['id'], cell, format)
    except Exception, e:
      raise PopupException(e)

  def cancel(self, notebook, snippet):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)
    response = api.cancel(session['id'])

    return {'status': 0}

  def get_log(self, notebook, snippet, startFrom=0, size=None):
    api = get_spark_api(self.user)
    session = _get_snippet_session(notebook, snippet)

    return api.get_log(session['id'], startFrom=startFrom, size=size)

  def progress(self, snippet, logs):
    return 50

  def close_statement(self, snippet): # Individual statements cannot be closed
    pass

  def close_session(self, session):
    api = get_spark_api(self.user)

    if session['id'] is not None:
      try:
        api.close(session['id'])
        return {
          'session': session['id'],
          'status': 0
        }
      except RestException, e:
        if e.code == 404 or e.code == 500: # TODO remove the 500
          raise SessionExpired(e)
    else:
      return {'status': -1}

  def get_jobs(self, notebook, snippet, logs):
    if self._is_yarn_mode():
      # Tracking URL is found at the start of the logs
      start_logs = self.get_log(notebook, snippet, startFrom=0, size=100)
      return self._get_yarn_jobs(start_logs)
    else:
      return self._get_standalone_jobs(logs)

  def _get_standalone_jobs(self, logs):
    job_ids = set([])

    # Attempt to find Spark UI Host and Port from startup logs
    spark_ui_url = self.SPARK_UI_RE.search(logs)

    if not spark_ui_url:
      LOG.warn('Could not find the Spark UI URL in the session logs.')
      return []
    else:
      spark_ui_url = spark_ui_url.group(1)

    # Standalone/Local mode runs on same host as Livy, attempt to find Job IDs in Spark log
    for match in self.STANDALONE_JOB_RE.finditer(logs):
      job_id = match.group(1)
      job_ids.add(job_id)

    jobs = [{
      'name': job_id,
      'url': '%s/jobs/job/?id=%s' % (spark_ui_url, job_id)
    } for job_id in job_ids]

    return jobs

  def _get_yarn_jobs(self, logs):
    tracking_urls = set([])

    # YARN mode only outputs the tracking-proxy URL, not Job IDs
    for match in self.YARN_JOB_RE.finditer(logs):
      url = match.group(1)
      tracking_urls.add(url)

    jobs = [{
      'name': url.strip('/').split('/')[-1],  # application_id is the last token
      'url': url
    } for url in tracking_urls]

    return jobs

  def _is_yarn_mode(self):
    return LIVY_SERVER_SESSION_KIND.get() == "yarn"
