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

import json
from builtins import object
from unittest.mock import MagicMock, Mock, patch

import pytest

from azure.conf import ABFS_CLUSTERS
from beeswax.server import dbms
from desktop.lib.django_test_util import make_logged_in_client
from desktop.settings import BASE_DIR
from indexer.indexers.sql import SQLIndexer
from useradmin.models import User


def mock_uuid():
  return '52f840a8-3dde-434d-934a-2d6e06f3687e'


@pytest.mark.django_db
class TestSQLIndexer(object):
  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="empty", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_create_table_from_a_file_to_csv(self):
    fs = Mock(stats=Mock(return_value={'mode': 0o0777}))

    def source_dict(key):
      return {
        'path': 'hdfs:///path/data.csv',
        'format': {'quoteChar': '"', 'fieldSeparator': ','},
        'sampleCols': [{'operations': [], 'comment': '', 'name': 'customers.id'}],
        'sourceType': 'hive',
      }.get(key, Mock())

    source = MagicMock()
    source.__getitem__.side_effect = source_dict

    def destination_dict(key):
      return {
        'name': 'default.export_table',
        'tableFormat': 'csv',
        'importData': True,
        'isIceberg': False,
        'nonDefaultLocation': '/user/hue/customer_stats.csv',
        'columns': [{'name': 'id', 'type': 'int'}],
        'partitionColumns': [{'name': 'day', 'type': 'date', 'partitionValue': '20200101'}],
        'description': 'No comment!',
        'sourceType': 'hive-1',
      }.get(key, Mock())

    destination = MagicMock()
    destination.__getitem__.side_effect = destination_dict

    with patch('notebook.models.get_interpreter') as get_interpreter:
      notebook = SQLIndexer(user=self.user, fs=fs).create_table_from_a_file(source, destination)

    assert [
      statement.strip()
      for statement in '''DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;

CREATE TABLE IF NOT EXISTS `default`.`hue__tmp_export_table`
(
  `id` int ) COMMENT "No comment!"
PARTITIONED BY (
  `day` date )
ROW FORMAT   SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
  WITH SERDEPROPERTIES ("separatorChar" = ",",
    "quoteChar"     = """,
    "escapeChar"    = "\\\\"
    )
  STORED AS TextFile TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;

LOAD DATA INPATH 'hdfs:///path/data.csv' INTO TABLE `default`.`hue__tmp_export_table` PARTITION (day='20200101');

CREATE TABLE `default`.`export_table` COMMENT "No comment!"
        STORED AS csv
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_export_table`;

DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;'''.split(';')
    ] == [statement.strip() for statement in notebook.get_data()['snippets'][0]['statement_raw'].split(';')]

  @patch('uuid.uuid4', mock_uuid)
  def test_create_table_from_a_file_to_csv_for_kms_encryption(self):
    def mock_parent_path(path):
      return '/'.join(path.split('/')[:-1])

    class MockStat:
      def __init__(self, encBit=True, mode=16877):
        self.encBit = encBit
        self.mode = mode

      def __getitem__(self, key):
        if key == 'mode':
          return 16877

    def enc_source_dict(key):
      return {
        'path': '/enc_zn/upload_dir/data.csv',
        'format': {'quoteChar': '"', 'fieldSeparator': ','},
        'sampleCols': [{'operations': [], 'comment': '', 'name': 'customers.id'}],
        'sourceType': 'hive',
      }.get(key, Mock())

    source = MagicMock()
    source.__getitem__.side_effect = enc_source_dict

    def destination_dict(key):
      return {
        'name': 'default.export_table',
        'tableFormat': 'csv',
        'importData': True,
        'isIceberg': False,
        'nonDefaultLocation': '/warehouse/tablespace/managed/hive/customer_stats.csv',
        'columns': [{'name': 'id', 'type': 'int'}],
        'partitionColumns': [{'name': 'day', 'type': 'date', 'partitionValue': '20200101'}],
        'description': 'No comment!',
        'sourceType': 'hive-1',
      }.get(key, Mock())

    destination = MagicMock()
    destination.__getitem__.side_effect = destination_dict

    fs = Mock(
      stats=Mock(return_value=MockStat()),
      parent_path=mock_parent_path,
      get_home_dir=Mock(return_value='/user/test'),
    )

    notebook = SQLIndexer(user=self.user, fs=fs).create_table_from_a_file(source, destination)

    # source dir is in encryption zone, so the scratch dir is in the same dir
    assert [
      statement.strip()
      for statement in '''DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;
CREATE TABLE IF NOT EXISTS `default`.`hue__tmp_export_table`
(
  `id` int ) COMMENT "No comment!"
PARTITIONED BY (
  `day` date )
ROW FORMAT   SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
  WITH SERDEPROPERTIES ("separatorChar" = ",",
    "quoteChar"     = """,
    "escapeChar"    = "\\\\"
    )
  STORED AS TextFile TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;
LOAD DATA INPATH '/enc_zn/upload_dir/.scratchdir/52f840a8-3dde-434d-934a-2d6e06f3687e/data.csv' \
INTO TABLE `default`.`hue__tmp_export_table` PARTITION (day='20200101');
CREATE TABLE `default`.`export_table` COMMENT "No comment!"
        STORED AS csv
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_export_table`;
DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;'''.split(';')  # noqa: E501
    ] == [statement.strip() for statement in notebook.get_data()['snippets'][0]['statement_raw'].split(';')]

    fs = Mock(
      stats=Mock(return_value=MockStat(encBit=False)),
      parent_path=mock_parent_path,
      get_home_dir=Mock(return_value='/user/test'),
    )

    def source_dict(key):
      return {
        'path': '/user/test/data.csv',
        'format': {'quoteChar': '"', 'fieldSeparator': ','},
        'sampleCols': [{'operations': [], 'comment': '', 'name': 'customers.id'}],
        'sourceType': 'hive',
      }.get(key, Mock())

    source = MagicMock()
    source.__getitem__.side_effect = source_dict

    notebook = SQLIndexer(user=self.user, fs=fs).create_table_from_a_file(source, destination)

    # source dir is not in encryption zone, so the scratch dir is in user's home dir
    assert [
      statement.strip()
      for statement in '''DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;
CREATE TABLE IF NOT EXISTS `default`.`hue__tmp_export_table`
(
  `id` int ) COMMENT "No comment!"
PARTITIONED BY (
  `day` date )
ROW FORMAT   SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
  WITH SERDEPROPERTIES ("separatorChar" = ",",
    "quoteChar"     = """,
    "escapeChar"    = "\\\\"
    )
  STORED AS TextFile TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;
LOAD DATA INPATH '/user/test/.scratchdir/52f840a8-3dde-434d-934a-2d6e06f3687e/data.csv' \
INTO TABLE `default`.`hue__tmp_export_table` PARTITION (day='20200101');
CREATE TABLE `default`.`export_table` COMMENT "No comment!"
        STORED AS csv
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_export_table`;
DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;'''.split(';')  # noqa: E501
    ] == [statement.strip() for statement in notebook.get_data()['snippets'][0]['statement_raw'].split(';')]


class MockRequest(object):
  def __init__(self, fs=None, user=None):
    self.fs = fs if fs is not None else MockFs()
    if user is None:
      self.c = make_logged_in_client(username='test_importer', is_superuser=False)
      self.user = User.objects.get(username='test_importer')
    else:
      self.user = user


