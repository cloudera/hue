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
import time
import uuid

from string import Template

from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from desktop.models import Document2

from hadoop.fs.hadoopfs import Hdfs
from liboozie.submission2 import Submission
from liboozie.submission2 import create_directories

from oozie.conf import REMOTE_SAMPLE_DIR
from oozie.models import Workflow as OldWorflows


LOG = logging.getLogger(__name__)



class Workflow():
  XML_FILE_NAME = 'workflow.xml'
  PROPERTY_APP_PATH = 'oozie.wf.application.path'
  SLA_DEFAULT = [
      {'key': 'enabled', 'value': False},
      {'key': 'nominal-time', 'value': ''},
      {'key': 'should-start', 'value': ''},
      {'key': 'should-end', 'value': ''},
      {'key': 'max-duration', 'value': ''},
      {'key': 'alert-events', 'value': ''},
      {'key': 'alert-contact', 'value': ''},
      {'key': 'notification-msg', 'value': ''},
      {'key': 'upstream-apps', 'value': ''},
  ]
  HUE_ID = 'hue-id-w'
  
  def __init__(self, data=None, document=None, workflow=None):
    self.document = document

    if document is not None:
      self.data = document.data
    elif data is not None:
      self.data = data
    else:
      self.data = json.dumps({
          'layout': [{
              "size":12, "rows":[
                  {"widgets":[{"size":12, "name":"Start", "id":"3f107997-04cc-8733-60a9-a4bb62cebffc", "widgetType":"start-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"End", "id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "widgetType":"end-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]}
              ], 
              "drops":[ "temp"],
              "klass":"card card-home card-column span12"
          }],
          'workflow': workflow if workflow is not None else {
              "id": None, 
              "uuid": None,
              "name": "My Workflow",
              "properties": {
                  "job_xml": "",
                  "sla_enabled": False,
                  "schema_version": "uri:oozie:workflow:0.4",
                  "sla_workflow_enabled": False,
                  "credentials": [],
                  "properties": [],
                  "sla": Workflow.SLA_DEFAULT
              },
              "nodes":[
                  {"id":"3f107997-04cc-8733-60a9-a4bb62cebffc","name":"Start","type":"start-widget","properties":{},"children":[{'to': '33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}]},            
                  {"id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a","name":"End","type":"end-widget","properties":{},"children":[]},
                  {"id":"17c9c895-5a16-7443-bb81-f34b30b21548","name":"Kill","type":"kill-widget","properties":{'message': _('Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]')},"children":[]}
              ]
          }
      })
      
  @property
  def id(self):
    return self.document.id

  @property      
  def deployment_dir(self):
    _data = json.loads(self.data)
    return _data['workflow']['properties']['deployment_dir']
  
  @property      
  def parameters(self):
    _data = json.loads(self.data)
    return _data['workflow']['properties']['parameters']  
  
  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)
 
  def get_data(self):
    _data = json.loads(self.data)
    
    if self.document is not None:
      _data['workflow']['id'] = self.document.id
      _data['workflow']['dependencies'] = list(self.document.dependencies.values())
    else:
      _data['workflow']['dependencies'] = []

    if 'properties' not in _data['workflow']:
      _data['workflow']['properties'] = {}
      
    if 'properties' not in _data['workflow']['properties']:
      _data['workflow']['properties']['properties'] = []      
    if 'deployment_dir' not in _data['workflow']['properties']:
      default_dir = Hdfs.join(REMOTE_SAMPLE_DIR.get(), 'hue-oozie-%s' % time.time()) # Could be home of user too
      _data['workflow']['properties']['deployment_dir'] = default_dir
    if 'parameters' not in _data['workflow']['properties']:
      _data['workflow']['properties']['parameters'] = [
          {'name': 'oozie.use.system.libpath', 'value': True},
      ]

    if 'sla_workflow_enabled' not in _data['workflow']['properties']:
      _data['workflow']['properties']['sla_workflow_enabled'] = False
    if 'sla_enabled' not in _data['workflow']['properties']:
      _data['workflow']['properties']['sla_enabled'] = False            
    
    if 'schema_version' not in _data['workflow']['properties']:
      _data['workflow']['properties']['schema_version'] = 'uri:oozie:workflow:0.4'
    if 'job_xml' not in _data['workflow']['properties']:
      _data['workflow']['properties']['job_xml'] = ''

    if 'credentials' not in _data['workflow']['properties']:
      _data['workflow']['properties']['credentials'] = []

    return _data
  
  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = 'editor/gen2/workflow.xml.mako'

    data = self.get_data()
    nodes = [Node(node) for node in data['workflow']['nodes'] if node['name'] != 'End'] + [
                Node(node) for node in data['workflow']['nodes'] if node['name'] == 'End'] # End at the end
    node_mapping = dict([(node.id, node) for node in nodes])
    
    sub_wfs_ids = [node.data['properties']['workflow'] for node in nodes if node.data['type'] == 'subworkflow']
    workflow_mapping = dict([(workflow.uuid, Workflow(document=workflow)) for workflow in Document2.objects.filter(uuid__in=sub_wfs_ids)])

    xml = re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {
              'workflow': data['workflow'],
              'nodes': nodes,
              'mapping': mapping,
              'node_mapping': node_mapping,
              'workflow_mapping': workflow_mapping
          }))
    return force_unicode(xml)  

  def find_parameters(self):
    params = set()

#    if self.sla_enabled:
#      for param in find_json_parameters(self.sla):
#        params.add(param)

#    for node in self.node_list:
#      if hasattr(node, 'find_parameters'):
#        params.update(node.find_parameters())

    return dict([(param, '') for param in list(params)])

  def find_all_parameters(self):
    params = self.find_parameters()

#    if hasattr(self, 'sla') and self.sla_enabled:
#      for param in find_json_parameters(self.sla):
#        if param not in params:
#          params[param] = ''

    for param in self.parameters:
      params[param['name'].strip()] = param['value']

    return  [{'name': name, 'value': value} for name, value in params.iteritems()]

  def check_workspace(self, fs):
    create_directories(fs, [REMOTE_SAMPLE_DIR.get()])
      
    perms = 0711
    # if shared, perms = 0755

    Submission(self.document.owner, self, fs, None, {})._create_dir(self.deployment_dir, perms=perms)
    Submission(self.document.owner, self, fs, None, {})._create_dir(Hdfs.join(self.deployment_dir, 'lib'))


class Node():
  def __init__(self, data):    
    self.data = data
    
    self._augment_data()
    
  def to_xml(self, mapping=None, node_mapping=None, workflow_mapping=None):
    if mapping is None:
      mapping = {}
    if node_mapping is None:
      node_mapping = {}
    if workflow_mapping is None:
      workflow_mapping = {}

    data = {
      'node': self.data,
      'mapping': mapping,
      'node_mapping': node_mapping,
      'workflow_mapping': workflow_mapping
    }

    return django_mako.render_to_string(self.get_template_name(), data)

  @property      
  def name(self):
    return self.data['name']
  
  @property      
  def id(self):
    return self.data['id']    

  def _augment_data(self):
    self.data['type'] = self.data['type'].replace('-widget', '')
    self.data['uuid'] = self.data['id']
    
    # Action Node
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
    if 'sla_enabled' not in self.data['properties']:
      self.data['properties']['sla_enabled'] = False
    if 'sla' not in self.data['properties']:
      self.data['properties']['sla'] = []
    
  def get_template_name(self):
    return 'editor/gen2/workflow-%s.xml.mako' % self.data['type']    


class Action(object):
  
  @classmethod
  def get_fields(cls):
    return [(f['name'], f['value']) for f in cls.FIELDS.itervalues()] + [('sla', Workflow.SLA_DEFAULT), ('credentials', [])]


class PigAction(Action):
  TYPE = 'pig'
  FIELDS = {
     'script_path': { 
          'name': 'script_path',
          'label': _('Script name'),
          'value': '',
          'help_text': _('Script name or path to the Pig script. E.g. my_script.pig.')
     },            
     'parameters': { 
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The Pig parameters of the script without -param. e.g. INPUT=${inputDir}')
     },
     'arguments': { 
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('The Pig parameters of the script as is. e.g. -param, INPUT=${inputDir}')
     },
     # Common
     'files': { 
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('List of names or paths of files to be added to the distributed cache and the task running directory.')
     },
     'archives': { 
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('List of names or paths of the archives to be added to the distributed cache.')
     },
     'job_properties': { 
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('For the job configuration (e.g. mapred.job.queue.name=production).')
     },
     'prepares': { 
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('List of absolute paths to delete and then to create before starting the application. This should be used exclusively for directory cleanup.')
     },
     'job_xml': { 
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                       'Properties specified in the Job Properties element override properties specified in the '
                       'files specified in the Job XML element.')
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['script_path']]


class JavaAction(Action):
  TYPE = 'java'
  FIELDS = {
     'jar_path': { 
          'name': 'jar_path',
          'label': _('Jar name'),
          'value': '',
          'help_text': _('Name or path to the %(program)s jar file on HDFS. E.g. examples.jar.') % {'program': 'Java'}
     },            
     'main_class': { 
          'name': 'main_class',
          'label': _('Main class'),
          'value': '',
          'help_text': _('Full name of the Java class. E.g. org.apache.hadoop.examples.Grep')
     },
     'arguments': { 
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('Arguments of the main method. The value of each arg element is considered a single argument '
                       'and they are passed to the main method in the same order.')
     },
     'java_opts': { 
          'name': 'java_opts',
          'label': _('Java options'),
          'value': [],
          'help_text': _('Command-line parameters used to start the JVM that will execute '
                        'the Java application. Using this element is equivalent to using the mapred.child.java.opts '
                        'configuration property. E.g. -Dexample-property=hue')
     },
     'capture_output': { 
          'name': 'capture_output',
          'label': _('Capture output'),
          'value': False,
          'help_text': _('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                         'command output must be in Java Properties file format and it must not exceed 2KB. '
                         'From within the workflow definition, the output of an %(program)s action node is accessible '
                         'via the String action:output(String node, String key) function') % {'program': TYPE.title()}
     },
     # Common
     'files': { 
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('List of names or paths of files to be added to the distributed cache and the task running directory.')
     },
     'archives': { 
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('List of names or paths of the archives to be added to the distributed cache.')
     },
     'job_properties': { 
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('For the job configuration (e.g. mapred.job.queue.name=production).')
     },
     'prepares': { 
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('List of absolute paths to delete and then to create before starting the application. This should be used exclusively for directory cleanup.')
     },
     'job_xml': { 
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                       'Properties specified in the Job Properties element override properties specified in the '
                       'files specified in the Job XML element.')
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['jar_path'], cls.FIELDS['main_class']]
  
  
class HiveAction(Action):
  TYPE = 'hive'
  FIELDS = {
     'script_path': { 
          'name': 'script_path',
          'label': _('Script name'),
          'value': '',
          'help_text': _('Script name or path to the Pig script. E.g. my_script.pig.')
     },            
     'parameters': { 
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': ('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()}
     },
     # Common
     'files': { 
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('List of names or paths of files to be added to the distributed cache and the task running directory.')
     },
     'archives': { 
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('List of names or paths of the archives to be added to the distributed cache.')
     },
     'job_properties': { 
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('For the job configuration (e.g. mapred.job.queue.name=production).')
     },
     'prepares': { 
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('List of absolute paths to delete and then to create before starting the application. This should be used exclusively for directory cleanup.')
     },
     'job_xml': { 
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                       'Properties specified in the Job Properties element override properties specified in the '
                       'files specified in the Job XML element.')
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['script_path']]


class SubWorkflowAction(Action):
  TYPE = 'subworkflow'
  FIELDS = {
     'workflow': { 
          'name': 'workflow',
          'label': _('Sub-workflow'),
          'value': None,
          'help_text': _('The sub-workflow application to include. You must own all the sub-workflows')
     },
     'propagate_configuration': { 
          'name': 'propagate_configuration',
          'label': _('Propagate configuration'),
          'value': True,
          'help_text': _('If the workflow job configuration should be propagated to the child workflow.')
     },
     'job_properties': { 
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('Can be used to specify the job properties that are required to run the child workflow job.')
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return []


class KillAction(Action):
  TYPE = 'kill'
  FIELDS = {
     'message': { 
          'name': 'message',
          'label': _('Message'),
          'value': _('Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]'),
          'help_text': _('Message to display when the workflow fails. Can contain some EL functions.')
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['message']]


class JoinAction(Action):
  TYPE = 'join'
  FIELDS = {}
  
  @classmethod
  def get_mandatory_fields(cls):
    return []


NODES = {
  'pig-widget': PigAction,
  'java-widget': JavaAction,
  'hive-widget': HiveAction,
  'subworkflow-widget': SubWorkflowAction,
  'kill-widget': KillAction,
  'join-widget': JoinAction,
}


WORKFLOW_NODE_PROPERTIES = {}
for node in NODES.itervalues():
  WORKFLOW_NODE_PROPERTIES.update(node.FIELDS)



def find_parameters(instance, fields=None):
  """Find parameters in the given fields"""
  if fields is None:
    fields = [field.name for field in instance._meta.fields]

  params = []
  for field in fields:
    data = getattr(instance, field)
    if field == 'sla' and not instance.sla_enabled:
      continue
    if isinstance(data, list):
      params.extend(find_json_parameters(data))
    elif isinstance(data, basestring):
      for match in Template.pattern.finditer(data):
        name = match.group('braced')
        if name is not None:
          params.append(name)

  return params

def find_json_parameters(fields):
  # To make smarter
  # Input is list of json dict
  params = []

  for field in fields:
    for data in field.values():
      if isinstance(data, basestring):
        for match in Template.pattern.finditer(data):
          name = match.group('braced')
          if name is not None:
            params.append(name)

  return params



def import_workflows_from_hue_3_7():
#[<Start: start>, <Pig: Pig>, [<Kill: kill>], [<End: end>]]
#[<Start: start>, <Mapreduce: Sleep>, [<Kill: kill>], [<End: end>]]
#[<Start: start>, <Java: TeraGenWorkflow>, <Java: TeraSort>, [<Kill: kill>], [<End: end>]]
#[<Start: start>, <Hive: Hive>, [<Kill: kill>], [<End: end>]]
#[<Start: start>, [<Fork: fork-34>, [[<Mapreduce: Sleep-1>, <Mapreduce: Sleep-10>], [<Mapreduce: Sleep-5>, [<Fork: fork-38>, [[<Mapreduce: Sleep-3>], [<Mapreduce: Sleep-4>]], <Join: join-39>]]], <Join: join-35>], [<Kill: kill>], [<End: end>]]
#[<Start: start>, <Pig: Pig>, [<Kill: kill>], [<End: end>]]
#[<Start: start>, <Mapreduce: Sleep>, [<Kill: kill>], [<End: end>]]
  
  uuids = {}
  
  old_wf = OldWorflows.objects.filter(managed=True).filter(is_trashed=False)[10].get_full_node() 
  old_nodes = old_wf.get_hierarchy()
  
  wf = Workflow()
  wf_rows = []
  wf_nodes = []
  
  data = wf.get_data()
  
  # UUIDs node mapping
  for node in old_wf.node_list:    
    if node.name == 'kill':
      node_uuid = '17c9c895-5a16-7443-bb81-f34b30b21548'
    elif node.name == 'start':
      node_uuid = '3f107997-04cc-8733-60a9-a4bb62cebffc'
    elif node.name == 'end':
      node_uuid = '33430f0f-ebfa-c3ec-f237-3e77efa03d0a'
    else:
      node_uuid = str(uuid.uuid4())

    uuids[node.id] = node_uuid
    
  # Workflow
  data['workflow']['uuid'] = str(uuid.uuid4())
  data['workflow']['name'] = old_wf.name
  data['workflow']['properties']['properties'] = json.loads(old_wf.job_properties)
  data['workflow']['properties']['job_xml'] = old_wf.job_xml
  data['workflow']['properties']['description'] = old_wf.description
  data['workflow']['properties']['schema_version'] = old_wf.schema_version
  data['workflow']['properties']['deployment_dir'] = old_wf.deployment_dir
  data['workflow']['properties']['parameters'] = json.loads(old_wf.parameters)
    
  # Layout
  rows = data['layout'][0]['rows']
  
  def _create_layout(nodes, size=12):
    wf_rows = []
    
    for node in nodes:      
      if type(node) == list and len(node) == 1:
        node = node[0]
      if type(node) != list:
        if node.node_type != 'kill': # No kill widget displayed yet
          wf_rows.append({"widgets":[{"size":size, "name": node.name.title(), "id":  uuids[node.id], "widgetType": "%s-widget" % node.node_type, "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size}]})
      else:
        if node[0].node_type == 'fork':
          wf_rows.append({"widgets":[{"size":size, "name": node[0].name.title(), "id":  uuids[node[0].id], "widgetType": "%s-widget" % node[0].node_type, "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size}]})  
          
          wf_rows.append({  
            "id": str(uuid.uuid4()),
            "widgets":[  

            ],
            "columns":[  
               {  
                  "id": str(uuid.uuid4()),
                  "size": (size / len(node[1])),
                  "rows":
                     [{  
                        "id": str(uuid.uuid4()),
                        "widgets": col['widgets'] 
                      } 
                  ]
                  ,                  
                  "klass":"card card-home card-column span%s" % (size / len(node[1]))
               }
               for col in _create_layout(node[1], size)
            ]
          })
          
          wf_rows.append({"widgets":[{"size":size, "name": node[2].name.title(), "id":  uuids[node[2].id], "widgetType": "%s-widget" % node[2].node_type, "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size}]})
        else:
          wf_rows += _create_layout(node, size)

    return wf_rows
  
  wf_rows = _create_layout(old_nodes[1:-1])      

    
  if wf_rows:
    data['layout'][0]['rows'] = [data['layout'][0]['rows'][0]] + wf_rows + [data['layout'][0]['rows'][-1]]
  
  # Content
  def _dig_nodes(nodes):
    for node in nodes:
      if type(node) != list:
        properties = {}
        if '%s-widget' % node.node_type in NODES and node.node_type != 'kill-widget':
          properties = dict(NODES['%s-widget' % node.node_type].get_fields())
        # TODO map and fill up properties
        
        wf_nodes.append({
            "id": uuids[node.id],
            "name": node.name.title(), # + uuid
            "type": "%s-widget" % node.node_type,
            "properties": properties,
            "children":[{('to' if link.name == 'ok' else link.name): uuids[link.child.get_full_node().id]} for link in node.get_children_links()]
        })
      else:
        _dig_nodes(node)
  _dig_nodes(old_nodes)
  
  data['workflow']['nodes'] = wf_nodes

  return Workflow(data=json.dumps(data))
  


