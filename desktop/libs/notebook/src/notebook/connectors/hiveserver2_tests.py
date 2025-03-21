#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import re
import sys
import json
import time
import logging
from builtins import next, object
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from TCLIService.ttypes import TOperationType, TProtocolVersion, TStatusCode

from beeswax.server import dbms
from beeswax.server.dbms import QueryServerException
from beeswax.test_base import BeeswaxSampleProvider, get_query_server_config, is_hive_on_spark
from desktop.auth.backend import rewrite_user
from desktop.conf import has_connectors
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.i18n import smart_str
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster
from notebook.api import _save_notebook
from notebook.connectors.base import QueryError, QueryExpired
from notebook.connectors.hiveserver2 import HS2Api
from notebook.models import Notebook, make_notebook
from useradmin.models import User

LOG = logging.getLogger()


@pytest.mark.django_db
class TestApiWithConnectors(object):

  NOTEBOOK_JSON = """
    {
      "selectedSnippet": "impala",
      "showHistory": false,
      "description": "Test Impala Query",
      "name": "Test Impala Query",
      "sessions": [
          {
              "type": "impala",
              "properties": [],
              "id": null
          }
      ],
      "type": "query-impala",
      "id": null,
      "snippets": [{
        "id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"impala-xx","status":"running",
        "statement_raw":"select * from web_logs",
        "statement":"select * from web_logs",
        "variables":[],
        "properties":{"settings":[],"variables":[],"files":[],"functions":[]},
        "result":{
            "id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table",
            "handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,
                "start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,
                "statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}
            },
        "lastExecuted": 1462554843817,"database":"default"
      }],
      "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a",
      "isSaved":false
  }
  """

  CONNECTOR = [{
      'nice_name': 'Impala', 'name': 'impala-xx', 'dialect': 'impala', 'interface': 'hiveserver2',
      'settings': [
          {'name': 'server_host', 'value': 'gethue.com'},
          {'name': 'server_port', 'value': '21050'},
        ],
        'id': 1, 'category': 'editor', 'description': '', 'is_sql': True
      },
    ]

  def setup_method(self):
    if not has_connectors():
      pytest.skip("Skipping Test")

    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)

    self.user = rewrite_user(User.objects.get(username="test"))
    grant_access("test", "default", "notebook")

  def test_execute_impala(self):

    with patch('desktop.lib.connectors.api.CONNECTOR_INSTANCES', TestApi.CONNECTOR):
      with patch('desktop.lib.thrift_util.get_client') as get_client:
        tclient = Mock()
        successfullCall = Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
            sessionHandle=Mock(
              sessionId=Mock(
                secret='\x7f\x98\x97s\xe1\xa8G\xf4\x8a\x8a\\r\x0e6\xc2\xee\xf0',
                guid='\xfa\xb0/\x04 \xfeDX\x99\xfcq\xff2\x07\x02\xfe',
              )
            ),
            configuration={},
            serverProtocolVersion=TProtocolVersion.HIVE_CLI_SERVICE_PROTOCOL_V7,
            # TFetchResultsResp
            results=Mock(
              startRowOffset=0,
              rows=[],
              columns=[]
            ),
            # ExecuteStatement
            operationHandle=Mock(
              operationId=Mock(
                secret='\x7f\x98\x97s\xe1\xa8G\xf4\x8a\x8a\\r\x0e6\xc2\xee\xf0',
                guid='\xfa\xb0/\x04 \xfeDX\x99\xfcq\xff2\x07\x02\xfe',
              ),
              hasResultSet=True,
              operationType=TOperationType.EXECUTE_STATEMENT,
              modifiedRowCount=0
            ),
          )
        )

        tclient.OpenSession = successfullCall
        tclient.ExecuteStatement = successfullCall
        tclient.FetchResults = successfullCall
        tclient.GetResultSetMetadata = successfullCall
        tclient.CloseOperation = successfullCall

        get_client.return_value = tclient
        tclient.get_coordinator_host = Mock(return_value={})

        response = self.client.post(reverse('notebook:execute'), {
            'notebook': TestApi.NOTEBOOK_JSON,
            'snippet': json.dumps(json.loads(TestApi.NOTEBOOK_JSON)['snippets'][0]),
        })

      get_client.assert_called()

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 0

  def test_autocomplete_database_impala(self):

    with patch('desktop.lib.connectors.api.CONNECTOR_INSTANCES', TestApi.CONNECTOR):
      with patch('beeswax.server.dbms.get') as get:
        get.return_value = Mock(
          get_databases=Mock(
            return_value=[{'comment': '', 'hdfs_link': 'hdfs://table'}]
          )
        )

        response = self.client.post(reverse('notebook:api_autocomplete_databases'), {
            'notebook': TestApi.NOTEBOOK_JSON,
            'snippet': json.dumps(json.loads(TestApi.NOTEBOOK_JSON)['snippets'][0]),
        })

      get.assert_called()

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 0
    assert data['databases'] == [{u'comment': u'', u'hdfs_link': u'hdfs://table'}]

  def test_sample_data_table_sync_impala(self):

    with patch('desktop.lib.connectors.api.CONNECTOR_INSTANCES', TestApi.CONNECTOR):
      with patch('beeswax.server.dbms.get') as get:
        get.return_value = Mock(
          get_table=Mock(
            return_value=Mock(is_impala_only=False)
          ),
          get_sample=Mock(
            return_value=Mock(
              rows=Mock(return_value=[[1], [2]]),
              cols=Mock(return_value=['name']),
              full_cols=Mock(return_value=[{'name': 'name'}])
            )
          )
        )

        response = self.client.post(
          reverse('notebook:api_sample_data', kwargs={'database': 'sfdc', 'table': 'customers'}), {
            'notebook': TestApi.NOTEBOOK_JSON,
            'snippet': json.dumps(json.loads(TestApi.NOTEBOOK_JSON)['snippets'][0]),
          }
        )

      get.assert_called()

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 0
    assert data['headers'] == ['name']
    assert data['full_headers'] == [{'name': 'name'}]
    assert data['rows'] == [[1], [2]]

  def test_sample_data_table_async_impala(self):

    with patch('desktop.lib.connectors.api.CONNECTOR_INSTANCES', TestApi.CONNECTOR):
      with patch('beeswax.server.dbms.get') as get:
        get.return_value = Mock(
          get_table=Mock(
            return_value=Mock(is_impala_only=False)
          ),
          server_name='impala-xx',
          get_sample=Mock(
            return_value='SELECT * from customers'
          ),
          client=Mock(
            user=self.user,
            query=Mock(
              return_value=Mock(
                get=Mock(
                  return_value=('server_id', 'server_guid')
                ),
                log_context='log_context',
                has_result_set=True,
                session_guid='session_guid',
                modified_row_count=0,
                operation_type=1
              ),
            )
          )
        )

        response = self.client.post(
          reverse('notebook:api_sample_data', kwargs={'database': 'sfdc', 'table': 'customers'}), {
            'notebook': TestApi.NOTEBOOK_JSON,
            'snippet': json.dumps(json.loads(TestApi.NOTEBOOK_JSON)['snippets'][0]),
            'async': '"true"'
          }
        )

      get.assert_called()

    assert response.status_code == 200
    data = json.loads(response.content)
    assert data['status'] == 0
    assert data['result']['handle']['secret'] == 'server_id'
    assert data['result']['handle']['statement'] == 'SELECT * from customers'


