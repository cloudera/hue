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

import json
import logging

from desktop.lib.connectors.lib.impala import Impala
from desktop.lib.connectors.lib.hive import Hive

from desktop.lib.django_util import JsonResponse, render


LOG = logging.getLogger(__name__)

CONNECTOR_TYPES = [
  {'name': connector.NAME, 'settings': connector.PROPERTIES}
  for connector in [
    Impala(), Hive()
  ]
]

CONNECTORS = {
  "timestamp": "2019-04-05T23:36:47.533981",
  "connectors": [
    {"category": "Query Engines", "values": [
      {"name": "Impala", "id": 1, "instances": []},
      {"name": "SQL Database", "id": 2, "instances": []},
      {"name": "Hive", "id": 3, "instances": [1, 2]},
      {"name": "Hive Tez", "id": 4, "instances": []},
      {"name": "Hive LLAP", "id": 5, "instances": []},
      {"name": "Druid", "id": 6, "instances": []},
      {"name": "Kafka SQL", "id": 6, "instances": []},
      {"name": "SparkSQL", "id": 6, "instances": []},
      {"name": "Presto", "id": 6, "instances": []},
      {"name": "Athena", "id": 6, "instances": []},
      {"name": "Redshift", "id": 6, "instances": []},
      {"name": "Big Query", "id": 6, "instances": []},
      {"name": "Oracle", "id": 6, "instances": []},
    ]},
    {"category": "Browsers", "values": [
      {"name": "HDFS", "id": 30, "instances": []},
      {"name": "YARN", "id": 30, "instances": []},
      {"name": "S3", "id": 31, "instances": []},
      {"name": "ADLS", "id": 32, "instances": []}
    ]},
    {"category": "Catalogs", "values": [
      {"name": "Navigator", "id": 7, "instances": []},
      {"name": "Atlas", "id": 8, "instances": []}
    ]},
    {"category": "Optimizers", "values": [
      {"name": "Optimizer", "id": 9, "instances": []}
    ]},
    {"category": "Schedulers", "values": [
      {"name": "Oozie", "id": 10, "instances": []},
      {"name": "Celery", "id": 11, "instances": []}
    ]},
    {"category": "Apps", "values": []},
    {"category": "Plugins", "values": []},
  ]
}


def connectors(request):
  return JsonResponse({
    'connectors': CONNECTOR_TYPES
  })


def connector(request):
  insance = json.loads(request.POST.get('id', 'null'))

  return JsonResponse(CONNECTOR_TYPES[0])


def connector_types(request):
  global CONNECTORS

  return JsonResponse(CONNECTORS)
