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

import logging
import sys

from nose.tools import assert_equal, assert_true, assert_raises, assert_not_equal
from nose.plugins.skip import SkipTest
from TCLIService.ttypes import TStatusCode

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

from beeswax.conf import MAX_NUMBER_OF_SESSIONS, CLOSE_SESSIONS
from beeswax.models import HiveServerQueryHandle, Session
from beeswax.server.dbms import get_query_server_config, QueryServerException
from beeswax.server.hive_server2_lib import HiveServerTable, HiveServerClient, HiveServerClientCompatible

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


LOG = logging.getLogger()


class TestHiveServerClient():

  def setUp(self):
    self.client = make_logged_in_client(username="test_hive_server2_lib", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test_hive_server2_lib"))

    self.query_server = {
        'principal': 'hue',
        'server_name': 'hive',
        'QUERY_TIMEOUT_S': 60,
        'auth_username': 'hue',
        'auth_password': 'hue',
        'use_sasl': True,
        'server_host': 'localhost',
        'server_port': 10000,
    }

  def test_open_session(self):
    query = Mock(
      get_query_statement=Mock(return_value=['SELECT 1']),
      settings=[]
    )

    with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
      original_secret = b's\xb6\x0ePP\xbdL\x17\xa3\x0f\\\xf7K\xe8Y\x1d'
      original_guid = b'\xd9\xe0hT\xd6wO\xe1\xa3S\xfb\x04\xca\x93V\x01'
      get_client.return_value = Mock(
        OpenSession=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
            configuration={},
            sessionHandle=Mock(
              sessionId=Mock(
                secret=original_secret,
                guid=original_guid
              )
            ),
            serverProtocolVersion=11
          )
        ),
        get_coordinator_host=Mock(return_value='hive-host')
      )
      session_count = Session.objects.filter(owner=self.user, application=self.query_server['server_name']).count()

      # Send open session
      session = HiveServerClient(self.query_server, self.user).open_session(self.user)

      assert_equal(
        session_count + 1,  # +1 as setUp resets the user which deletes cascade the sessions
        Session.objects.filter(owner=self.user, application=self.query_server['server_name']).count()
      )

      session = Session.objects.get_session(self.user, self.query_server['server_name'])
      secret, guid = session.get_adjusted_guid_secret()
      secret, guid = HiveServerQueryHandle.get_decoded(secret, guid)
      assert_equal(
        original_secret,
        secret
      )
      assert_equal(
        original_guid,
        guid
      )
      handle = session.get_handle()
      assert_equal(
        original_secret,
        handle.sessionId.secret
      )
      assert_equal(
        original_guid,
        handle.sessionId.guid
      )


  def test_get_configuration(self):

    with patch('beeswax.server.hive_server2_lib.HiveServerClient.execute_query_statement') as execute_query_statement:
      with patch('beeswax.server.hive_server2_lib.CONFIG_WHITELIST.get') as CONFIG_WHITELIST:
        execute_query_statement.return_value = Mock(
          rows=Mock(
            return_value=[
              ['hive.server2.tez.default.queues=gethue'],
              ['hive.server2.tez.initialize.default.sessions=true']
            ]
          )
        )
        CONFIG_WHITELIST.return_value = ['hive.server2.tez.default.queues']

        configuration = HiveServerClient(self.query_server, self.user).get_configuration()

        assert_equal(
          configuration,
          {'hive.server2.tez.default.queues': 'gethue'}
        )

  def test_explain(self):
    query = Mock(
      get_query_statement=Mock(return_value=['SELECT 1']),
      settings=[]
    )

    with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
      get_client.return_value = Mock(
        OpenSession=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
            configuration={},
            sessionHandle=Mock(
              sessionId=Mock(
                secret=b'1',
                guid=b'1'
              )
            ),
            serverProtocolVersion=11
          )
        ),
        ExecuteStatement=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
          )
        ),
        FetchResults=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
            results=Mock(
              columns=[
                # Dump of `EXPLAIN SELECT 1`
                Mock(stringVal=Mock(values=['Plan optimized by CBO.', '', 'Stage-0', '	  Fetch Operator', '5	    limit:-1'], nulls='')),
              ]
            ),
            schema=Mock(
              columns=[
                Mock(columnName='Explain'),
              ]
            )
          )
        ),
        GetResultSetMetadata=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
            results=Mock(
              columns=[
                Mock(stringVal=Mock(values=['Explain',], nulls='')),  # Fake but ok
              ]
            ),
            schema=Mock(
              columns=[
                Mock(columnName='primitiveEntry 7'),
              ]
            )
          )
        ),
        get_coordinator_host=Mock(return_value='hive-host')
      )
      session_count = Session.objects.filter(owner=self.user, application=self.query_server['server_name']).count()

      # Send explain
      explain = HiveServerClient(self.query_server, self.user).explain(query)

      assert_equal(
        [['Plan optimized by CBO.'], [''], ['Stage-0'], ['	  Fetch Operator'], ['5	    limit:-1']],
        list(explain.rows())
      )
      assert_equal(
        session_count + 1,
        Session.objects.filter(owner=self.user, application=self.query_server['server_name']).count()
      )

  def test_get_databases_impala_specific(self):
    query = Mock(
      get_query_statement=Mock(return_value=['SELECT 1']),
      settings=[]
    )

    with patch('beeswax.server.hive_server2_lib.HiveServerTRowSet') as HiveServerTRowSet:

      client = HiveServerClient(self.query_server, self.user)

      client.call = Mock(return_value=(Mock(), Mock()))
      client.fetch_result = Mock(return_value=(Mock(), Mock()))
      client._close = Mock()

      client.get_databases(query)

      assert_not_equal(
        None,
        client.call.call_args[0][1].schemaName,
        client.call.call_args.args
      )

      with patch.dict(self.query_server, {'dialect': 'impala'}, clear=True):
        client.get_databases(query)

        assert_equal(
          None, # Should be empty and not '*' with Impala
          client.call.call_args[0][1].schemaName,
          client.call.call_args.args
        )


  def test_get_table_with_error(self):
    query = Mock(
      get_query_statement=Mock(return_value=['SELECT 1']),
      settings=[]
    )

    original_secret = b's\xb6\x0ePP\xbdL\x17\xa3\x0f\\\xf7K\xe8Y\x1d'
    original_guid = b'\xd9\xe0hT\xd6wO\xe1\xa3S\xfb\x04\xca\x93V\x01'
    with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
      get_client.return_value = Mock(
        OpenSession=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
            configuration={},
            sessionHandle=Mock(
              sessionId=Mock(
                secret=original_secret,
                guid=original_guid
              )
            ),
            serverProtocolVersion=11
          )
        ),
        ExecuteStatement=Mock(
          return_value=Mock(
            status=Mock(
              statusCode=TStatusCode.SUCCESS_STATUS
            ),
          )
        ),
        get_coordinator_host=Mock(return_value='hive-host')
      )

      client = HiveServerClient(self.query_server, self.user)

      # Non empty error message from HS2
      client._client.GetTables = Mock(
        return_value=Mock(
          status=Mock(
            errorMessage='Error while compiling statement: FAILED: HiveAccessControlException Permission denied'
          )
        )
      )

      assert_raises(QueryServerException, client.get_table, database='database', table_name='table_name')

      try:
        client.get_table(database='database', table_name='table_name')
      except QueryServerException as e:
        assert_equal(
          'Error while compiling statement: FAILED: HiveAccessControlException Permission denied',
          str(e)
        )

      # Empty error message from HS2
      get_tables_res = Mock(
          status=Mock(
            errorMessage=None
          )
      )
      client._client.GetTables = Mock(
        return_value=get_tables_res
      )

      try:
        client.get_table(database='database', table_name='table_name')
      except QueryServerException as e:
        if sys.version_info[0] > 2:
          req_string = ("TGetTablesReq(sessionHandle=TSessionHandle(sessionId=THandleIdentifier(guid=%s, secret=%s)), "
            "catalogName=None, schemaName='database', tableName='table_name', tableTypes=None)")\
            % (str(original_guid), str(original_secret))
        else:
          req_string = ("TGetTablesReq(schemaName='database', sessionHandle=TSessionHandle(sessionId=THandleIdentifier"
            "(secret='%s', guid='%s')), tableName='table_name', tableTypes=None, catalogName=None)")\
            % ('s\\xb6\\x0ePP\\xbdL\\x17\\xa3\\x0f\\\\\\xf7K\\xe8Y\\x1d',
               '\\xd9\\xe0hT\\xd6wO\\xe1\\xa3S\\xfb\\x04\\xca\\x93V\\x01') # manually adding '\'
        assert_equal(
          "Bad status for request %s:\n%s" % (req_string, get_tables_res),
          str(e)
        )