@pytest.mark.django_db
class TestApi():

  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))

  @patch('notebook.connectors.hiveserver2.has_jobbrowser', True)
  def test_get_jobs_with_jobbrowser(self):
    notebook = Mock()
    snippet = {'type': 'hive', 'properties': {}}
    logs = ''

    with patch('notebook.connectors.hiveserver2.HS2Api._get_hive_execution_engine') as _get_hive_execution_engine:
      with patch('notebook.connectors.hiveserver2.parse_out_jobs') as parse_out_jobs:

        _get_hive_execution_engine.return_value = 'tez'
        parse_out_jobs.return_value = [{'job_id': 'job_id_00001'}]

        jobs = HS2Api(self.user).get_jobs(notebook, snippet, logs)

        assert jobs, jobs
        assert jobs[0]['name'] == 'job_id_00001'
        assert jobs[0]['url'] == '/jobbrowser/jobs/job_id_00001'

  @patch('notebook.connectors.hiveserver2.has_jobbrowser', False)
  def test_get_jobs_without_jobbrowser(self):
    notebook = Mock()
    snippet = {'type': 'hive', 'properties': {}}
    logs = ''

    with patch('notebook.connectors.hiveserver2.HS2Api._get_hive_execution_engine') as _get_hive_execution_engine:
      with patch('notebook.connectors.hiveserver2.parse_out_jobs') as parse_out_jobs:

        _get_hive_execution_engine.return_value = 'tez'
        parse_out_jobs.return_value = [{'job_id': 'job_id_00001'}]

        jobs = HS2Api(self.user).get_jobs(notebook, snippet, logs)

        assert jobs, jobs
        assert jobs[0]['name'] == 'job_id_00001'
        assert jobs[0]['url'] == ''  # Is empty

  def test_close_statement(self):
    with patch('notebook.connectors.hiveserver2.HS2Api._get_db') as _get_db:
      _get_db.return_value = Mock(
        use=Mock(
        ),
        client=Mock(
          query=Mock(
            side_effect=QueryServerException(
              Exception('Execution error!'),
              message='Error while compiling statement: FAILED: HiveAccessControlException Permission denied'
            )
          ),
        ),
      )
      notebook = {}
      snippet = {
        'id': '7ccdd296-20a3-da33-16ec-db58149aba0b', 'type': 'impala', 'status': 'running', 'statementType': 'text',
        'statement': 'SELECT *\nFROM `default`.sample_07\nLIMIT 100\n;', 'aceCursorPosition': None, 'statementPath': '',
        'associatedDocumentUuid': None,
        'properties': {'settings': []},
        'result': {
          'id': 'd9a8dc1b-7f6d-169f-7dd7-660723cba3f4', 'type': 'table',
          'handle': {
            'secret': 'obUXjEDWTh+ke73YLlOlMw==', 'guid': '2iv5rEXrRE4AAAAABtXdxA==', 'operation_type': 0, 'has_result_set': True,
            'modified_row_count': None, 'log_context': None, 'session_guid': '2440c57bc3806c6e:598514f42764cc91', 'session_id': 2094,
            'session_type': 'impala', 'statement_id': 0, 'has_more_statements': False, 'statements_count': 1,
            'previous_statement_hash': '39b8e5b3c37fda5ebd438da23f3e198c914750a64aa147f819a6a1e0', 'start': {'row': 0, 'column': 0},
            'end': {'row': 0, 'column': 43}, 'statement': 'SELECT *\nFROM `default`.sample_07\nLIMIT 100'
          }
        }, 'database': 'default',
        'compute': {
          'id': 'default', 'name': 'default', 'namespace': 'default', 'interface': 'impala', 'type': 'direct', 'options': {}
        }, 'wasBatchExecuted': False, 'dialect': 'impala'
      }
      api = HS2Api(self.user)

      response = api.close_statement(notebook, snippet)
      assert response['status'] == 0

      snippet = {
        'id': '7ccdd296-20a3-da33-16ec-db58149aba0b', 'type': 'impala', 'status': 'running',
        'statementType': 'text', 'statement': 'SELECT *\nFROM `default`.sample_07\nLIMIT 100\n;',
        'aceCursorPosition': None, 'statementPath': '', 'associatedDocumentUuid': None,
        'properties': {'settings': []},
        'result': {
          'id': 'd9a8dc1b-7f6d-169f-7dd7-660723cba3f4', 'type': 'table',
          'handle': {
            'has_more_statements': False, 'statement_id': 0, 'statements_count': 1,
            'previous_statement_hash': '39b8e5b3c37fda5ebd438da23f3e198c914750a64aa147f819a6a1e0'
          }
        }, 'database': 'default', 'compute': {'id': 'default', 'name': 'default', 'namespace': 'default',
        'interface': 'impala', 'type': 'direct', 'options': {}}, 'wasBatchExecuted': False, 'dialect': 'impala'
      }
      api = HS2Api(self.user)

      response = api.close_statement(notebook, snippet)
      assert response['status'] == -1  # snippet['result']['handel'] ['guid'] and ['secret'] are missing

  def test_get_error_message_from_query(self):
    with patch('notebook.connectors.hiveserver2.HS2Api._get_db') as _get_db:
      with patch('notebook.connectors.hiveserver2.HS2Api._get_current_statement') as _get_current_statement:
        with patch('notebook.connectors.hiveserver2.HS2Api._get_session') as _get_session:
          with patch('notebook.connectors.hiveserver2.HS2Api._prepare_hql_query') as _prepare_hql_query:
            with patch('notebook.connectors.hiveserver2.HS2Api._get_session_by_id') as _get_session_by_id:
              _get_db.return_value = Mock(
                use=Mock(
                ),
                client=Mock(
                  query=Mock(
                    side_effect=QueryServerException(
                      Exception('Execution error!'),
                      message='Error while compiling statement: FAILED: HiveAccessControlException Permission denied'
                    )
                  ),
                ),
              )
              notebook, snippet = {}, {'type': 'hive'}

              api = HS2Api(self.user)

              with pytest.raises(QueryError):
                api.execute(notebook, snippet)

              try:
                api = api.execute(notebook, snippet)
              except QueryError as e:
                assert (
                  e.message ==
                  'Error while compiling statement: FAILED: HiveAccessControlException Permission denied')

  def test_autocomplete_time_out(self):
    snippet = {'type': 'hive', 'properties': {}}

    with patch('notebook.connectors.hiveserver2._autocomplete') as _autocomplete:

      _autocomplete.return_value = {
        'code': 500,
        'error': "HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)"
      }

      api = HS2Api(self.user)

      try:
        resp = api.autocomplete(snippet, database='database')
        assert not True
      except QueryExpired as e:
        assert e.message == "HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)"

  def test_autocomplete_functions_hive(self):
    snippet = {'type': 'hive', 'properties': {}}

    with patch('notebook.connectors.hiveserver2.HS2Api._get_db') as _get_db:
      with patch('beeswax.api._get_functions') as _get_functions:
        db = Mock()
        _get_functions.return_value = [
          {'name': 'f1'}, {'name': 'f2'}, {'name': 'f3'}
        ]

        api = HS2Api(self.user)
        data = api.autocomplete(snippet, operation='functions')

        assert (
          data['functions'] ==
          [{'name': 'f1'}, {'name': 'f2'}, {'name': 'f3'}])

  def test_describe_column_view(self):
    mock_get_db = Mock(get_table=Mock(return_value=Mock(is_view=True)), get_table_columns_stats=Mock())
    with patch('notebook.connectors.hiveserver2.HS2Api._get_db', return_value=mock_get_db) as _get_db:
      with patch('notebook.connectors.hiveserver2.LOG') as LOG:
        api = HS2Api(self.user)

        result = api.describe_column({}, {}, 'test_db', 'test_view', 'test_col')

        LOG.debug.assert_called_with('Cannot describe column for view: test_view')
        assert result['message'] == 'Cannot describe column for view: test_view'
        _get_db.get_table_columns_stats.assert_not_called()

  def test_describe_column_table(self):
    mock_get_db = Mock(
      get_table=Mock(return_value=Mock(is_view=False)),
      get_table_columns_stats=Mock(return_value=[{'test_field1': 'value1', 'test_field2': 'value2'}]),
    )
    with patch('notebook.connectors.hiveserver2.HS2Api._get_db', return_value=mock_get_db) as _get_db:
      api = HS2Api(self.user)

      result = api.describe_column({}, {}, 'test_db', 'test_table', 'test_col')

      assert result == [{'test_field1': 'value1', 'test_field2': 'value2'}]


