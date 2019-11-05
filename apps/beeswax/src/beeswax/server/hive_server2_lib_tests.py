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
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

from nose.tools import assert_equal, assert_true

from beeswax.server.hive_server2_lib import HiveServerTable


LOG = logging.getLogger(__name__)


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
