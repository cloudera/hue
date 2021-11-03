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
# limitations under the License.from indexer.indexers.phoenix_sql import PhoenixIndexer

import sys
from nose.tools import assert_equal

from desktop.settings import BASE_DIR
from indexer.indexers.phoenix_sql import PhoenixIndexer

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


def test_create_table_phoenix():
  with patch('indexer.indexers.phoenix_sql.get_ordered_interpreters') as get_ordered_interpreters:
    get_ordered_interpreters.return_value = [{'Name': 'Phoenix', 'dialect': 'phoenix', 'type': 'phoenix'}]
    source = {
      'inputFormat': 'localfile',
      'path': BASE_DIR + '/apps/beeswax/data/tables/us_population.csv',
      'sourceType': 'phoenix',
      'format': {'hasHeader': False}
    }
    destination = {
      'name': 'default.test1',
      'columns': [
        {'name': 'field_1', 'type': 'string'},
        {'name': 'field_2', 'type': 'string'},
        {'name': 'field_3', 'type': 'bigint'},
      ],
      'sourceType': 'phoenix',
      'indexerPrimaryKey': ['field_3'],
      'indexerRunJob': True
    }
    request = Mock()
    sql = PhoenixIndexer(user=Mock(), fs=Mock()).create_table_from_file(request, source, destination).get_str()

    statement = '''USE default;

CREATE TABLE IF NOT EXISTS test1 (
  field_1 varchar,
  field_2 varchar,
  field_3 bigint
CONSTRAINT my_pk PRIMARY KEY (field_3)
);

UPSERT INTO test1 VALUES ('NY', 'New York', 8143197);

UPSERT INTO test1 VALUES ('CA', 'Los Angeles', 3844829);

UPSERT INTO test1 VALUES ('IL', 'Chicago', 2842518);

UPSERT INTO test1 VALUES ('TX', 'Houston', 2016582);

UPSERT INTO test1 VALUES ('PA', 'Philadelphia', 1463281);

UPSERT INTO test1 VALUES ('AZ', 'Phoenix', 1461575);

UPSERT INTO test1 VALUES ('TX', 'San Antonio', 1256509);

UPSERT INTO test1 VALUES ('CA', 'San Diego', 1255540);

UPSERT INTO test1 VALUES ('TX', 'Dallas', 1213825);

UPSERT INTO test1 VALUES ('CA', 'San Jose', 912332);'''

    assert_equal(statement, sql)
