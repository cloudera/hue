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
"""
Dumps a Cloudera Manager Monitor Descriptor file.
"""

import json

from django.core.management.base import BaseCommand

# Force loading the metrics
import desktop.urls
from desktop.lib.metrics import global_registry


class Command(BaseCommand):
  def handle(self, *args, **options):
    """Generates a Monitor Descriptor file."""
    registry = global_registry()
    definitions = []

    for schema in registry.schemas:
      definitions.extend(schema.to_json())

    definitions.sort(lambda a, b: cmp(a['context'], b['context']))

    d = {
        'name': 'HUE',
        'nameForCrossEntityAggregateMetrics': 'hues',
        'version': 1,
        'metricDefinitions': [],
        'roles': [
          {
            'name': 'HUE_SERVER',
            'nameForCrossEntityAggregateMetrics': 'hue_servers',
            'metricDefinitions': definitions,
          },
        ],
    }

    print json.dumps(d)
