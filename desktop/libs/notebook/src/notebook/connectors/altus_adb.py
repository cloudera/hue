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
import json
import urllib

from django.urls import reverse
from django.utils.translation import ugettext as _

from notebook.connectors.altus import AnalyticDbApi
from notebook.connectors.base import Api, QueryError


LOG = logging.getLogger(__name__)


RUNNING_STATES = ('QUEUED', 'RUNNING', 'SUBMITTING')


class AltusAdbApi(Api):

  def __init__(self, user, cluster_name, interpreter=None, request=None):
    Api.__init__(self, user, interpreter=interpreter, request=request)
    self.cluster_name = cluster_name


  def execute(self, notebook, snippet):
    statement = snippet['statement']

    return HueQuery(self.user, cluster_crn=self.cluster_name).do_execute(statement)


  def check_status(self, notebook, snippet):
    handle = snippet['result']['handle']

    return HueQuery(self.user, cluster_crn=self.cluster_name).do_check_status(handle)


  def fetch_result(self, notebook, snippet, rows, start_over):
    handle = snippet['result']['handle']

    return HueQuery(self.user, cluster_crn=self.cluster_name).do_fetch_result(handle)


  def close_statement(self, notebook, snippet):
    return {'status': -1}


  def cancel(self, notebook, snippet):
    return {'status': -1, 'message': _('Could not cancel.')}


  def get_log(self, notebook, snippet, startFrom=0, size=None):
    return '...'


  def get_jobs(self, notebook, snippet, logs):
    return []


  def autocomplete(self, snippet, database=None, table=None, column=None, nested=None):
    url_path = '/notebook/api/autocomplete'

    if database is not None:
      url_path = '%s/%s' % (url_path, database)
    if table is not None:
      url_path = '%s/%s' % (url_path, table)
    if column is not None:
      url_path = '%s/%s' % (url_path, column)
    if nested is not None:
      url_path = '%s/%s' % (url_path, nested)

    return HueQuery(self.user, cluster_crn=self.cluster_name).do_post(url_path=url_path)


