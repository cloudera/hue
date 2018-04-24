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

from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_true

from indexer.indexers.envelope import EnvelopeIndexer


def test_generate_from_kafka_to_file_csv():
  properties = {
    'app_name': 'Ingest',

    'inputFormat': 'kafka',
    'brokers': 'broker:9092',
    'topics': 'kafkaTopic',

    'ouputFormat': 'file',
    'path': '/tmp/output',
    'format': 'csv'
  }

  config = EnvelopeIndexer(username='test').generate_config(properties)

  assert_true('''application {
    name = Ingest
    batch.milliseconds = 5000
    executors = 1
    executor.cores = 1
    executor.memory = 1G
}

steps {
    inputdata {
        input {
              type = kafka
              brokers = "broker:9092"
              topics = kafkaTopic
              encoding = string
              window {
                  enabled = true
                  milliseconds = 30000
              }

        }
    }

    outputdata {
    dependencies = [inputdata]
    planner = {
      type = overwrite
    }
    output = {
      type = filesystem
      path = %(path)s
      format = %(format)s
      header = true
    }
    }
}''' in  config, config)
