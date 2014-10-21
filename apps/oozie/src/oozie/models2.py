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
import re

from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from desktop.models import Document2


LOG = logging.getLogger(__name__)



class Workflow():
  
  def __init__(self, data=None, document=None, workflow=None):
    self.document = document

    if document is not None:
      self.data = document.data
    elif data is not None:
      self.data = data
    else:
      self.data = json.dumps({
          'layout': [
              #{"size":12,"rows":[{"widgets":[]}],"drops":["temp"],"klass":"card card-home card-column span2"}
{"size":12, "rows":[
      {"widgets":[{"size":12, "name":"Start", "id":"3f107997-04cc-8733-60a9-a4bb62cebffc", "widgetType":"start-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
      {"widgets":[]},  
      {"widgets":[{"size":12, "name":"End", "id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "widgetType":"end-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]}], 
   "drops":[ "temp"],
   "klass":"card card-home card-column span12"}              
          ],
           'workflow': workflow if workflow is not None else {"id": None,"uuid":"549e2697-97cf-f931-2ce4-83dfdd03b7e7","name":"",
   "properties":{"job_xml":"","sla_enabled":False,"schema_version":"uri:oozie:workflow:0.4","sla_workflow_enabled":False,"credentials":[],"properties":{}},
   "nodes":[{"id":"3f107997-04cc-8733-60a9-a4bb62cebffc","name":"Start","type":"start-widget","properties":{},"children":[{'to': '33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}]},            
            {"id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a","name":"End","type":"end-widget","properties":{},"children":[]}]
   }
      })
  
  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)
 
  def get_data(self):
    _data = json.loads(self.data)
    
    if self.document is not None:
      _data['workflow']['id'] = self.document.id
    if 'properties' not in _data['workflow']:
      _data['workflow']['properties'] = {}

    if 'sla_workflow_enabled' not in _data['workflow']['properties']:
      _data['workflow']['properties']['sla_workflow_enabled'] = False
    if 'sla_enabled' not in _data['workflow']['properties']:
      _data['workflow']['properties']['sla_enabled'] = False            
    
    if 'schema_version' not in _data['workflow']['properties']:
      _data['workflow']['properties']['schema_version'] = 'uri:oozie:workflow:0.4'
    if 'job_xml' not in _data['workflow']['properties']:
      _data['workflow']['properties']['job_xml'] = ''
    if 'properties' not in _data['workflow']['properties']:
      _data['workflow']['properties']['properties'] = {}

    if 'credentials' not in _data['workflow']['properties']:
      _data['workflow']['properties']['credentials'] = []      

    return _data
  
  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = 'editor/gen2/workflow.xml.mako'

    data = self.get_data()  
    nodes = [Node(node) for node in data['workflow']['nodes']]

    xml = re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {
              'workflow': data['workflow'],
              'nodes': nodes,
              'mapping': mapping
          }))
    return force_unicode(xml)  


class Node():
  def __init__(self, data):
    self.data = data
    
    self._augment_data()
    
  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}

    data = {
      'node': self.data,
      'mapping': mapping
    }

    return django_mako.render_to_string(self.get_template_name(), data)
  
  def _augment_data(self):
    self.data['type'] = self.data['type'].replace('-widget', '')
    self.data['uuid'] = self.data['id']
    
    # if action node?
    if 'credentials' not in self.data['properties']:
      self.data['properties']['credentials'] = []     
    if 'prepares' not in self.data['properties']:
      self.data['properties']['prepares'] = []
    if 'job_xml' not in self.data['properties']:
      self.data['properties']['job_xml'] = []      
    if 'properties' not in self.data['properties']:
      self.data['properties']['properties'] = []
    if 'params' not in self.data['properties']:
      self.data['properties']['params'] = []
    if 'files' not in self.data['properties']:
      self.data['properties']['files'] = []
    if 'archives' not in self.data['properties']:
      self.data['properties']['archives'] = []

#    if 'script_path' not in self.data['properties']:
#      self.data['properties']['script_path'] = 'test.pig'      

    if 'sla_enabled' not in self.data['properties']:
      self.data['properties']['sla_enabled'] = False
    
  def get_template_name(self):
    return 'editor/gen2/workflow-%s.xml.mako' % self.data['type']    