class HueQuery():
  def __init__(self, user, cluster_crn):
    self.user = user
    self.cluster_crn = cluster_crn
    self.api = AnalyticDbApi(self.user)

  def do_post(self, url_path):
    payload = '''{"method":"POST","url":"https://localhost:8888''' + url_path +'''","httpVersion":"HTTP/1.1","headers":[{"name":"Accept-Encoding","value":"gzip, deflate, br"},{"name":"Content-Type","value":"application/x-www-form-urlencoded; charset=UTF-8"},{"name":"Accept","value":"*/*"},{"name":"X-Requested-With","value":"XMLHttpRequest"},{"name":"Connection","value":"keep-alive"}],"queryString":[],"postData": {
        "mimeType": "application/x-www-form-urlencoded; charset=UTF-8",
        "text": "snippet=%7B%22type%22%3A%22impala%22%2C%22source%22%3A%22data%22%7D",
        "params": [
          {
            "name": "snippet",
            "value": "%7B%22type%22%3A%22impala%22%2C%22source%22%3A%22data%22%7D"
          }
        ]
      }}'''

    resp = self.api.submit_hue_query(self.cluster_crn, payload)
    return json.loads(resp['payload'])

  def do_execute(self, query):
    payload = '''
            {
              "method": "POST",
              "url": "http://127.0.0.1:8000/notebook/api/execute/impala",
              "httpVersion": "HTTP/1.1",
              "headers": [
                {
                  "name": "Accept-Encoding",
                  "value": "gzip, deflate, br"
                },
                {
                  "name": "Content-Type",
                  "value": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                {
                  "name": "Accept",
                  "value": "*/*"
                },
                {
                  "name": "X-Requested-With",
                  "value": "XMLHttpRequest"
                },
                {
                  "name": "Connection",
                  "value": "keep-alive"
                }
              ],
              "queryString": [],
              "cookies": [
              ],
              "postData": {
                "mimeType": "application/x-www-form-urlencoded; charset=UTF-8",
                "text": "notebook=%7B%22uuid%22%3A%22f2b8a233-c34c-44b8-a8a1-0e6123996216%22%2C%22name%22%3A%22%22%2C%22description%22%3A%22%22%2C%22type%22%3A%22query-impala%22%2C%22initialType%22%3A%22impala%22%2C%22coordinatorUuid%22%3Anull%2C%22isHistory%22%3Atrue%2C%22isManaged%22%3Afalse%2C%22parentSavedQueryUuid%22%3Anull%2C%22isSaved%22%3Afalse%2C%22onSuccessUrl%22%3Anull%2C%22pubSubUrl%22%3Anull%2C%22isPresentationModeDefault%22%3Afalse%2C%22isPresentationMode%22%3Afalse%2C%22isPresentationModeInitialized%22%3Atrue%2C%22presentationSnippets%22%3A%7B%7D%2C%22isHidingCode%22%3Afalse%2C%22snippets%22%3A%5B%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22name%22%3A%22%22%2C%22type%22%3A%22impala%22%2C%22isBatchable%22%3Atrue%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22errors%22%3A%5B%5D%2C%22aceErrorsHolder%22%3A%5B%5D%2C%22aceWarningsHolder%22%3A%5B%5D%2C%22aceErrors%22%3A%5B%5D%2C%22aceWarnings%22%3A%5B%5D%2C%22editorMode%22%3Atrue%2C%22dbSelectionVisible%22%3Afalse%2C%22isSqlDialect%22%3Atrue%2C%22namespaceRefreshEnabled%22%3Afalse%2C%22availableNamespaces%22%3A%5B%5D%2C%22availableComputes%22%3A%5B%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute1%22%2C%22id%22%3A%22compute1%22%2C%22name%22%3A%22compute1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute2%22%2C%22id%22%3A%22compute2%22%2C%22name%22%3A%22compute2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22altus%22%2C%22namespace%22%3A%22Altus%22%2C%22id%22%3A%22Altus%22%2C%22name%22%3A%22Altus%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage1%22%2C%22id%22%3A%22storage1%22%2C%22name%22%3A%22storage1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage2%22%2C%22id%22%3A%22storage2%22%2C%22name%22%3A%22storage2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22Default%22%2C%22id%22%3A%22Default%22%2C%22name%22%3A%22default%22%7D%5D%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22database%22%3A%22default%22%2C%22currentQueryTab%22%3A%22queryHistory%22%2C%22pinnedContextTabs%22%3A%5B%5D%2C%22loadingQueries%22%3Afalse%2C%22queriesHasErrors%22%3Afalse%2C%22queriesCurrentPage%22%3A1%2C%22queriesTotalPages%22%3A1%2C%22queriesFilter%22%3A%22%22%2C%22queriesFilterVisible%22%3Afalse%2C%22statementType%22%3A%22text%22%2C%22statementTypes%22%3A%5B%22text%22%2C%22file%22%5D%2C%22statementPath%22%3A%22%22%2C%22externalStatementLoaded%22%3Afalse%2C%22associatedDocumentLoading%22%3Atrue%2C%22associatedDocumentUuid%22%3Anull%2C%22statement_raw%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22statementsList%22%3A%5B%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%5D%2C%22aceSize%22%3A100%2C%22status%22%3A%22running%22%2C%22statusForButtons%22%3A%22executing%22%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22viewSettings%22%3A%7B%22placeHolder%22%3A%22Example%3A+SELECT+*+FROM+tablename%2C+or+press+CTRL+%2B+space%22%2C%22sqlDialect%22%3Atrue%7D%2C%22variables%22%3A%5B%5D%2C%22hasCurlyBracketParameters%22%3Atrue%2C%22variableNames%22%3A%5B%5D%2C%22variableValues%22%3A%7B%7D%2C%22statement%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22hasResultset%22%3Atrue%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%2C%22meta%22%3A%5B%5D%2C%22rows%22%3Anull%2C%22hasMore%22%3Afalse%2C%22statement_id%22%3A0%2C%22statement_range%22%3A%7B%22start%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%2C%22end%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%7D%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3Anull%2C%22metaFilter%22%3A%7B%22query%22%3A%22%22%2C%22facets%22%3A%7B%7D%2C%22text%22%3A%5B%5D%7D%2C%22isMetaFilterVisible%22%3Afalse%2C%22filteredMetaChecked%22%3Atrue%2C%22filteredMeta%22%3A%5B%5D%2C%22fetchedOnce%22%3Afalse%2C%22startTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22endTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22executionTime%22%3A0%2C%22data%22%3A%5B%5D%2C%22explanation%22%3A%22%22%2C%22logs%22%3A%22%22%2C%22logLines%22%3A0%2C%22hasSomeResults%22%3Afalse%7D%2C%22showGrid%22%3Atrue%2C%22showChart%22%3Afalse%2C%22showLogs%22%3Atrue%2C%22progress%22%3A0%2C%22jobs%22%3A%5B%5D%2C%22isLoading%22%3Afalse%2C%22resultsKlass%22%3A%22results+impala%22%2C%22errorsKlass%22%3A%22results+impala+alert+alert-error%22%2C%22is_redacted%22%3Afalse%2C%22chartType%22%3A%22bars%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartLimits%22%3A%5B5%2C10%2C25%2C50%2C100%5D%2C%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartData%22%3A%5B%5D%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22hideStacked%22%3Atrue%2C%22hasDataForChart%22%3Afalse%2C%22previousChartOptions%22%3A%7B%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%7D%2C%22isResultSettingsVisible%22%3Afalse%2C%22settingsVisible%22%3Afalse%2C%22checkStatusTimeout%22%3Anull%2C%22topRisk%22%3Anull%2C%22suggestion%22%3A%22%22%2C%22hasSuggestion%22%3Anull%2C%22compatibilityCheckRunning%22%3Afalse%2C%22compatibilitySourcePlatform%22%3A%22impala%22%2C%22compatibilitySourcePlatforms%22%3A%5B%7B%22name%22%3A%22Teradata%22%2C%22value%22%3A%22teradata%22%7D%2C%7B%22name%22%3A%22Oracle%22%2C%22value%22%3A%22oracle%22%7D%2C%7B%22name%22%3A%22Netezza%22%2C%22value%22%3A%22netezza%22%7D%2C%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22DB2%22%2C%22value%22%3A%22db2%22%7D%2C%7B%22name%22%3A%22Greenplum%22%2C%22value%22%3A%22greenplum%22%7D%2C%7B%22name%22%3A%22MySQL%22%2C%22value%22%3A%22mysql%22%7D%2C%7B%22name%22%3A%22PostgreSQL%22%2C%22value%22%3A%22postgresql%22%7D%2C%7B%22name%22%3A%22Informix%22%2C%22value%22%3A%22informix%22%7D%2C%7B%22name%22%3A%22SQL+Server%22%2C%22value%22%3A%22sqlserver%22%7D%2C%7B%22name%22%3A%22Sybase%22%2C%22value%22%3A%22sybase%22%7D%2C%7B%22name%22%3A%22Access%22%2C%22value%22%3A%22access%22%7D%2C%7B%22name%22%3A%22Firebird%22%2C%22value%22%3A%22firebird%22%7D%2C%7B%22name%22%3A%22ANSISQL%22%2C%22value%22%3A%22ansisql%22%7D%2C%7B%22name%22%3A%22Generic%22%2C%22value%22%3A%22generic%22%7D%5D%2C%22compatibilityTargetPlatform%22%3A%22impala%22%2C%22compatibilityTargetPlatforms%22%3A%5B%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%5D%2C%22showOptimizer%22%3Atrue%2C%22delayedStatement%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22wasBatchExecuted%22%3Afalse%2C%22isReady%22%3Atrue%2C%22lastExecuted%22%3A1528820101947%2C%22lastAceSelectionRowOffset%22%3A0%2C%22executingBlockingOperation%22%3Anull%2C%22showLongOperationWarning%22%3Afalse%2C%22formatEnabled%22%3Atrue%2C%22isFetchingData%22%3Afalse%2C%22isCanceling%22%3Afalse%2C%22aceAutoExpand%22%3Afalse%7D%5D%2C%22selectedSnippet%22%3A%22impala%22%2C%22creatingSessionLocks%22%3A%5B%5D%2C%22sessions%22%3A%5B%7B%22type%22%3A%22impala%22%2C%22properties%22%3A%5B%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Files%22%2C%22key%22%3A%22files%22%2C%22help_text%22%3A%22Add+one+or+more+files%2C+jars%2C+or+arcimpalas+to+the+list+of+resources.%22%2C%22type%22%3A%22hdfs-files%22%7D%2C%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Functions%22%2C%22key%22%3A%22functions%22%2C%22help_text%22%3A%22Add+one+or+more+registered+UDFs+(requires+function+name+and+fully-qualified+class+name).%22%2C%22type%22%3A%22functions%22%7D%2C%7B%22nice_name%22%3A%22Settings%22%2C%22multiple%22%3Atrue%2C%22key%22%3A%22settings%22%2C%22help_text%22%3A%22impala+and+Hadoop+configuration+properties.%22%2C%22defaultValue%22%3A%5B%5D%2C%22type%22%3A%22settings%22%2C%22options%22%3A%5B%22impala.map.aggr%22%2C%22impala.exec.compress.output%22%2C%22impala.exec.parallel%22%2C%22impala.execution.engine%22%2C%22mapreduce.job.queuename%22%5D%2C%22value%22%3A%5B%5D%7D%5D%2C%22reuse_session%22%3Atrue%2C%22id%22%3A6865%2C%22session_id%22%3A%22714fb09b96ba3368%3A4d02ec93d7ffbfb6%22%7D%5D%2C%22directoryUuid%22%3A%22%22%2C%22dependentsCoordinator%22%3A%5B%5D%2C%22historyFilter%22%3A%22%22%2C%22historyFilterVisible%22%3Afalse%2C%22loadingHistory%22%3Afalse%2C%22historyInitialHeight%22%3A1679%2C%22forceHistoryInitialHeight%22%3Atrue%2C%22historyCurrentPage%22%3A1%2C%22historyTotalPages%22%3A3%2C%22schedulerViewModel%22%3Anull%2C%22schedulerViewModelIsLoaded%22%3Afalse%2C%22isBatchable%22%3Atrue%2C%22isExecutingAll%22%3Afalse%2C%22executingAllIndex%22%3A0%2C%22retryModalConfirm%22%3Anull%2C%22retryModalCancel%22%3Anull%2C%22unloaded%22%3Afalse%2C%22updateHistoryFailed%22%3Afalse%2C%22viewSchedulerId%22%3A%22%22%2C%22loadingScheduler%22%3Afalse%7D&snippet=%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22type%22%3A%22impala%22%2C%22status%22%3A%22running%22%2C%22statementType%22%3A%22text%22%2C%22statement%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22statementPath%22%3A%22%22%2C%22associatedDocumentUuid%22%3Anull%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%7D%2C%22database%22%3A%22default%22%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22wasBatchExecuted%22%3Afalse%7D",
                "params": [
                  {
                    "name": "notebook",
                    "value": "%7B%22uuid%22%3A%22f2b8a233-c34c-44b8-a8a1-0e6123996216%22%2C%22name%22%3A%22%22%2C%22description%22%3A%22%22%2C%22type%22%3A%22query-impala%22%2C%22initialType%22%3A%22impala%22%2C%22coordinatorUuid%22%3Anull%2C%22isHistory%22%3Atrue%2C%22isManaged%22%3Afalse%2C%22parentSavedQueryUuid%22%3Anull%2C%22isSaved%22%3Afalse%2C%22onSuccessUrl%22%3Anull%2C%22pubSubUrl%22%3Anull%2C%22isPresentationModeDefault%22%3Afalse%2C%22isPresentationMode%22%3Afalse%2C%22isPresentationModeInitialized%22%3Atrue%2C%22presentationSnippets%22%3A%7B%7D%2C%22isHidingCode%22%3Afalse%2C%22snippets%22%3A%5B%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22name%22%3A%22%22%2C%22type%22%3A%22impala%22%2C%22isBatchable%22%3Atrue%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22errors%22%3A%5B%5D%2C%22aceErrorsHolder%22%3A%5B%5D%2C%22aceWarningsHolder%22%3A%5B%5D%2C%22aceErrors%22%3A%5B%5D%2C%22aceWarnings%22%3A%5B%5D%2C%22editorMode%22%3Atrue%2C%22dbSelectionVisible%22%3Afalse%2C%22isSqlDialect%22%3Atrue%2C%22namespaceRefreshEnabled%22%3Afalse%2C%22availableNamespaces%22%3A%5B%5D%2C%22availableComputes%22%3A%5B%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute1%22%2C%22id%22%3A%22compute1%22%2C%22name%22%3A%22compute1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22compute2%22%2C%22id%22%3A%22compute2%22%2C%22name%22%3A%22compute2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22altus%22%2C%22namespace%22%3A%22Altus%22%2C%22id%22%3A%22Altus%22%2C%22name%22%3A%22Altus%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage1%22%2C%22id%22%3A%22storage1%22%2C%22name%22%3A%22storage1%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22storage2%22%2C%22id%22%3A%22storage2%22%2C%22name%22%3A%22storage2%22%7D%2C%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22Default%22%2C%22id%22%3A%22Default%22%2C%22name%22%3A%22default%22%7D%5D%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22database%22%3A%22default%22%2C%22currentQueryTab%22%3A%22queryHistory%22%2C%22pinnedContextTabs%22%3A%5B%5D%2C%22loadingQueries%22%3Afalse%2C%22queriesHasErrors%22%3Afalse%2C%22queriesCurrentPage%22%3A1%2C%22queriesTotalPages%22%3A1%2C%22queriesFilter%22%3A%22%22%2C%22queriesFilterVisible%22%3Afalse%2C%22statementType%22%3A%22text%22%2C%22statementTypes%22%3A%5B%22text%22%2C%22file%22%5D%2C%22statementPath%22%3A%22%22%2C%22externalStatementLoaded%22%3Afalse%2C%22associatedDocumentLoading%22%3Atrue%2C%22associatedDocumentUuid%22%3Anull%2C%22statement_raw%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22statementsList%22%3A%5B%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%5D%2C%22aceSize%22%3A100%2C%22status%22%3A%22running%22%2C%22statusForButtons%22%3A%22executing%22%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22viewSettings%22%3A%7B%22placeHolder%22%3A%22Example%3A+SELECT+*+FROM+tablename%2C+or+press+CTRL+%2B+space%22%2C%22sqlDialect%22%3Atrue%7D%2C%22variables%22%3A%5B%5D%2C%22hasCurlyBracketParameters%22%3Atrue%2C%22variableNames%22%3A%5B%5D%2C%22variableValues%22%3A%7B%7D%2C%22statement%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22hasResultset%22%3Atrue%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%2C%22meta%22%3A%5B%5D%2C%22rows%22%3Anull%2C%22hasMore%22%3Afalse%2C%22statement_id%22%3A0%2C%22statement_range%22%3A%7B%22start%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%2C%22end%22%3A%7B%22row%22%3A0%2C%22column%22%3A0%7D%7D%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3Anull%2C%22metaFilter%22%3A%7B%22query%22%3A%22%22%2C%22facets%22%3A%7B%7D%2C%22text%22%3A%5B%5D%7D%2C%22isMetaFilterVisible%22%3Afalse%2C%22filteredMetaChecked%22%3Atrue%2C%22filteredMeta%22%3A%5B%5D%2C%22fetchedOnce%22%3Afalse%2C%22startTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22endTime%22%3A%222018-06-12T16%3A15%3A01.951Z%22%2C%22executionTime%22%3A0%2C%22data%22%3A%5B%5D%2C%22explanation%22%3A%22%22%2C%22logs%22%3A%22%22%2C%22logLines%22%3A0%2C%22hasSomeResults%22%3Afalse%7D%2C%22showGrid%22%3Atrue%2C%22showChart%22%3Afalse%2C%22showLogs%22%3Atrue%2C%22progress%22%3A0%2C%22jobs%22%3A%5B%5D%2C%22isLoading%22%3Afalse%2C%22resultsKlass%22%3A%22results+impala%22%2C%22errorsKlass%22%3A%22results+impala+alert+alert-error%22%2C%22is_redacted%22%3Afalse%2C%22chartType%22%3A%22bars%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartLimits%22%3A%5B5%2C10%2C25%2C50%2C100%5D%2C%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartData%22%3A%5B%5D%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22hideStacked%22%3Atrue%2C%22hasDataForChart%22%3Afalse%2C%22previousChartOptions%22%3A%7B%22chartLimit%22%3Anull%2C%22chartX%22%3Anull%2C%22chartXPivot%22%3Anull%2C%22chartYSingle%22%3Anull%2C%22chartMapType%22%3A%22marker%22%2C%22chartMapLabel%22%3Anull%2C%22chartMapHeat%22%3Anull%2C%22chartYMulti%22%3A%5B%5D%2C%22chartScope%22%3A%22world%22%2C%22chartTimelineType%22%3A%22bar%22%2C%22chartSorting%22%3A%22none%22%2C%22chartScatterGroup%22%3Anull%2C%22chartScatterSize%22%3Anull%7D%2C%22isResultSettingsVisible%22%3Afalse%2C%22settingsVisible%22%3Afalse%2C%22checkStatusTimeout%22%3Anull%2C%22topRisk%22%3Anull%2C%22suggestion%22%3A%22%22%2C%22hasSuggestion%22%3Anull%2C%22compatibilityCheckRunning%22%3Afalse%2C%22compatibilitySourcePlatform%22%3A%22impala%22%2C%22compatibilitySourcePlatforms%22%3A%5B%7B%22name%22%3A%22Teradata%22%2C%22value%22%3A%22teradata%22%7D%2C%7B%22name%22%3A%22Oracle%22%2C%22value%22%3A%22oracle%22%7D%2C%7B%22name%22%3A%22Netezza%22%2C%22value%22%3A%22netezza%22%7D%2C%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22DB2%22%2C%22value%22%3A%22db2%22%7D%2C%7B%22name%22%3A%22Greenplum%22%2C%22value%22%3A%22greenplum%22%7D%2C%7B%22name%22%3A%22MySQL%22%2C%22value%22%3A%22mysql%22%7D%2C%7B%22name%22%3A%22PostgreSQL%22%2C%22value%22%3A%22postgresql%22%7D%2C%7B%22name%22%3A%22Informix%22%2C%22value%22%3A%22informix%22%7D%2C%7B%22name%22%3A%22SQL+Server%22%2C%22value%22%3A%22sqlserver%22%7D%2C%7B%22name%22%3A%22Sybase%22%2C%22value%22%3A%22sybase%22%7D%2C%7B%22name%22%3A%22Access%22%2C%22value%22%3A%22access%22%7D%2C%7B%22name%22%3A%22Firebird%22%2C%22value%22%3A%22firebird%22%7D%2C%7B%22name%22%3A%22ANSISQL%22%2C%22value%22%3A%22ansisql%22%7D%2C%7B%22name%22%3A%22Generic%22%2C%22value%22%3A%22generic%22%7D%5D%2C%22compatibilityTargetPlatform%22%3A%22impala%22%2C%22compatibilityTargetPlatforms%22%3A%5B%7B%22name%22%3A%22Impala%22%2C%22value%22%3A%22impala%22%7D%2C%7B%22name%22%3A%22impala%22%2C%22value%22%3A%22impala%22%7D%5D%2C%22showOptimizer%22%3Atrue%2C%22delayedStatement%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22wasBatchExecuted%22%3Afalse%2C%22isReady%22%3Atrue%2C%22lastExecuted%22%3A1528820101947%2C%22lastAceSelectionRowOffset%22%3A0%2C%22executingBlockingOperation%22%3Anull%2C%22showLongOperationWarning%22%3Afalse%2C%22formatEnabled%22%3Atrue%2C%22isFetchingData%22%3Afalse%2C%22isCanceling%22%3Afalse%2C%22aceAutoExpand%22%3Afalse%7D%5D%2C%22selectedSnippet%22%3A%22impala%22%2C%22creatingSessionLocks%22%3A%5B%5D%2C%22sessions%22%3A%5B%7B%22type%22%3A%22impala%22%2C%22properties%22%3A%5B%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Files%22%2C%22key%22%3A%22files%22%2C%22help_text%22%3A%22Add+one+or+more+files%2C+jars%2C+or+arcimpalas+to+the+list+of+resources.%22%2C%22type%22%3A%22hdfs-files%22%7D%2C%7B%22multiple%22%3Atrue%2C%22defaultValue%22%3A%5B%5D%2C%22value%22%3A%5B%5D%2C%22nice_name%22%3A%22Functions%22%2C%22key%22%3A%22functions%22%2C%22help_text%22%3A%22Add+one+or+more+registered+UDFs+(requires+function+name+and+fully-qualified+class+name).%22%2C%22type%22%3A%22functions%22%7D%2C%7B%22nice_name%22%3A%22Settings%22%2C%22multiple%22%3Atrue%2C%22key%22%3A%22settings%22%2C%22help_text%22%3A%22impala+and+Hadoop+configuration+properties.%22%2C%22defaultValue%22%3A%5B%5D%2C%22type%22%3A%22settings%22%2C%22options%22%3A%5B%22impala.map.aggr%22%2C%22impala.exec.compress.output%22%2C%22impala.exec.parallel%22%2C%22impala.execution.engine%22%2C%22mapreduce.job.queuename%22%5D%2C%22value%22%3A%5B%5D%7D%5D%2C%22reuse_session%22%3Atrue%2C%22id%22%3A6865%2C%22session_id%22%3A%22714fb09b96ba3368%3A4d02ec93d7ffbfb6%22%7D%5D%2C%22directoryUuid%22%3A%22%22%2C%22dependentsCoordinator%22%3A%5B%5D%2C%22historyFilter%22%3A%22%22%2C%22historyFilterVisible%22%3Afalse%2C%22loadingHistory%22%3Afalse%2C%22historyInitialHeight%22%3A1679%2C%22forceHistoryInitialHeight%22%3Atrue%2C%22historyCurrentPage%22%3A1%2C%22historyTotalPages%22%3A3%2C%22schedulerViewModel%22%3Anull%2C%22schedulerViewModelIsLoaded%22%3Afalse%2C%22isBatchable%22%3Atrue%2C%22isExecutingAll%22%3Afalse%2C%22executingAllIndex%22%3A0%2C%22retryModalConfirm%22%3Anull%2C%22retryModalCancel%22%3Anull%2C%22unloaded%22%3Afalse%2C%22updateHistoryFailed%22%3Afalse%2C%22viewSchedulerId%22%3A%22%22%2C%22loadingScheduler%22%3Afalse%7D"
                  },
                  {
                    "name": "snippet",
                    "value": "%7B%22id%22%3A%22dd5755a3-e8db-82d9-4f98-9f4fb5a99a06%22%2C%22type%22%3A%22impala%22%2C%22status%22%3A%22running%22%2C%22statementType%22%3A%22text%22%2C%22statement%22%3A%22SELECT+*+FROM+web_logs+LIMIT+100%3B%22%2C%22aceCursorPosition%22%3A%7B%22column%22%3A33%2C%22row%22%3A0%7D%2C%22statementPath%22%3A%22%22%2C%22associatedDocumentUuid%22%3Anull%2C%22properties%22%3A%7B%22files%22%3A%5B%5D%2C%22functions%22%3A%5B%5D%2C%22arguments%22%3A%5B%5D%2C%22settings%22%3A%5B%5D%7D%2C%22result%22%3A%7B%22id%22%3A%2206840534-9434-33b5-5eca-2cd08432ceb3%22%2C%22type%22%3A%22table%22%2C%22handle%22%3A%7B%22has_more_statements%22%3Afalse%2C%22statement_id%22%3A0%2C%22statements_count%22%3A1%2C%22previous_statement_hash%22%3A%22acb6478fcf28c31b5e76d49de7d77bbe46fe5e4f9436c16c0ca8ed5f%22%7D%7D%2C%22database%22%3A%22default%22%2C%22compute%22%3A%7B%22interface%22%3A%22impala%22%2C%22type%22%3A%22direct%22%2C%22namespace%22%3A%22default-romain%22%2C%22id%22%3A%22default-romain%22%2C%22name%22%3A%22default-romain%22%7D%2C%22wasBatchExecuted%22%3Afalse%7D"
                  }
                ]
              }
            }'''

    payload = payload.replace('SELECT+*+FROM+web_logs+LIMIT+100', urllib.quote_plus(query.replace('\n', ' ')))

    resp = self.api.submit_hue_query(self.cluster_crn, payload)

    if 'payload' in resp:
      resp_payload = json.loads(resp['payload'])
      if 'handle' in resp_payload:
        return resp_payload['handle']
      else:
        raise QueryError(resp_payload.get('message'))
    else:
      raise QueryError(resp.get('message'))


  def do_check_status(self, handle):
    notebook = {"type":"impala", "name": "query", "isSaved": False, "sessions": [], "snippets": [{"id": "1234", "type":"impala","statement_raw": "SHOW DATABASES", "result": {"handle": {} }}]}
    snippet = {"id": "1234", "type": "impala", "statement":"SHOW DATABASES", "status": "running", "result": {'handle': {"log_context":None,"statements_count":1,"end":{"column":13,"row":0},"statement_id":0,"has_more_statements":False,"start":{"column":0,"row":0},"secret":"3h9WBnLbTUYAAAAAPQjxlQ==\n","has_result_set":True,"session_guid":"qcrpEBmCTGacxfhM+CxbkQ==\n","statement":"SHOW DATABASES","operation_type":0,"modified_row_count":None,"guid":"3h9WBnLbTUYAAAAAPQjxlQ==\n","previous_statement_hash":"5b1f14102d749be7b41da376bcdbb64f993ce00bc46e3aab0b8008c4"}}, "properties": {}}

    snippet['result']['handle'] = handle

    notebook_payload = urllib.quote(json.dumps(notebook))
    snippet_payload = urllib.quote(json.dumps(snippet))

    payload = '''
            {
              "method": "POST",
              "url": "http://127.0.0.1:8000/notebook/api/check_status",
              "httpVersion": "HTTP/1.1",
              "headers": [
                {
                  "name": "Accept-Encoding",
                  "value": "gzip, deflate, br"
                },
                {
                  "name": "Content-Type",
                  "value": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                {
                  "name": "Accept",
                  "value": "*/*"
                },
                {
                  "name": "X-Requested-With",
                  "value": "XMLHttpRequest"
                },
                {
                  "name": "Connection",
                  "value": "keep-alive"
                }
              ],
              "queryString": [],
              "cookies": [
              ],
              "postData": {
                "mimeType": "application/x-www-form-urlencoded; charset=UTF-8",
                "text": "notebook=%(notebook)s&snippet=%(snippet)s",
                "params": [
                  {
                    "name": "notebook",
                    "value": "%(notebook)s"
                  },
                  {
                    "name": "snippet",
                    "value": "%(snippet)s"
                  }
                ]
              }
            }''' % {'notebook': notebook_payload, 'snippet': snippet_payload}

    resp = self.api.submit_hue_query(self.cluster_crn, payload)
    resp_payload = json.loads(resp['payload'])

    if 'query_status' in resp_payload:
      return resp_payload['query_status']
    else:
      return resp_payload


  def do_fetch_result(self, handle):
    notebook = {"type":"impala", "name": "query", "isSaved": False, "sessions": [], "snippets": [{"id": "1234", "type":"impala","statement_raw": "SHOW DATABASES", "result": {"handle": {} }}]}
    snippet = {"id": "1234", "type": "impala", "statement":"SHOW DATABASES", "status": "running", "result": {'handle': {"log_context":None,"statements_count":1,"end":{"column":13,"row":0},"statement_id":0,"has_more_statements":False,"start":{"column":0,"row":0},"secret":"3h9WBnLbTUYAAAAAPQjxlQ==\n","has_result_set":True,"session_guid":"qcrpEBmCTGacxfhM+CxbkQ==\n","statement":"SHOW DATABASES","operation_type":0,"modified_row_count":None,"guid":"3h9WBnLbTUYAAAAAPQjxlQ==\n","previous_statement_hash":"5b1f14102d749be7b41da376bcdbb64f993ce00bc46e3aab0b8008c4"}}, "properties": {}}

    rows = 100
    start_over = True

    snippet['result']['handle'] = handle

    notebook_payload = urllib.quote(json.dumps(notebook))
    snippet_payload = urllib.quote(json.dumps(snippet))
    rows_payload = urllib.quote(json.dumps(rows))
    start_over_payload = urllib.quote(json.dumps(start_over))

    payload = '''
            {
              "method": "POST",
              "url": "http://127.0.0.1:8000/notebook/api/fetch_result_data",
              "httpVersion": "HTTP/1.1",
              "headers": [
                {
                  "name": "Accept-Encoding",
                  "value": "gzip, deflate, br"
                },
                {
                  "name": "Content-Type",
                  "value": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                {
                  "name": "Accept",
                  "value": "*/*"
                },
                {
                  "name": "X-Requested-With",
                  "value": "XMLHttpRequest"
                },
                {
                  "name": "Connection",
                  "value": "keep-alive"
                }
              ],
              "queryString": [],
              "cookies": [
              ],
              "postData": {
                "mimeType": "application/x-www-form-urlencoded; charset=UTF-8",
                "text": "notebook=%(notebook)s&snippet=%(snippet)s&rows=%(rows)s&startOver=%(start_over)s",
                "params": [
                  {
                    "name": "notebook",
                    "value": "%(notebook)s"
                  },
                  {
                    "name": "snippet",
                    "value": "%(snippet)s"
                  },
                  {
                    "name": "rows",
                    "value": %(rows)s
                  },
                  {
                    "name": "startOver",
                    "value": "%(start_over)s"
                  }
                ]
              }
            }''' % {'notebook': notebook_payload, 'snippet': snippet_payload, 'rows': rows_payload, 'start_over': start_over_payload}

    resp = self.api.submit_hue_query(self.cluster_crn, payload)
    return json.loads(resp['payload'])['result']
