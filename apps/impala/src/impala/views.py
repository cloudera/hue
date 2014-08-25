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


## Main views are inherited from Beeswax.


import logging
import json

from django.http import HttpResponse

from desktop.lib.django_util import render
from beeswax.design import hql_query
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config


LOG = logging.getLogger(__name__)


def dashboard(request):
  return render('dashboard.mako', request, {
    'query_json': json.dumps({}),
    'dashboard_json': json.dumps({'layout': [
              {"size":2,"rows":[{"widgets":[{"size":12,"name":"Pie Results","id":"52f07188-f30f-1296-2450-f77e02e1a5c1","widgetType":"pie-widget",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],"drops":["temp"],"klass":"card card-home card-column span2"},
              {"size":10,"rows":[{"widgets":[
                  {"size":12,"name":"Grid Results","id":"52f07188-f30f-1296-2450-f77e02e1a5c0","widgetType":"resultset-widget",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
              "drops":["temp"],"klass":"card card-home card-column span10"}
         ],
        'facets': [{'id': '52f07188-f30f-1296-2450-f77e02e1a5c1', 'label': 'aa', 'field': 'salary', 'widget_type': 'pie'}],
        'properties': [{'database': 'default', 'table': 'sample_07'}]
        }), 
                                            # type: MAX, / ORDER BY, LIMIT 100
  })


def query(request):  
  result = {
    'status': -1,
    'data': {}
  }
    
  if 'facet' in request.POST: 
    database = 'default'
    table = 'sample_07'    
    hql = "SELECT salary FROM %s.%s WHERE salary IS NOT NULL ORDER BY salary DESC LIMIT 10" % (database, table,)
    result['id'] = json.loads(request.POST['facet'])['id']
  else:
    database = 'default'
    table = 'sample_07'    
    hql = "SELECT * FROM %s.%s" % (database, table,)

  query_server = get_query_server_config(name='impala')
  query = hql_query(hql)
  db = dbms.get(request.user, query_server=query_server)
  handle = db.execute_and_wait(query, timeout_sec=5.0)

  if handle:
    result['data'] = list(db.fetch(handle, rows=100).rows())
    result['status'] = 0
    db.close(handle)
    
  return HttpResponse(json.dumps(result), mimetype="application/json")

  