@pytest.mark.django_db
class TestHiveserver2ApiNonMock(object):

  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="test", recreate=False, is_superuser=False)
    self.user = User.objects.get(username='test')

    add_to_group('test')
    grant_access("test", "test", "notebook")
    grant_access("test", "test", "hive")

    self.db = dbms.get(self.user, get_query_server_config())
    self.api = HS2Api(self.user)

  def test_prepare_hql_query(self):
    statement = "SELECT myUpper(description) FROM sample_07 LIMIT 10"
    snippet_json = """
        {
            "status": "running",
            "database": "default",
            "properties": {
                "files": [],
                "functions": [{
                    "class_name": "org.hue.udf.MyUpper",
                    "name": "myUpper"
                }],
                "settings": []
            },
            "result": {
                "handle": {
                    "log_context": null,
                    "statements_count": 1,
                    "statement_id": 0,
                    "has_more_statements": false,
                    "secret": "UVZXF/qtTQumumz0Q8tNDQ==",
                    "has_result_set": true,
                    "operation_type": 0,
                    "modified_row_count": null,
                    "guid": "ZxOd4IjqTeK1PUTq+MdcDA=="
                },
                "type": "table",
                "id": "ae81b805-dcf1-9692-0452-797681e997ed"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "id": "9b50e364-f7b2-303d-e924-db8b0bd9866d"
        }
    """ % {'statement': statement}
    session_json = """
            {
                "type": "hive",
                "properties": [
                    {
                        "multiple": true,
                        "value": [
                            {
                                "path": "/user/test/myudfs.jar",
                                "type": "jar"
                            }
                        ],
                        "nice_name": "Files",
                        "key": "files",
                        "help_text": "Add one or more files, jars, or archives to the list of resources.",
                        "type": "hdfs-files"
                    },
                    {
                        "multiple": true,
                        "value": [
                            {
                                "class_name": "org.hue.udf.MyUpper",
                                "name": "myUpper"
                            }
                        ],
                        "nice_name": "Functions",
                        "key": "functions",
                        "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
                        "type": "functions"
                    },
                    {
                        "multiple": true,
                        "value": [
                            {
                                "value": "spark",
                                "key": "hive.execution.engine"
                            }
                        ],
                        "nice_name": "Settings",
                        "key": "settings",
                        "help_text": "Hive and Hadoop configuration properties.",
                        "type": "settings",
                        "options": [
                            "hive.map.aggr",
                            "hive.exec.compress.output",
                            "hive.exec.parallel",
                            "hive.execution.engine",
                            "mapreduce.job.queuename"
                        ]
                    }
                ],
                "id": 30
            }
    """

    snippet = json.loads(snippet_json)
    session = json.loads(session_json)
    hql_query = self.api._prepare_hql_query(snippet, statement, session)

    assert [{'key': 'hive.execution.engine', 'value': 'spark'}] == hql_query.settings
    assert [{'type': 'jar', 'path': '/user/test/myudfs.jar'}] == hql_query.file_resources
    assert [{'name': 'myUpper', 'class_name': 'org.hue.udf.MyUpper'}] == hql_query.functions

    config_statements = ', '.join(hql_query.get_configuration_statements())

    pattern = re.compile("ADD JAR hdfs://[A-Za-z0-9.:_-]+/user/test/myudfs.jar")
    assert pattern.search(config_statements), config_statements
    assert "CREATE TEMPORARY FUNCTION myUpper AS 'org.hue.udf.MyUpper'" in config_statements, config_statements

  def test_upgrade_properties(self):
    properties = None
    # Verify that upgrade will return defaults if current properties not formatted as settings
    upgraded_props = self.api.upgrade_properties(lang='hive', properties=properties)
    assert upgraded_props == self.api.get_properties(lang='hive')

    # Verify that upgrade will save old properties and new settings
    properties = [
        {
            'key': 'hive.execution.engine',
            'value': 'mr'
        },
        {
            'key': 'hive.exec.compress.output',
            'value': False
        }
    ]
    upgraded_props = self.api.upgrade_properties(lang='hive', properties=properties)
    settings = next((prop for prop in upgraded_props if prop['key'] == 'settings'), None)
    assert settings['value'] == properties

    # Verify that already upgraded properties will be unchanged
    properties = [
        {
            "multiple": True,
            "value": [],
            "nice_name": "Files",
            "key": "files",
            "help_text": "Add one or more files, jars, or archives to the list of resources.",
            "type": "hdfs-files"
        },
        {
            "multiple": True,
            "value": [],
            "nice_name": "Functions",
            "key": "functions",
            "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
            "type": "functions"
        },
        {
            "multiple": True,
            "value": [
                {
                    "key": "hive.execution.engine",
                    "value": "spark"
                }
            ],
            "nice_name": "Settings",
            "key": "settings",
            "help_text": "Hive and Hadoop configuration properties.",
            "type": "settings",
            "options": [
                "hive.map.aggr",
                "hive.exec.compress.output",
                "hive.exec.parallel",
                "hive.execution.engine",
                "mapreduce.job.queuename"
            ]
        }
    ]
    upgraded_props = self.api.upgrade_properties(lang='hive', properties=properties)
    assert upgraded_props == properties

  def test_progress(self):
    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 2,
                  "has_more_statements": true
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': "SELECT * FROM sample_07;"}
    )

    logs = """INFO  : Compiling command(queryId=hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb): SELECT app,
                 AVG(bytes) AS avg_bytes
        FROM web_logs
        GROUP BY  app
        HAVING app IS NOT NULL
        ORDER BY avg_bytes DESC
        INFO  : Semantic Analysis Completed
        INFO  : Returning Hive schema: Schema(fieldSchemas:[FieldSchema(name:app, type:string, comment:null), FieldSchema(name:avg_bytes, type:double, comment:null)], properties:null)
        INFO  : Completed compiling command(queryId=hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb); Time taken: 0.116 seconds
        INFO  : Executing command(queryId=hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb): SELECT app,
                 AVG(bytes) AS avg_bytes
        FROM web_logs
        GROUP BY  app
        HAVING app IS NOT NULL
        ORDER BY avg_bytes DESC
        INFO  : Query ID = hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb
        INFO  : Total jobs = 2
        INFO  : Launching Job 1 out of 2
        INFO  : Starting task [Stage-1:MAPRED] in serial mode
        INFO  : Number of reduce tasks not specified. Estimated from input data size: 1
        INFO  : In order to change the average load for a reducer (in bytes):
        INFO  :   set hive.exec.reducers.bytes.per.reducer=<number>
        INFO  : In order to limit the maximum number of reducers:
        INFO  :   set hive.exec.reducers.max=<number>
        INFO  : In order to set a constant number of reducers:
        INFO  :   set mapreduce.job.reduces=<number>
        INFO  : number of splits:1
        INFO  : Submitting tokens for job: job_1466104358744_0003
        INFO  : The url to track the job: http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466104358744_0003/
    """  # noqa: E501

    assert self.api.progress({}, snippet, logs=logs) == 5

    logs += """INFO  : Starting Job = job_1466104358744_0003, Tracking URL = """\
      """http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466104358744_0003/
        INFO  : Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1466104358744_0003
        INFO  : Hadoop job information for Stage-1: number of mappers: 1; number of reducers: 1
        INFO  : 2016-06-20 13:30:34,494 Stage-1 map = 0%,  reduce = 0%
        INFO  : 2016-06-20 13:30:47,081 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 3.13 sec
        INFO  : 2016-06-20 13:30:58,606 Stage-1 map = 100%,  reduce = 100%, Cumulative CPU 5.59 sec
        INFO  : MapReduce Total cumulative CPU time: 5 seconds 590 msec
        INFO  : Ended Job = job_1466104358744_0003
    """

    assert self.api.progress({}, snippet, logs=logs) == 50

    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 2,
                  "has_more_statements": true
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "impala",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': "SELECT * FROM sample_07;"}
    )

    logs = "Query 734a81444c85be66:d05f3bb1a6c2d0a5: 0% Complete (1 out of 4693)"

    assert self.api.progress({}, snippet, logs=logs) == 0

    logs += """Query 734a81444c85be66:d05f3bb1a6c2d0a5: 20% Complete (4 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 30% Complete (7 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 40% Complete (7 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 50% Complete (234 out of 4693)
    """

    assert self.api.progress({}, snippet, logs=logs) == 50

  def test_get_jobs(self):

    notebook = json.loads("""
      {
        "uuid": "f5d6394d-364f-56e8-6dd3-b1c5a4738c52",
        "id": 1234,
        "sessions": [{"type": "hive", "properties": [], "id": "1234"}],
        "type": "query-hive",
        "name": "Test Hiveserver2 Editor",
        "isSaved": false,
        "parentUuid": null
      }
    """)

    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 2,
                  "has_more_statements": true
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': "SELECT * FROM sample_07;"}
                         )

    logs = """INFO  : Compiling command(queryId=hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13): SELECT app,
                     AVG(bytes) AS avg_bytes
            FROM web_logs
            GROUP BY  app
            HAVING app IS NOT NULL
            ORDER BY avg_bytes DESC
            INFO  : Semantic Analysis Completed
            INFO  : Returning Hive schema: Schema(fieldSchemas:[FieldSchema(name:app, type:string, comment:null), FieldSchema(name:avg_bytes, type:double, comment:null)], properties:null)
            INFO  : Completed compiling command(queryId=hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13); Time taken: 0.073 seconds
            INFO  : Executing command(queryId=hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13): SELECT app,
                     AVG(bytes) AS avg_bytes
            FROM web_logs
            GROUP BY  app
            HAVING app IS NOT NULL
            ORDER BY avg_bytes DESC
            INFO  : Query ID = hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13
            INFO  : Total jobs = 2
            INFO  : Launching Job 1 out of 2
            INFO  : Starting task [Stage-1:MAPRED] in serial mode
            INFO  : Number of reduce tasks not specified. Estimated from input data size: 1
            INFO  : In order to change the average load for a reducer (in bytes):
            INFO  :   set hive.exec.reducers.bytes.per.reducer=<number>
            INFO  : In order to limit the maximum number of reducers:
            INFO  :   set hive.exec.reducers.max=<number>
            INFO  : In order to set a constant number of reducers:
            INFO  :   set mapreduce.job.reduces=<number>
            INFO  : number of splits:1
            INFO  : Submitting tokens for job: job_1466630204796_0059
            INFO  : The url to track the job: http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466630204796_0059/
            INFO  : Starting Job = job_1466630204796_0059, Tracking URL = http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466630204796_0059/
            INFO  : Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1466630204796_0059
    """  # noqa: E501

    jobs = self.api.get_jobs(notebook, snippet, logs)
    assert isinstance(jobs, list)
    assert len(jobs), 1
    assert jobs[0]['name'] == 'job_1466630204796_0059'
    assert jobs[0]['started'] is True
    assert jobs[0]['finished'] is False
    assert 'url' in jobs[0]

    logs += """INFO  : Hadoop job information for Stage-1: number of mappers: 1; number of reducers: 1
        INFO  : 2016-06-24 15:55:51,125 Stage-1 map = 0%,  reduce = 0%
        INFO  : 2016-06-24 15:56:00,410 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 2.12 sec
        INFO  : 2016-06-24 15:56:09,709 Stage-1 map = 100%,  reduce = 100%, Cumulative CPU 4.04 sec
        INFO  : MapReduce Total cumulative CPU time: 4 seconds 40 msec
        INFO  : Ended Job = job_1466630204796_0059
        INFO  : Launching Job 2 out of 2
    """

    jobs = self.api.get_jobs(notebook, snippet, logs)
    assert len(jobs), 1
    assert jobs[0]['name'] == 'job_1466630204796_0059'
    assert jobs[0]['started'] is True
    assert jobs[0]['finished'] is True

  def test_get_current_statement(self):
    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 1,
                  "has_more_statements": false
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': u"SELECT 'Привет', '你好';"}
    )

    statement = self.api._get_current_statement(MockDb(), snippet)

    assert '086ecec9a8b89b1b47cce358bdbb343be23b1f8b54ca76bc81927e27' == statement['previous_statement_hash']

  def test_plan_extraction_from_profile(self):
    query_plan = self.api._get_impala_profile_plan(
      query_id='e147228183f1f0b3:6f086cc600000000', profile=IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE
    )

    assert query_plan
    assert IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE_PLAN == query_plan


