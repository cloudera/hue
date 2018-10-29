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

from django.utils.translation import ugettext as _

from notebook.connectors.altus import _exec


LOG = logging.getLogger(__name__)


class WorkfloadAnalyticsClient():

  def __init__(self, user):
    self.user = user

  def get_impala_query(self, cluster, query_id):
    return WorkloadAnalytics(self.user).get_impala_query(cluster=cluster, query_id=query_id)

  def list_uploads(self):
    return WorkloadAnalytics(self.user).list_uploads()

  def list_environments(self):
    return WorkloadAnalytics(self.user).list_environments()

  def get_operation_execution_details(self, operation_id):
    return WorkloadAnalytics(self.user).get_operation_execution_details(operation_id=operation_id, include_tree=True)

  def get_mr_task_attempt_log(self, operation_execution_id, attempt_id):
    return WorkloadAnalytics(self.user).get_mr_task_attempt_log(operation_execution_id=operation_execution_id, attempt_id=attempt_id)



class WorkloadAnalytics():

  def __init__(self, user): pass

  def get_impala_query(self, cluster, query_id):
    parameters = {'clusterId': cluster.get('id'), 'queryId': query_id}

    return _exec('wa', 'getImpalaQuery', parameters=parameters)


  def list_uploads(self):
    return _exec('wa', 'listUploads')


  def list_environments(self):
    return _exec('wa', 'listEnvironments')


  def get_operation_execution_details(self, operation_id, include_tree=False):
    parameters = {'id': operation_id}

    if include_tree:
      parameters['includeTree'] = ''

    return _exec('wa', 'getOperationExecutionDetails', parameters=parameters)


  def get_mr_task_attempt_log(self, operation_execution_id, attempt_id):
    parameters = {'operationExecutionId': operation_execution_id, 'attemptId': attempt_id}

    return _exec('wa', 'getMrTaskAttemptLog', parameters=parameters)
