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

from desktop.lib.django_util import JsonResponse, render


LOG = logging.getLogger(__name__)


def index(request):
  CONNECTORS = {
    "timestamp": "2019-04-05T23:36:47.533981",
    "metric": [
      {"category": "Query Engines", "values": [
        {"name": "Impala"},
        {"name": "SQL Database"},
        {"name": "Hive"}
      ]},
      {"category": "Browsers", "values": [{"name": "HDFS"}, {"name": "S3"}, {"name": "ADLS"}]},
      {"category": "Catalogs", "values": [{"name": "Navigator"}, {"name": "Atlas"}]},
      {"category": "Optimizers", "values": [{"name": "Optimizer"}]},
      {"category": "Schedulers", "values": [{"name": "Oozie"}, {"name": "Celery"}]},
      {"category": "Apps", "values": []},
      {"category": "Plugins", "values": []},
    ]
  }

  if request.is_ajax():
    return JsonResponse(CONNECTORS)
  else:
    return render("connectors.mako", request, {'connectors': json.dumps(CONNECTORS), 'is_embeddable': request.GET.get('is_embeddable', False)})