def MockDb():
  def close_operation(handle): pass


@pytest.mark.integration
class TestHiveserver2ApiWithHadoop(BeeswaxSampleProvider):

  @classmethod
  def setup_class(cls):
    if not is_live_cluster():
      pytest.skip('These tests can only run on a live cluster')

    super(TestHiveserver2ApiWithHadoop, cls).setup_class(load_data=False)

  def setup_method(self):
    self.client.post('/beeswax/install_examples')

    self.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "notebook")
    grant_access("test", "test", "impala")

    self.db = dbms.get(self.user, get_query_server_config())
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')
    self.api = HS2Api(self.user)

    self.statement = 'SELECT description, salary FROM sample_07 WHERE (sample_07.salary > 100000) ORDER BY salary DESC LIMIT 1000'

  def create_query_document(self, owner, query_type='hive', database='default',
                            name='Test Query', description='Test Query', statement='',
                            files=None, functions=None, settings=None):
    """
    Creates and returns a query Document2 object
    :param owner: owner of doc
    :param query_type: hive, impala or spark
    :param database: database name
    :param name: name of document
    :param description: description of document
    :param statement: SQL statement (can be multi-query statement)
    :param files: list of dicts representing files
    :param functions: list of dicts representing functions
    :param settings: list of dicts representing settings
    :return: Document2 object representing query
    """
    if query_type not in ('hive', 'impala', 'spark'):
      raise ValueError("Invalid query_type: %s" % query_type)

    notebook = make_notebook(name=name, description=description, editor_type=query_type, statement=statement,
                              status='ready', database=database, files=files, functions=functions, settings=settings)
    notebook_doc, save_as = _save_notebook(notebook.get_data(), owner)
    return notebook_doc

  def get_snippet(self, notebook, snippet_idx=0):
    data = notebook.get_data()
    snippet = data['snippets'][snippet_idx]

    if 'result' not in snippet:
      snippet['result'] = {}
    if 'handle' not in snippet['result']:
      snippet['result']['handle'] = {}

    return snippet

  def execute_and_wait(self, query_doc, snippet_idx=0, timeout=30.0, wait=1.0):
    notebook = Notebook(document=query_doc)
    snippet = self.get_snippet(notebook, snippet_idx=snippet_idx)

    curr = time.time()
    end = curr + timeout
    status = 'ready'

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    notebook = Notebook(document=query_doc)
    snippet = self.get_snippet(notebook, snippet_idx=snippet_idx)
    data = json.loads(response.content)
    snippet['result']['handle'] = data['handle']

    while status != 'available' and curr <= end:
      response = self.client.post(reverse('notebook:check_status'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
      data = json.loads(response.content)
      status = data['query_status']['status']
      snippet['status'] = status
      time.sleep(wait)
      curr = time.time()

    if status != 'available':
      raise Exception('Query failed to complete or return results.')

    return snippet

  def test_query_with_unicode(self):
    statement = "SELECT * FROM sample_07 WHERE code='한';"

    doc = self.create_query_document(owner=self.user, statement=statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)
    assert 0 == data['status'], data

    snippet['result']['handle'] = data['handle']

    response = self.client.post(reverse('notebook:get_logs'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert "SELECT * FROM sample_07 WHERE code='한'" in smart_str(data['logs'])

  def test_get_current_statement(self):
    multi_statement = "SELECT description, salary FROM sample_07 LIMIT 20;\r\nSELECT AVG(salary) FROM sample_07;"

    doc = self.create_query_document(owner=self.user, statement=multi_statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert 0 == data['status'], data
    assert 0 == data['handle']['statement_id'], data
    assert 2 == data['handle']['statements_count'], data
    assert True is data['handle']['has_more_statements'], data
    assert {'row': 0, 'column': 0} == data['handle']['start'], data
    assert {'row': 0, 'column': 51} == data['handle']['end'], data

    snippet['result']['handle'] = data['handle']

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert 0 == data['status'], data
    assert 1 == data['handle']['statement_id'], data
    assert 2 == data['handle']['statements_count'], data
    assert False is data['handle']['has_more_statements'], data
    assert {'row': 1, 'column': 0} == data['handle']['start'], data
    assert {'row': 1, 'column': 33} == data['handle']['end'], data

  def test_explain(self):
    # Hive 2 with Tez set hive.explain.user to true by default, but this test is expecting output when this setting
    # is set to false.
    doc = self.create_query_document(owner=self.user, statement=self.statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)
    snippet['properties']['settings'].append({"key": "hive.explain.user", "value": "false"})

    response = self.client.post(reverse('notebook:explain'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)

    assert 0 == data['status'], data
    assert 'STAGE DEPENDENCIES' in data['explanation'], data
    assert self.statement == data['statement'], data

  def test_download(self):
    statement = "SELECT 'hello world';"

    doc = self.create_query_document(owner=self.user, statement=statement)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0)

    response = self.client.post(reverse('notebook:download'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'format': 'csv'})

    assert 200 == response.status_code
    assert ('Content-Disposition', 'attachment; filename="Test Query.csv"') == response._headers['content-disposition']

  def test_get_sample(self):
    doc = self.create_query_document(owner=self.user, statement=self.statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)

    response = self.client.post(reverse('notebook:api_sample_data',
      kwargs={'database': 'default', 'table': 'sample_07'}),
      {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert 0 == data['status'], data
    assert 'headers' in data
    assert 'rows' in data
    assert len(data['rows']) > 0

    response = self.client.post(reverse('notebook:api_sample_data_column',
      kwargs={'database': 'default', 'table': 'sample_07', 'column': 'code'}),
      {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert 0 == data['status'], data
    assert 'headers' in data
    assert ['code'] == data['headers']
    assert 'rows' in data
    assert len(data['rows']) > 0

  def test_fetch_result_size_mr(self):
    if not is_live_cluster():  # Mini-cluster does not have JHS
      pytest.skip("Skipping Test")

    # Assert that a query with no job will return no rows or size
    statement = "SELECT 'hello world';"

    settings = [
        {
            'key': 'hive.execution.engine',
            'value': 'mr'
        }
    ]
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert 'result' in data
    assert 'rows' in data['result']
    assert 'size' in data['result']
    assert None is data['result']['rows']
    assert None is data['result']['size']

    # Assert that a query with map & reduce task returns rows
    statement = "SELECT DISTINCT code FROM sample_07;"
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert 'result' in data
    assert 'rows' in data['result']
    assert 'size' in data['result']
    assert 823 == data['result']['rows']
    assert data['result']['size'] > 0, data['result']

    # Assert that a query with multiple jobs returns rows
    statement = "SELECT app, COUNT(1) AS count FROM web_logs GROUP BY app ORDER BY count DESC;"
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=120.0, wait=2.0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert 'result' in data
    assert 'rows' in data['result']
    assert 23 == data['result']['rows']
    assert data['result']['size'] > 0, data['result']

  def test_fetch_result_size_spark(self):
    if not is_live_cluster() or not is_hive_on_spark():
      pytest.skip("Skipping Test")

    # TODO: Add session cleanup here so we don't have orphan spark sessions

    # Assert that a query with no job will return no rows or size
    statement = "SELECT 'hello world';"

    settings = [
        {
            'key': 'hive.execution.engine',
            'value': 'spark'
        }
    ]
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert 'result' in data
    assert 'rows' in data['result']
    assert 'size' in data['result']
    assert None is data['result']['rows']
    assert None is data['result']['size']

    # Assert that a query that runs a job will return rows and size
    statement = "SELECT app, COUNT(1) AS count FROM web_logs GROUP BY app ORDER BY count DESC;"
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert 'result' in data
    assert 'rows' in data['result']
    assert 'size' in data['result']
    assert 23 == data['result']['rows']
    assert data['result']['size'] > 0

  def test_fetch_result_size_impala(self):
    if not is_live_cluster():
      pytest.skip("Skipping Test")

    # Create session so that session object is saved to DB for server URL lookup
    session = self.api.create_session(lang='impala')

    try:
      # Assert that a query that runs a job will return rows
      statement = "SELECT app, COUNT(1) AS count FROM web_logs GROUP BY app ORDER BY count DESC;"
      doc = self.create_query_document(owner=self.user, query_type='impala', statement=statement)
      notebook = Notebook(document=doc)
      snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

      self.client.post(reverse('notebook:fetch_result_data'),
                       {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'rows': 100, 'startOver': 'false'})

      response = self.client.post(reverse('notebook:fetch_result_size'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

      data = json.loads(response.content)
      assert 0 == data['status'], data
      assert 'result' in data
      assert 'rows' in data['result']
      assert 'size' in data['result']
      assert 23 == data['result']['rows']
      assert None is data['result']['size']

      # Assert that selecting all from partitioned table works
      statement = "SELECT * FROM web_logs;"
      doc = self.create_query_document(owner=self.user, query_type='impala', statement=statement)
      notebook = Notebook(document=doc)
      snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=5.0)

      self.client.post(reverse('notebook:fetch_result_data'),
                       {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'rows': 100, 'startOver': 'false'})

      response = self.client.post(reverse('notebook:fetch_result_size'),
                                 {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

      data = json.loads(response.content)
      assert 0 == data['status'], data
      assert 'result' in data
      assert 'rows' in data['result']
      assert 1000 == data['result']['rows']
    finally:
      self.api.close_session(session)

  def test_fetch_result_abbreviated(self):
    if not is_live_cluster():
      pytest.skip("Skipping Test")

    # Create session so that session object is saved to DB for server URL lookup
    session = self.api.create_session(lang='impala')

    try:

      # Assert that abbreviated rows returned (e.g. - 1.00K) still returns actual rows
      statement = "SELECT * FROM web_logs;"
      doc = self.create_query_document(owner=self.user, query_type='impala', statement=statement)
      notebook = Notebook(document=doc)
      snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=5.0)

      self.client.post(reverse('notebook:fetch_result_data'),
                       {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'rows': 100, 'startOver': 'false'})

      response = self.client.post(reverse('notebook:fetch_result_size'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

      data = json.loads(response.content)
      assert 0 == data['status'], data
      assert 'result' in data
      assert 'rows' in data['result']
      assert 1000 == data['result']['rows']
    finally:
      self.api.close_session(session)


IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE_PLAN = """Query (id=e147228183f1f0b3:6f086cc600000000):
  Summary:
    Session ID: 4043f7580371e0e6:f1068bf772ce4cb3
    Session Type: HIVESERVER2
    HiveServer2 Protocol Version: V6
    Start Time: 2017-10-13 10:47:09.373244000
    End Time: 2017-10-13 10:50:08.731647000
    Query Type: QUERY
    Query State: FINISHED
    Query Status: OK
    Impala Version: impalad version 2.11.0-SNAPSHOT RELEASE (build e9a30f67655a8da5b8526507fbe853adbd184932)
    User: romain
    Connected User: romain
    Delegated User:
    Network Address: 172.21.3.229:60523
    Default Db: default
    Sql Statement:



-- Compute total amount per order for all customers
SELECT
  c.id AS customer_id,
 c.name AS customer_name,
  o.order_id,
  v.total
FROM
  customers c,
  c.orders o,
  (SELECT SUM(price * qty) total FROM o.items) v
    Coordinator: self-service-analytics-2.gce.cloudera.com:22000
    Query Options (set by configuration): QUERY_TIMEOUT_S=600
    Query Options (set by configuration and planner): QUERY_TIMEOUT_S=600,MT_DOP=0
    Plan:
----------------
Max Per-Host Resource Reservation: Memory=0B
Per-Host Resource Estimates: Memory=42.00MB
WARNING: The following tables have potentially corrupt table statistics.
Drop and re-compute statistics to resolve this problem.
default.customers
WARNING: The following tables are missing relevant table and/or column statistics.
default.customers

F01:PLAN FRAGMENT [UNPARTITIONED] hosts=1 instances=1
|  Per-Host Resources: mem-estimate=0B mem-reservation=0B
PLAN-ROOT SINK
|  mem-estimate=0B mem-reservation=0B
|
10:EXCHANGE [UNPARTITIONED]
|  mem-estimate=0B mem-reservation=0B
|  tuple-ids=3,1,0 row-size=75B cardinality=0
|
F00:PLAN FRAGMENT [RANDOM] hosts=1 instances=1
Per-Host Resources: mem-estimate=42.00MB mem-reservation=0B
01:SUBPLAN
|  mem-estimate=0B mem-reservation=0B
|  tuple-ids=3,1,0 row-size=75B cardinality=0
|
|--09:NESTED LOOP JOIN [CROSS JOIN]
|  |  mem-estimate=35B mem-reservation=0B
|  |  tuple-ids=3,1,0 row-size=75B cardinality=10
|  |
|  |--02:SINGULAR ROW SRC
|  |     parent-subplan=01
|  |     mem-estimate=0B mem-reservation=0B
|  |     tuple-ids=0 row-size=35B cardinality=1
|  |
|  04:SUBPLAN
|  |  mem-estimate=0B mem-reservation=0B
|  |  tuple-ids=3,1 row-size=40B cardinality=10
|  |
|  |--08:NESTED LOOP JOIN [CROSS JOIN]
|  |  |  mem-estimate=32B mem-reservation=0B
|  |  |  tuple-ids=3,1 row-size=40B cardinality=1
|  |  |
|  |  |--05:SINGULAR ROW SRC
|  |  |     parent-subplan=04
|  |  |     mem-estimate=0B mem-reservation=0B
|  |  |     tuple-ids=1 row-size=32B cardinality=1
|  |  |
|  |  07:AGGREGATE [FINALIZE]
|  |  |  output: sum(price * qty)
|  |  |  mem-estimate=10.00MB mem-reservation=0B spill-buffer=2.00MB
|  |  |  tuple-ids=3 row-size=8B cardinality=1
|  |  |
|  |  06:UNNEST [o.items]
|  |     parent-subplan=04
|  |     mem-estimate=0B mem-reservation=0B
|  |     tuple-ids=2 row-size=0B cardinality=10
|  |
|  03:UNNEST [c.orders o]
|     parent-subplan=01
|     mem-estimate=0B mem-reservation=0B
|     tuple-ids=1 row-size=0B cardinality=10
|
00:SCAN HDFS [default.customers c, RANDOM]
   partitions=1/1 files=1 size=15.44KB
   predicates: !empty(c.orders)
   stats-rows=0 extrapolated-rows=disabled
   table stats: rows=0 size=15.44KB
   column stats: unavailable
   mem-estimate=32.00MB mem-reservation=0B
   tuple-ids=0 row-size=35B cardinality=0
----------------
    Estimated Per-Host Mem: 44040259
    Tables Missing Stats: default.customers
    Tables With Corrupt Table Stats: default.customers
    Per Host Min Reservation: self-service-analytics-2.gce.cloudera.com:22000(0)
    Request Pool: root.romain
    Admission result: Admitted immediately
    ExecSummary:
Operator                       #Hosts  Avg Time  Max Time  #Rows  Est. #Rows   Peak Mem  Est. Peak Mem  Detail
----------------------------------------------------------------------------------------------------------------------------
10:EXCHANGE                         1  62.005ms  62.005ms    106           0          0              0  UNPARTITIONED
01:SUBPLAN                          1   0.000ns   0.000ns      0           0  140.00 KB              0
|--09:NESTED LOOP JOIN              1   0.000ns   0.000ns  5.67K          10   32.00 KB        35.00 B  CROSS JOIN
|  |--02:SINGULAR ROW SRC           1   0.000ns   0.000ns      0           1          0              0
|  04:SUBPLAN                       1   0.000ns   0.000ns      0          10    8.00 KB              0
|  |--08:NESTED LOOP JOIN           1   0.000ns   0.000ns    160           1   24.00 KB        32.00 B  CROSS JOIN
|  |  |--05:SINGULAR ROW SRC        1   0.000ns   0.000ns      0           1          0              0
|  |  07:AGGREGATE                  1   0.000ns   0.000ns      1           1   16.00 KB       10.00 MB  FINALIZE
|  |  06:UNNEST                     1   0.000ns   0.000ns      2          10          0              0  o.items
|  03:UNNEST                        1   0.000ns   0.000ns      2          10          0              0  c.orders o
00:SCAN HDFS                        1  39.003ms  39.003ms     53           0  417.04 KB       32.00 MB  default.customers c
    Errors:
    Planner Timeline: 36.379ms
       - Analysis finished: 13.156ms (13.156ms)
       - Equivalence classes computed: 13.775ms (619.949us)
       - Single node plan created: 20.763ms (6.987ms)
       - Runtime filters computed: 21.325ms (562.117us)
       - Distributed plan created: 21.460ms (135.254us)
       - Lineage info computed: 21.684ms (223.594us)
       - Planning finished: 36.379ms (14.694ms)
    Query Timeline: 2m59s
       - Query submitted: 0.000ns (0.000ns)
       - Planning finished: 42.003ms (42.003ms)
       - Submit for admission: 43.003ms (1.000ms)
       - Completed admission: 43.003ms (0.000ns)
       - Ready to start on 1 backends: 43.003ms (0.000ns)
       - All 1 execution backends (2 fragment instances) started: 44.003ms (1.000ms)
       - Rows available: 121.009ms (77.006ms)
       - First row fetched: 1s152ms (1s031ms)
       - Unregister query: 2m59s (2m58s)
     - ComputeScanRangeAssignmentTimer: 0.000ns
  ImpalaServer:
     - ClientFetchWaitTimer: 2m59s
     - RowMaterializationTimer: 1.000ms
  Execution Profile e147228183f1f0b3:6f086cc600000000"""

IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE = IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE_PLAN + \
  """:(Total: 79.006ms, non-child: 0.000ns, % non-child: 0.00%)
    Number of filters: 0
    Filter routing table:
 ID  Src. Node  Tgt. Node(s)  Target type  Partition filter  Pending (Expected)  First arrived  Completed   Enabled
-------------------------------------------------------------------------------------------------------------------

    Backend startup latencies: Count: 1, min / max: 1ms / 1ms, 25th %-ile: 1ms, 50th %-ile: 1ms, """\
      """75th %-ile: 1ms, 90th %-ile: 1ms, 95th %-ile: 1ms, 99.9th %-ile: 1ms
    Per Node Peak Memory Usage: self-service-analytics-2.gce.cloudera.com:22000(530.52 KB)
     - FiltersReceived: 0 (0)
     - FinalizationTimer: 0.000ns
    Averaged Fragment F01:(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
      split sizes:  min: 0, max: 0, avg: 0, stddev: 0
      completion times: min:2m59s  max:2m59s  mean: 2m59s  stddev:0.000ns
      execution rates: min:0.00 /sec  max:0.00 /sec  mean:0.00 /sec  stddev:0.00 /sec
      num instances: 1
       - AverageThreadTokens: 0.00
       - BloomFilterBytes: 0
       - PeakMemoryUsage: 34.12 KB (34939)
       - PeakReservation: 0
       - PeakUsedReservation: 0
       - PerHostPeakMemUsage: 530.52 KB (543253)
       - RowsProduced: 106 (106)
       - TotalNetworkReceiveTime: 62.005ms
       - TotalNetworkSendTime: 0.000ns
       - TotalStorageWaitTime: 0.000ns
       - TotalThreadsInvoluntaryContextSwitches: 0 (0)
       - TotalThreadsTotalWallClockTime: 62.005ms
         - TotalThreadsSysTime: 3.000us
         - TotalThreadsUserTime: 12.000us
       - TotalThreadsVoluntaryContextSwitches: 1 (1)
      Fragment Instance Lifecycle Timings:
         - ExecTime: 0.000ns
           - ExecTreeExecTime: 0.000ns
         - OpenTime: 62.005ms
           - ExecTreeOpenTime: 62.005ms
         - PrepareTime: 14.001ms
           - ExecTreePrepareTime: 0.000ns
      PLAN_ROOT_SINK:
         - PeakMemoryUsage: 0
      CodeGen:(Total: 13.001ms, non-child: 13.001ms, % non-child: 100.00%)
         - CodegenTime: 0.000ns
         - CompileTime: 0.000ns
         - LoadTime: 0.000ns
         - ModuleBitcodeSize: 1.84 MB (1929624)
         - NumFunctions: 0 (0)
         - NumInstructions: 0 (0)
         - OptimizationTime: 0.000ns
         - PeakMemoryUsage: 0
         - PrepareTime: 13.001ms
      EXCHANGE_NODE (id=10):(Total: 62.005ms, non-child: 62.005ms, % non-child: 100.00%)
         - ConvertRowBatchTime: 0.000ns
         - PeakMemoryUsage: 0
         - RowsReturned: 106 (106)
         - RowsReturnedRate: 1.71 K/sec
        DataStreamReceiver:
           - BytesReceived: 5.50 KB (5632)
           - DeserializeRowBatchTimer: 0.000ns
           - FirstBatchArrivalWaitTime: 62.005ms
           - PeakMemoryUsage: 10.12 KB (10363)
           - SendersBlockedTimer: 0.000ns
           - SendersBlockedTotalTimer(*): 0.000ns
    Coordinator Fragment F01:
      Instance e147228183f1f0b3:6f086cc600000000 (host=self-service-analytics-2.gce.cloudera.com:22000):"""\
        """(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
        MemoryUsage(4s000ms): 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, """\
          """31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, """\
          """31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, """\
          """31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB
         - AverageThreadTokens: 0.00
         - BloomFilterBytes: 0
         - PeakMemoryUsage: 34.12 KB (34939)
         - PeakReservation: 0
         - PeakUsedReservation: 0
         - PerHostPeakMemUsage: 530.52 KB (543253)
         - RowsProduced: 106 (106)
         - TotalNetworkReceiveTime: 62.005ms
         - TotalNetworkSendTime: 0.000ns
         - TotalStorageWaitTime: 0.000ns
         - TotalThreadsInvoluntaryContextSwitches: 0 (0)
         - TotalThreadsTotalWallClockTime: 62.005ms
           - TotalThreadsSysTime: 3.000us
           - TotalThreadsUserTime: 12.000us
         - TotalThreadsVoluntaryContextSwitches: 1 (1)
        Fragment Instance Lifecycle Timings:
           - ExecTime: 0.000ns
             - ExecTreeExecTime: 0.000ns
           - OpenTime: 62.005ms
             - ExecTreeOpenTime: 62.005ms
           - PrepareTime: 14.001ms
             - ExecTreePrepareTime: 0.000ns
        PLAN_ROOT_SINK:
           - PeakMemoryUsage: 0
        CodeGen:(Total: 13.001ms, non-child: 13.001ms, % non-child: 100.00%)
           - CodegenTime: 0.000ns
           - CompileTime: 0.000ns
           - LoadTime: 0.000ns
           - ModuleBitcodeSize: 1.84 MB (1929624)
           - NumFunctions: 0 (0)
           - NumInstructions: 0 (0)
           - OptimizationTime: 0.000ns
           - PeakMemoryUsage: 0
           - PrepareTime: 13.001ms
        EXCHANGE_NODE (id=10):(Total: 62.005ms, non-child: 62.005ms, % non-child: 100.00%)
           - ConvertRowBatchTime: 0.000ns
           - PeakMemoryUsage: 0
           - RowsReturned: 106 (106)
           - RowsReturnedRate: 1.71 K/sec
          DataStreamReceiver:
            BytesReceived(4s000ms): 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, """\
              """5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, """\
              """5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, """\
              """5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB
             - BytesReceived: 5.50 KB (5632)
             - DeserializeRowBatchTimer: 0.000ns
             - FirstBatchArrivalWaitTime: 62.005ms
             - PeakMemoryUsage: 10.12 KB (10363)
             - SendersBlockedTimer: 0.000ns
             - SendersBlockedTotalTimer(*): 0.000ns
    Averaged Fragment F00:(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
      split sizes:  min: 15.44 KB, max: 15.44 KB, avg: 15.44 KB, stddev: 0
      completion times: min:78.006ms  max:78.006ms  mean: 78.006ms  stddev:0.000ns
      execution rates: min:197.95 KB/sec  max:197.95 KB/sec  mean:197.95 KB/sec  stddev:0.00 /sec
      num instances: 1
       - AverageThreadTokens: 0.00
       - BloomFilterBytes: 0
       - PeakMemoryUsage: 506.52 KB (518677)
       - PeakReservation: 0
       - PeakUsedReservation: 0
       - PerHostPeakMemUsage: 530.52 KB (543253)
       - RowsProduced: 106 (106)
       - TotalNetworkReceiveTime: 0.000ns
       - TotalNetworkSendTime: 0.000ns
       - TotalStorageWaitTime: 38.003ms
       - TotalThreadsInvoluntaryContextSwitches: 1 (1)
       - TotalThreadsTotalWallClockTime: 100.008ms
         - TotalThreadsSysTime: 1.520ms
         - TotalThreadsUserTime: 22.153ms
       - TotalThreadsVoluntaryContextSwitches: 8 (8)
      Fragment Instance Lifecycle Timings:
         - ExecTime: 39.003ms
           - ExecTreeExecTime: 39.003ms
         - OpenTime: 22.001ms
           - ExecTreeOpenTime: 0.000ns
         - PrepareTime: 15.001ms
           - ExecTreePrepareTime: 0.000ns
      DataStreamSender (dst_id=10):
         - BytesSent: 5.50 KB (5632)
         - NetworkThroughput(*): 0.00 /sec
         - OverallThroughput: 0.00 /sec
         - PeakMemoryUsage: 4.85 KB (4968)
         - RowsReturned: 106 (106)
         - SerializeBatchTime: 0.000ns
         - TransmitDataRPCTime: 0.000ns
         - UncompressedRowBatchSize: 8.89 KB (9103)
      CodeGen:(Total: 36.002ms, non-child: 36.002ms, % non-child: 100.00%)
         - CodegenTime: 2.000ms
         - CompileTime: 7.000ms
         - LoadTime: 0.000ns
         - ModuleBitcodeSize: 1.84 MB (1929624)
         - NumFunctions: 23 (23)
         - NumInstructions: 365 (365)
         - OptimizationTime: 15.001ms
         - PeakMemoryUsage: 182.50 KB (186880)
         - PrepareTime: 14.001ms
      SUBPLAN_NODE (id=1):(Total: 39.003ms, non-child: 0.000ns, % non-child: 0.00%)
         - PeakMemoryUsage: 140.00 KB (143360)
         - RowsReturned: 0 (0)
         - RowsReturnedRate: 0
        NESTED_LOOP_JOIN_NODE (id=9):
           - BuildRows: 0 (0)
           - BuildTime: 0.000ns
           - PeakMemoryUsage: 32.00 KB (32768)
           - ProbeRows: 106 (106)
           - ProbeTime: 0.000ns
           - RowsReturned: 5.67K (5671)
           - RowsReturnedRate: 0
          Nested Loop Join Builder:
             - PeakMemoryUsage: 8.00 KB (8192)
          SINGULAR_ROW_SRC_NODE (id=2):
             - PeakMemoryUsage: 0
             - RowsReturned: 0 (0)
             - RowsReturnedRate: 0
        SUBPLAN_NODE (id=4):
           - PeakMemoryUsage: 8.00 KB (8192)
           - RowsReturned: 0 (0)
           - RowsReturnedRate: 0
          NESTED_LOOP_JOIN_NODE (id=8):
             - BuildRows: 0 (0)
             - BuildTime: 0.000ns
             - PeakMemoryUsage: 24.00 KB (24576)
             - ProbeRows: 106 (106)
             - ProbeTime: 0.000ns
             - RowsReturned: 160 (160)
             - RowsReturnedRate: 0
            Nested Loop Join Builder:
               - PeakMemoryUsage: 8.00 KB (8192)
            SINGULAR_ROW_SRC_NODE (id=5):
               - PeakMemoryUsage: 0
               - RowsReturned: 0 (0)
               - RowsReturnedRate: 0
          AGGREGATION_NODE (id=7):
             - BuildTime: 0.000ns
             - GetResultsTime: 0.000ns
             - HTResizeTime: 0.000ns
             - HashBuckets: 0 (0)
             - LargestPartitionPercent: 0 (0)
             - MaxPartitionLevel: 0 (0)
             - NumRepartitions: 0 (0)
             - PartitionsCreated: 0 (0)
             - PeakMemoryUsage: 16.00 KB (16384)
             - RowsRepartitioned: 0 (0)
             - RowsReturned: 1 (1)
             - RowsReturnedRate: 0
             - SpilledPartitions: 0 (0)
          UNNEST_NODE (id=6):
             - AvgCollectionSize: 1.50
             - MaxCollectionSize: 3 (3)
             - MinCollectionSize: 1 (1)
             - NumCollections: 106 (106)
             - PeakMemoryUsage: 0
             - RowsReturned: 2 (2)
             - RowsReturnedRate: 0
        UNNEST_NODE (id=3):
           - AvgCollectionSize: 2.00
           - MaxCollectionSize: 3 (3)
           - MinCollectionSize: 1 (1)
           - NumCollections: 53 (53)
           - PeakMemoryUsage: 0
           - RowsReturned: 2 (2)
           - RowsReturnedRate: 0
      HDFS_SCAN_NODE (id=0):(Total: 39.003ms, non-child: 39.003ms, % non-child: 100.00%)
         - AverageHdfsReadThreadConcurrency: 0.00
         - AverageScannerThreadConcurrency: 0.00
         - BytesRead: 19.30 KB (19766)
         - BytesReadDataNodeCache: 0
         - BytesReadLocal: 19.30 KB (19766)
         - BytesReadRemoteUnexpected: 0
         - BytesReadShortCircuit: 19.30 KB (19766)
         - CachedFileHandlesHitCount: 5 (5)
         - CachedFileHandlesMissCount: 1 (1)
         - CollectionItemsRead: 265 (265)
         - DecompressionTime: 0.000ns
         - MaxCompressedTextFileLength: 0
         - NumColumns: 5 (5)
         - NumDictFilteredRowGroups: 0 (0)
         - NumDisksAccessed: 1 (1)
         - NumRowGroups: 1 (1)
         - NumScannerThreadsStarted: 1 (1)
         - NumScannersWithNoReads: 0 (0)
         - NumStatsFilteredRowGroups: 0 (0)
         - PeakMemoryUsage: 417.04 KB (427045)
         - PerReadThreadRawHdfsThroughput: 507.92 KB/sec
         - RemoteScanRanges: 0 (0)
         - RowBatchQueueGetWaitTime: 39.003ms
         - RowBatchQueuePutWaitTime: 0.000ns
         - RowsRead: 53 (53)
         - RowsReturned: 53 (53)
         - RowsReturnedRate: 1.36 K/sec
         - ScanRangesComplete: 1 (1)
         - ScannerThreadsInvoluntaryContextSwitches: 0 (0)
         - ScannerThreadsTotalWallClockTime: 39.003ms
           - MaterializeTupleTime(*): 1.000ms
           - ScannerThreadsSysTime: 346.000us
           - ScannerThreadsUserTime: 346.000us
         - ScannerThreadsVoluntaryContextSwitches: 4 (4)
         - TotalRawHdfsReadTime(*): 38.003ms
         - TotalReadThroughput: 0.00 /sec
    Fragment F00:
      Instance e147228183f1f0b3:6f086cc600000001 (host=self-service-analytics-2.gce.cloudera.com:22000):"""\
        """(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
        Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/15.44 KB
         - AverageThreadTokens: 0.00
         - BloomFilterBytes: 0
         - PeakMemoryUsage: 506.52 KB (518677)
         - PeakReservation: 0
         - PeakUsedReservation: 0
         - PerHostPeakMemUsage: 530.52 KB (543253)
         - RowsProduced: 106 (106)
         - TotalNetworkReceiveTime: 0.000ns
         - TotalNetworkSendTime: 0.000ns
         - TotalStorageWaitTime: 38.003ms
         - TotalThreadsInvoluntaryContextSwitches: 1 (1)
         - TotalThreadsTotalWallClockTime: 100.008ms
           - TotalThreadsSysTime: 1.520ms
           - TotalThreadsUserTime: 22.153ms
         - TotalThreadsVoluntaryContextSwitches: 8 (8)
        Fragment Instance Lifecycle Timings:
           - ExecTime: 39.003ms
             - ExecTreeExecTime: 39.003ms
           - OpenTime: 22.001ms
             - ExecTreeOpenTime: 0.000ns
           - PrepareTime: 15.001ms
             - ExecTreePrepareTime: 0.000ns
        DataStreamSender (dst_id=10):
           - BytesSent: 5.50 KB (5632)
           - NetworkThroughput(*): 0.00 /sec
           - OverallThroughput: 0.00 /sec
           - PeakMemoryUsage: 4.85 KB (4968)
           - RowsReturned: 106 (106)
           - SerializeBatchTime: 0.000ns
           - TransmitDataRPCTime: 0.000ns
           - UncompressedRowBatchSize: 8.89 KB (9103)
        CodeGen:(Total: 36.002ms, non-child: 36.002ms, % non-child: 100.00%)
           - CodegenTime: 2.000ms
           - CompileTime: 7.000ms
           - LoadTime: 0.000ns
           - ModuleBitcodeSize: 1.84 MB (1929624)
           - NumFunctions: 23 (23)
           - NumInstructions: 365 (365)
           - OptimizationTime: 15.001ms
           - PeakMemoryUsage: 182.50 KB (186880)
           - PrepareTime: 14.001ms
        SUBPLAN_NODE (id=1):(Total: 39.003ms, non-child: 0.000ns, % non-child: 0.00%)
           - PeakMemoryUsage: 140.00 KB (143360)
           - RowsReturned: 0 (0)
           - RowsReturnedRate: 0
          NESTED_LOOP_JOIN_NODE (id=9):
             - BuildRows: 0 (0)
             - BuildTime: 0.000ns
             - PeakMemoryUsage: 32.00 KB (32768)
             - ProbeRows: 106 (106)
             - ProbeTime: 0.000ns
             - RowsReturned: 5.67K (5671)
             - RowsReturnedRate: 0
            Nested Loop Join Builder:
               - PeakMemoryUsage: 8.00 KB (8192)
            SINGULAR_ROW_SRC_NODE (id=2):
               - PeakMemoryUsage: 0
               - RowsReturned: 0 (0)
               - RowsReturnedRate: 0
          SUBPLAN_NODE (id=4):
             - PeakMemoryUsage: 8.00 KB (8192)
             - RowsReturned: 0 (0)
             - RowsReturnedRate: 0
            NESTED_LOOP_JOIN_NODE (id=8):
               - BuildRows: 0 (0)
               - BuildTime: 0.000ns
               - PeakMemoryUsage: 24.00 KB (24576)
               - ProbeRows: 106 (106)
               - ProbeTime: 0.000ns
               - RowsReturned: 160 (160)
               - RowsReturnedRate: 0
              Nested Loop Join Builder:
                 - PeakMemoryUsage: 8.00 KB (8192)
              SINGULAR_ROW_SRC_NODE (id=5):
                 - PeakMemoryUsage: 0
                 - RowsReturned: 0 (0)
                 - RowsReturnedRate: 0
            AGGREGATION_NODE (id=7):
              ExecOption: Codegen Enabled
               - BuildTime: 0.000ns
               - GetResultsTime: 0.000ns
               - HTResizeTime: 0.000ns
               - HashBuckets: 0 (0)
               - LargestPartitionPercent: 0 (0)
               - MaxPartitionLevel: 0 (0)
               - NumRepartitions: 0 (0)
               - PartitionsCreated: 0 (0)
               - PeakMemoryUsage: 16.00 KB (16384)
               - RowsRepartitioned: 0 (0)
               - RowsReturned: 1 (1)
               - RowsReturnedRate: 0
               - SpilledPartitions: 0 (0)
            UNNEST_NODE (id=6):
               - AvgCollectionSize: 1.50
               - MaxCollectionSize: 3 (3)
               - MinCollectionSize: 1 (1)
               - NumCollections: 106 (106)
               - PeakMemoryUsage: 0
               - RowsReturned: 2 (2)
               - RowsReturnedRate: 0
          UNNEST_NODE (id=3):
             - AvgCollectionSize: 2.00
             - MaxCollectionSize: 3 (3)
             - MinCollectionSize: 1 (1)
             - NumCollections: 53 (53)
             - PeakMemoryUsage: 0
             - RowsReturned: 2 (2)
             - RowsReturnedRate: 0
        HDFS_SCAN_NODE (id=0):(Total: 39.003ms, non-child: 39.003ms, % non-child: 100.00%)
          Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/15.44 KB
          ExecOption: PARQUET Codegen Enabled, Codegen enabled: 1 out of 1
          Hdfs Read Thread Concurrency Bucket: 0:0% 1:0% 2:0% 3:0% 4:0%
          File Formats: PARQUET/NONE:5
           - FooterProcessingTime: (Avg: 38.003ms ; Min: 38.003ms ; Max: 38.003ms ; Number of samples: 1)
           - AverageHdfsReadThreadConcurrency: 0.00
           - AverageScannerThreadConcurrency: 0.00
           - BytesRead: 19.30 KB (19766)
           - BytesReadDataNodeCache: 0
           - BytesReadLocal: 19.30 KB (19766)
           - BytesReadRemoteUnexpected: 0
           - BytesReadShortCircuit: 19.30 KB (19766)
           - CachedFileHandlesHitCount: 5 (5)
           - CachedFileHandlesMissCount: 1 (1)
           - CollectionItemsRead: 265 (265)
           - DecompressionTime: 0.000ns
           - MaxCompressedTextFileLength: 0
           - NumColumns: 5 (5)
           - NumDictFilteredRowGroups: 0 (0)
           - NumDisksAccessed: 1 (1)
           - NumRowGroups: 1 (1)
           - NumScannerThreadsStarted: 1 (1)
           - NumScannersWithNoReads: 0 (0)
           - NumStatsFilteredRowGroups: 0 (0)
           - PeakMemoryUsage: 417.04 KB (427045)
           - PerReadThreadRawHdfsThroughput: 507.92 KB/sec
           - RemoteScanRanges: 0 (0)
           - RowBatchQueueGetWaitTime: 39.003ms
           - RowBatchQueuePutWaitTime: 0.000ns
           - RowsRead: 53 (53)
           - RowsReturned: 53 (53)
           - RowsReturnedRate: 1.36 K/sec
           - ScanRangesComplete: 1 (1)
           - ScannerThreadsInvoluntaryContextSwitches: 0 (0)
           - ScannerThreadsTotalWallClockTime: 39.003ms
             - MaterializeTupleTime(*): 1.000ms
             - ScannerThreadsSysTime: 346.000us
             - ScannerThreadsUserTime: 346.000us
           - ScannerThreadsVoluntaryContextSwitches: 4 (4)
           - TotalRawHdfsReadTime(*): 38.003ms
           - TotalReadThroughput: 0.00 /sec
"""
