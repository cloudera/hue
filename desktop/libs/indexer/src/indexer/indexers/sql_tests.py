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

from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_true

from desktop.lib.django_test_util import make_logged_in_client

from indexer.indexers.sql import SQLIndexer


class MockRequest():
  def __init__(self, fs=None, user=None):
    self.fs = fs if fs is not None else MockFs()
    if user is None:
      self.c = make_logged_in_client(username='test_importer', is_superuser=False)
      self.user = User.objects.get(username='test_importer')
    else:
      self.user = user


class MockFs():
  def __init__(self, path=None):
    self.path = {'isDir': False, 'split': ('/A', 'a'), 'listdir': ['/A']} if path is None else path

  def isdir(self, path):
    return self.path['isDir']

  def split(self, path):
    return self.path['split']

  def listdir(self, path):
    return self.path['listdir']


def test_generate_create_text_table_with_data_partition():
  source = {u'sourceType': 'hive', u'sampleCols': [{u'operations': [], u'comment': u'', u'name': u'customers.id', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.name', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.email_preferences', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.addresses', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.orders', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'name': u'', u'inputFormat': u'file', u'format': {u'status': 0, u'fieldSeparator': u',', u'hasHeader': True, u'quoteChar': u'"', u'recordSeparator': u'\\n', u'type': u'csv'}, u'defaultName': u'default.customer_stats', u'show': True, u'tableName': u'', u'sample': [], u'apiHelperType': u'hive', u'inputFormatsAll': [{u'name': u'File', u'value': u'file'}, {u'name': u'Manually', u'value': u'manual'}, {u'name': u'SQL Query', u'value': u'query'}, {u'name': u'Table', u'value': u'table'}], u'query': u'', u'databaseName': u'default', u'table': u'', u'inputFormats': [{u'name': u'File', u'value': u'file'}, {u'name': u'Manually', u'value': u'manual'}, {u'name': u'SQL Query', u'value': u'query'}, {u'name': u'Table', u'value': u'table'}], u'path': u'/user/romain/customer_stats.csv', u'draggedQuery': u'', u'inputFormatsManual': [{u'name': u'Manually', u'value': u'manual'}], u'isObjectStore': False}
  destination = {u'sourceType': 'hive', u'KUDU_DEFAULT_PARTITION_COLUMN': {u'int_val': 16, u'name': u'HASH', u'columns': [], u'range_partitions': [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}]}, u'isTargetChecking': False, u'tableName': u'customer_stats', u'outputFormatsList': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr index', u'value': u'index'}, {u'name': u'File', u'value': u'file'}, {u'name': u'Database', u'value': u'database'}], u'customRegexp': u'', u'isTargetExisting': False, u'partitionColumns': [{u'operations': [], u'comment': u'', u'name': u'new_field_1', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': True, u'length': 100, u'partitionValue': u'AAA', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'useCustomDelimiters': False, u'apiHelperType': u'hive', u'kuduPartitionColumns': [], u'outputFormats': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr index', u'value': u'index'}], u'customMapDelimiter': u'\\003', u'showProperties': False, u'useDefaultLocation': True, u'description': u'', u'primaryKeyObjects': [], u'customFieldDelimiter': u',', u'existingTargetUrl': u'', u'importData': True, u'databaseName': u'default', u'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}, u'primaryKeys': [], u'outputFormat': u'table', u'nonDefaultLocation': u'/user/romain/customer_stats.csv', u'name': u'default.customer_stats', u'tableFormat': u'text', 'ouputFormat': u'table', u'bulkColumnNames': u'customers.id,customers.name,customers.email_preferences,customers.addresses,customers.orders', u'columns': [{u'operations': [], u'comment': u'', u'name': u'customers.id', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.name', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.email_preferences', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.addresses', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'customers.orders', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'partitionValue': u'', u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'hasHeader': True, u'tableFormats': [{u'name': u'Text', u'value': u'text'}, {u'name': u'Parquet', u'value': u'parquet'}, {u'name': u'Kudu', u'value': u'kudu'}, {u'name': u'Csv', u'value': u'csv'}, {u'name': u'Avro', u'value': u'avro'}, {u'name': u'Json', u'value': u'json'}, {u'name': u'Regexp', u'value': u'regexp'}, {u'name': u'ORC', u'value': u'orc'}], u'customCollectionDelimiter': u'\\002'}
  request = MockRequest(fs=MockFs())

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''USE default;''' in  sql, sql)

  assert_true('''CREATE TABLE `default`.`customer_stats`
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
  STORED AS TextFile TBLPROPERTIES("skip.header.line.count" = "1")
;''' in  sql, sql)

  assert_true('''LOAD DATA INPATH '/user/romain/customer_stats.csv' INTO TABLE `default`.`customer_stats` PARTITION (new_field_1='AAA');''' in  sql, sql)


def test_generate_create_kudu_table_with_data():
  source = {u'sourceType': 'impala', u'apiHelperType': 'hive', u'sampleCols': [], u'name': u'', u'inputFormat': u'file', u'format': {u'quoteChar': u'"', u'recordSeparator': u'\\n', u'type': u'csv', u'hasHeader': True, u'fieldSeparator': u','}, u'show': True, u'tableName': u'', u'sample': [], u'defaultName': u'index_data', u'query': u'', u'databaseName': u'default', u'table': u'', u'inputFormats': [{u'name': u'File', u'value': u'file'}, {u'name': u'Manually', u'value': u'manual'}], u'path': u'/user/admin/index_data.csv', u'draggedQuery': u'', u'isObjectStore': False}
  destination = {u'sourceType': 'impala', u'KUDU_DEFAULT_PARTITION_COLUMN': {u'int_val': 16, u'name': u'HASH', u'columns': [], u'range_partitions': [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}]}, u'tableName': u'index_data', u'outputFormatsList': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr+index', u'value': u'index'}, {u'name': u'File', u'value': u'file'}, {u'name': u'Database', u'value': u'database'}], u'customRegexp': u'', u'isTargetExisting': False, u'partitionColumns': [], u'useCustomDelimiters': True, u'kuduPartitionColumns': [{u'int_val': 16, u'name': u'HASH', u'columns': [u'id'], u'range_partitions': [{u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}]}], u'outputFormats': [{u'name': u'Table', u'value': u'table'}, {u'name': u'Solr+index', u'value': u'index'}], u'customMapDelimiter': None, u'showProperties': False, u'useDefaultLocation': True, u'description': u'Big Data', u'primaryKeyObjects': [{u'operations': [], u'comment': u'', u'name': u'id', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'customFieldDelimiter': u',', u'existingTargetUrl': u'', u'importData': True, u'databaseName': u'default', u'KUDU_DEFAULT_RANGE_PARTITION_COLUMN': {u'include_upper_val': u'<=', u'upper_val': 1, u'name': u'VALUES', u'include_lower_val': u'<=', u'lower_val': 0, u'values': [{u'value': u''}]}, u'primaryKeys': [u'id'], u'outputFormat': u'table', u'nonDefaultLocation': u'/user/admin/index_data.csv', u'name': u'index_data', u'tableFormat': u'kudu', u'bulkColumnNames': u'business_id,cool,date,funny,id,stars,text,type,useful,user_id,name,full_address,latitude,longitude,neighborhoods,open,review_count,state', u'columns': [{u'operations': [], u'comment': u'', u'name': u'business_id', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'cool', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': False}, {u'operations': [], u'comment': u'', u'name': u'date', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'funny', u'level': 0, u'scale':4, u'precision':10, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'decimal', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'id', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'stars', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'text', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'type', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'useful', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'user_id', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'name', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'full_address', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'latitude', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'double', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'longitude', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'double', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'neighborhoods', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'open', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'review_count', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'bigint', u'showProperties': False, u'keep': True}, {u'operations': [], u'comment': u'', u'name': u'state', u'level': 0, u'keyType': u'string', u'required': False, u'nested': [], u'isPartition': False, u'length': 100, u'multiValued': False, u'unique': False, u'type': u'string', u'showProperties': False, u'keep': True}], u'hasHeader': True, u'tableFormats': [{u'name': u'Text', u'value': u'text'}, {u'name': u'Parquet', u'value': u'parquet'}, {u'name': u'Json', u'value': u'json'}, {u'name': u'Kudu', u'value': u'kudu'}, {u'name': u'Avro', u'value': u'avro'}, {u'name': u'Regexp', u'value': u'regexp'}, {u'name': u'RCFile', u'value': u'rcfile'}, {u'name': u'ORC', u'value': u'orc'}, {u'name': u'SequenceFile', u'value': u'sequencefile'}], u'customCollectionDelimiter': None}
  request = MockRequest(fs=MockFs())

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''DROP TABLE IF EXISTS `default`.`hue__tmp_index_data`;''' in  sql, sql)

  assert_true('''CREATE EXTERNAL TABLE `default`.`hue__tmp_index_data`
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
TBLPROPERTIES("skip.header.line.count" = "1")''' in  sql, sql)

  assert_true('''CREATE TABLE `default`.`index_data` COMMENT "Big Data"
        PRIMARY KEY (id)
        PARTITION BY HASH PARTITIONS 16
        STORED AS kudu
        TBLPROPERTIES(
        'kudu.num_tablet_replicas' = '1'
        )
        AS SELECT `id`, `business_id`, `date`, `funny`, `stars`, `text`, `type`, `useful`, `user_id`, `name`, `full_address`, `latitude`, `longitude`, `neighborhoods`, `open`, `review_count`, `state`
        FROM `default`.`hue__tmp_index_data`;''' in  sql, sql)


def test_generate_create_parquet_table():
  source = json.loads('''{"sourceType": "hive", "name":"","sample":[["Bank Of America","3000000.0","US","Miami","37.6801986694","-121.92150116"],["Citi Bank","2800000.0","US","Richmond","37.5242004395","-77.4932022095"],["Deutsche Bank","2600000.0","US","Corpus Christi","40.7807998657","-73.9772033691"],["Thomson Reuters","2400000.0","US","Albany","35.7976989746","-78.6252975464"],["OpenX","2200000.0","US","Des Moines","40.5411987305","-119.586898804"]],"sampleCols":[{"operations":[],"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0}],"inputFormat":"file","inputFormatsAll":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],"inputFormatsManual":[{"value":"manual","name":"Manually"}],"inputFormats":[{"value":"file","name":"File"},{"value":"manual","name":"Manually"},{"value":"query","name":"SQL Query"},{"value":"table","name":"Table"}],"path":"/user/hue/data/query-hive-360.csv","isObjectStore":false,"table":"","tableName":"","databaseName":"default","apiHelperType":"hive","query":"","draggedQuery":"","format":{"type":"csv","fieldSeparator":",","recordSeparator":"\\n","quoteChar":"\\"","hasHeader":true,"status":0},"show":true,"defaultName":"default.query-hive-360"}''')
  destination = json.loads('''{"sourceType": "hive", "name":"default.parquet_table","apiHelperType":"hive","description":"","outputFormat":"table","outputFormatsList":[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"},{"name":"File","value":"file"},{"name":"Database","value":"database"}],"outputFormats":[{"name":"Table","value":"table"},{"name":"Solr index","value":"index"}],"columns":[{"operations":[],"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,tran_amount,tran_country_cd,vrfcn_city,vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,"isTargetChecking":false,"existingTargetUrl":"","tableName":"parquet_table","databaseName":"default","tableFormat":"parquet","KUDU_DEFAULT_RANGE_PARTITION_COLUMN":{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="},"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH","int_val":16},"tableFormats":[{"value":"text","name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},{"value":"csv","name":"Csv"},{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},{"value":"orc","name":"ORC"}],"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys":[],"primaryKeyObjects":[],"importData":true,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv","hasHeader":true,"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002","customMapDelimiter":"\\\\003","customRegexp":""}''')

  path = {'isDir': False, 'split': ('/user/hue/data', 'query-hive-360.csv'), 'listdir': ['/user/hue/data']}
  request = MockRequest(fs=MockFs(path=path))

  sql = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination).get_str()

  assert_true('''USE default;''' in  sql, sql)

  assert_true('''CREATE EXTERNAL TABLE `default`.`hue__tmp_parquet_table`
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
TBLPROPERTIES("skip.header.line.count" = "1")
;''' in  sql, sql)

  assert_true('''CREATE TABLE `default`.`parquet_table`
        STORED AS parquet
        AS SELECT *
        FROM `default`.`hue__tmp_parquet_table`;
''' in  sql, sql)

  assert_true('''DROP TABLE IF EXISTS `default`.`hue__tmp_parquet_table`;
''' in  sql, sql)


def test_generate_create_empty_kudu_table():
  source = json.loads('''{"sourceType": "impala", "apiHelperType": "impala", "path": "", "inputFormat": "manual"}''')
  destination = json.loads('''{"sourceType": "impala", "name":"default.manual_empty_kudu","apiHelperType":"impala","description":"","outputFormat":"table","columns":[{"operations":[],"comment":"","nested":[],"name":"acct_client","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_amount","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"tran_country_cd","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"string","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lat","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0},{"operations":[],"comment":"","nested":[],"name":"vrfcn_city_lon","level":0,"keyType":"string","required":false,"precision":10,"keep":true,"isPartition":false,"length":100,"partitionValue":"","multiValued":false,"unique":false,"type":"double","showProperties":false,"scale":0}],"bulkColumnNames":"acct_client,tran_amount,tran_country_cd,vrfcn_city,vrfcn_city_lat,vrfcn_city_lon","showProperties":false,"isTargetExisting":false,"isTargetChecking":false,"existingTargetUrl":"","tableName":"manual_kudu_table","databaseName":"default","tableFormat":"kudu","KUDU_DEFAULT_RANGE_PARTITION_COLUMN":{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="},"KUDU_DEFAULT_PARTITION_COLUMN":{"columns":[],"range_partitions":[{"values":[{"value":""}],"name":"VALUES","lower_val":0,"include_lower_val":"<=","upper_val":1,"include_upper_val":"<="}],"name":"HASH","int_val":16},"tableFormats":[{"value":"text","name":"Text"},{"value":"parquet","name":"Parquet"},{"value":"kudu","name":"Kudu"},{"value":"csv","name":"Csv"},{"value":"avro","name":"Avro"},{"value":"json","name":"Json"},{"value":"regexp","name":"Regexp"},{"value":"orc","name":"ORC"}],"partitionColumns":[],"kuduPartitionColumns":[],"primaryKeys": ["acct_client"],"primaryKeyObjects":[],"importData":false,"useDefaultLocation":true,"nonDefaultLocation":"/user/hue/data/query-hive-360.csv","hasHeader":false,"useCustomDelimiters":false,"customFieldDelimiter":",","customCollectionDelimiter":"\\\\002","customMapDelimiter":"\\\\003","customRegexp":""}''')

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
)   STORED AS kudu ;''' in  sql, sql)
