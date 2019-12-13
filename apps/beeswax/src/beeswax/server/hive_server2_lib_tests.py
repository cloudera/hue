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

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock

from nose.tools import assert_equal, assert_true
from TCLIService.ttypes import TStatusCode

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from useradmin.models import User

from beeswax.models import Session
from beeswax.server.hive_server2_lib import HiveServerTable, HiveServerClient


LOG = logging.getLogger(__name__)


class TestHiveServerClient():

  def setUp(self):
    self.client = make_logged_in_client(username="test_hive_server2_lib", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_hive_server2_lib")

    grant_access(self.user.username, self.user.username, "beeswax")

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
        get_coordinator_host=Mock(return_value='hive-host')
      )
      session_count = Session.objects.filter(owner=self.user, application=self.query_server['server_name']).count()

      # Send open session
      session = HiveServerClient(self.query_server, self.user).open_session(self.user)

      assert_equal(
        session_count + 1,  # +1 as setUp resets the user which deletes cascade the sessions
        Session.objects.filter(owner=self.user, application=self.query_server['server_name']).count()
      )
      assert_equal(
        session.guid,
        Session.objects.get_session(self.user, self.query_server['server_name']).guid.encode()
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
                Mock(stringVal=Mock(values=['Plan optimized by CBO.', '', 'Stage-0', '	  Fetch Operator', '5	    limit:-1' ], nulls='')),
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
                Mock(stringVal=Mock(values=['Explain', ], nulls='')),  # Fake but ok
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


class TestHiveServerTable():

  def test_cols_impala(self):

    table_results = Mock()
    table_schema = Mock()
    desc_results = Mock(
      columns=[
        # Dump of `DESCRIBE FORMATTED table`
        Mock(stringVal=Mock(values=['# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:', 'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information', 'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:', 'Storage Desc Params:', ], nulls='')),
        Mock(stringVal=Mock(values=['data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0', 'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional', 'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL', 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format', ], nulls='')),
        Mock(stringVal=Mock(values=['comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', ], nulls='')),
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
          Mock(stringVal=Mock(values=['code', 'description', 'total_emp', 'salary', '', '# Detailed Table Information', 'Database:           ', 'OwnerType:          ', 'Owner:              ', 'CreateTime:         ', 'LastAccessTime:     ', 'Retention:          ', 'Location:           ', 'Table Type:         ', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information', 'SerDe Library:      ', 'InputFormat:        ', 'OutputFormat:       ', 'Compressed:         ', 'Num Buckets:        ', 'Bucket Columns:     ', 'Sort Columns:       ', 'Storage Desc Params:', ], nulls='')),
          Mock(stringVal=Mock(values=['string', 'string', 'int', 'int', 'NULL', 'NULL', 'default             ', 'USER                ', 'hive                ', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN             ', '0', 'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE       ', 'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version   ', 'numFiles            ', 'numRows             ', 'rawDataSize         ', 'totalSize           ', 'transactional       ', 'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL', 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No                  ', '-1', '[]                  ', '[]                  ', 'NULL', 'serialization.format', ], nulls='')),
          Mock(stringVal=Mock(values=['', '', '', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'TRUE', 'insert_only         ', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', ], nulls='')),
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


  def test_partition_keys_impala(self):

      table_results = Mock()
      table_schema = Mock()
      desc_results = Mock(
        columns=[
          # Dump of `DESCRIBE FORMATTED table`
          Mock(stringVal=Mock(values=['# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', '', 'date', '', '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:', 'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information', 'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:', 'Storage Desc Params:', ], nulls='')),
          Mock(stringVal=Mock(values=['data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'NULL', 'string', 'NULL', 'NULL', 'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0', 'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional', 'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL', 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format', ], nulls='')),
          Mock(stringVal=Mock(values=['comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', ], nulls='')),
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
          Mock(stringVal=Mock(values=['# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', 'date', '', '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:', 'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information', 'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:', 'Storage Desc Params:', ], nulls='')),
          Mock(stringVal=Mock(values=['data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'string', 'NULL', 'NULL', 'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0', 'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional', 'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL', 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format', ], nulls='')),
          Mock(stringVal=Mock(values=['comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', ], nulls='')),
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


  def test_primary_keys_hive(self):

      table_results = Mock()
      table_schema = Mock()
      desc_results = Mock(
        columns=[
          # Dump of `DESCRIBE FORMATTED table`
          Mock(stringVal=Mock(values=['# col_name', '', 'code', 'description', 'total_emp', 'salary', '', '# Partition Information', '# col_name', 'date', '', '# Detailed Table Information', 'Database:', 'OwnerType:', 'Owner:', 'CreateTime:', 'LastAccessTime:', 'Retention:', 'Location:', 'Table Type:', 'Table Parameters:', '', '', '', '', '', '', '', '', '', '', '# Storage Information', 'SerDe Library:', 'InputFormat:', 'OutputFormat:', 'Compressed:', 'Num Buckets:', 'Bucket Columns:', 'Sort Columns:', 'Storage Desc Params:', '', '', '# Constraints', '', '# Primary Key', 'Table:', 'Constraint Name:', 'Column Name:', 'Column Name:'], nulls='')),
          Mock(stringVal=Mock(values=['data_type', 'NULL', 'string', 'string', 'int', 'int', 'NULL', 'NULL', 'data_type', 'string', 'NULL', 'NULL', 'default', 'USER', 'hive', 'Mon Nov 04 07:44:10 PST 2019', 'UNKNOWN', '0', 'hdfs://nightly7x-unsecure-1.vpc.cloudera.com:8020/warehouse/tablespace/managed/hive/sample_07', 'MANAGED_TABLE', 'NULL', 'COLUMN_STATS_ACCURATE', 'bucketing_version', 'numFiles', 'numRows', 'rawDataSize', 'totalSize', 'transactional', 'transactional_properties', 'transient_lastDdlTime', 'NULL', 'NULL', 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat', 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', 'No', '-1', '[]', '[]', 'NULL', 'serialization.format', 'NULL', 'NULL', 'NULL', 'NULL', 'default.pk', 'pk_165400321_1572980510006_0', 'id1 ', 'id2 '], nulls='')),
          Mock(stringVal=Mock(values=['comment', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'comment', '', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '{\"BASIC_STATS\":\"true\",\"COLUMN_STATS\":{\"code\":\"true\",\"description\":\"true\",\"salary\":\"true\",\"total_emp\":\"true\"}}', '2', '1', '822', '3288', '48445', 'true', 'insert_only', '1572882268', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', '1', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'], nulls='')),
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
