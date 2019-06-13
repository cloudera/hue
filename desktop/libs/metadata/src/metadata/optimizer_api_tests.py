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

from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access

from metadata.optimizer_api import _convert_queries


LOG = logging.getLogger(__name__)


class TestOptimizerApi(object):
  integration = True

  @classmethod
  def setup_class(cls):
    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    cls.user = rewrite_user(cls.user)
    add_to_group('test')
    grant_access("test", "test", "metadata")
    grant_access("test", "test", "optimizer")


  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()


  # Should run first
  def test_upload(self):
    query_docs = [
      {'snippets': [{u'wasBatchExecuted': False, u'chartLimits': [5, 10, 25, 50, 100], u'associatedDocumentLoading': True, u'isReady': True, u'statement_raw': u'SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000', u'statusForButtons': u'executing', u'showLogs': True, u'variableNames': [], u'associatedDocumentUuid': None, u'compatibilitySourcePlatform': u'hive', u'progress': 0, u'chartType': u'bars', u'isFetchingData': False, u'name': u'Sample: Top salary', u'statementTypes': [u'text', u'file'], u'is_redacted': False, u'currentQueryTab': u'queryHistory', u'chartScope': u'world', u'result': {u'logs': u'', u'isMetaFilterVisible': False, u'meta': [], u'logLines': 0, u'id': u'15862a85-d73e-1611-6e8b-1dad4df72a06', u'statement_id': 0, u'statements_count': 1, u'rows': None, u'hasSomeResults': False, u'filteredMetaChecked': True, u'hasMore': False, u'filteredMeta': [], u'type': u'table', u'handle': {u'log_context': None, u'statements_count': 1, u'end': {u'column': 145, u'row': 0}, u'statement_id': 0, u'has_more_statements': False, u'start': {u'column': 0, u'row': 0}, u'secret': u'EjC753YQTNqERq3UOqnXYg==\n', u'has_result_set': True, u'session_guid': u'9o/kHUQ8Qi+rs+Arw31zww==\n', u'statement': u'SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000', u'operation_type': 0, u'modified_row_count': None, u'guid': u'p3Caqe9fST6pzNkVTTc3xw==\n', u'previous_statement_hash': u'13951b16cfb60a82977a0f70e547f5c45fb87472662741fb5d51838d'}, u'metaFilter': u'', u'explanation': u'', u'statement_range': {u'start': {u'column': 0, u'row': 0}, u'end': {u'column': 0, u'row': 0}}, u'startTime': u'2017-04-13T15:56:36.868Z', u'data': [], u'previous_statement_hash': None, u'executionTime': 0, u'fetchedOnce': False, u'hasResultset': True, u'endTime': u'2017-04-13T15:56:36.868Z'}, u'errors': [], u'chartMapHeat': None, u'compatibilitySourcePlatforms': [{u'name': u'Teradata', u'value': u'teradata'}, {u'name': u'Oracle', u'value': u'oracle'}, {u'name': u'Netezza', u'value': u'netezza'}, {u'name': u'Impala', u'value': u'impala'}, {u'name': u'Hive', u'value': u'hive'}, {u'name': u'DB2', u'value': u'db2'}, {u'name': u'Greenplum', u'value': u'greenplum'}, {u'name': u'MySQL', u'value': u'mysql'}, {u'name': u'PostgreSQL', u'value': u'postgresql'}, {u'name': u'Informix', u'value': u'informix'}, {u'name': u'SQL Server', u'value': u'sqlserver'}, {u'name': u'Sybase', u'value': u'sybase'}, {u'name': u'Access', u'value': u'access'}, {u'name': u'Firebird', u'value': u'firebird'}, {u'name': u'ANSISQL', u'value': u'ansisql'}, {u'name': u'Generic', u'value': u'generic'}], u'aceErrorsHolder': [], u'showOptimizer': True, u'compatibilityTargetPlatform': u'hive', u'jobs': [], u'statementType': u'text', u'isCanceling': False, u'queriesTotalPages': 1, u'formatEnabled': True, u'properties': {u'files': [], u'functions': [], u'settings': []}, u'complexityCheckRunning': True, u'aceErrors': [], u'externalStatementLoaded': False, u'chartScatterSize': None, u'chartYSingle': None, u'suggestion': u'', u'statementPath': u'', u'hasComplexity': False, u'showLongOperationWarning': False, u'chartX': u'sample_07.description', u'lastExecuted': 1492098996862, u'variables': [], u'showChart': False, u'isResultSettingsVisible': False, u'showGrid': True, u'pinnedContextTabs': [], u'viewSettings': {u'sqlDialect': True, u'placeHolder': u'Example: SELECT * FROM tablename, or press CTRL + space'}, u'executingBlockingOperation': None, u'errorsKlass': u'results hive alert alert-error', u'statement': u'SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000', u'type': u'hive', u'chartSorting': u'none', u'previousChartOptions': {u'chartTimelineType': u'bar', u'chartSorting': u'none', u'chartLimit': None, u'chartMapHeat': None, u'chartMapType': u'marker', u'chartX': u'sample_07.description', u'chartYMulti': [u'sample_07.salary'], u'chartScatterSize': None, u'chartScope': u'world', u'chartMapLabel': None, u'chartScatterGroup': None, u'chartYSingle': None, u'chartXPivot': None}, u'aceWarningsHolder': [], u'resultsKlass': u'results hive', u'delayedStatement': u'SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000', u'chartTimelineType': u'bar', u'compatibilityTargetPlatforms': [{u'name': u'Impala', u'value': u'impala'}, {u'name': u'Hive', u'value': u'hive'}], u'chartLimit': None, u'chartScatterGroup': None, u'settingsVisible': False, u'queriesFilterVisible': False, u'aceWarnings': [], u'compatibilityCheckRunning': False, u'isLoading': False, u'loadingQueries': False, u'hasDataForChart': True, u'id': u'df59d618-4c9a-4321-adbc-c296c38d7c2c', u'aceSize': 100, u'chartData': [], u'queriesHasErrors': False, u'chartMapLabel': None, u'status': u'expired', u'isSqlDialect': True, u'chartMapType': u'marker', u'queriesFilter': u'', u'queriesCurrentPage': 1, u'isBatchable': True, u'chartYMulti': [u'sample_07.salary'], u'dbSelectionVisible': False, u'database': u'default\r', u'hasSuggestion': None, u'complexity': [], u'chartXPivot': None, u'checkStatusTimeout': None}]},
      {'snippets': [{u'wasBatchExecuted': False, u'chartLimits': [5, 10, 25, 50, 100], u'associatedDocumentLoading': True, u'isReady': True, u'statement_raw': u"-- Get email survey opt-in values for all customers\nSELECT\n  c.id,\n  c.name,\n  c.email_preferences.categories.surveys\nFROM customers c;\n\n\n\n-- Select customers for a given shipping ZIP Code\nSELECT\n  customers.id,\n  customers.name\nFROM customers\nWHERE customers.addresses['shipping'].zip_code = '76710';\n\n\n\n-- Compute total amount per order for all customers\nSELECT\n  c.id AS customer_id,\n  c.name AS customer_name,\n  ords.order_id AS order_id,\n  SUM(order_items.price * order_items.qty) AS total_amount\nFROM\n  customers c\nLATERAL VIEW EXPLODE(c.orders) o AS ords\nLATERAL VIEW EXPLODE(ords.items) i AS order_items\nGROUP BY c.id, c.name, ords.order_id;", u'statusForButtons': u'executing', u'showLogs': True, u'variableNames': [], u'associatedDocumentUuid': None, u'compatibilitySourcePlatform': u'hive', u'progress': 0, u'chartType': u'bars', u'isFetchingData': False, u'name': u'Sample: Customers', u'statementTypes': [u'text', u'file'], u'is_redacted': False, u'currentQueryTab': u'queryHistory', u'chartScope': u'world', u'result': {u'logs': u'', u'isMetaFilterVisible': False, u'meta': [], u'logLines': 0, u'id': u'b38261e7-d644-5c4c-2c98-f6f0c7ad56a8', u'statement_id': 0, u'statements_count': 3, u'rows': None, u'hasSomeResults': False, u'filteredMetaChecked': True, u'hasMore': False, u'filteredMeta': [], u'type': u'table', u'handle': {u'log_context': None, u'statements_count': 3, u'end': {u'column': 17, u'row': 5}, u'statement_id': 0, u'has_more_statements': True, u'start': {u'column': 0, u'row': 0}, u'secret': u'c+zxQ8qHQcWaGNe6eSfVgw==\n', u'has_result_set': True, u'session_guid': u'rJHY2R+MSzaMI1JNa3yC1g==\n', u'statement': u'-- Get email survey opt-in values for all customers\nSELECT\n  c.id,\n  c.name,\n  c.email_preferences.categories.surveys\nFROM customers c', u'operation_type': 0, u'modified_row_count': None, u'guid': u't5tR8DMASNemucmHtHpGHQ==\n', u'previous_statement_hash': u'3506b74b9f398fcb4ef5c3dddd2513f163b569c0c7b59a88cf9ab572'}, u'metaFilter': u'', u'explanation': u'', u'statement_range': {u'start': {u'column': 0, u'row': 0}, u'end': {u'column': 0, u'row': 0}}, u'startTime': u'2017-04-13T01:06:11.960Z', u'data': [], u'previous_statement_hash': None, u'executionTime': 0, u'fetchedOnce': False, u'hasResultset': True, u'endTime': u'2017-04-13T01:06:11.960Z'}, u'errors': [], u'chartMapHeat': None, u'compatibilitySourcePlatforms': [{u'name': u'Teradata', u'value': u'teradata'}, {u'name': u'Oracle', u'value': u'oracle'}, {u'name': u'Netezza', u'value': u'netezza'}, {u'name': u'Impala', u'value': u'impala'}, {u'name': u'Hive', u'value': u'hive'}, {u'name': u'DB2', u'value': u'db2'}, {u'name': u'Greenplum', u'value': u'greenplum'}, {u'name': u'MySQL', u'value': u'mysql'}, {u'name': u'PostgreSQL', u'value': u'postgresql'}, {u'name': u'Informix', u'value': u'informix'}, {u'name': u'SQL Server', u'value': u'sqlserver'}, {u'name': u'Sybase', u'value': u'sybase'}, {u'name': u'Access', u'value': u'access'}, {u'name': u'Firebird', u'value': u'firebird'}, {u'name': u'ANSISQL', u'value': u'ansisql'}, {u'name': u'Generic', u'value': u'generic'}], u'aceErrorsHolder': [], u'showOptimizer': True, u'compatibilityTargetPlatform': u'hive', u'jobs': [], u'statementType': u'text', u'isCanceling': False, u'queriesTotalPages': 1, u'formatEnabled': True, u'properties': {u'files': [], u'functions': [], u'settings': []}, u'complexityCheckRunning': True, u'aceErrors': [], u'externalStatementLoaded': False, u'chartScatterSize': None, u'chartYSingle': None, u'suggestion': u'', u'statementPath': u'', u'hasComplexity': False, u'showLongOperationWarning': False, u'chartX': None, u'lastExecuted': 1492045571956, u'variables': [], u'showChart': False, u'isResultSettingsVisible': False, u'showGrid': True, u'pinnedContextTabs': [], u'viewSettings': {u'sqlDialect': True, u'placeHolder': u'Example: SELECT * FROM tablename, or press CTRL + space'}, u'executingBlockingOperation': None, u'errorsKlass': u'results hive alert alert-error', u'statement': u"-- Get email survey opt-in values for all customers\nSELECT\n  c.id,\n  c.name,\n  c.email_preferences.categories.surveys\nFROM customers c;\n\n\n\n-- Select customers for a given shipping ZIP Code\nSELECT\n  customers.id,\n  customers.name\nFROM customers\nWHERE customers.addresses['shipping'].zip_code = '76710';\n\n\n\n-- Compute total amount per order for all customers\nSELECT\n  c.id AS customer_id,\n  c.name AS customer_name,\n  ords.order_id AS order_id,\n  SUM(order_items.price * order_items.qty) AS total_amount\nFROM\n  customers c\nLATERAL VIEW EXPLODE(c.orders) o AS ords\nLATERAL VIEW EXPLODE(ords.items) i AS order_items\nGROUP BY c.id, c.name, ords.order_id;", u'type': u'hive', u'chartSorting': u'none', u'previousChartOptions': {u'chartTimelineType': u'bar', u'chartSorting': u'none', u'chartLimit': None, u'chartMapHeat': None, u'chartMapType': u'marker', u'chartX': None, u'chartYMulti': [], u'chartScatterSize': None, u'chartScope': u'world', u'chartMapLabel': None, u'chartScatterGroup': None, u'chartYSingle': None, u'chartXPivot': None}, u'aceWarningsHolder': [], u'resultsKlass': u'results hive', u'delayedStatement': u"-- Get email survey opt-in values for all customers\nSELECT\n  c.id,\n  c.name,\n  c.email_preferences.categories.surveys\nFROM customers c;\n\n\n\n-- Select customers for a given shipping ZIP Code\nSELECT\n  customers.id,\n  customers.name\nFROM customers\nWHERE customers.addresses['shipping'].zip_code = '76710';\n\n\n\n-- Compute total amount per order for all customers\nSELECT\n  c.id AS customer_id,\n  c.name AS customer_name,\n  ords.order_id AS order_id,\n  SUM(order_items.price * order_items.qty) AS total_amount\nFROM\n  customers c\nLATERAL VIEW EXPLODE(c.orders) o AS ords\nLATERAL VIEW EXPLODE(ords.items) i AS order_items\nGROUP BY c.id, c.name, ords.order_id;", u'chartTimelineType': u'bar', u'compatibilityTargetPlatforms': [{u'name': u'Impala', u'value': u'impala'}, {u'name': u'Hive', u'value': u'hive'}], u'chartLimit': None, u'chartScatterGroup': None, u'settingsVisible': False, u'queriesFilterVisible': False, u'aceWarnings': [], u'compatibilityCheckRunning': False, u'isLoading': False, u'loadingQueries': False, u'hasDataForChart': False, u'id': u'71733a5c-f191-42b2-8eb8-11161a84b714', u'aceSize': 100, u'chartData': [], u'queriesHasErrors': False, u'chartMapLabel': None, u'status': u'expired', u'isSqlDialect': True, u'chartMapType': u'marker', u'queriesFilter': u'', u'queriesCurrentPage': 1, u'isBatchable': True, u'chartYMulti': [], u'dbSelectionVisible': False, u'database': u'default', u'hasSuggestion': None, u'complexity': [], u'chartXPivot': None, u'checkStatusTimeout': None}]},
    ]

    csv_queries = _convert_queries(query_docs)

    expected_queries = [(
      '4488223986598703271:14355003141485350057',
      0,
      'SELECT sample_07.description, sample_07.salary FROM   sample_07 WHERE ( sample_07.salary > 100000) ORDER BY sample_07.salary DESC LIMIT 1000',
      'default'
      ), (
      '15512649139552885687:2109508391260502438',
      0,
      '''SELECT   c.id,   c.name,   c.email_preferences.categories.surveys FROM customers c;    SELECT   customers.id,   customers.name FROM customers WHERE customers.addresses['shipping'].zip_code = '76710';    SELECT   c.id AS customer_id,   c.name AS customer_name,   ords.order_id AS order_id,   SUM(order_items.price * order_items.qty) AS total_amount FROM   customers c LATERAL VIEW EXPLODE(c.orders) o AS ords LATERAL VIEW EXPLODE(ords.items) i AS order_items GROUP BY c.id, c.name, ords.order_id;''',
      'default'
      )
    ]

    for query, expected_query in zip(csv_queries, expected_queries):
      assert_equal(query, expected_query)
