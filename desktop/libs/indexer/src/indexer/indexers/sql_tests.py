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

from builtins import object
import json
import sys

from nose.tools import assert_equal, assert_true

from desktop.lib.django_test_util import make_logged_in_client
from desktop.settings import BASE_DIR
from useradmin.models import User

from azure.conf import ABFS_CLUSTERS
from beeswax.server import dbms
from indexer.indexers.sql import SQLIndexer


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


class TestSQLIndexer(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="empty", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")


  def test_create_table_from_a_file_to_csv(self):
    fs = Mock(
      stats=Mock(return_value={'mode': 0o0777})
    )

    def source_dict(key):
      return {
        'path': 'hdfs:///path/data.csv',
        'format': {'quoteChar': '"', 'fieldSeparator': ','},
        'sampleCols': [{u'operations': [], u'comment': u'', u'name': u'customers.id'}],
        'sourceType': 'hive'
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
        'sourceType': 'hive-1'
      }.get(key, Mock())
    destination = MagicMock()
    destination.__getitem__.side_effect = destination_dict

    with patch('notebook.models.get_interpreter') as get_interpreter:
      notebook = SQLIndexer(user=self.user, fs=fs).create_table_from_a_file(source, destination)

    assert_equal(
      [statement.strip() for statement in u'''DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;

CREATE TABLE `default`.`hue__tmp_export_table`
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

DROP TABLE IF EXISTS `default`.`hue__tmp_export_table`;'''.split(';')],
    [statement.strip() for statement in notebook.get_data()['snippets'][0]['statement_raw'].split(';')]
  )


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


def test_generate_create_text_table_with_data_partition():
  source = {
    u'sourceType': 'hive', u'sampleCols': [{u'operations': [], u'comment': u'', u'name': u'customers.id', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'',
    u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'customers.name', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False,
    u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'customers.email_preferences', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [],
    u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type':
    u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.addresses',
    u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100,
    u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'customers.orders', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False,
    u'type': u'string', u'showProperties': False, u'keep': True}], u'name': u'', u'inputFormat': u'file',
    u'format': {u'status': 0, u'fieldSeparator': u',', u'hasHeader': True, u'quoteChar': u'"',
    u'recordSeparator': u'\\n', u'type': u'csv'}, u'defaultName': u'default.customer_stats', u'show': True,
    u'tableName': u'', u'sample': [], u'apiHelperType': u'hive', u'inputFormatsAll': [{u'name': u'File', u'value': u'file'},
    {u'name': u'Manually', u'value': u'manual'}, {u'name': u'SQL Query', u'value': u'query'},
    {u'name': u'Table', u'value': u'table'}], u'query': u'', u'databaseName': u'default', u'table': u'',
    u'inputFormats': [{u'name': u'File', u'value': u'file'}, {u'name': u'Manually', u'value': u'manual'},
    {u'name': u'SQL Query', u'value': u'query'}, {u'name': u'Table', u'value': u'table'}],
    u'path': u'/user/romain/customer_stats.csv', u'draggedQuery': u'',
    u'inputFormatsManual': [{u'name': u'Manually', u'value': u'manual'}], u'isObjectStore': False
  }
  destination = {
    u'isTransactional': False, u'isInsertOnly': False, u'sourceType': 'hive',
    u'KUDU_DEFAULT_PARTITION_COLUMN': {u'int_val': 16, u'name': u'HASH', u'columns': [],
    u'range_partitions': [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=',
    u'lower_val': 0, u'values': [{u'value': u''}]}]}, u'isTargetChecking': False, u'tableName': u'customer_stats',
    u'outputFormatsList': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr index', u'value': u'index'},
    {u'name': u'File', u'value': u'file'}, {u'name': u'Database', u'value': u'database'}], u'customRegexp': u'',
    u'isTargetExisting': False, u'partitionColumns': [{u'operations': [], u'comment': u'', u'name': u'new_field_1',
    u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': True, u'length': 100,
    u'partitionValue': u'AAA', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}],
    u'useCustomDelimiters': False, u'apiHelperType': u'hive', u'kuduPartitionColumns': [],
    u'outputFormats': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr index', u'value': u'index'}],
    u'customMapDelimiter': u'\\003', u'showProperties': False, u'useDefaultLocation': True, u'description': u'',
    u'primaryKeyObjects': [], u'customFieldDelimiter': u',', u'existingTargetUrl': u'', u'importData': True, u'isIceberg': False,
    u'databaseName': u'default', u'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {u'include_upper_val': u'<=', u'upper_val': 1,
    u'name': u'VALUES', u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}, u'primaryKeys': [],
    u'outputFormat': u'table', u'nonDefaultLocation': u'/user/romain/customer_stats.csv', u'name': u'default.customer_stats',
    u'tableFormat': u'text', 'ouputFormat': u'table',
    u'bulkColumnNames': u'customers.id,customers.name,customers.email_preferences,customers.addresses,customers.orders',
    u'columns': [{u'operations': [], u'comment': u'', u'name': u'customers.id', u'level': 0, u'keyType': u'string',
    u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
    u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'customers.name', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False,
    u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False,
    u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.email_preferences', u'level': 0, u'keyType': u'string',
    u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
    u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'customers.addresses', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False,
    u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False,
    u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.orders', u'level': 0, u'keyType': u'string',
    u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
    u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'hasHeader': True,
    u'tableFormats': [{u'name': u'Text', u'value': u'text'}, {u'name': u'Parquet', u'value': u'parquet'},
    {u'name': u'Kudu', u'value': u'kudu'}, {u'name': u'Csv', u'value': u'csv'}, {u'name': u'Avro', u'value': u'avro'},
    {u'name': u'Json', u'value': u'json'}, {u'name': u'Regexp', u'value': u'regexp'}, {u'name': u'ORC', u'value': u'orc'}],
    u'customCollectionDelimiter': u'\\002'
  }
  request = MockRequest(fs=MockFs())

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''USE default;''' in sql, sql)

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
  assert_true(statement in sql, sql)

  assert_true(
    '''LOAD DATA INPATH '/user/romain/customer_stats.csv' '''
    '''INTO TABLE `default`.`customer_stats` PARTITION (new_field_1='AAA');''' in sql,
    sql
  )


def test_generate_create_kudu_table_with_data():
  source = {
    u'sourceType': 'impala', u'apiHelperType': 'hive', u'sampleCols': [], u'name': u'', u'inputFormat': u'file',
    u'format': {u'quoteChar': u'"', u'recordSeparator': u'\\n', u'type': u'csv', u'hasHeader': True, u'fieldSeparator': u','},
    u'show': True, u'tableName': u'', u'sample': [], u'defaultName': u'index_data', u'query': u'', u'databaseName': u'default',
    u'table': u'', u'inputFormats': [{u'name': u'File', u'value': u'file'}, {u'name': u'Manually', u'value': u'manual'}],
    u'path': u'/user/admin/index_data.csv', u'draggedQuery': u'', u'isObjectStore': False
  }
  destination = {
    u'isTransactional': False, u'isInsertOnly': False, u'sourceType': 'impala',
    u'KUDU_DEFAULT_PARTITION_COLUMN': {u'int_val': 16, u'name': u'HASH', u'columns': [],
    u'range_partitions': [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=',
    u'lower_val': 0, u'values': [{u'value': u''}]}]}, u'tableName': u'index_data',
    u'outputFormatsList': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr+index', u'value': u'index'},
    {u'name': u'File', u'value': u'file'}, {u'name': u'Database', u'value': u'database'}], u'customRegexp': u'',
    u'isTargetExisting': False, u'partitionColumns': [], u'useCustomDelimiters': True,
    u'kuduPartitionColumns': [{u'int_val': 16, u'name': u'HASH', u'columns': [u'id'],
    u'range_partitions': [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=',
    u'lower_val': 0, u'values': [{u'value': u''}]}]}], u'outputFormats': [{u'name': u'Table', u'value': u'table'},
    {u'name': u'Solr+index', u'value': u'index'}], u'customMapDelimiter': None, u'showProperties': False, u'useDefaultLocation': True,
    u'description': u'Big Data', u'primaryKeyObjects': [{u'operations': [], u'comment': u'', u'name': u'id', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False,
    u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'customFieldDelimiter': u',',
    u'existingTargetUrl': u'', u'importData': True, u'isIceberg': False, u'databaseName': u'default',
    u'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES',
    u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}, u'primaryKeys': [u'id'],
    u'outputFormat': u'table', u'nonDefaultLocation': u'/user/admin/index_data.csv', u'name': u'index_data',
    u'tableFormat': u'kudu',
    u'bulkColumnNames': u'business_id,cool,date,funny,id,stars,text,type,useful,user_id,name,full_address,latitude,'
    'longitude,neighborhoods,open,review_count,state', u'columns': [{u'operations': [], u'comment': u'', u'name': u'business_id',
    u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100,
    u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'cool', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint',
    u'showProperties': False, u'keep': False}, {u'operations': [], u'comment': u'', u'name': u'date', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False,
    u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'funny', u'level': 0, u'scale': 4, u'precision': 10, u'keyType': u'string', u'required': False, u'nested': [],
    u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'decimal', u'showProperties': False,
    u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'id', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string',
    u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'stars', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False,
    u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'text', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100,
    u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'type', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [],
    u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False,
    u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'useful', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint',
    u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'user_id', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False,
    u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'name', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False,
    u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'full_address', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string',
    u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'latitude', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False,
    u'unique': False, u'type': u'double', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'longitude', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False,
    u'length': 100, u'multiValued': False, u'unique': False, u'type': u'double', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'neighborhoods', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string',
    u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'open', u'level': 0,
    u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False,
    u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'',
    u'name': u'review_count', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False,
    u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True},
    {u'operations': [], u'comment': u'', u'name': u'state', u'level': 0, u'keyType': u'string', u'required': False,
    u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string',
    u'showProperties': False, u'keep': True}], u'hasHeader': True, u'tableFormats': [{u'name': u'Text', u'value': u'text'},
    {u'name': u'Parquet', u'value': u'parquet'}, {u'name': u'Json', u'value': u'json'}, {u'name': u'Kudu', u'value': u'kudu'},
    {u'name': u'Avro', u'value': u'avro'}, {u'name': u'Regexp', u'value': u'regexp'}, {u'name': u'RCFile', u'value': u'rcfile'},
    {u'name': u'ORC', u'value': u'orc'}, {u'name': u'SequenceFile', u'value': u'sequencefile'}], u'customCollectionDelimiter': None
  }
  request = MockRequest(fs=MockFs())

  with patch('hadoop.fs.hadoopfs.Hdfs.split') as split:
    split.return_value = ('/A', 'a')
    sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

    assert_true('''DROP TABLE IF EXISTS `default`.`hue__tmp_index_data`;''' in sql, sql)

    statement = '''CREATE EXTERNAL TABLE `default`.`hue__tmp_index_data`
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
    assert_true(statement in sql, sql)

    assert_true('''CREATE TABLE `default`.`index_data` COMMENT "Big Data"
        PRIMARY KEY (id)
        PARTITION BY HASH PARTITIONS 16
        STORED AS kudu
        TBLPROPERTIES(
        'kudu.num_tablet_replicas'='1'
        )
        AS SELECT `id`, `business_id`, `date`, `funny`, `stars`, `text`, `type`, `useful`, `user_id`, `name`, '''
        '''`full_address`, `latitude`, `longitude`, `neighborhoods`, `open`, `review_count`, `state`
        FROM `default`.`hue__tmp_index_data`''' in sql,
      sql
    )


def test_generate_create_parquet_table():
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
  destination = json.loads('''{"isTransactional": false, "isInsertOnly": false, "sourceType": "hive", "name":"default.parquet_table"'''
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
    '''"isIceberg":false,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv","hasHeader":true,'''
    '''"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002","customMapDelimiter":"\\\\003",'''
    '''"customRegexp":""}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''USE default;''' in sql, sql)

  statement = '''CREATE EXTERNAL TABLE `default`.`hue__tmp_parquet_table`
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
  assert_true(statement in sql, sql)

  assert_true('''CREATE TABLE `default`.`parquet_table`
        STORED AS parquet
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
''' in sql, sql)

  assert_true('''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;''' in sql, sql)


def test_generate_create_iceberg_table():
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
  destination = json.loads('''{"isTransactional": false, "isInsertOnly": false, "sourceType": "hive", "name":"default.parquet_table"'''
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
    '''"isIceberg":true,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv","hasHeader":true,'''
    '''"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002","customMapDelimiter":"\\\\003",'''
    '''"customRegexp":""}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  print(sql)
  assert_true('''USE default;''' in sql, sql)

  statement = '''CREATE EXTERNAL TABLE `default`.`hue__tmp_parquet_table`
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
  assert_true(statement in sql, sql)

  assert_true('''CREATE TABLE `default`.`parquet_table`
        STORED BY ICEBERG
STORED AS parquet
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
''' in sql, sql)

  assert_true('''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;''' in sql, sql)


def test_generate_create_orc_table_transactional():
  source = json.loads('''{"sourceType": "hive", "name":"","sample":[["Bank Of America","3000000.0","US","Miami","37.6801986694",'''
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
  destination = json.loads('''{"isTransactional": true, "isInsertOnly": true, "sourceType": "hive", "name":'''
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
  '''"customRegexp":"","isIceberg":false}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''USE default;''' in sql, sql)

  statement = '''CREATE EXTERNAL TABLE `default`.`hue__tmp_parquet_table`
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
  assert_true(statement in sql, sql)

  assert_true('''CREATE TABLE `default`.`parquet_table`
        STORED AS orc
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
''' in sql, sql)

  assert_true('''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;
''' in sql, sql)


def test_generate_create_empty_kudu_table():
  source = json.loads('''{"sourceType": "impala", "apiHelperType": "impala", "path": "", "inputFormat": "manual"}''')
  destination = json.loads('''{"isTransactional": false, "isInsertOnly": false, "sourceType": "impala", '''
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
    '''"isIceberg":false}'''
  )

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''CREATE TABLE `default`.`manual_empty_kudu`
(
  `acct_client` string ,
  `tran_amount` double ,
  `tran_country_cd` string ,
  `vrfcn_city` string ,
  `vrfcn_city_lat` double ,
  `vrfcn_city_lon` double , PRIMARY KEY (acct_client)
)   STORED AS kudu TBLPROPERTIES('transactional'='false')
;''' in sql, sql)


def test_create_ddl_with_nonascii():
  source = {u'kafkaFieldType': u'delimited', u'rdbmsUsername': u'', u'kafkaFieldTypes': u'',
            u'selectedTableIndex': 0, u'rdbmsJdbcDriverNames': [], u'tableName': u'',
            u'sample': [[u'Weihaiwei', u'\u5a01\u6d77\u536b\u5e02', u'Weihai', u'\u5a01\u6d77\u5e02', u'1949-11-01'],
                        [u'Xingshan', u'\u5174\u5c71\u5e02', u'Hegang', u'\u9e64\u5c97\u5e02', u'1950-03-23'],
                        [u"Xi'an", u'\u897f\u5b89\u5e02', u'Liaoyuan', u'\u8fbd\u6e90\u5e02', u'1952-04-03'],
                        [u'Nanzheng', u'\u5357\u90d1\u5e02', u'Hanzhong', u'\u6c49\u4e2d\u5e02', u'1953-10-24'],
                        [u'Dihua', u'\u8fea\u5316\u5e02', u'?r\xfcmqi', u'\u4e4c\u9c81\u6728\u9f50\u5e02', u'1953-11-20']],
            u'rdbmsTypes': [], u'isFetchingDatabaseNames': False, u'rdbmsDbIsValid': False, u'query': u'',
            u'channelSourceSelectedHosts': [], u'table': u'', u'rdbmsAllTablesSelected': False,
            u'inputFormatsManual': [{u'name': u'Manually', u'value': u'manual'}], u'rdbmsPassword': u'',
            u'isObjectStore': False, u'tables': [{u'name': u''}], u'streamUsername': u'',
            u'kafkaSchemaManual': u'detect', u'connectorSelection': u'sfdc', u'namespace':
              {u'status': u'CREATED', u'computes':
                [{u'credentials': {}, u'type': u'direct', u'id': u'default', u'name': u'default'}],
               u'id': u'default', u'name': u'default'}, u'rdbmsIsAllTables': False, u'rdbmsDatabaseNames': [],
            u'hasStreamSelected': False, u'channelSourcePath': u'/var/log/hue-httpd/access_log',
            u'channelSourceHosts': [], u'show': True, u'streamObjects': [], u'streamPassword': u'',
            u'tablesNames': [], u'sampleCols': [{u'operations': [], u'comment': u'', u'unique': False,
                                                 u'name': u'Before', u'level': 0, u'keyType': u'string',
                                                 u'required': False, u'precision': 10, u'nested': [],
                                                 u'isPartition': False, u'length': 100, u'partitionValue': u'',
                                                 u'multiValued': False, u'keep': True, u'type': u'string',
                                                 u'showProperties': False, u'scale': 0},
                                                {u'operations': [], u'comment': u'', u'unique': False,
                                                 u'name': u'old_Chinese_name', u'level': 0, u'keyType':
                                                   u'string', u'required': False, u'precision': 10, u'nested': [],
                                                 u'isPartition': False, u'length': 100, u'partitionValue': u'',
                                                 u'multiValued': False, u'keep': True, u'type': u'string',
                                                 u'showProperties': False, u'scale': 0},
                                                {u'operations': [], u'comment': u'', u'unique': False,
                                                 u'name': u'After', u'level': 0, u'keyType': u'string',
                                                 u'required': False, u'precision': 10, u'nested': [],
                                                 u'isPartition': False, u'length': 100, u'partitionValue': u'',
                                                 u'multiValued': False, u'keep': True, u'type': u'string',
                                                 u'showProperties': False, u'scale': 0},
                                                {u'operations': [], u'comment': u'', u'unique': False,
                                                 u'name': u'new_Chinese_name', u'level': 0, u'keyType':
                                                   u'string', u'required': False, u'precision': 10, u'nested': [],
                                                 u'isPartition': False, u'length': 100, u'partitionValue': u'',
                                                 u'multiValued': False, u'keep': True, u'type': u'string',
                                                 u'showProperties': False, u'scale': 0},
                                                {u'operations': [], u'comment': u'', u'unique': False,
                                                 u'name': u'Renamed_date', u'level': 0, u'keyType': u'string',
                                                 u'required': False, u'precision': 10, u'nested': [],
                                                 u'isPartition': False, u'length': 100, u'partitionValue': u'',
                                                 u'multiValued': False, u'keep': True, u'type': u'string',
                                                 u'showProperties': False, u'scale': 0}], u'rdbmsDatabaseName': u'',
            u'sourceType': u'hive', u'inputFormat': u'file', u'format': {u'status': 0, u'fieldSeparator': u',',
                                                                         u'hasHeader': True, u'quoteChar': u'"',
                                                                         u'recordSeparator': u'\\n', u'type': u'csv'},
            u'connectorList': [{u'name': u'Salesforce', u'value': u'sfdc'}], u'kafkaFieldDelimiter': u',',
            u'rdbmsPort': u'', u'rdbmsTablesExclude': [], u'isFetchingDriverNames': False, u'publicStreams':
              [{u'name': u'Kafka Topics', u'value': u'kafka'}, {u'name': u'Flume Agent', u'value': u'flume'}],
            u'channelSourceTypes': [{u'name': u'Directory or File', u'value': u'directory'},
                                    {u'name': u'Program', u'value': u'exec'},
                                    {u'name': u'Syslogs', u'value': u'syslogs'},
                                    {u'name': u'HTTP', u'value': u'http'}],
            u'databaseName': u'default', u'inputFormats': [{u'name': u'File', u'value': u'file'},
                                                           {u'name': u'External Database', u'value': u'rdbms'},
                                                           {u'name': u'Manually', u'value': u'manual'}],
            u'path': u'/user/admin/renamed_chinese_cities_gb2312.csv', u'streamToken': u'', u'kafkaFieldNames': u'',
            u'streamSelection': u'kafka', u'compute': {u'credentials': {}, u'type': u'direct',
                                                       u'id': u'default', u'name': u'default'},
            u'name': u'', u'kafkaFieldSchemaPath': u'', u'kafkaTopics': [], u'rdbmsJdbcDriver': u'',
            u'rdbmsHostname': u'', u'isFetchingTableNames': False, u'rdbmsType': None, u'inputFormatsAll':
              [{u'name': u'File', u'value': u'file'}, {u'name': u'External Database', u'value': u'rdbms'},
               {u'name': u'Manually', u'value': u'manual'}], u'rdbmsTableNames': [],
            u'streamEndpointUrl': u'https://login.salesforce.com/services/Soap/u/42.0', u'kafkaSelectedTopics': u''}
  destination = {u'isTransactionalVisible': True, u'KUDU_DEFAULT_PARTITION_COLUMN':
    {u'int_val': 16, u'name': u'HASH', u'columns': [], u'range_partitions':
      [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=',
        u'lower_val': 0, u'values': [{u'value': u''}]}]}, u'namespaces':
    [{u'status': u'CREATED', u'computes': [{u'credentials': {}, u'type': u'direct', u'id': u'default', u'name': u'default'}],
      u'id': u'default', u'name': u'default'}], u'isTargetChecking': False, 'ouputFormat': u'table',
                 u'tableName': u'renamed_chinese_cities_gb2312', u'outputFormatsList':
                   [{u'name': u'Table', u'value': u'table'}, {u'name': u'Search index', u'value': u'index'},
                    {u'name': u'Database', u'value': u'database'}, {u'name': u'Folder', u'value': u'file'},
                    {u'name': u'HBase Table', u'value': u'hbase'}],
                 u'fieldEditorPlaceHolder': u'Example: SELECT * FROM [object Promise]', u'indexerDefaultField': [],
                 u'fieldEditorValue':
                   u'SELECT Before,\n    old_Chinese_name,\n    After,\n    new_Chinese_name,\n    Renamed_date\n FROM [object Promise];',
                 u'customRegexp': u'', u'customLineDelimiter': u'\\n', u'isTargetExisting': False,
                 u'customEnclosedByDelimiter': u"'", u'indexerConfigSets': [], u'sourceType': u'hive',
                 u'useCustomDelimiters': False, u'apiHelperType': u'hive', u'numMappers': 1,
                 u'fieldEditorDatabase': u'default', u'namespace': {u'status': u'CREATED', u'computes':
      [{u'credentials': {}, u'type': u'direct', u'id': u'default', u'name': u'default'}], u'id': u'default', u'name': u'default'},
                 u'indexerPrimaryKeyObject': [], u'kuduPartitionColumns': [], u'rdbmsFileOutputFormats':
                   [{u'name': u'text', u'value': u'text'}, {u'name': u'sequence', u'value': u'sequence'},
                    {u'name': u'avro', u'value': u'avro'}], u'outputFormats': [{u'name': u'Table', u'value': u'table'},
                                                                               {u'name': u'Search index', u'value': u'index'}],
                 u'fieldEditorEnabled': False, u'indexerDefaultFieldObject': [],
                 u'customMapDelimiter': u'', u'partitionColumns': [], u'rdbmsFileOutputFormat': u'text',
                 u'showProperties': False, u'isTransactional': True, u'useDefaultLocation': True, u'description': u'',
                 u'customFieldsDelimiter': u',', u'primaryKeyObjects': [], u'customFieldDelimiter': u',',
                 u'rdbmsSplitByColumn': [], u'existingTargetUrl': u'', u'channelSinkTypes':
                   [{u'name': u'This topic', u'value': u'kafka'}, {u'name': u'Solr', u'value': u'solr'},
                    {u'name': u'HDFS', u'value': u'hdfs'}], u'defaultName': u'default.renamed_chinese_cities_gb2312',
                 u'isTransactionalUpdateEnabled': False, u'importData': True, u'isIceberg': False, u'databaseName': u'default',
                 u'indexerRunJob': False, u'indexerReplicationFactor': 1, u'KUDU_DEFAULT_RANGE_PARTITION_COLUMN':
                   {u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=',
                    u'lower_val': 0, u'values': [{u'value': u''}]}, u'primaryKeys': [], u'indexerConfigSet': u'',
                 u'sqoopJobLibPaths': [{u'path': u''}], u'outputFormat': u'table',
                 u'nonDefaultLocation': u'/user/admin/renamed_chinese_cities_gb2312.csv',
                 u'compute': {u'credentials': {}, u'type': u'direct', u'id': u'default', u'name': u'default'},
                 u'name': u'default.renamed_chinese_cities_gb2312', u'tableFormat': u'text', u'isInsertOnly': True,
                 u'targetNamespaceId': u'default', u'bulkColumnNames': u'Before,old_Chinese_name,After,new_Chinese_name,Renamed_date',
                 u'columns': [{u'operations': [], u'comment': u'', u'unique': False, u'name': u'Before', u'level': 0,
                               u'keyType': u'string', u'required': False, u'precision': 10, u'nested': [],
                               u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
                               u'keep': True, u'type': u'string', u'showProperties': False, u'scale': 0},
                              {u'operations': [], u'comment': u'', u'unique': False, u'name': u'old_Chinese_name',
                               u'level': 0, u'keyType': u'string', u'required': False, u'precision': 10, u'nested': [],
                               u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
                               u'keep': True, u'type': u'string', u'showProperties': False, u'scale': 0},
                              {u'operations': [], u'comment': u'', u'unique': False, u'name': u'After', u'level': 0,
                               u'keyType': u'string', u'required': False, u'precision': 10, u'nested': [],
                               u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
                               u'keep': True, u'type': u'string', u'showProperties': False, u'scale': 0},
                              {u'operations': [], u'comment': u'', u'unique': False, u'name': u'new_Chinese_name',
                               u'level': 0, u'keyType': u'string', u'required': False, u'precision': 10, u'nested': [],
                               u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
                               u'keep': True, u'type': u'string', u'showProperties': False, u'scale': 0},
                              {u'operations': [], u'comment': u'', u'unique': False, u'name': u'Renamed_date',
                               u'level': 0, u'keyType': u'string', u'required': False, u'precision': 10, u'nested': [],
                               u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False,
                               u'keep': True, u'type': u'string', u'showProperties': False, u'scale': 0}],
                 u'hasHeader': True, u'indexerPrimaryKey': [], u'tableFormats':
                   [{u'name': u'Text', u'value': u'text'}, {u'name': u'Parquet', u'value': u'parquet'},
                    {u'name': u'Csv', u'value': u'csv'}, {u'name': u'Avro', u'value': u'avro'},
                    {u'name': u'Json', u'value': u'json'}, {u'name': u'Regexp', u'value': u'regexp'},
                    {u'name': u'ORC', u'value': u'orc'}], u'customCollectionDelimiter': u'', u'indexerNumShards': 1,
                 u'useFieldEditor': False, u'indexerJobLibPath': u'/tmp/smart_indexer_lib'}

  file_encoding = u'gb2312'
  path = {
    'isDir': False,
    'split': ('/user/admin', 'renamed_chinese_cities_gb2312.csv'),
    'listdir': ['/user/admin/data'],
    'parent_path': '/user/admin/.scratchdir/03d184ad-dd11-4ae1-aace-378daaa094e5/renamed_chinese_cities_gb2312.csv/..'
  }
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination, start_time=-1,
                                                                              file_encoding=file_encoding).get_str()

  assert_true('''USE default;''' in sql, sql)

  statement = '''CREATE TABLE `default`.`hue__tmp_renamed_chinese_cities_gb2312`
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
  assert_true(statement in sql, sql)

  statement = "LOAD DATA INPATH '/user/admin/renamed_chinese_cities_gb2312.csv' " + \
              "INTO TABLE `default`.`hue__tmp_renamed_chinese_cities_gb2312`;"
  assert_true(statement in sql, sql)

  statement = '''CREATE TABLE `default`.`renamed_chinese_cities_gb2312`
        STORED AS TextFile
