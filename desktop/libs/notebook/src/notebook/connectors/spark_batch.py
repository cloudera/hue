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


LOG = logging.getLogger(__name__)


try:
  from spark.job_server_api import get_api as get_spark_api
except ImportError, e:
  LOG.exception('Spark is not enabled')

from notebook.connectors.base import Api


class SparkBatchApi(Api):

  def execute(self, notebook, snippet):
    api = get_spark_api(self.user)
    if snippet['type'] == 'jar':
        properties = {
            'file': snippet['properties'].get('app_jar'),
            'className': snippet['properties'].get('class'),
            'args': snippet['properties'].get('arguments'),
        }
    elif snippet['type'] == 'py':
        properties = {
            'file': snippet['properties'].get('py_file'),
            'args': snippet['properties'].get('argument', []),
        }
    else:
        properties = {
            'file': snippet['properties'].get('app_jar'),
            'className': snippet['properties'].get('class'),
            'args': snippet['properties'].get('arguments'),
            'pyFiles': snippet['properties'].get('py_file'),
            'files': snippet['properties'].get('files'),
            # driverMemory
            # driverCores
            # executorMemory
            # executorCores
            # archives
        }

    response = api.submit_batch(properties)
    return {
        'id': response['id'],
        'has_result_set': True,
        'properties': []
    }

  def check_status(self, notebook, snippet):
    api = get_spark_api(self.user)

    state = api.get_batch_status(snippet['result']['handle']['id'])
    return {
        'status': state,
    }

  def get_log(self, notebook, snippet, startFrom=0, size=None):
    api = get_spark_api(self.user)

    return api.get_batch_log(snippet['result']['handle']['id'], startFrom=startFrom, size=size)

  def close_statement(self, notebook, snippet):
    api = get_spark_api(self.user)

    session_id = snippet['result']['handle']['id']
    if session_id is not None:
      api.close_batch(session_id)
      return {
        'session': session_id,
        'status': 0
      }
    else:
      return {'status': -1}  # skipped

  def cancel(self, notebook, snippet):
    # Batch jobs do not support interruption, so close statement instead.
    return self.close_statement(snippet)
