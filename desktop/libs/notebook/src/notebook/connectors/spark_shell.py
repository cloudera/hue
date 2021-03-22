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

from builtins import range, object
import logging
import re
import sys
import time

from desktop.conf import USE_DEFAULT_CONFIGURATION
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode
from desktop.lib.rest.http_client import RestException
from desktop.models import DefaultConfiguration

from notebook.data_export import download as spark_download
from notebook.connectors.base import Api, QueryError, SessionExpired, _get_snippet_session

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


try:
  from spark.conf import LIVY_SERVER_SESSION_KIND
  from spark.livy_client import get_api as get_spark_api
except ImportError as e:
  LOG.exception('Spark is not enabled')


class SparkApi(Api):

  SPARK_UI_RE = re.compile("Started SparkUI at (http[s]?://([0-9a-zA-Z-_\.]+):(\d+))")
  YARN_JOB_RE = re.compile("tracking URL: (http[s]?://.+/)")
  STANDALONE_JOB_RE = re.compile("Got job (\d+)")

  def __init__(self, user, interpreter):
    super(SparkApi, self).__init__(user=user, interpreter=interpreter)

  def get_api(self):
    return get_spark_api(self.user, self.interpreter)

  @staticmethod
  def get_livy_props(lang, properties=None):
    props = dict([(p['name'], p['value']) for p in SparkConfiguration.PROPERTIES])
    if properties is not None:
      props.update(dict([(p['name'], p['value']) for p in properties]))

    # HUE-4761: Hue's session request is causing Livy to fail with "JsonMappingException: Can not deserialize
    # instance of scala.collection.immutable.List out of VALUE_STRING token" due to List type values
    # not being formed properly, they are quoted csv strings (without brackets) instead of proper List
    # types, this is for keys; archives, jars, files and pyFiles. The Mako frontend probably should be
    # modified to pass the values as Livy expects but for now we coerce these types to be Lists.
    # Issue only occurs when non-default values are used because the default path properly sets the
    # empty list '[]' for these four values.
    # Note also that Livy has a 90 second timeout for the session request to complete, this needs to
    # be increased for requests that take longer, for example when loading large archives.
    for key in ['archives', 'jars', 'files', 'pyFiles']:
      if key not in props:
        continue
      if type(props[key]) is list:
        continue
      LOG.debug("Check List type: {} was not a list".format(key))
      _tmp = props[key]
      props[key] = _tmp.split(",")

    # Convert the conf list to a dict for Livy
    LOG.debug("Property Spark Conf kvp list from UI is: " + str(props['conf']))
    props['conf'] = {conf.get('key'): conf.get('value') for i, conf in enumerate(props['conf'])}
    LOG.debug("Property Spark Conf dictionary is: " + str(props['conf']))

    props['kind'] = 'sql' if lang == 'sparksql' else lang

    return props

  @staticmethod
  def to_properties(props=None):
    properties = list()
    for p in SparkConfiguration.PROPERTIES:
      properties.append(p.copy())

    if props is not None:
      for p in properties:
        if p['name'] in props:
          p['value'] = props[p['name']]

    return properties

  def create_session(self, lang='scala', properties=None):
    if not properties and USE_DEFAULT_CONFIGURATION.get():
      user_config = DefaultConfiguration.objects.get_configuration_for_user(app='spark', user=self.user)
      if user_config is not None:
        properties = user_config.properties_list

    props = self.get_livy_props(lang, properties)

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
      raise QueryError(_('The Spark session is %s and could not be created in the cluster: %s') % (status['state'], info))

    return {
        'type': lang,
        'id': response['id'],
        'properties': self.to_properties(props)
    }

  def execute(self, notebook, snippet):
    api = self.get_api()
    session = _get_snippet_session(notebook, snippet)

    try:
      response = api.submit_statement(session['id'], snippet['statement'])
      return {
          'id': response['id'],
          'has_result_set': True,
          'sync': False
      }
    except Exception as e:
      message = force_unicode(str(e)).lower()
      if re.search("session ('\d+' )?not found", message) or 'connection refused' in message or 'session is in state busy' in message:
        raise SessionExpired(e)
      else:
        raise e

  def check_status(self, notebook, snippet):
    api = self.get_api()
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
      return {
          'status': response['state'],
      }
    except Exception as e:
      message = force_unicode(str(e)).lower()
      if re.search("session ('\d+' )?not found", message):
        raise SessionExpired(e)
      else:
        raise e

  def fetch_result(self, notebook, snippet, rows, start_over):
    api = self.get_api()
    session = _get_snippet_session(notebook, snippet)
    cell = snippet['result']['handle']['id']

    try:
      response = api.fetch_data(session['id'], cell)
    except Exception as e:
      message = force_unicode(str(e)).lower()
      if re.search("session ('\d+' )?not found", message):
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
        if 'application/json' in data:
          result = data['application/json']
          data = result['data']
          meta = [{'name': field['name'], 'type': field['type'], 'comment': ''} for field in result['schema']['fields']]
          type = 'table'
        else:
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

      if tb is None or not tb:
        msg = content.get('ename', 'unknown error')

        evalue = content.get('evalue')
        if evalue is not None:
          msg = '%s: %s' % (msg, evalue)
      else:
        msg = ''.join(tb)

      raise QueryError(msg)

  def cancel(self, notebook, snippet):
    api = self.get_api()
    session = _get_snippet_session(notebook, snippet)
    response = api.cancel(session['id'])

    return {'status': 0}

  def get_log(self, notebook, snippet, startFrom=0, size=None):
    api = self.get_api()
    session = _get_snippet_session(notebook, snippet)

    return api.get_log(session['id'], startFrom=startFrom, size=size)

  def close_statement(self, notebook, snippet): # Individual statements cannot be closed
    pass

  def close_session(self, session):
    api = self.get_api()

    if session['id'] is not None:
      try:
        api.close(session['id'])
        return {
          'session': session['id'],
          'status': 0
        }
      except RestException as e:
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

  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None, operation=None):
    response = {}

    # As booting a new SQL session is slow and we don't send the id of the current one in /autocomplete
    # we could implement this by introducing an API cache per user similarly to SqlAlchemy.

    return response

  def get_sample_data(self, snippet, database=None, table=None, column=None, is_async=False, operation=None):
    if operation != 'hello':
      raise NotImplementedError()

    response = {}

    api = self.get_api()

    api.get_status()

    response['status'] = 0
    response['rows'] = []

    return response

  def _get_standalone_jobs(self, logs):
    job_ids = set([])

    # Attempt to find Spark UI Host and Port from startup logs
    spark_ui_url = self.SPARK_UI_RE.search(logs)

    if not spark_ui_url:
      LOG.warning('Could not find the Spark UI URL in the session logs.')
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