TBLPROPERTIES('transactional'='true', 'transactional_properties'='insert_only')
        AS SELECT *
        FROM `default`.`hue__tmp_renamed_chinese_cities_gb2312`;'''
  assert_true(statement in sql, sql)

  statement = '''DROP TABLE IF EXISTS `default`.`hue__tmp_renamed_chinese_cities_gb2312`;'''
  assert_true(statement in sql, sql)

  statement = '''ALTER TABLE `default`.`renamed_chinese_cities_gb2312` ''' + \
              '''SET serdeproperties ("serialization.encoding"="gb2312");'''
  assert_true(statement in sql, sql)


def test_create_ddl_with_abfs():
  finish = ABFS_CLUSTERS.set_for_testing(
    {
      'default': {
        'fs_defaultfs': 'abfs://my-data@yingstorage.dfs.core.windows.net',
        'webhdfs_url': 'https://yingstorage.dfs.core.windows.net'
      }
    }
  )

  form_data = {'path': u'abfs://my-data/test_data/cars.csv', 'partition_columns': [], 'overwrite': False}
  sql = ''
  request = MockRequest(fs=MockFs())
  query_server_config = dbms.get_query_server_config(name='impala')
  db = dbms.get(request.user, query_server=query_server_config)
  try:
    sql = "\n\n%s;" % db.load_data('default', 'cars', form_data, None, generate_ddl_only=True)
  finally:
    finish()
  assert_true(u"\'abfs://my-data@yingstorage.dfs.core.windows.net/test_data/cars.csv\'" in sql)


def test_create_table_from_local():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Hive', 'dialect': 'hive'}
    source = {
      'path': '',
      'sourceType': 'hive'
    }
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
      'sourceType': 'hive'
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

    assert_equal(statement, sql)


def test_create_table_from_local_mysql():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'MySQL', 'dialect': 'mysql'}
    source = {
      'path': BASE_DIR + '/apps/beeswax/data/tables/us_population.csv',
      'sourceType': 'mysql',
      'format': {'hasHeader': False}
    }
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'field_1', 'type': 'string', 'keep': True},
        {'name': 'field_2', 'type': 'string', 'keep': True},
        {'name': 'field_3', 'type': 'bigint', 'keep': True},
      ],
      'sourceType': 'mysql'
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

    assert_equal(statement, sql)


def test_create_table_from_local_impala():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Impala', 'dialect': 'impala'}
    source = {
      'path': BASE_DIR + '/apps/beeswax/data/tables/flights.csv',
      'sourceType': 'impala',
      'format': {'hasHeader': True}
    }
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
      'sourceType': 'impala'
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

    assert_equal(statement, sql)


def test_create_table_only_header_file_local_impala():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Impala', 'dialect': 'impala'}
    source = {
      'path': BASE_DIR + '/apps/beeswax/data/tables/onlyheader.csv',
      'sourceType': 'impala',
      'format': {'hasHeader': True}
    }
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
      'sourceType': 'impala'
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

    assert_equal(statement, sql)


def test_create_table_with_drop_column_from_local():
  with patch('indexer.indexers.sql.get_interpreter') as get_interpreter:
    get_interpreter.return_value = {'Name': 'Hive', 'dialect': 'hive'}
    source = {
      'path': '',
      'sourceType': 'hive'
    }
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
      'sourceType': 'hive'
    }
    sql = SQLIndexer(user=Mock(), fs=Mock()).create_table_from_local_file(source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS default.test1 (
  `hour` bigint,
  `dep` bigint);'''

    assert_equal(statement, sql)
