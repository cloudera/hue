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

from beeswax.server.dbms import get_query_server_config
from beeswax.server import dbms


class Dashboard():
  
  data = json.dumps(
      {'layout': [
              {"size":2,"rows":[{"widgets":[{"size":12,"name":"Top salaries","id":"52f07188-f30f-1296-2450-f77e02e1a5c1","widgetType":"facet-widget",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],"drops":["temp"],"klass":"card card-home card-column span2"},
              {"size":10,"rows":[{"widgets":[
                  {"size":12,"name":"Grid Results","id":"52f07188-f30f-1296-2450-f77e02e1a5c0","widgetType":"resultset-widget",
                   "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
              "drops":["temp"],"klass":"card card-home card-column span10"}
         ],
      'facets': [{'id': '52f07188-f30f-1296-2450-f77e02e1a5c1', 'label': 'Top salaries', 'field': 'salary', 'widget_type': 'facet-widget', 
                    'properties': {'limit': 10}}],
      'properties': [{'database': 'default', 'table': 'sample_07', 'fields': []}]
  })

  def get_json(self, user):
    _data = self.get_data()

    _data['properties'][0]['fields'] = Controller(user).get_fields(_data['properties'][0]['database'], _data['properties'][0]['table'])
    
    return json.dumps(_data)
 
  def get_data(self):
    return json.loads(self.data)

    
class Controller():
  
  def __init__(self, user):
    query_server = get_query_server_config(name='impala')
    self.db = dbms.get(user, query_server=query_server)      
      
  def get_fields(self, database, table):
        
    _table = self.db.get_table(database, table)
    return [dict([('name', col.name), ('type', col.type), ('comment', col.comment)]) for col in _table.cols]    
        
        
        