class TestHiveServerTable():

  def test_cols_impala(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(stringVal=Mock(
          values=[
            '# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Detailed Table Information', 'Database:', 'OwnerType:',
            'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:', 'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '',
            '', '', '', '', '', '# Storage Information', 'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:',
            'Bucket Columns:', 'Sort Columns:', 'Storage Desc Params:',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'default', 'USER', 'hive',
            'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0',
            'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL',
            'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional',
            'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
            'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",'\
            '\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1',
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.cols), 4)
    assert_equal(table.cols[0], {'col_name': 'code', 'data_type': 'string', 'comment': 'NULL'})
    assert_equal(table.cols[1], {'col_name': 'description', 'data_type': 'string', 'comment': 'NULL'})
    assert_equal(table.cols[2], {'col_name': 'total_emp', 'data_type': 'int', 'comment': 'NULL'})
    assert_equal(table.cols[3], {'col_name': 'salary', 'data_type': 'int', 'comment': 'NULL'})


  def test_cols_hive_tez(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(stringVal=Mock(
          values=[
            'code', 'description', 'total_emp', 'salary', '', '# Detailed Table Information', 'Database:           ',
            'OwnerType:          ', 'Owner:              ', 'CreateTime:         ', 'LastAccessTime:     ', 'Retention:          ',
            'Location:           ', 'Table Type:         ', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '',
            '# Storage Information', 'SerDe Library:      ', 'InputFormat:        ', 'OutputFormat:       ', 'Compressed:         ',
            'Num Buckets:        ', 'Bucket Columns:     ', 'Sort Columns:       ', 'Storage Desc Params:',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'string', 'string', 'int', 'int', 'NULL', 'NULL', 'default             ', 'USER                ', 'hive                ',
            'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN             ', '0',
            'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE       ',
            'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version   ', 'numFiles            ', 'numRows             ',
            'rawDataSize         ', 'totalSize           ', 'transactional       ', 'transactional_properties', 'transient_lastDdlTime',
            'NULL', 'NULL', 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No                  ', '-1', '[]                  ',
            '[]                  ', 'NULL', 'serialization.format',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            '', '', '', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":'\
            '\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2',
            '1', '822', '3288', '48445', 'TRUE', 'insert_only         ', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', '1',
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.cols), 4)
    assert_equal(table.cols[0], {'col_name': 'code', 'data_type': 'string', 'comment': ''})
    assert_equal(table.cols[1], {'col_name': 'description', 'data_type': 'string', 'comment': ''})
    assert_equal(table.cols[2], {'col_name': 'total_emp', 'data_type': 'int', 'comment': ''})
    assert_equal(table.cols[3], {'col_name': 'salary', 'data_type': 'int', 'comment': ''})


  def test_cols_hive_llap_upstream(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # No empty line after headers
        Mock(stringVal=Mock(
          values=[
            '# col_name', 'code', 'description', 'total_emp', 'salary', '', '# Detailed Table Information', 'Database:', 'OwnerType:',
            'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:', 'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '',
            '', '', '', '', '', '', '# Storage Information', 'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:',
            'Num Buckets:', 'Bucket Columns:', 'Sort Columns:', 'Storage Desc Params:',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'data_type', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019',
            'UNKNOWN', '0', 'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07',
            'MANAGED_TABLE', 'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize',
            'transactional', 'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
            'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL',
            'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",'\
            '\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1',
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.cols), 4)
    assert_equal(table.cols[0], {'col_name': 'code', 'data_type': 'string', 'comment': 'NULL'})
    assert_equal(table.cols[1], {'col_name': 'description', 'data_type': 'string', 'comment': 'NULL'})
    assert_equal(table.cols[2], {'col_name': 'total_emp', 'data_type': 'int', 'comment': 'NULL'})
    assert_equal(table.cols[3], {'col_name': 'salary', 'data_type': 'int', 'comment': 'NULL'})


  def test_partition_keys_impala(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(stringVal=Mock(
          values=[
            '# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', '', 'date', '',
            '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:',
            'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information',
            'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:',
            'Storage Desc Params:',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'NULL', 'string', 'NULL', 'NULL',
            'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0',
            'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL',
            'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional',
            'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
            'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=['comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":'\
            '{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445',
            'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1',
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.partition_keys), 1)
    assert_equal(table.partition_keys[0].name, 'date')
    assert_equal(table.partition_keys[0].type, 'string')
    assert_equal(table.partition_keys[0].comment, 'NULL')


  def test_partition_keys_hive(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        # Note: missing blank line below '# Partition Information'
        Mock(stringVal=Mock(
          values=[
            '# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', 'date', '',
            '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:',
            'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information',
            'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:',
            'Storage Desc Params:',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'string', 'NULL', 'NULL', 'default',
            'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0',
            'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL',
            'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional',
            'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
            'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":'\
            '\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only',
            '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1',
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.partition_keys), 1)
    assert_equal(table.partition_keys[0].name, 'date')
    assert_equal(table.partition_keys[0].type, 'string')
    assert_equal(table.partition_keys[0].comment, '')


  def test_single_primary_key_hive(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(stringVal=Mock(
          values=[
            '# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', 'date', '',
            '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:',
            'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information',
            'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:',
            'Storage Desc Params:', '', '', '# Constraints', '', '# Primary Key', 'Table:', 'Constraint Name:', 'Column Name:', ''
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'string', 'NULL', 'NULL', 'default',
            'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0',
            'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL',
            'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional',
            'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
            'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
            'NULL', 'NULL', 'NULL', 'NULL', 'default.pk', 'pk_165400321_1572980510006_0', 'id1 ', 'NULL'
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":'\
            '\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only',
            '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.primary_keys), 1)
    assert_equal(table.primary_keys[0].name, 'id1')
    assert_equal(table.primary_keys[0].type, 'NULL')
    assert_equal(table.primary_keys[0].comment, 'NULL')


  def test_multi_primary_keys_hive(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(stringVal=Mock(
          values=[
            '# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', 'date', '',
            '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:',
            'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information',
            'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:',
            'Storage Desc Params:', '', '', '# Constraints', '', '# Primary Key', 'Table:', 'Constraint Name:', 'Column Name:',
            'Column Name:'
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'string', 'NULL', 'NULL', 'default',
            'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0',
            'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL',
            'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional',
            'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
            'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
            'NULL', 'NULL', 'NULL', 'NULL', 'default.pk', 'pk_165400321_1572980510006_0', 'id1 ', 'id2 '
          ],
          nulls='')),
        Mock(stringVal=Mock(
          values=[
            'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":'\
            '\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only',
            '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', 'NULL', 'NULL', 'NULL',
            'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'
          ],
          nulls='')),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.primary_keys), 2)
    assert_equal(table.primary_keys[0].name, 'id1')
    assert_equal(table.primary_keys[0].type, 'NULL')
    assert_equal(table.primary_keys[0].comment, 'NULL')

    assert_equal(table.primary_keys[1].name, 'id2')
    assert_equal(table.primary_keys[1].type, 'NULL')
    assert_equal(table.primary_keys[1].comment, 'NULL')


  def test_foreign_keys_hive(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(
          stringVal=Mock(
            values=[
              '# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', 'date', '',
              '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:',
              'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information',
              'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:',
              'Storage Desc Params:', '', '', '# Constraints', '',
              '# Primary Key', 'Table:', 'Constraint Name:', 'Column Name:', '',
              '# Foreign Keys', 'Table:', 'Constraint Name:', 'Parent Column Name:default.persons.id', ''
            ],
            nulls=''
          )
        ),
        Mock(
          stringVal=Mock(
            values=[
              'data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'string', 'NULL',
              'NULL', 'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0',
              'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL',
              'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional',
              'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL',
              'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
              'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
              'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format',
              'NULL', 'NULL', 'NULL', 'NULL', 'default.pk', 'pk_165400321_1572980510006_0', 'id1 ', 'NULL',
              'NULL', 'default.businessunit', 'fk', 'Column Name:head', 'NULL'
            ],
            nulls=''
          )
        ),
        Mock(
          stringVal=Mock(
            values=[
              'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', '', 'NULL', 'NULL', 'NULL', 'NULL',
              'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",'\
              '\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true',
              'insert_only', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1',
              'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'Key Sequence:1',
              'NULL',
            ],
            nulls=''
          )
        ),
      ]
    )
    desc_schema = Mock(
      columns=[
        Mock(columnName='col_name'),
        Mock(columnName='data_type'),
        Mock(columnName='comment')
      ]
    )

    table = HiveServerTable(
      table_results=table_results,
      table_schema=table_schema,
      desc_results=desc_results,
      desc_schema=desc_schema
    )

    assert_equal(len(table.foreign_keys), 1)
    assert_equal(table.foreign_keys[0].name, 'head')  # 'from' column
    assert_equal(table.foreign_keys[0].type, 'default.persons.id')  # 'to' column
    assert_equal(table.foreign_keys[0].comment, 'NULL')



class TestSessionManagement():

  def setUp(self):
    self.client = make_logged_in_client(username="test_hive_server2_lib", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_hive_server2_lib")

  def test_call_session_single(self):
    finish = (
        MAX_NUMBER_OF_SESSIONS.set_for_testing(1),
        CLOSE_SESSIONS.set_for_testing(False)
    )

    try:
      with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
        with patch('beeswax.server.hive_server2_lib.HiveServerClient.open_session') as open_session:
          with patch('beeswax.server.hive_server2_lib.Session.objects.get_session') as get_session:
            open_session.return_value = MagicMock(status_code=0)
            get_session.return_value = None
            fn = MagicMock(attr='test')
            req = MagicMock()
            server_config = get_query_server_config(name='beeswax')

            client = HiveServerClient(server_config, self.user)

            (res, session1) = client.call(fn, req, status=None)
            open_session.assert_called_once()

            # Reuse session from argument
            (res, session2) = client.call(fn, req, status=None, session=session1)
            open_session.assert_called_once() # open_session should not be called again, because we're reusing session
            assert_equal(session1, session2)

            # Reuse session from get_session
            get_session.return_value = session1
            (res, session3) = client.call(fn, req, status=None)
            open_session.assert_called_once() # open_session should not be called again, because we're reusing session
            assert_equal(session1, session3)
    finally:
      for f in finish:
        f()

  def test_call_session_pool(self):
    finish = (
        MAX_NUMBER_OF_SESSIONS.set_for_testing(2),
        CLOSE_SESSIONS.set_for_testing(False)
    )

    try:
      with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
        with patch('beeswax.server.hive_server2_lib.HiveServerClient.open_session') as open_session:
          with patch('beeswax.server.hive_server2_lib.Session.objects.get_tez_session') as get_session:
            open_session.return_value = MagicMock(status_code=0)
            get_session.return_value = None
            fn = MagicMock(return_value=MagicMock(status=MagicMock(statusCode=0)))
            req = MagicMock()
            server_config = get_query_server_config(name='beeswax')

            client = HiveServerClient(server_config, self.user)

            (res, session1) = client.call(fn, req, status=None)
            open_session.assert_called_once()

            # Reuse session from argument
            (res, session2) = client.call(fn, req, status=None, session=session1)
            open_session.assert_called_once() # open_session should not be called again, because we're reusing session
            assert_equal(session1, session2)

            # Reuse session from get_session
            get_session.return_value = session1
            (res, session3) = client.call(fn, req, status=None)
            open_session.assert_called_once() # open_session should not be called again, because we're reusing session
            assert_equal(session1, session3)
    finally:
      for f in finish:
        f()

  def test_call_session_pool_limit(self):
    finish = (
        MAX_NUMBER_OF_SESSIONS.set_for_testing(2),
        CLOSE_SESSIONS.set_for_testing(False)
    )

    try:
      with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
        with patch('beeswax.server.hive_server2_lib.HiveServerClient.open_session') as open_session:
          with patch('beeswax.server.hive_server2_lib.Session.objects.get_tez_session') as get_tez_session:
            get_tez_session.side_effect = Exception('')
            open_session.return_value = MagicMock(status_code=0)
            fn = MagicMock(return_value=MagicMock(status=MagicMock(statusCode=0)))
            req = MagicMock()
            server_config = get_query_server_config(name='beeswax')

            client = HiveServerClient(server_config, self.user)

            assert_raises(Exception, client.call, fn, req, status=None)
    finally:
      for f in finish:
        f()

  def test_call_session_close_idle(self):
    finish = (
        MAX_NUMBER_OF_SESSIONS.set_for_testing(-1),
        CLOSE_SESSIONS.set_for_testing(True)
    )

    try:
      with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
        with patch('beeswax.server.hive_server2_lib.HiveServerClient.open_session') as open_session:
          open_session.return_value = MagicMock(status_code=0)
          fn = MagicMock(return_value=MagicMock(status=MagicMock(statusCode=0)))
          req = MagicMock()
          server_config = get_query_server_config(name='beeswax')

          client = HiveServerClient(server_config, self.user)

          (res, session1) = client.call(fn, req, status=None)
          open_session.assert_called_once()

          # Reuse session from argument
          (res, session2) = client.call(fn, req, status=None, session=session1)
          open_session.assert_called_once() # open_session should not be called again, because we're reusing session
          assert_equal(session1, session2)

          # Create new session
          open_session.return_value = MagicMock(status_code=0)
          (res, session3) = client.call(fn, req, status=None)
          assert_equal(open_session.call_count, 2)
          assert_not_equal(session1, session3)
    finally:
      for f in finish:
        f()

  def test_call_session_close_idle_managed_queries(self):
    finish = (
        MAX_NUMBER_OF_SESSIONS.set_for_testing(-1),
        CLOSE_SESSIONS.set_for_testing(True)
    )

    try:
      with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
        with patch('beeswax.server.hive_server2_lib.HiveServerClient.open_session') as open_session:
          with patch('beeswax.server.hive_server2_lib.HiveServerClient.close_session') as close_session:
            with patch('beeswax.server.hive_server2_lib.HiveServerTRowSet') as HiveServerTRowSet:
              status = MagicMock(status=MagicMock(statusCode=0))
              status_return = MagicMock(return_value=status)
              get_client.return_value = MagicMock(
                  return_value=status, GetSchemas=status_return, FetchResults=status_return, GetResultSetMetadata=status_return,
                  CloseOperation=status_return, ExecuteStatement=status_return, GetTables=status_return, GetColumns=status_return
              )
              open_session.return_value = MagicMock(status_code=0)
              server_config = get_query_server_config(name='beeswax')

              client = HiveServerClient(server_config, self.user)

              res = client.get_databases()
              assert_equal(open_session.call_count, 1)
              assert_equal(close_session.call_count, 1)

              res = client.get_database(MagicMock())
              assert_equal(open_session.call_count, 2)
              assert_equal(close_session.call_count, 2)

              res = client.get_tables_meta(MagicMock(), MagicMock())
              assert_equal(open_session.call_count, 3)
              assert_equal(close_session.call_count, 3)

              res = client.get_tables(MagicMock(), MagicMock())
              assert_equal(open_session.call_count, 4)
              assert_equal(close_session.call_count, 4)

              res = client.get_table(MagicMock(), MagicMock())
              assert_equal(open_session.call_count, 5)
              assert_equal(close_session.call_count, 5)

              res = client.get_columns(MagicMock(), MagicMock())
              assert_equal(open_session.call_count, 6)
              assert_equal(close_session.call_count, 6)

              res = client.get_partitions(MagicMock(), MagicMock()) # get_partitions does 2 requests with 1 session each
              assert_equal(open_session.call_count, 8)
              assert_equal(close_session.call_count, 8)
    finally:
      for f in finish:
        f()

  def test_call_session_close_idle_limit(self):
    finish = (
        MAX_NUMBER_OF_SESSIONS.set_for_testing(2),
        CLOSE_SESSIONS.set_for_testing(True)
    )

    try:
      with patch('beeswax.server.hive_server2_lib.thrift_util.get_client') as get_client:
        with patch('beeswax.server.hive_server2_lib.HiveServerClient.open_session') as open_session:
          with patch('beeswax.server.hive_server2_lib.Session.objects.get_n_sessions') as get_n_sessions:
            get_n_sessions.return_value = MagicMock(count=MagicMock(return_value=2))
            open_session.return_value = MagicMock(status_code=0)
            fn = MagicMock(return_value=MagicMock(status=MagicMock(statusCode=0)))
            req = MagicMock()
            server_config = get_query_server_config(name='beeswax')

            client = HiveServerClient(server_config, self.user)
            assert_raises(Exception, client.call, fn, req, status=None)

            get_n_sessions.return_value = MagicMock(count=MagicMock(return_value=1))
            (res, session1) = client.call(fn, req, status=None)
            open_session.assert_called_once()
    finally:
      for f in finish:
        f()

class TestHiveServerClientCompatible():


  def test_get_tables_meta(self):
    client = Mock(
      get_tables_meta=Mock(return_value=[
        {'TABLE_NAME': 'sample_07', 'TABLE_TYPE': 'TABLE', 'REMARKS': None},
        {'TABLE_NAME': 'sample_08', 'TABLE_TYPE': 'TABLE', 'REMARKS': None},
        {'TABLE_NAME': 'web_logs', 'TABLE_TYPE': 'TABLE', 'REMARKS': None},
        {'TABLE_NAME': 'flights_13', 'TABLE_TYPE': 'TABLE', 'REMARKS': None},
        {'TABLE_NAME': 'flights', 'TABLE_TYPE': 'TABLE', 'REMARKS': None},
        {'TABLE_NAME': 'lights', 'TABLE_TYPE': 'TABLE', 'REMARKS': None}
      ])
    )
    database = Mock()
    table_names = Mock()
    massaged_tables = HiveServerClientCompatible(client).get_tables_meta(database, table_names)
    sorted_table = [
      {'name': 'flights', 'comment': None, 'type': 'Table'},
      {'name': 'flights_13', 'comment': None, 'type': 'Table'},
      {'name': 'lights', 'comment': None, 'type': 'Table'},
      {'name': 'sample_07', 'comment': None, 'type': 'Table'},
      {'name': 'sample_08', 'comment': None, 'type': 'Table'},
      {'name': 'web_logs', 'comment': None, 'type': 'Table'}
    ]

    assert_equal(sorted_table, massaged_tables)