class MockFs(object):
  def __init__(self, path=None):
    self.path = {'isDir': False, 'listdir': ['/A'], 'parent_path': '/A'} if path is None else path

  def isdir(self, path):
    return self.path['isDir']

  def split(self, path):
    return self.path['split']

  def listdir(self, path):
    return self.path['listdir']

  def parent_path(self, path):
    return self.path['parent_path']

  def stats(self, path):
    return {"mode": 0o0777}


@pytest.mark.django_db
def test_generate_create_text_table_with_data_partition():
  source = {
    'sourceType': 'hive',
    'sampleCols': [
      {
        'operations': [],
        'comment': '',
        'name': 'customers.id',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'bigint',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.email_preferences',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.addresses',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.orders',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
    ],
    'name': '',
    'inputFormat': 'file',
    'format': {'status': 0, 'fieldSeparator': ',', 'hasHeader': True, 'quoteChar': '"', 'recordSeparator': '\\n', 'type': 'csv'},
    'defaultName': 'default.customer_stats',
    'show': True,
    'tableName': '',
    'sample': [],
    'apiHelperType': 'hive',
    'inputFormatsAll': [
      {'name': 'File', 'value': 'file'},
      {'name': 'Manually', 'value': 'manual'},
      {'name': 'SQL Query', 'value': 'query'},
      {'name': 'Table', 'value': 'table'},
    ],
    'query': '',
    'databaseName': 'default',
    'table': '',
    'inputFormats': [
      {'name': 'File', 'value': 'file'},
      {'name': 'Manually', 'value': 'manual'},
      {'name': 'SQL Query', 'value': 'query'},
      {'name': 'Table', 'value': 'table'},
    ],
    'path': '/user/romain/customer_stats.csv',
    'draggedQuery': '',
    'inputFormatsManual': [{'name': 'Manually', 'value': 'manual'}],
    'isObjectStore': False,
  }
  destination = {
    'isTransactional': False,
    'isInsertOnly': False,
    'sourceType': 'hive',
    'KUDU_DEFAULT_PARTITION_COLUMN': {
      'int_val': 16,
      'name': 'HASH',
      'columns': [],
      'range_partitions': [
        {'include_upper_val': '<=', 'upper_val': 1, 'name': 'VALUES', 'include_lower_val': '<=', 'lower_val': 0, 'values': [{'value': ''}]}
      ],
    },
    'isTargetChecking': False,
    'tableName': 'customer_stats',
    'outputFormatsList': [
      {'name': 'Table', 'value': 'table'},
      {'name': 'Solr index', 'value': 'index'},
      {'name': 'File', 'value': 'file'},
      {'name': 'Database', 'value': 'database'},
    ],
    'customRegexp': '',
    'isTargetExisting': False,
    'partitionColumns': [
      {
        'operations': [],
        'comment': '',
        'name': 'new_field_1',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': True,
        'length': 100,
        'partitionValue': 'AAA',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      }
    ],
    'useCustomDelimiters': False,
    'apiHelperType': 'hive',
    'kuduPartitionColumns': [],
    'outputFormats': [{'name': 'Table', 'value': 'table'}, {'name': 'Solr index', 'value': 'index'}],
    'customMapDelimiter': '\\003',
    'showProperties': False,
    'useDefaultLocation': True,
    'description': '',
    'primaryKeyObjects': [],
    'customFieldDelimiter': ',',
    'existingTargetUrl': '',
    'importData': True,
    'isIceberg': False,
    'useCopy': False,
    'databaseName': 'default',
    'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {
      'include_upper_val': '<=',
      'upper_val': 1,
      'name': 'VALUES',
      'include_lower_val': '<=',
      'lower_val': 0,
      'values': [{'value': ''}],
    },
    'primaryKeys': [],
    'outputFormat': 'table',
    'nonDefaultLocation': '/user/romain/customer_stats.csv',
    'name': 'default.customer_stats',
    'tableFormat': 'text',
    'ouputFormat': 'table',
    'bulkColumnNames': 'customers.id,customers.name,customers.email_preferences,customers.addresses,customers.orders',
    'columns': [
      {
        'operations': [],
        'comment': '',
        'name': 'customers.id',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'bigint',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.email_preferences',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.addresses',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'customers.orders',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
    ],
    'hasHeader': True,
    'tableFormats': [
      {'name': 'Text', 'value': 'text'},
      {'name': 'Parquet', 'value': 'parquet'},
      {'name': 'Kudu', 'value': 'kudu'},
      {'name': 'Csv', 'value': 'csv'},
      {'name': 'Avro', 'value': 'avro'},
      {'name': 'Json', 'value': 'json'},
      {'name': 'Regexp', 'value': 'regexp'},
      {'name': 'ORC', 'value': 'orc'},
    ],
    'customCollectionDelimiter': '\\002',
  }
  request = MockRequest(fs=MockFs())

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert '''USE default;''' in sql, sql

  statement = '''CREATE TABLE `default`.`customer_stats`
(
  `customers.id` bigint ,
  `customers.name` string ,
  `customers.email_preferences` string ,
  `customers.addresses` string ,
  `customers.orders` string ) PARTITIONED BY (
  `new_field_1` string )
ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert (
    '''LOAD DATA INPATH '/user/romain/customer_stats.csv' '''
    '''INTO TABLE `default`.`customer_stats` PARTITION (new_field_1='AAA');''' in sql
  ), sql


@pytest.mark.django_db
def test_generate_create_kudu_table_with_data():
  source = {
    'sourceType': 'impala',
    'apiHelperType': 'hive',
    'sampleCols': [],
    'name': '',
    'inputFormat': 'file',
    'format': {'quoteChar': '"', 'recordSeparator': '\\n', 'type': 'csv', 'hasHeader': True, 'fieldSeparator': ','},
    'show': True,
    'tableName': '',
    'sample': [],
    'defaultName': 'index_data',
    'query': '',
    'databaseName': 'default',
    'table': '',
    'inputFormats': [{'name': 'File', 'value': 'file'}, {'name': 'Manually', 'value': 'manual'}],
    'path': '/user/admin/index_data.csv',
    'draggedQuery': '',
    'isObjectStore': False,
  }
  destination = {
    'isTransactional': False,
    'isInsertOnly': False,
    'sourceType': 'impala',
    'KUDU_DEFAULT_PARTITION_COLUMN': {
      'int_val': 16,
      'name': 'HASH',
      'columns': [],
      'range_partitions': [
        {'include_upper_val': '<=', 'upper_val': 1, 'name': 'VALUES', 'include_lower_val': '<=', 'lower_val': 0, 'values': [{'value': ''}]}
      ],
    },
    'tableName': 'index_data',
    'outputFormatsList': [
      {'name': 'Table', 'value': 'table'},
      {'name': 'Solr+index', 'value': 'index'},
      {'name': 'File', 'value': 'file'},
      {'name': 'Database', 'value': 'database'},
    ],
    'customRegexp': '',
    'isTargetExisting': False,
    'partitionColumns': [],
    'useCustomDelimiters': True,
    'kuduPartitionColumns': [
      {
        'int_val': 16,
        'name': 'HASH',
        'columns': ['id'],
        'range_partitions': [
          {
            'include_upper_val': '<=',
            'upper_val': 1,
            'name': 'VALUES',
            'include_lower_val': '<=',
            'lower_val': 0,
            'values': [{'value': ''}],
          }
        ],
      }
    ],
    'outputFormats': [{'name': 'Table', 'value': 'table'}, {'name': 'Solr+index', 'value': 'index'}],
    'customMapDelimiter': None,
    'showProperties': False,
    'useDefaultLocation': True,
    'description': 'Big Data',
    'primaryKeyObjects': [
      {
        'operations': [],
        'comment': '',
        'name': 'id',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      }
    ],
    'customFieldDelimiter': ',',
    'existingTargetUrl': '',
    'importData': True,
    'isIceberg': False,
    'useCopy': False,
    'databaseName': 'default',
    'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {
      'include_upper_val': '<=',
      'upper_val': 1,
      'name': 'VALUES',
      'include_lower_val': '<=',
      'lower_val': 0,
      'values': [{'value': ''}],
    },
    'primaryKeys': ['id'],
    'outputFormat': 'table',
    'nonDefaultLocation': '/user/admin/index_data.csv',
    'name': 'index_data',
    'tableFormat': 'kudu',
    'bulkColumnNames': 'business_id,cool,date,funny,id,stars,text,type,useful,user_id,name,full_address,latitude,'
    'longitude,neighborhoods,open,review_count,state',
    'columns': [
      {
        'operations': [],
        'comment': '',
        'name': 'business_id',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'cool',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'bigint',
        'showProperties': False,
        'keep': False,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'date',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'funny',
        'level': 0,
        'scale': 4,
        'precision': 10,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'decimal',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'id',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'stars',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'bigint',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'text',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'type',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'useful',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'bigint',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'user_id',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'full_address',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'latitude',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'double',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'longitude',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'double',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'neighborhoods',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'open',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'review_count',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'bigint',
        'showProperties': False,
        'keep': True,
      },
      {
        'operations': [],
        'comment': '',
        'name': 'state',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'multiValued': False,
        'unique': False,
        'type': 'string',
        'showProperties': False,
        'keep': True,
      },
    ],
    'hasHeader': True,
    'tableFormats': [
      {'name': 'Text', 'value': 'text'},
      {'name': 'Parquet', 'value': 'parquet'},
      {'name': 'Json', 'value': 'json'},
      {'name': 'Kudu', 'value': 'kudu'},
      {'name': 'Avro', 'value': 'avro'},
      {'name': 'Regexp', 'value': 'regexp'},
      {'name': 'RCFile', 'value': 'rcfile'},
      {'name': 'ORC', 'value': 'orc'},
      {'name': 'SequenceFile', 'value': 'sequencefile'},
    ],
    'customCollectionDelimiter': None,
  }
  request = MockRequest(fs=MockFs())

  with patch('hadoop.fs.hadoopfs.Hdfs.split') as split:
    split.return_value = ('/A', 'a')
    sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

    assert '''DROP TABLE IF EXISTS `default`.`hue__tmp_index_data`;''' in sql, sql

    statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_index_data`
(
  `business_id` string ,
  `cool` bigint ,
  `date` string ,
  `funny` decimal(10, 4) ,
  `id` string ,
  `stars` bigint ,
  `text` string ,
  `type` string ,
  `useful` bigint ,
  `user_id` string ,
  `name` string ,
  `full_address` string ,
  `latitude` double ,
  `longitude` double ,
  `neighborhoods` string ,
  `open` string ,
  `review_count` bigint ,
  `state` string ) COMMENT "Big Data"
ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
  STORED AS TextFile LOCATION '/A'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')'''
    assert statement in sql, sql

    assert (
      '''CREATE TABLE `default`.`index_data` COMMENT "Big Data"
        PRIMARY KEY (id)
        PARTITION BY HASH PARTITIONS 16
        STORED AS kudu
        TBLPROPERTIES(
        'kudu.num_tablet_replicas'='1'
        )
        AS SELECT `id`, `business_id`, `date`, `funny`, `stars`, `text`, `type`, `useful`, `user_id`, `name`, '''
      '''`full_address`, `latitude`, `longitude`, `neighborhoods`, `open`, `review_count`, `state`
        FROM `default`.`hue__tmp_index_data`''' in sql
    ), sql


@pytest.mark.django_db
def test_generate_create_parquet_table():
  source = json.loads(
    '''{"sourceType": "hive", "name":"","sample":[["Bank Of America","3000000.0","US","Miami","37.6801986694",'''
    '''"-121.92150116"],["Citi Bank","2800000.0","US","Richmond","37.5242004395","-77.4932022095"],["Deutsche Bank","2600000.0","US",'''
    '''"Corpus Christi","40.7807998657","-73.9772033691"],["Thomson Reuters","2400000.0","US","Albany","35.7976989746",'''
    '''"-78.6252975464"],'''
    '''["OpenX","2200000.0","US","Des Moines","40.5411987305","-119.586898804"]],"sampleCols":[{"operations":[],"comment":"",'''
    '''"nested":[],'''
    '''"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double",'''
    '''"showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":'''
    '''"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,'''
    '''"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],'''
    '''"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,'''
    '''"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,'''
    '''"scale":0}],"inputFormat":"file","inputFormatsAll":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},'''
    '''{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],"inputFormatsManual":[{"value":"manual","name":'''
    '''"Manually"}],"inputFormats":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},{"value":"query","name":'''
    '''"SQL Query"},{"value":"table","name":"Table"}],"path":"/user/hue/data/query-hive-360.csv","isObjectStore":false,"table":"",'''
    '''"tableName":"","databaseName":"default","apiHelperType":"hive","query":"","draggedQuery":"","format":{"type":"csv",'''
    '''"fieldSeparator":",","recordSeparator":"\\n","quoteChar":"\\"","hasHeader":true,"status":0},"show":true,"defaultName":'''
    '''"default.query-hive-360"}'''
  )
  destination = json.loads(
    '''{"isTransactional": false, "isInsertOnly": false, "sourceType": "hive", "name":"default.parquet_table"'''
    ''',"apiHelperType":"hive","description":"","outputFormat":"table","outputFormatsList":[{"name":"Table","value":"table"},'''
    '''{"name":"Solr index","value":"index"},{"name":"File","value":"file"},{"name":"Database","value":"database"}],'''
    '''"outputFormats":[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"}],"columns":[{"operations":[],'''
    '''"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":'''
    '''"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,'''
    '''"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":'''
    '''[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":'''
    '''100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":'''
    '''false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,tran_amount,tran_country_cd,vrfcn_city,'''
    '''vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,"isTargetChecking":false,"existingTargetUrl":'''
    '''"","tableName":"parquet_table","databaseName":"default","tableFormat":"parquet","KUDU_DEFAULT_RANGE_PARTITION_COLUMN":'''
    '''{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="},'''
    '''"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":[{"value":""}],"name":"VALUES","lower_val":0,'''
    '''"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH","int_val":16},"tableFormats":[{"value":'''
    '''"text","name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},{"value":"csv","name":"Csv"},'''
    '''{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},{"value":"orc",'''
    '''"name":"ORC"}],"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys":[],"primaryKeyObjects":[],"importData":true,'''
    '''"isIceberg":false,"useCopy":false,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv",'''
    '''"hasHeader":true,"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002",'''
    '''"customMapDelimiter":"\\\\003","customRegexp":""}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert '''USE default;''' in sql, sql

  statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_parquet_table`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile LOCATION '/user/hue/data'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert (
    '''CREATE TABLE `default`.`parquet_table`
        STORED AS parquet
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
'''
    in sql
  ), sql

  assert '''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;''' in sql, sql

  destination['useDefaultLocation'] = False
  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert '''USE default;''' in sql, sql

  statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_parquet_table`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile LOCATION '/user/hue/data'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert '''CREATE EXTERNAL TABLE `default`.`parquet_table`
        STORED AS parquet
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
''' in sql, sql

  assert '''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;''' in sql, sql


@pytest.mark.django_db
def test_generate_create_avro_table():
  source = json.loads('''{"sourceType": "hive", "name":"","sample":[["Bank Of America","3000000.0","US","Miami","37.6801986694",'''
    '''"-121.92150116"],["Citi Bank","2800000.0","US","Richmond","37.5242004395","-77.4932022095"],["Deutsche Bank","2600000.0","US",'''
    '''"Corpus Christi","40.7807998657","-73.9772033691"],["Thomson Reuters","2400000.0","US","Albany","35.7976989746",'''
    '''"-78.6252975464"],'''
    '''["OpenX","2200000.0","US","Des Moines","40.5411987305","-119.586898804"]],"sampleCols":[{"operations":[],"comment":"",'''
    '''"nested":[],'''
    '''"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double",'''
    '''"showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":'''
    '''"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,'''
    '''"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],'''
    '''"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,'''
    '''"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,'''
    '''"scale":0}],"inputFormat":"file","inputFormatsAll":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},'''
    '''{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],"inputFormatsManual":[{"value":"manual","name":'''
    '''"Manually"}],"inputFormats":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},{"value":"query","name":'''
    '''"SQL Query"},{"value":"table","name":"Table"}],"path":"/user/hue/data/query-hive-360.csv","isObjectStore":false,"table":"",'''
    '''"tableName":"","databaseName":"default","apiHelperType":"hive","query":"","draggedQuery":"","format":{"type":"csv",'''
    '''"fieldSeparator":",","recordSeparator":"\\n","quoteChar":"\\"","hasHeader":true,"status":0},"show":true,"defaultName":'''
    '''"default.query-hive-360"}'''
  )
  destination = json.loads('''{"isTransactional": false, "isInsertOnly": false, "sourceType": "hive", "name":"default.avro_table"'''
    ''',"apiHelperType":"hive","description":"","outputFormat":"table","outputFormatsList":[{"name":"Table","value":"table"},'''
    '''{"name":"Solr index","value":"index"},{"name":"File","value":"file"},{"name":"Database","value":"database"}],'''
    '''"outputFormats":[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"}],"columns":[{"operations":[],'''
    '''"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":'''
    '''"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,'''
    '''"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":'''
    '''[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":'''
    '''100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":'''
    '''false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,tran_amount,tran_country_cd,vrfcn_city,'''
    '''vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,"isTargetChecking":false,"existingTargetUrl":'''
    '''"","tableName":"avro_table","databaseName":"default","tableFormat":"avro","KUDU_DEFAULT_RANGE_PARTITION_COLUMN":'''
    '''{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="},'''
    '''"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":[{"value":""}],"name":"VALUES","lower_val":0,'''
    '''"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH","int_val":16},"tableFormats":[{"value":'''
    '''"text","name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},{"value":"csv","name":"Csv"},'''
    '''{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},{"value":"orc",'''
    '''"name":"ORC"}],"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys":[],"primaryKeyObjects":[],"importData":true,'''
    '''"isIceberg":false,"useCopy":false,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv",'''
    '''"hasHeader":true,"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002",'''
    '''"customMapDelimiter":"\\\\003","customRegexp":""}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert '''USE default;''' in sql, sql

  statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_avro_table`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile LOCATION '/user/hue/data'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert '''CREATE TABLE `default`.`avro_table`
        STORED AS avro
        AS SELECT *
        FROM `default`.`hue__tmp_avro_table`;
''' in sql, sql

  assert '''DROP TABLE IF EXISTS `default`.`hue__tmp_avro_table`;''' in sql, sql

  destination['useDefaultLocation'] = False
  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert '''USE default;''' in sql, sql

  statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_avro_table`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile LOCATION '/user/hue/data'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert '''CREATE EXTERNAL TABLE `default`.`avro_table`
        STORED AS avro
        AS SELECT *
        FROM `default`.`hue__tmp_avro_table`;
''' in sql, sql

  assert '''DROP TABLE IF EXISTS `default`.`hue__tmp_avro_table`;''' in sql, sql


@pytest.mark.django_db
def test_generate_create_iceberg_table():
  source = json.loads(
    '''{"sourceType": "hive", "name":"","sample":[["Bank Of America","3000000.0","US","Miami","37.6801986694",'''
    '''"-121.92150116"],["Citi Bank","2800000.0","US","Richmond","37.5242004395","-77.4932022095"],["Deutsche Bank","2600000.0","US",'''
    '''"Corpus Christi","40.7807998657","-73.9772033691"],["Thomson Reuters","2400000.0","US","Albany","35.7976989746",'''
    '''"-78.6252975464"],'''
    '''["OpenX","2200000.0","US","Des Moines","40.5411987305","-119.586898804"]],"sampleCols":[{"operations":[],"comment":"",'''
    '''"nested":[],'''
    '''"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double",'''
    '''"showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":'''
    '''"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,'''
    '''"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],'''
    '''"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,'''
    '''"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,'''
    '''"scale":0}],"inputFormat":"file","inputFormatsAll":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},'''
    '''{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],"inputFormatsManual":[{"value":"manual","name":'''
    '''"Manually"}],"inputFormats":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},{"value":"query","name":'''
    '''"SQL Query"},{"value":"table","name":"Table"}],"path":"/user/hue/data/query-hive-360.csv","isObjectStore":false,"table":"",'''
    '''"tableName":"","databaseName":"default","apiHelperType":"hive","query":"","draggedQuery":"","format":{"type":"csv",'''
    '''"fieldSeparator":",","recordSeparator":"\\n","quoteChar":"\\"","hasHeader":true,"status":0},"show":true,"defaultName":'''
    '''"default.query-hive-360"}'''
  )
  destination = json.loads(
    '''{"isTransactional": false, "isInsertOnly": false, "sourceType": "hive", "name":"default.parquet_table"'''
    ''',"apiHelperType":"hive","description":"","outputFormat":"table","outputFormatsList":[{"name":"Table","value":"table"},'''
    '''{"name":"Solr index","value":"index"},{"name":"File","value":"file"},{"name":"Database","value":"database"}],'''
    '''"outputFormats":[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"}],"columns":[{"operations":[],'''
    '''"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":'''
    '''"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,'''
    '''"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":'''
    '''[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":'''
    '''100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":'''
    '''false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,tran_amount,tran_country_cd,vrfcn_city,'''
    '''vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,"isTargetChecking":false,"existingTargetUrl":'''
    '''"","tableName":"parquet_table","databaseName":"default","tableFormat":"parquet","KUDU_DEFAULT_RANGE_PARTITION_COLUMN":'''
    '''{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="},'''
    '''"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":[{"value":""}],"name":"VALUES","lower_val":0,'''
    '''"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH","int_val":16},"tableFormats":[{"value":'''
    '''"text","name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},{"value":"csv","name":"Csv"},'''
    '''{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},{"value":"orc",'''
    '''"name":"ORC"}],"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys":[],"primaryKeyObjects":[],"importData":true,'''
    '''"isIceberg":true,"useCopy":false,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv",'''
    '''"hasHeader":true,"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002",'''
    '''"customMapDelimiter":"\\\\003","customRegexp":""}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  print(sql)
  assert '''USE default;''' in sql, sql

  statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_parquet_table`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile LOCATION '/user/hue/data'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert (
    '''CREATE TABLE `default`.`parquet_table`
        STORED BY ICEBERG
STORED AS parquet
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
'''
    in sql
  ), sql

  assert '''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;''' in sql, sql


@pytest.mark.django_db
def test_generate_create_orc_table_transactional():
  source = json.loads(
    '''{"sourceType": "hive", "name":"","sample":[["Bank Of America","3000000.0","US","Miami","37.6801986694",'''
    '''"-121.92150116"],["Citi Bank","2800000.0","US","Richmond","37.5242004395","-77.4932022095"],["Deutsche Bank","2600000.0","US",'''
    '''"Corpus Christi","40.7807998657","-73.9772033691"],["Thomson Reuters","2400000.0","US","Albany","35.7976989746",'''
    '''"-78.6252975464"],'''
    '''["OpenX","2200000.0","US","Des Moines","40.5411987305","-119.586898804"]],"sampleCols":[{"operations":[],"comment":"",'''
    '''"nested":[],'''
    '''"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],'''
    '''"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":"string","required":'''
    '''false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city","level":0,'''
    '''"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"",'''
    '''"multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"",'''
    '''"nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":'''
    '''false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"double","showProperties":false,"scale":0}],"inputFormat":"file","inputFormatsAll":[{"value":"file","name":"File"},'''
    '''{"value":"manual","name":"Manually"},{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],'''
    '''"inputFormatsManual":[{"value":"manual","name":"Manually"}],"inputFormats":[{"value":"file","name":"File"},{"value":"manual",'''
    '''"name":"Manually"},{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],'''
    '''"path":"/user/hue/data/query-hive-360.csv","isObjectStore":false,"table":"","tableName":"","databaseName":"default",'''
    '''"apiHelperType":"hive","query":"","draggedQuery":"","format":{"type":"csv","fieldSeparator":",","recordSeparator":"\\n",'''
    '''"quoteChar":"\\"","hasHeader":true,"status":0},"show":true,"defaultName":"default.query-hive-360"}'''
  )
  destination = json.loads(
    '''{"isTransactional": true, "isInsertOnly": true, "sourceType": "hive", "name":'''
    '''"default.parquet_table","apiHelperType":"hive","description":"","outputFormat":"table","outputFormatsList":'''
    '''[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"},{"name":"File","value":"file"},'''
    '''{"name":"Database","value":"database"}],"outputFormats":[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"}],'''
    '''"columns":[{"operations":[],"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},'''
    '''{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},'''
    '''{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":'''
    '''"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,'''
    '''tran_amount,tran_country_cd,vrfcn_city,vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,'''
    '''"isTargetChecking":false,"existingTargetUrl":"","tableName":"parquet_table","databaseName":"default","tableFormat":"orc",'''
    '''"KUDU_DEFAULT_RANGE_PARTITION_COLUMN":{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=",'''
    '''"upper_val":1,"include_upper_val":"<="},"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":'''
    '''[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH",'''
    '''"int_val":16},"tableFormats":[{"value":"text","name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},'''
    '''{"value":"csv","name":"Csv"},{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},'''
    '''{"value":"orc","name":"ORC"}],"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys":[],"primaryKeyObjects":[],'''
    '''"importData":true,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv","hasHeader":true,'''
    '''"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002","customMapDelimiter":"\\\\003",'''
    '''"customRegexp":"","isIceberg":false,"useCopy":false}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert '''USE default;''' in sql, sql

  statement = '''CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`hue__tmp_parquet_table`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile LOCATION '/user/hue/data'
TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  assert (
    '''CREATE TABLE `default`.`parquet_table`
        STORED AS orc
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
'''
    in sql
  ), sql

  assert (
    '''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;
'''
    in sql
  ), sql


@pytest.mark.django_db
def test_generate_create_empty_kudu_table():
  source = json.loads('''{"sourceType": "impala", "apiHelperType": "impala", "path": "", "inputFormat": "manual"}''')
  destination = json.loads(
    '''{"isTransactional": false, "isInsertOnly": false, "sourceType": "impala", '''
    '''"name":"default.manual_empty_kudu","apiHelperType":"impala","description":"","outputFormat":"table",'''
    '''"columns":[{"operations":[],"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":'''
    '''"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"",'''
    '''"nested":[],"name":"tran_country_cd","level":0,"keyType":"string","required":false,"precision":10,"keep":true,'''
    '''"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":'''
    '''false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lat",'''
    '''"level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,'''
    '''"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},'''
    '''{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,'''
    '''"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,'''
    '''"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,tran_amount,tran_country_cd,vrfcn_city,'''
    '''vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,"isTargetChecking":false,"existingTargetUrl":'''
    '''"","tableName":"manual_kudu_table","databaseName":"default","tableFormat":"kudu","KUDU_DEFAULT_RANGE_PARTITION_COLUMN":'''
    '''{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="},'''
    '''"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":[{"value":""}],"name":"VALUES","lower_val":0,'''
    '''"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH","int_val":16},"tableFormats":[{"value":"text",'''
    '''"name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},{"value":"csv","name":"Csv"},'''
    '''{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},{"value":"orc","name":"ORC"}],'''
    '''"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys": ["acct_client"],"primaryKeyObjects":[],"importData":false,'''
    '''"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv","hasHeader":false,"useCustomDelimiters":'''
    '''false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002","customMapDelimiter":"\\\\003","customRegexp":"",'''
    '''"isIceberg":false,"useCopy":false}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert (
    '''CREATE TABLE `default`.`manual_empty_kudu`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double , PRIMARY KEY (acct_client)
)   STORED AS kudu TBLPROPERTIES('transactional'='false')
;'''
    in sql
  ), sql


@pytest.mark.django_db
def test_create_ddl_with_nonascii():
  source = {
    'kafkaFieldType': 'delimited',
    'rdbmsUsername': '',
    'kafkaFieldTypes': '',
    'selectedTableIndex': 0,
    'rdbmsJdbcDriverNames': [],
    'tableName': '',
    'sample': [
      ['Weihaiwei', '\u5a01\u6d77\u536b\u5e02', 'Weihai', '\u5a01\u6d77\u5e02', '1949-11-01'],
      ['Xingshan', '\u5174\u5c71\u5e02', 'Hegang', '\u9e64\u5c97\u5e02', '1950-03-23'],
      ["Xi'an", '\u897f\u5b89\u5e02', 'Liaoyuan', '\u8fbd\u6e90\u5e02', '1952-04-03'],
      ['Nanzheng', '\u5357\u90d1\u5e02', 'Hanzhong', '\u6c49\u4e2d\u5e02', '1953-10-24'],
      ['Dihua', '\u8fea\u5316\u5e02', '?r\xfcmqi', '\u4e4c\u9c81\u6728\u9f50\u5e02', '1953-11-20'],
    ],
    'rdbmsTypes': [],
    'isFetchingDatabaseNames': False,
    'rdbmsDbIsValid': False,
    'query': '',
    'channelSourceSelectedHosts': [],
    'table': '',
    'rdbmsAllTablesSelected': False,
    'inputFormatsManual': [{'name': 'Manually', 'value': 'manual'}],
    'rdbmsPassword': '',
    'isObjectStore': False,
    'tables': [{'name': ''}],
    'streamUsername': '',
    'kafkaSchemaManual': 'detect',
    'connectorSelection': 'sfdc',
    'namespace': {
      'status': 'CREATED',
      'computes': [{'credentials': {}, 'type': 'direct', 'id': 'default', 'name': 'default'}],
      'id': 'default',
      'name': 'default',
    },
    'rdbmsIsAllTables': False,
    'rdbmsDatabaseNames': [],
    'hasStreamSelected': False,
    'channelSourcePath': '/var/log/hue-httpd/access_log',
    'channelSourceHosts': [],
    'show': True,
    'streamObjects': [],
    'streamPassword': '',
    'tablesNames': [],
    'sampleCols': [
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'Before',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'old_Chinese_name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'After',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'new_Chinese_name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'Renamed_date',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
    ],
    'rdbmsDatabaseName': '',
    'sourceType': 'hive',
    'inputFormat': 'file',
    'format': {'status': 0, 'fieldSeparator': ',', 'hasHeader': True, 'quoteChar': '"', 'recordSeparator': '\\n', 'type': 'csv'},
    'connectorList': [{'name': 'Salesforce', 'value': 'sfdc'}],
    'kafkaFieldDelimiter': ',',
    'rdbmsPort': '',
    'rdbmsTablesExclude': [],
    'isFetchingDriverNames': False,
    'publicStreams': [{'name': 'Kafka Topics', 'value': 'kafka'}, {'name': 'Flume Agent', 'value': 'flume'}],
    'channelSourceTypes': [
      {'name': 'Directory or File', 'value': 'directory'},
      {'name': 'Program', 'value': 'exec'},
      {'name': 'Syslogs', 'value': 'syslogs'},
      {'name': 'HTTP', 'value': 'http'},
    ],
    'databaseName': 'default',
    'inputFormats': [
      {'name': 'File', 'value': 'file'},
      {'name': 'External Database', 'value': 'rdbms'},
      {'name': 'Manually', 'value': 'manual'},
    ],
    'path': '/user/admin/renamed_chinese_cities_gb2312.csv',
    'streamToken': '',
    'kafkaFieldNames': '',
    'streamSelection': 'kafka',
    'compute': {'credentials': {}, 'type': 'direct', 'id': 'default', 'name': 'default'},
    'name': '',
    'kafkaFieldSchemaPath': '',
    'kafkaTopics': [],
    'rdbmsJdbcDriver': '',
    'rdbmsHostname': '',
    'isFetchingTableNames': False,
    'rdbmsType': None,
    'inputFormatsAll': [
      {'name': 'File', 'value': 'file'},
      {'name': 'External Database', 'value': 'rdbms'},
      {'name': 'Manually', 'value': 'manual'},
    ],
    'rdbmsTableNames': [],
    'streamEndpointUrl': 'https://login.salesforce.com/services/Soap/u/42.0',
    'kafkaSelectedTopics': '',
  }
  destination = {
    'isTransactionalVisible': True,
    'KUDU_DEFAULT_PARTITION_COLUMN': {
      'int_val': 16,
      'name': 'HASH',
      'columns': [],
      'range_partitions': [
        {'include_upper_val': '<=', 'upper_val': 1, 'name': 'VALUES', 'include_lower_val': '<=', 'lower_val': 0, 'values': [{'value': ''}]}
      ],
    },
    'namespaces': [
      {
        'status': 'CREATED',
        'computes': [{'credentials': {}, 'type': 'direct', 'id': 'default', 'name': 'default'}],
        'id': 'default',
        'name': 'default',
      }
    ],
    'isTargetChecking': False,
    'ouputFormat': 'table',
    'tableName': 'renamed_chinese_cities_gb2312',
    'outputFormatsList': [
      {'name': 'Table', 'value': 'table'},
      {'name': 'Search index', 'value': 'index'},
      {'name': 'Database', 'value': 'database'},
      {'name': 'Folder', 'value': 'file'},
      {'name': 'HBase Table', 'value': 'hbase'},
    ],
    'fieldEditorPlaceHolder': 'Example: SELECT * FROM [object Promise]',
    'indexerDefaultField': [],
    'fieldEditorValue': 'SELECT Before,\n    old_Chinese_name,\n    After,\n    new_Chinese_name,\n    Renamed_date\n FROM [object Promise];',  # noqa: E501
    'customRegexp': '',
    'customLineDelimiter': '\\n',
    'isTargetExisting': False,
    'customEnclosedByDelimiter': "'",
    'indexerConfigSets': [],
    'sourceType': 'hive',
    'useCustomDelimiters': False,
    'apiHelperType': 'hive',
    'numMappers': 1,
    'fieldEditorDatabase': 'default',
    'namespace': {
      'status': 'CREATED',
      'computes': [{'credentials': {}, 'type': 'direct', 'id': 'default', 'name': 'default'}],
      'id': 'default',
      'name': 'default',
    },
    'indexerPrimaryKeyObject': [],
    'kuduPartitionColumns': [],
    'rdbmsFileOutputFormats': [
      {'name': 'text', 'value': 'text'},
      {'name': 'sequence', 'value': 'sequence'},
      {'name': 'avro', 'value': 'avro'},
    ],
    'outputFormats': [{'name': 'Table', 'value': 'table'}, {'name': 'Search index', 'value': 'index'}],
    'fieldEditorEnabled': False,
    'indexerDefaultFieldObject': [],
    'customMapDelimiter': '',
    'partitionColumns': [],
    'rdbmsFileOutputFormat': 'text',
    'showProperties': False,
    'isTransactional': True,
    'useDefaultLocation': True,
    'description': '',
    'customFieldsDelimiter': ',',
    'primaryKeyObjects': [],
    'customFieldDelimiter': ',',
    'rdbmsSplitByColumn': [],
    'existingTargetUrl': '',
    'channelSinkTypes': [{'name': 'This topic', 'value': 'kafka'}, {'name': 'Solr', 'value': 'solr'}, {'name': 'HDFS', 'value': 'hdfs'}],
    'defaultName': 'default.renamed_chinese_cities_gb2312',
    'isTransactionalUpdateEnabled': False,
    'importData': True,
    'isIceberg': False,
    'useCopy': False,
    'databaseName': 'default',
    'indexerRunJob': False,
    'indexerReplicationFactor': 1,
    'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {
      'include_upper_val': '<=',
      'upper_val': 1,
      'name': 'VALUES',
      'include_lower_val': '<=',
      'lower_val': 0,
      'values': [{'value': ''}],
    },
    'primaryKeys': [],
    'indexerConfigSet': '',
    'sqoopJobLibPaths': [{'path': ''}],
    'outputFormat': 'table',
    'nonDefaultLocation': '/user/admin/renamed_chinese_cities_gb2312.csv',
    'compute': {'credentials': {}, 'type': 'direct', 'id': 'default', 'name': 'default'},
    'name': 'default.renamed_chinese_cities_gb2312',
    'tableFormat': 'text',
    'isInsertOnly': True,
    'targetNamespaceId': 'default',
    'bulkColumnNames': 'Before,old_Chinese_name,After,new_Chinese_name,Renamed_date',
    'columns': [
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'Before',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'old_Chinese_name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'After',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'new_Chinese_name',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
      {
        'operations': [],
        'comment': '',
        'unique': False,
        'name': 'Renamed_date',
        'level': 0,
        'keyType': 'string',
        'required': False,
        'precision': 10,
        'nested': [],
        'isPartition': False,
        'length': 100,
        'partitionValue': '',
        'multiValued': False,
        'keep': True,
        'type': 'string',
        'showProperties': False,
        'scale': 0,
      },
    ],
    'hasHeader': True,
    'indexerPrimaryKey': [],
    'tableFormats': [
      {'name': 'Text', 'value': 'text'},
      {'name': 'Parquet', 'value': 'parquet'},
      {'name': 'Csv', 'value': 'csv'},
      {'name': 'Avro', 'value': 'avro'},
      {'name': 'Json', 'value': 'json'},
      {'name': 'Regexp', 'value': 'regexp'},
      {'name': 'ORC', 'value': 'orc'},
    ],
    'customCollectionDelimiter': '',
    'indexerNumShards': 1,
    'useFieldEditor': False,
    'indexerJobLibPath': '/tmp/smart_indexer_lib',
  }

  file_encoding = 'gb2312'
  path = {
    'isDir': False,
    'split': ('/user/admin', 'renamed_chinese_cities_gb2312.csv'),
    'listdir': ['/user/admin/data'],
    'parent_path': '/user/admin/.scratchdir/03d184ad-dd11-4ae1-aace-378daaa094e5/renamed_chinese_cities_gb2312.csv/..',
  }
  request = MockRequest(fs=MockFs(path=path))

  sql = (
    SQLIndexer(user=request.user, fs=request.fs)
    .create_table_from_a_file(source, destination, start_time=-1, file_encoding=file_encoding)
    .get_str()
  )

  assert '''USE default;''' in sql, sql

  statement = '''CREATE TABLE IF NOT EXISTS `default`.`hue__tmp_renamed_chinese_cities_gb2312`
(
  `Before` string ,
  `old_Chinese_name` string ,
  `After` string ,
  `new_Chinese_name` string ,
  `Renamed_date` string ) ROW FORMAT   DELIMITED
    FIELDS TERMINATED BY ','
    COLLECTION ITEMS TERMINATED BY '\\002'
    MAP KEYS TERMINATED BY '\\003'
  STORED AS TextFile TBLPROPERTIES('skip.header.line.count'='1', 'transactional'='false')
;'''
  assert statement in sql, sql

  statement = (
    "LOAD DATA INPATH '/user/admin/renamed_chinese_cities_gb2312.csv' " + "INTO TABLE `default`.`hue__tmp_renamed_chinese_cities_gb2312`;"
  )
  assert statement in sql, sql

  statement = '''CREATE TABLE `default`.`renamed_chinese_cities_gb2312`
        STORED AS TextFile
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_renamed_chinese_cities_gb2312`;'''
  assert statement in sql, sql

  statement = '''DROP TABLE IF EXISTS `default`.`hue__tmp_renamed_chinese_cities_gb2312`;'''
  assert statement in sql, sql

  statement = '''ALTER TABLE `default`.`renamed_chinese_cities_gb2312` ''' + '''SET serdeproperties ("serialization.encoding"="gb2312");'''
  assert statement in sql, sql


@pytest.mark.django_db
def test_create_ddl_with_abfs():
  finish = ABFS_CLUSTERS.set_for_testing(
    {
      'default': {
        'fs_defaultfs': 'abfs://my-data@yingstorage.dfs.core.windows.net',
        'webhdfs_url': 'https://yingstorage.dfs.core.windows.net',
      }
    }
  )

  form_data = {'path': 'abfs://my-data/test_data/cars.csv', 'partition_columns': [], 'overwrite': False}
  sql = ''
  request = MockRequest(fs=MockFs())
  query_server_config = dbms.get_query_server_config(name='impala')
  db = dbms.get(request.user, query_server=query_server_config)
  try:
    sql = "\n\n%s;" % db.load_data('default', 'cars', form_data, None, generate_ddl_only=True)
  finally:
    finish()
  assert "'abfs://my-data@yingstorage.dfs.core.windows.net/test_data/cars.csv'" in sql


@pytest.mark.django_db
def test_create_table_from_local():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Hive', 'dialect': 'hive'}
    source = {'path': '', 'sourceType': 'hive'}
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'date', 'type': 'timestamp', 'keep': True},
        {'name': 'hour', 'type': 'bigint', 'keep': True},
        {'name': 'minute', 'type': 'bigint', 'keep': True},
        {'name': 'dep', 'type': 'bigint', 'keep': True},
        {'name': 'arr', 'type': 'bigint', 'keep': True},
        {'name': 'dep_delay', 'type': 'bigint', 'keep': True},
        {'name': 'arr_delay', 'type': 'bigint', 'keep': True},
        {'name': 'carrier', 'type': 'string', 'keep': True},
        {'name': 'flight', 'type': 'bigint', 'keep': True},
        {'name': 'dest', 'type': 'string', 'keep': True},
        {'name': 'plane', 'type': 'string', 'keep': True},
        {'name': 'cancelled', 'type': 'boolean', 'keep': True},
        {'name': 'time', 'type': 'bigint', 'keep': True},
        {'name': 'dist', 'type': 'bigint', 'keep': True},
      ],
      'indexerPrimaryKey': [],
      'sourceType': 'hive',
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_local_file(source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS default.test1 (
  `date` timestamp,
  `hour` bigint,
  `minute` bigint,
  `dep` bigint,
  `arr` bigint,
  `dep_delay` bigint,
  `arr_delay` bigint,
  `carrier` string,
  `flight` bigint,
  `dest` string,
  `plane` string,
  `cancelled` boolean,
  `time` bigint,
  `dist` bigint);'''

    assert statement == sql


def test_create_table_from_local_mysql():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'MySQL', 'dialect': 'mysql'}
    source = {'path': BASE_DIR + '/apps/beeswax/data/tables/us_population.csv', 'sourceType': 'mysql', 'format': {'hasHeader': False}}
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'field_1', 'type': 'string', 'keep': True},
        {'name': 'field_2', 'type': 'string', 'keep': True},
        {'name': 'field_3', 'type': 'bigint', 'keep': True},
      ],
      'sourceType': 'mysql',
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_local_file(source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS default.test1 (
  `field_1` VARCHAR(255),
  `field_2` VARCHAR(255),
  `field_3` bigint);

INSERT INTO default.test1 VALUES ('NY', 'New York', '8143197'), ('CA', 'Los Angeles', '3844829'), \
('IL', 'Chicago', '2842518'), ('TX', 'Houston', '2016582'), ('PA', 'Philadelphia', '1463281'), \
('AZ', 'Phoenix', '1461575'), ('TX', 'San Antonio', '1256509'), ('CA', 'San Diego', '1255540'), \
('TX', 'Dallas', '1213825'), ('CA', 'San Jose', '912332');'''

    assert statement == sql


@pytest.mark.django_db
def test_create_table_from_local_impala():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Impala', 'dialect': 'impala'}
    source = {'path': BASE_DIR + '/apps/beeswax/data/tables/flights.csv', 'sourceType': 'impala', 'format': {'hasHeader': True}}
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'date', 'type': 'timestamp', 'keep': True},
        {'name': 'hour', 'type': 'bigint', 'keep': True},
        {'name': 'minute', 'type': 'bigint', 'keep': True},
        {'name': 'dep', 'type': 'bigint', 'keep': True},
        {'name': 'arr', 'type': 'bigint', 'keep': True},
        {'name': 'dep_delay', 'type': 'bigint', 'keep': True},
        {'name': 'arr_delay', 'type': 'bigint', 'keep': True},
        {'name': 'carrier', 'type': 'string', 'keep': True},
        {'name': 'flight', 'type': 'bigint', 'keep': True},
        {'name': 'dest', 'type': 'string', 'keep': True},
        {'name': 'plane', 'type': 'string', 'keep': True},
        {'name': 'cancelled', 'type': 'boolean', 'keep': True},
        {'name': 'time', 'type': 'bigint', 'keep': True},
        {'name': 'dist', 'type': 'bigint', 'keep': True},
      ],
      'sourceType': 'impala',
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_local_file(source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS default.test1_tmp (
  `date` string,
  `hour` string,
  `minute` string,
  `dep` string,
  `arr` string,
  `dep_delay` string,
  `arr_delay` string,
  `carrier` string,
  `flight` string,
  `dest` string,
  `plane` string,
  `cancelled` string,
  `time` string,
  `dist` string);

INSERT INTO default.test1_tmp VALUES \
('2011-12-14 12:00:00', '13', '4', '1304', '1704', '24', '14', 'WN', '3085', 'PHL', 'N524SW', '1', '159', '1336'), \
('2011-12-14 12:00:00', '17', '52', '1752', '1943', '12', '8', 'WN', '39', 'PHX', 'N503SW', '1', '155', '1020'), \
('2011-12-14 12:00:00', '7', '9', '709', '853', '-1', '-12', 'WN', '424', 'PHX', 'N761RR', '1', '152', '1020'), \
('2011-12-14 12:00:00', '13', '32', '1332', '1514', '17', '4', 'WN', '1098', 'PHX', 'N941WN', '1', '151', '1020'), \
('2011-12-14 12:00:00', '9', '55', '955', '1141', '5', '-4', 'WN', '1403', 'PHX', 'N472WN', '1', '155', '1020'), \
('2011-12-14 12:00:00', '16', '13', '1613', '1731', '8', '-4', 'WN', '33', 'SAN', 'N707SA', '1', '185', '1313'), \
('2011-12-14 12:00:00', '11', '45', '1145', '1257', '5', '-13', 'WN', '1212', 'SAN', 'N279WN', '0', '183', '1313'), \
('2011-12-14 12:00:00', '20', '16', '2016', '2112', '36', '32', 'WN', '207', 'SAT', 'N929WN', '0', '44', '192');

CREATE TABLE IF NOT EXISTS default.test1
AS SELECT
  CAST ( `date` AS timestamp ) `date`,
  CAST ( `hour` AS bigint ) `hour`,
  CAST ( `minute` AS bigint ) `minute`,
  CAST ( `dep` AS bigint ) `dep`,
  CAST ( `arr` AS bigint ) `arr`,
  CAST ( `dep_delay` AS bigint ) `dep_delay`,
  CAST ( `arr_delay` AS bigint ) `arr_delay`,
  CAST ( `carrier` AS string ) `carrier`,
  CAST ( `flight` AS bigint ) `flight`,
  CAST ( `dest` AS string ) `dest`,
  CAST ( `plane` AS string ) `plane`,
  CAST ( CAST ( `cancelled` AS TINYINT ) AS boolean ) `cancelled`,
  CAST ( `time` AS bigint ) `time`,
  CAST ( `dist` AS bigint ) `dist`
FROM  default.test1_tmp;

DROP TABLE IF EXISTS default.test1_tmp;'''

    assert statement == sql


@pytest.mark.django_db
def test_create_table_only_header_file_local_impala():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Impala', 'dialect': 'impala'}
    source = {'path': BASE_DIR + '/apps/beeswax/data/tables/onlyheader.csv', 'sourceType': 'impala', 'format': {'hasHeader': True}}
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'date', 'type': 'timestamp', 'keep': True},
        {'name': 'hour', 'type': 'bigint', 'keep': True},
        {'name': 'minute', 'type': 'bigint', 'keep': True},
        {'name': 'dep', 'type': 'bigint', 'keep': True},
        {'name': 'arr', 'type': 'bigint', 'keep': True},
        {'name': 'dep_delay', 'type': 'bigint', 'keep': True},
        {'name': 'arr_delay', 'type': 'bigint', 'keep': True},
        {'name': 'carrier', 'type': 'string', 'keep': True},
        {'name': 'flight', 'type': 'bigint', 'keep': True},
        {'name': 'dest', 'type': 'string', 'keep': True},
        {'name': 'plane', 'type': 'string', 'keep': True},
        {'name': 'cancelled', 'type': 'boolean', 'keep': True},
        {'name': 'time', 'type': 'bigint', 'keep': True},
        {'name': 'dist', 'type': 'bigint', 'keep': True},
      ],
      'sourceType': 'impala',
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_local_file(source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS default.test1_tmp (
  `date` string,
  `hour` string,
  `minute` string,
  `dep` string,
  `arr` string,
  `dep_delay` string,
  `arr_delay` string,
  `carrier` string,
  `flight` string,
  `dest` string,
  `plane` string,
  `cancelled` string,
  `time` string,
  `dist` string);

CREATE TABLE IF NOT EXISTS default.test1
AS SELECT
  CAST ( `date` AS timestamp ) `date`,
  CAST ( `hour` AS bigint ) `hour`,
  CAST ( `minute` AS bigint ) `minute`,
  CAST ( `dep` AS bigint ) `dep`,
  CAST ( `arr` AS bigint ) `arr`,
  CAST ( `dep_delay` AS bigint ) `dep_delay`,
  CAST ( `arr_delay` AS bigint ) `arr_delay`,
  CAST ( `carrier` AS string ) `carrier`,
  CAST ( `flight` AS bigint ) `flight`,
  CAST ( `dest` AS string ) `dest`,
  CAST ( `plane` AS string ) `plane`,
  CAST ( CAST ( `cancelled` AS TINYINT ) AS boolean ) `cancelled`,
  CAST ( `time` AS bigint ) `time`,
  CAST ( `dist` AS bigint ) `dist`
FROM  default.test1_tmp;

DROP TABLE IF EXISTS default.test1_tmp;'''

    assert statement == sql


@pytest.mark.django_db
def test_create_table_with_drop_column_from_local():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Hive', 'dialect': 'hive'}
    source = {'path': '', 'sourceType': 'hive'}
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'date', 'type': 'timestamp', 'keep': False},
        {'name': 'hour', 'type': 'bigint', 'keep': True},
        {'name': 'minute', 'type': 'bigint', 'keep': False},
        {'name': 'dep', 'type': 'bigint', 'keep': True},
        {'name': 'arr', 'type': 'bigint', 'keep': False},
      ],
      'indexerPrimaryKey': [],
      'sourceType': 'hive',
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_local_file(source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS default.test1 (
  `hour` bigint,
  `dep` bigint);'''

    assert statement == sql


@pytest.mark.django_db
def test_create_table_with_manual_steps():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Hive', 'dialect': 'hive'}
    source = {
    'sourceType': 'impala', 'path': '', 'inputFormat': 'manual',
    'format': {
        'quoteChar': '"',
        'fieldSeparator': ','
      }
    }
    destination = {
    'sourceType': 'impala', 'name': 'complex_test2.test3', 'description': '', 'tableFormat': 'text',
    'columns': [
      {'name': 'new_field_1', 'type': 'string', 'keep': True},
      {'name': 'new_field_2', 'type': 'string', 'keep': True}
    ],
    'partitionColumns': [], 'kuduPartitionColumns': [], 'primaryKeys': [], 'importData': True, 'useDefaultLocation': True,
    'nonDefaultLocation': '', 'isTransactional': True, 'isInsertOnly': True, 'useCopy': False, 'hasHeader': False,
    'useCustomDelimiters': False, 'customFieldDelimiter': ',', 'customCollectionDelimiter': '', 'customMapDelimiter': '',
    'customRegexp': '', 'isIceberg': False,
    'compute': {'id': 'default', 'name': 'default', 'type': 'direct', 'credentials': {}},
    'namespace': {
      'id': 'default', 'name': 'default', 'status': 'CREATED',
      'computes': [{'id': 'default', 'name': 'default', 'type': 'direct', 'credentials': {}}]},
    'databaseName': 'complex_test2',
    'tableName': 'test3',
    'isTransactional': True
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_a_file(source, destination).get_str()

    statement = '''USE complex_test2;

CREATE TABLE `complex_test2`.`test3`
(
  `new_field_1` string ,
  `new_field_2` string )   STORED AS TextFile TBLPROPERTIES('transactional'='true')
;'''

    assert statement == sql
