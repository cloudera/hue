#!/usr/bin/env python
# -- coding: utf-8 --
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

from desktop.lib.exceptions_renderable import PopupException
from django.db.models import Count
from desktop.models import SqlQueryParser

from metadata.optimizer.base import Api

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class OptimizerParserClient(Api):
    # retriving the data from the database 
    def top_tables(self, workfloadId=None, database_name='default', page_size=1000, startingToken=None, connector=None):
            result_query = SqlQueryParser.objects.filter(database=database_name).values('database' , 'table_name').annotate(usage_count=Count('*')).order_by('-usage_count').values('database' , 'table_name', 'usage_count')[:5]
      
            data = {
                'results': [{
                    "database": "default",
                    "name": "sample_07",
                    "workloadPercent": 6,
                    "columnCount": 4,
                    "total": 6
                    }, {
                    "database": "default",
                    "name": "sample_08",
                    "workloadPercent": 5,
                    "columnCount": 4,
                    "total": 3
                    }, {
                    "database": "default",
                    "name": "web_logs",
                    "workloadPercent": 4,
                    "columnCount": 1,
                    "total": 3
                    }, {
                    "database": "default",
                    "name": "customers",
                    "workloadPercent": 3,
                    "columnCount": 44,
                    "total": 1
                    }, {
                    "database": "default",
                    "name": "customers",
                    "workloadPercent": 2,
                    "columnCount": 44,
                    "total": 1
                    }
                ]
            }

            i=0
            for d in data['results']:
                d['database'] = result_query[i]['database']
                d['name'] = result_query[i]['table_name']
                i = i+1

            return data