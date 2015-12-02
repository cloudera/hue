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

from beeswax.server.dbms import QueryServerException
from beeswax.server.hive_server2_lib import HiveServerClient, HiveServerDataTable
from TCLIService.ttypes import TExecuteStatementReq, TFetchOrientation, TStatusCode

from ImpalaService import ImpalaHiveServer2Service


LOG = logging.getLogger(__name__)


class ImpalaServerClientException(Exception):
  pass


class ImpalaServerClient(HiveServerClient):

  def get_exec_summary(self, operation_handle, session_handle):
    """
    Calls Impala HS2 API's GetExecSummary method on the given query handle
    :return: TExecSummary object serialized as a dict
    """
    req = ImpalaHiveServer2Service.TGetExecSummaryReq(operationHandle=operation_handle, sessionHandle=session_handle)

    # GetExecSummary() only works for closed queries
    self.close_operation(operation_handle)

    resp = self.call(self._client.GetExecSummary, req)

    if resp.status is not None and resp.status.statusCode not in (TStatusCode.SUCCESS_STATUS,):
      if hasattr(resp.status, 'errorMessage') and resp.status.errorMessage:
        message = resp.status.errorMessage
      else:
        message = ''
      raise QueryServerException(Exception('Bad status for request %s:\n%s' % (req, resp)), message=message)

    return self._serialize_exec_summary(resp.summary)


  def _serialize_exec_summary(self, summary):
    try:
      summary_dict = {
        'state': summary.state,
        'exch_to_sender_map': summary.exch_to_sender_map,
        'error_logs': summary.error_logs,
        'status': None,
        'progress': None,
        'nodes': [],
      }

      if summary.status is not None:
        summary_dict['status'] = summary.status.__dict__

      if summary.progress is not None:
        summary_dict['progress'] = summary.progress.__dict__

      if summary.nodes:
        for node in summary.nodes:
          node_dict = node.__dict__

          if node.exec_stats is not None:
            node_dict['exec_stats'] = [stat.__dict__ for stat in node.exec_stats]

          if node.estimated_stats is not None:
            node_dict['estimated_stats'] = node.estimated_stats.__dict__

          summary_dict['nodes'].append(node_dict)

      return summary_dict
    except Exception, e:
      raise ImpalaServerClientException('Failed to serialize the TExecSummary object: %s' % str(e))