class SparkConfiguration(object):

  APP_NAME = 'spark'

  PROPERTIES = [
    {
      "name": "conf",
      "nice_name": _("Spark Conf"),
      "help_text": _("Add one or more Spark conf properties to the session."),
      "type": "settings",
      "is_yarn": False,
      "multiple": True,
      "defaultValue": [],
      "value": [],
    },
    {
      "name": "jars",
      "nice_name": _("Jars"),
      "help_text": _("Add one or more JAR files to the list of resources."),
      "type": "csv-hdfs-files",
      "is_yarn": False,
      "multiple": True,
      "defaultValue": [],
      "value": [],
    }, {
      "name": "files",
      "nice_name": _("Files"),
      "help_text": _("Files to be placed in the working directory of each executor."),
      "type": "csv-hdfs-files",
      "is_yarn": False,
      "multiple": True,
      "defaultValue": [],
      "value": [],
    }, {
      "name": "pyFiles",
      "nice_name": _("pyFiles"),
      "help_text": _("Python files to be placed in the working directory of each executor."),
      "type": "csv-hdfs-files",
      "is_yarn": False,
      "multiple": True,
      "defaultValue": [],
      "value": [],
    }, {
      "name": "driverMemory",
      "nice_name": _("Driver Memory"),
      "help_text": _("Amount of memory to use for the driver process in GB. (Default: 1). "),
      "type": "jvm",
      "is_yarn": False,
      "multiple": False,
      "defaultValue": '1G',
      "value": '1G',
    },
    # YARN-only properties
    {
      "name": "driverCores",
      "nice_name": _("Driver Cores"),
      "help_text": _("Number of cores used by the driver, only in cluster mode (Default: 1)"),
      "type": "number",
      "is_yarn": True,
      "multiple": False,
      "defaultValue": 1,
      "value": 1,
    }, {
      "name": "executorMemory",
      "nice_name": _("Executor Memory"),
      "help_text": _("Amount of memory to use per executor process in GB. (Default: 1)"),
      "type": "jvm",
      "is_yarn": True,
      "multiple": False,
      "defaultValue": '1G',
      "value": '1G',
    }, {
      "name": "executorCores",
      "nice_name": _("Executor Cores"),
      "help_text": _("Number of cores used by the driver, only in cluster mode (Default: 1)"),
      "type": "number",
      "is_yarn": True,
      "multiple": False,
      "defaultValue": 1,
      "value": 1,
    }, {
      "name": "queue",
      "nice_name": _("Queue"),
      "help_text": _("The YARN queue to submit to, only in cluster mode (Default: default)"),
      "type": "string",
      "is_yarn": True,
      "multiple": False,
      "defaultValue": 'default',
      "value": 'default',
    }, {
      "name": "archives",
      "nice_name": _("Archives"),
      "help_text": _("Archives to be extracted into the working directory of each executor, only in cluster mode."),
      "type": "csv-hdfs-files",
      "is_yarn": True,
      "multiple": True,
      "defaultValue": [],
      "value": [],
    }
  ]
