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
import os
import re
import time
import uuid

from datetime import datetime, timedelta
from dateutil.parser import parse
from string import Template
from xml.sax.saxutils import escape

from django.urls import reverse
from django.db.models import Q
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from desktop.conf import USE_DEFAULT_CONFIGURATION
from desktop.lib import django_mako
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import DefaultConfiguration, Document2, Document

from hadoop.fs.hadoopfs import Hdfs
from hadoop.fs.exceptions import WebHdfsException

from liboozie.conf import SECURITY_ENABLED
from liboozie.oozie_api import get_oozie
from liboozie.submission2 import Submission
from liboozie.submission2 import create_directories
from notebook.models import Notebook

from oozie.conf import REMOTE_SAMPLE_DIR
from oozie.utils import utc_datetime_format, UTC_TIME_FORMAT, convert_to_server_timezone
from oozie.importlib.workflows import generate_v2_graph_nodes, MalformedWfDefException, InvalidTagWithNamespaceException

WORKFLOW_DEPTH_LIMIT = 24
LOG = logging.getLogger(__name__)


class Job(object):

  def find_all_parameters(self, with_lib_path=True):
    params = self.find_parameters()

    for param in self.parameters:
      params[param['name'].strip()] = param['value']

    if params.get('nominal_time') == '':
      params['nominal_time'] = datetime.today().strftime(UTC_TIME_FORMAT)

    return  [{'name': name, 'value': value} for name, value in params.iteritems() if with_lib_path or name != 'oozie.use.system.libpath']

  @classmethod
  def get_workspace(cls, user):
    if not isinstance(user, basestring):
      user = user.username
    return (REMOTE_SAMPLE_DIR.get() + '/hue-oozie-$TIME').replace('$USER', user).replace('$TIME', str(time.time()))

  @property
  def validated_name(self):
    return ''.join(escape(self.name[:40], entities={
        "'": "&apos;",
        "\"": "&quot;"
    }))

  def __str__(self):
    return '%s' % force_unicode(self.name)

  def deployment_dir(self):
    return None

  def check_workspace(self, fs, user):
    # Create optional default root workspace for the first submission
    if REMOTE_SAMPLE_DIR.get() == REMOTE_SAMPLE_DIR.config.default_value:
      create_directories(fs, [REMOTE_SAMPLE_DIR.get()])

    Submission(user, self, fs, None, {})._create_dir(self.deployment_dir)
    Submission(user, self, fs, None, {})._create_dir(Hdfs.join(self.deployment_dir, 'lib'))

  def import_workspace(self, fs, source_deployment_dir, owner):
    try:
      fs.copy_remote_dir(source_deployment_dir, self.deployment_dir, owner=owner)
    except WebHdfsException, e:
      msg = _('The copy of the deployment directory failed: %s.') % e
      LOG.error(msg)
      raise PopupException(msg)


class WorkflowConfiguration(object):

  APP_NAME = 'oozie-workflow'

  SLA_DEFAULT = [
      {'key': 'enabled', 'value': False},  # Always first element
      {'key': 'nominal-time', 'value': '${nominal_time}'},
      {'key': 'should-start', 'value': ''},
      {'key': 'should-end', 'value': '${30 * MINUTES}'},
      {'key': 'max-duration', 'value': ''},
      {'key': 'alert-events', 'value': ''},
      {'key': 'alert-contact', 'value': ''},
      {'key': 'notification-msg', 'value': ''},
      {'key': 'upstream-apps', 'value': ''},
  ]

  PROPERTIES = [
    {
      "multiple": True,
      "defaultValue": [
        {
          'name': 'oozie.use.system.libpath',
          'value': True
        }
      ],
      "value": [
        {
          'name': 'oozie.use.system.libpath',
          'value': True
        }
      ],
      "nice_name": _("Variables"),
      "key": "parameters",
      "help_text": _("Add one or more Oozie workflow job parameters."),
      "type": "parameters"
    }, {
      "multiple": False,
      "defaultValue": '',
      "value": '',
      "nice_name": _("Workspace"),
      "key": "deployment_dir",
      "help_text": _("Specify the deployment directory."),
      "type": "hdfs-file"
    }, {
      "multiple": True,
      "defaultValue": [],
      "value": [],
      "nice_name": _("Hadoop Properties"),
      "key": "properties",
      "help_text": _("Hadoop configuration properties."),
      "type": "settings"
    }, {
      "multiple": False,
      "defaultValue": True,
      "value": True,
      "nice_name": _("Show graph arrows"),
      "key": "show_arrows",
      "help_text": _("Toggles display of graph arrows."),
      "type": "boolean"
    }, {
      "multiple": False,
      "defaultValue": "uri:oozie:workflow:0.5",
      "value": "uri:oozie:workflow:0.5",
      "nice_name": _("Version"),
      "key": "schema_version",
      "help_text": _("Oozie XML Schema Version"),
      "type": "string",
      "options": [
        "uri:oozie:workflow:0.5",
        "uri:oozie:workflow:0.4.5",
        "uri:oozie:workflow:0.4",
      ]
    }, {
      "multiple": False,
      "defaultValue": '',
      "value": '',
      "nice_name": _("Job XML"),
      "key": "job_xml",
      "help_text": _("Oozie Job XML file"),
      "type": "hdfs-file"
    }, {
      "multiple": False,
      "defaultValue": False,
      "value": False,
      "nice_name": _("SLA Enabled"),
      "key": "sla_enabled",
      "help_text": _("SLA Enabled"),
      "type": "boolean"
    }, {
      "multiple": False,
      "defaultValue": SLA_DEFAULT,
      "value": SLA_DEFAULT,
      "nice_name": _("SLA Configuration"),
      "key": "sla",
      "help_text": _("Oozie SLA properties"),
      "type": "settings",
      "options": [prop['key'] for prop in SLA_DEFAULT]
    }
  ]


class WorkflowDepthReached(Exception):
  pass


class Workflow(Job):
  XML_FILE_NAME = 'workflow.xml'
  PROPERTY_APP_PATH = 'oozie.wf.application.path'
  HUE_ID = 'hue-id-w'

  def __init__(self, data=None, document=None, workflow=None, user=None):
    self.document = document
    self.user = user

    if document is not None:
      self.data = document.data
    elif data is not None:
      self.data = data
    else:
      if not workflow:
        workflow = self.get_default_workflow()

      workflow['properties'] = self.get_workflow_properties_for_user(user, workflow)

      self.data = json.dumps({
          'layout': [{
              "size":12, "rows":[
                  {"widgets":[{"size":12, "name":"Start", "id":"3f107997-04cc-8733-60a9-a4bb62cebffc", "widgetType":"start-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"End", "id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "widgetType":"end-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"Kill", "id":"17c9c895-5a16-7443-bb81-f34b30b21548", "widgetType":"kill-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]}
              ],
              "drops":[ "temp"],
              "klass":"card card-home card-column span12"
          }],
          'workflow': workflow
      })

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.wf.application.path'

  @classmethod
  def gen_workflow_data_from_xml(cls, user, oozie_workflow):
    node_list = []
    try:
      node_list = generate_v2_graph_nodes(oozie_workflow.definition)
    except MalformedWfDefException, e:
      LOG.exception("Could not find any nodes in Workflow definition. Maybe it's malformed?")
    except InvalidTagWithNamespaceException, e:
      LOG.exception(
        "Tag with namespace %(namespace)s is not valid. Please use one of the following namespaces: %(namespaces)s" % {
          'namespace': e.namespace,
          'namespaces': e.namespaces
        })

    _to_lowercase(node_list)
    adj_list = _create_graph_adjaceny_list(node_list)

    node_hierarchy = ['start']

    try:
      _get_hierarchy_from_adj_list(adj_list, adj_list['start']['ok_to'], node_hierarchy)
    except WorkflowDepthReached:
      LOG.warn("The Workflow: %s with id: %s, has reached the maximum allowed depth for Graph display " % (oozie_workflow.appName, oozie_workflow.id))
      # Hide graph same as when total nodes > 30
      return {}

    data = {'layout': [{}], 'workflow': {}}
    data['workflow']['nodes'] = []
    _update_adj_list(adj_list)

    nodes_uuid_set = set()
    wf_rows = _create_workflow_layout(node_hierarchy, adj_list, nodes_uuid_set)
    if wf_rows:
      data['layout'][0]['rows'] = wf_rows

    wf_nodes = []
    nodes_uuid_set = set()
    _dig_nodes(node_hierarchy, adj_list, user, wf_nodes, nodes_uuid_set)
    data['workflow']['nodes'] = wf_nodes

    data['workflow']['id'] = '123'
    data['workflow']['properties'] = cls.get_workflow_properties_for_user(user, workflow=None)
    data['workflow']['properties'].update({
      'deployment_dir': '/user/hue/oozie/workspaces/hue-oozie-1452553957.19'
    })

    return data

  @classmethod
  def get_default_workflow(cls):
    return {
      "id": None,
      "uuid": None,
      "name": "My Workflow",
      "nodes": [
        {"id": "3f107997-04cc-8733-60a9-a4bb62cebffc", "name": "Start", "type": "start-widget", "properties": {},
         "children": [{'to': '33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}]},
        {"id": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "name": "End", "type": "end-widget", "properties": {},
         "children": []},
        {"id": "17c9c895-5a16-7443-bb81-f34b30b21548", "name": "Kill", "type": "kill-widget",
         "properties": {'message': _('Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]')},
         "children": []}
      ]
    }

  @classmethod
  def get_workflow_properties_for_user(cls, user, workflow=None):
    workflow = workflow if workflow is not None else {}
    properties = workflow.get('properties', None)

    if not properties:
      config = None
      properties = cls.get_properties()

      if user is not None:
        if USE_DEFAULT_CONFIGURATION.get():
          config = DefaultConfiguration.objects.get_configuration_for_user(app=WorkflowConfiguration.APP_NAME, user=user)

      if config is not None:
        properties.update(config.properties_dict)

      properties.update({
        'wf1_id': None,
        'description': ''
      })

    return properties

  @staticmethod
  def get_properties():
    return dict((prop['key'], prop['value']) for prop in WorkflowConfiguration.PROPERTIES)

  @property
  def id(self):
    return self.document.id if self.document else None

  @property
  def uuid(self):
    return self.document.uuid

  @property
  def name(self):
    _data = self.get_data()
    return _data['workflow']['name']

  @property
  def deployment_dir(self):
    _data = self.get_data()
    return _data['workflow']['properties']['deployment_dir']

  @property
  def parameters(self):
    _data = self.get_data()
    return _data['workflow']['properties']['parameters']

  @property
  def sla_enabled(self):
    _data = self.get_data()
    return _data['workflow']['properties']['sla'][0].get('value')

  @property
  def has_some_slas(self):
    return self.sla_enabled or any([node.sla_enabled for node in self.nodes])

  @property
  def credentials(self):
    return list(set([cred for node in self.nodes for cred in node.data['properties']['credentials']]))

  @property
  def sla(self):
    _data = self.get_data()
    return _data['workflow']['properties']['sla']

  @property
  def nodes(self):
    _data = self.get_data()
    return [Node(node, self.user) for node in _data['workflow']['nodes']]

  def find_parameters(self):
    params = set()

    for param in find_dollar_braced_variables(self.name):
      params.add(param)

    if self.has_some_slas:
      for param in find_json_parameters(self.sla):
        params.add(param)

    parameters = dict([(param, '') for param in list(params)])

    for node in self.nodes:
      if 'document' in node.data['type']:
        for param in node.data['properties']['arguments'] if node.data['type'] == 'java-document' else node.data['properties']['parameters']:
          if param['value'] and '=' in param['value']:
            name, val = param['value'].split('=', 1)
            parameters[name] = val
        extra_fields = []
        if node.data['properties'].get('key_tab_path'):
          extra_fields.append('key_tab_path')
        if node.data['properties'].get('user_principal'):
          extra_fields.append('user_principal')
        extra = find_parameters(node, fields=extra_fields)
      else:
        extra = node.find_parameters()

      if extra:
        parameters.update(dict([(param, '') for param in list(extra)]))

    return parameters

  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)

  def get_data(self):
    _data = json.loads(self.data)

    if self.document is not None:
      _data['workflow']['id'] = self.document.id
      _data['workflow']['dependencies'] = list(self.document.dependencies.values('uuid', ))
    else:
      _data['workflow']['dependencies'] = []

    if 'parameters' not in _data['workflow']['properties']:
      _data['workflow']['properties']['parameters'] = [
        {'name': 'oozie.use.system.libpath', 'value': True},
      ]
    if 'show_arrows' not in _data['workflow']['properties']:
      _data['workflow']['properties']['show_arrows'] = True

    for node in _data['workflow']['nodes']:
      if 'credentials' in node['properties']:  # If node is an Action
        if 'retry_max' not in node['properties']:  # When displaying a workflow
          node['properties']['retry_max'] = []
        if 'retry_interval' not in node['properties']:
          node['properties']['retry_interval'] = []

      # Backward compatibility
      _upgrade_older_node(node)

    return _data

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = 'editor2/gen/workflow.xml.mako'

    data = self.get_data()
    nodes = [node for node in self.nodes if node.name != 'End'] + [node for node in self.nodes if node.name == 'End']  # End at the end
    node_mapping = dict([(node.id, node) for node in nodes])
    sub_wfs_ids = [node.data['properties']['workflow'] for node in nodes if node.data['type'] == 'subworkflow']
    workflow_mapping = dict(
        [(workflow.uuid, Workflow(document=workflow, user=self.user)) for workflow in Document2.objects.filter(uuid__in=sub_wfs_ids)]
    )

    xml = re.sub(re.compile('>\s*\n+', re.MULTILINE), '>\n', django_mako.render_to_string(tmpl, {
      'wf': self,
      'workflow': data['workflow'],
      'nodes': nodes,
      'mapping': mapping,
      'node_mapping': node_mapping,
      'workflow_mapping': workflow_mapping
    }))
    return force_unicode(xml.strip())

  def get_absolute_url(self):
    return reverse('oozie:edit_workflow') + '?workflow=%s' % self.id if self.document else ''

  def override_subworkflow_id(self, sub_wf_action, workflow_id):
    _data = self.get_data()

    action = [_action for _action in _data['workflow']['nodes'] if _action['id'] == sub_wf_action.id]
    if action:
      action[0]['properties']['job_properties'].append({'name': Workflow.HUE_ID, 'value': workflow_id})

    self.data = json.dumps(_data)

  def update_name(self, name):
    _data = self.get_data()
    _data['workflow']['name'] = name
    self.data = json.dumps(_data)

  def update_uuid(self, uuid):
    _data = self.get_data()
    _data['workflow']['uuid'] = uuid
    self.data = json.dumps(_data)

  def set_workspace(self, user):
    _data = json.loads(self.data)

    _data['workflow']['properties']['deployment_dir'] = Job.get_workspace(user)

    self.data = json.dumps(_data)

  def create_single_action_workflow_data(self, node_id):
    _data = json.loads(self.data)

    start_node = [node for node in _data['workflow']['nodes'] if node['name'] == 'Start'][0]
    submit_node = [node for node in _data['workflow']['nodes'] if node['id'] == node_id][0]
    end_node = [node for node in _data['workflow']['nodes'] if node['name'] == 'End'][0]
    kill_node = [node for node in _data['workflow']['nodes'] if node['name'] == 'Kill'][0]

    # Modify children to point Start -> Submit_node -> End/Kill
    start_node['children'] = [{'to': submit_node['id']}]
    submit_node['children'] = [{'to': end_node['id']}, {'error': kill_node['id']}]
    _data['workflow']['properties']['deployment_dir'] = None

    # Recursively find the widget node
    def _get_node(rows, node_id):
      for row in rows:
        if not row['widgets']:
          for col in row['columns']:
            node = _get_node(col['rows'], node_id)
            if node:
              return node
        elif row['widgets'][0]['id'] == node_id:
          return row


    # Create wf data with above nodes
    return json.dumps({
      'layout': [{
          "size": 12,
          "rows": [
              [row for row in _data['layout'][0]['rows'] if row['widgets'] and row['widgets'][0]['name'] == 'Start'][0],
              _get_node(_data['layout'][0]['rows'], node_id),
              [row for row in _data['layout'][0]['rows'] if row['widgets'] and row['widgets'][0]['name'] == 'End'][0],
              [row for row in _data['layout'][0]['rows'] if row['widgets'] and row['widgets'][0]['name'] == 'Kill'][0]
          ],
          "drops": ["temp"],
          "klass": "card card-home card-column span12"
      }],
      'workflow': {
          "id": None,
          "uuid": None,
          "name": _data['workflow']['name'],
          "properties": _data['workflow']['properties'],
          "nodes": [start_node, submit_node, end_node, kill_node]
      }
    })


# Updates node_list to lowercase names
# To avoid case-sensitive failures
def _to_lowercase(node_list):
  for node in node_list:
    for key in node.keys():
      if hasattr(node[key], 'lower'):
        node[key] = node[key].lower()


def _update_adj_list(adj_list):
  uuids = {}
  id = 1
  first_kill_node_seen = False

  for node in adj_list.keys():
    adj_list[node]['id'] = id

    # Oozie uses same action for streaming and mapreduce but Hue manages them differently
    if adj_list[node]['node_type'] == 'map-reduce':
      if 'streaming' in adj_list[node]['name']:
        adj_list[node]['node_type'] = 'streaming'
      else:
        adj_list[node]['node_type'] = 'mapreduce'
    elif adj_list[node]['node_type'] == 'sub-workflow':
      adj_list[node]['node_type'] = 'subworkflow'

    if adj_list[node]['node_type'] == 'kill':
      # JS requires at least one of the kill nodes to have this Id
      if not first_kill_node_seen:
        adj_list[node]['uuid'] = '17c9c895-5a16-7443-bb81-f34b30b21548'
        first_kill_node_seen = True
      else:
        adj_list[node]['uuid'] = str(uuid.uuid4())
    elif adj_list[node]['node_type'] == 'start':
      adj_list[node]['uuid'] = '3f107997-04cc-8733-60a9-a4bb62cebffc'
    elif adj_list[node]['node_type'] == 'end':
      adj_list[node]['uuid'] = '33430f0f-ebfa-c3ec-f237-3e77efa03d0a'
    else:
      adj_list[node]['uuid'] = node + str(uuid.uuid4())[len(node):]

    uuids[id] = adj_list[node]['uuid']
    id += 1
  return adj_list


def _dig_nodes(nodes, adj_list, user, wf_nodes, nodes_uuid_set):
  for node in nodes:
    if type(node) != list:
      node = adj_list[node]
      if node['uuid'] not in nodes_uuid_set:
        properties = {}
        if _get_widget_type(node['node_type']) in NODES:
          properties = dict(NODES[_get_widget_type(node['node_type'])].get_fields())

        if node['node_type'] == 'pig':
          properties['script_path'] = node.get('pig').get('script_path')
        elif node['node_type'] == 'spark':
          properties['class'] = node.get('spark').get('class')
          properties['jars'] = node.get('spark').get('jar')
        elif node['node_type'] == 'hive' or node['node_type'] == 'hive2':
          properties['script_path'] = node.get('hive').get('script')
        elif node['node_type'] == 'java':
          properties['main_class'] = node.get('java').get('main-class')
        elif node['node_type'] == 'sqoop':
          properties['command'] = node.get('sqoop').get('command')
        elif node['node_type'] == 'mapreduce':
          properties['job_properties'] = node.get('job_properties')
        elif node['node_type'] == 'shell':
          properties['shell_command'] = node.get('shell').get('command')
        elif node['node_type'] == 'ssh':
          properties['user'] = '%s@%s' % (node.get('ssh').get('user'), node.get('ssh').get('host'))
          properties['ssh_command'] = node.get('ssh').get('command')
        elif node['node_type'] == 'fs':
          properties['touchzs'] = node.get('fs').get('touchzs')
          properties['mkdirs'] = node.get('fs').get('mkdirs')
          properties['moves'] = node.get('fs').get('moves')
          properties['deletes'] = node.get('fs').get('deletes')
        elif node['node_type'] == 'email':
          properties['to'] = node.get('email').get('to')
          properties['subject'] = node.get('email').get('subject')
        elif node['node_type'] == 'streaming':
          properties['mapper'] = node.get('streaming').get('mapper')
          properties['reducer'] = node.get('streaming').get('reducer')
        elif node['node_type'] == 'distcp':
          properties['distcp_parameters'] = node.get('params')
        elif node['node_type'] == 'subworkflow':
          properties['app-path'] = node.get('subworkflow').get('app-path')
          properties['workflow'] = node.get('uuid')
          properties['job_properties'] = []
          properties['sla'] = ''

        children = []
        if node['node_type'] in ('fork', 'decision'):
          for key in node.keys():
            if key.startswith('path'):
              children.append({'to': adj_list[node[key]]['uuid'], 'condition': '${ 1 gt 0 }'})
          if node['node_type'] == 'decision':
            children.append({'to': adj_list[node['default']]['uuid'], 'condition': '${ 1 gt 0 }'})
        else:
          if node.get('ok_to'):
            children.append({'to': adj_list[node['ok_to']]['uuid']})
          if node.get('error_to'):
            children.append({'error': adj_list[node['error_to']]['uuid']})

        nodes_uuid_set.add(node['uuid'])
        wf_nodes.append({
            "id": node['uuid'],
            "name": '%s-%s' % (node['node_type'].split('-')[0], node['uuid'][:4]),
            "type": _get_widget_type(node['node_type']),
            "properties": properties,
            "children": children
        })
    else:
      _dig_nodes(node, adj_list, user, wf_nodes, nodes_uuid_set)


def _create_workflow_layout(nodes, adj_list, nodes_uuid_set, size=12):
  wf_rows = []
  for node in nodes:
    if type(node) == list and len(node) == 1:
      node = node[0]
    if type(node) != list:
      _append_to_wf_rows(wf_rows, nodes_uuid_set, row_id=adj_list[node]['uuid'],
        row = {"widgets":[{"size":size, "name": adj_list[node]['node_type'], "id":  adj_list[node]['uuid'], "widgetType": _get_widget_type(adj_list[node]['node_type']), "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size, "columns":[]}]})
    else:
      if adj_list[node[0]]['node_type'] in ('fork', 'decision'):
        _append_to_wf_rows(wf_rows, nodes_uuid_set, row_id=adj_list[node[0]]['uuid'],
          row = {"widgets":[{"size":size, "name": adj_list[node[0]]['name'], "id":  adj_list[node[0]]['uuid'], "widgetType": _get_widget_type(adj_list[node[0]]['node_type']), "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size, "columns":[]}]})

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
                      "widgets": c['widgets'],
                      "columns":c.get('columns') or []
                    } for c in col],
                "klass":"card card-home card-column span%s" % (size / len(node[1]))
             }
             for col in [_create_workflow_layout(item, adj_list, nodes_uuid_set, size) for item in node[1]]
          ]
        })
        if adj_list[node[0]]['node_type'] == 'fork':
          wf_rows.append({"widgets":[{"size":size, "name": adj_list[node[2]]['name'], "id":  adj_list[node[2]]['uuid'], "widgetType": _get_widget_type(adj_list[node[2]]['node_type']), "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size, "columns":[]}]})
      else:
        wf_rows.append(_create_workflow_layout(node, adj_list, nodes_uuid_set, size))
  return wf_rows


def _get_widget_type(node_type):
  widget_name = "%s-widget" % node_type
  return widget_name if widget_name in NODES.keys() else 'generic-widget'


# Prevent duplicate nodes in graph layout
def _append_to_wf_rows(wf_rows, nodes_uuid_set, row_id, row):
  if row['widgets'][0]['id'] not in nodes_uuid_set:
    nodes_uuid_set.add(row['widgets'][0]['id'])
    wf_rows.append(row)


def _get_hierarchy_from_adj_list(adj_list, curr_node, node_hierarchy):

  _get_hierarchy_from_adj_list_helper(adj_list, curr_node, node_hierarchy, WORKFLOW_DEPTH_LIMIT)

  # Add End and Kill nodes to node_hierarchy
  for key in adj_list.keys():
    if adj_list[key]['node_type'] == 'kill':
      node_hierarchy.append([adj_list[key]['name']])
  node_hierarchy.append([adj_list[key]['name'] for key in adj_list.keys() if adj_list[key]['node_type'] == 'end'])


def _get_hierarchy_from_adj_list_helper(adj_list, curr_node, node_hierarchy, workflow_depth):

  if workflow_depth <= 0:
    raise WorkflowDepthReached()

  if not curr_node or adj_list[curr_node]['node_type'] in ('join', 'end', 'kill'):
    return curr_node

  elif adj_list[curr_node]['node_type'] in ('fork', 'decision'):
    branch_nodes = []
    branch_nodes.append(curr_node)

    join_node = None
    children = []
    for key in adj_list[curr_node].keys():
      if key.startswith('path') or key == 'default':
        child = []
        return_node = _get_hierarchy_from_adj_list_helper(adj_list, adj_list[curr_node][key], child, workflow_depth - 1)
        join_node = return_node if not join_node else join_node
        if child:
          children.append(child)

    branch_nodes.append(children)
    if adj_list[curr_node]['node_type'] == 'fork':
      branch_nodes.append(join_node)
      node_hierarchy.append(branch_nodes)
      return _get_hierarchy_from_adj_list_helper(adj_list, adj_list[join_node]['ok_to'], node_hierarchy, workflow_depth - 1)

    node_hierarchy.append(branch_nodes)
    return join_node

  else:
    node_hierarchy.append(curr_node)
    return _get_hierarchy_from_adj_list_helper(adj_list, adj_list[curr_node]['ok_to'], node_hierarchy, workflow_depth - 1)

def _create_graph_adjaceny_list(nodes):
  start_node = [node for node in nodes if node.get('node_type') == 'start'][0]
  adj_list = {'start': start_node}

  for node in nodes:
    if node and node.get('node_type') != 'start':
      adj_list[node['name']] = node

  return adj_list


class Node():

  def __init__(self, data, user=None):
    self.data = data
    self.user = user

    self._augment_data()

  def to_xml(self, mapping=None, node_mapping=None, workflow_mapping=None):
    if mapping is None:
      mapping = {}
    if node_mapping is None:
      node_mapping = {}
    if workflow_mapping is None:
      workflow_mapping = {}

    if self.data['type'] in ('hive2', 'hive-document') and not self.data['properties']['jdbc_url']:
      self.data['properties']['jdbc_url'] = _get_hiveserver2_url()

    if self.data['type'] == 'fork':
      links = [link for link in self.data['children'] if link['to'] in node_mapping]
      if len(links) != len(self.data['children']):
        LOG.warn('Fork has some children links that do not exist, ignoring them: links %s, existing links %s, links %s, existing links %s' \
                 % (len(links), len(self.data['children']), links, self.data['children']))
        self.data['children'] = links

    if self.data['type'] == AltusAction.TYPE or \
          (('altus' in mapping.get('cluster', '') and (self.data['type'] == SparkDocumentAction.TYPE or self.data['type'] == 'spark-document'))) or \
          mapping.get('auto-cluster'):
      shell_command_name = self.data['name'] + '.sh'
      self.data['properties']['shell_command'] = shell_command_name
      self.data['properties']['env_var'] = []
      self.data['properties']['arguments'] = []
      self.data['properties']['job_properties'] = []
      self.data['properties']['capture_output'] = True
      self.data['properties']['files'] = [{'value': shell_command_name}, {'value': 'altus.py'}]
      self.data['properties']['archives'] = []

    elif self.data['type'] == JavaDocumentAction.TYPE:
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
      properties = notebook.get_data()['snippets'][0]['properties']

      self.data['properties']['main_class'] = properties['class']
      self.data['properties']['app_jar'] = properties['app_jar'] # Not used here
      self.data['properties']['files'] = [{'value': f['path']} for f in properties['files']]
      self.data['properties']['arguments'] = [{'value': prop} for prop in properties['arguments']]
    elif self.data['type'] == SparkDocumentAction.TYPE or self.data['type'] == 'spark-document':
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
      properties = notebook.get_data()['snippets'][0]['properties']

      if self.data['type'] == 'spark-document': # Oozie Document Action
        self.data['properties']['app_name'] = properties['app_name']

      self.data['properties']['class'] = properties['class']
      self.data['properties']['jars'] = os.path.basename(properties['jars'][0])
      self.data['properties']['files'] = [{'value': f} for f in properties['jars']] + [{'value': f['path']} for f in properties['files']]
      self.data['properties']['spark_arguments'] = [{'value': prop} for prop in properties['spark_arguments']]
      self.data['properties']['spark_opts'] = ' '.join(properties['spark_opts'])
      if len(properties['jars']) > 1:
        self.data['properties']['spark_opts'] += ' --py-files ' + ','.join([os.path.basename(f) for f in properties['jars'][1:]])
    elif self.data['type'] == PigDocumentAction.TYPE:
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
      action = notebook.get_data()['snippets'][0]

      name = '%s-%s' % (self.data['type'].split('-')[0], self.data['id'][:4])
      self.data['properties']['script_path'] = "${wf:appPath()}/" + name + ".pig"
      if 'parameters' not in self.data['properties']:
        self.data['properties']['parameters'] = []
      for param in action['variables']:
        self.data['properties']['parameters'].insert(0, {'value': '%(name)s=%(value)s' % param})
      self.data['properties']['arguments'] = [] # Not Picked yet

      job_properties = []
      for prop in action['properties']['hadoopProperties']:
        name, value = prop.split('=', 1)
        job_properties.append({'name': name, 'value': value})
      self.data['properties']['job_properties'] = job_properties
      self.data['properties']['files'] = [{'value': prop} for prop in action['properties']['resources']]

    elif self.data['type'] == SqoopDocumentAction.TYPE:
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
      action = notebook.get_data()['snippets'][0]

      name = '%s-%s' % (self.data['type'].split('-')[0], self.data['id'][:4])

      command = action['statement']
      if command.startswith('sqoop '):
        _ignore, command = command.split('sqoop ', 1)
      self.data['properties']['command'] = command

      self.data['properties']['files'] = [{'value': f['path']} for f in action['properties']['files']]
      self.data['properties']['arguments'] = []

    elif self.data['type'] == DistCpDocumentAction.TYPE:
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
      action = notebook.get_data()['snippets'][0]

      name = '%s-%s' % (self.data['type'].split('-')[0], self.data['id'][:4])
      self.data['properties']['source_path'] = action['properties']['source_path']
      self.data['properties']['destination_path'] = action['properties']['destination_path']

    elif self.data['type'] == ShellAction.TYPE or self.data['type'] == ShellDocumentAction.TYPE:
      if self.data['properties'].get('uuid'):
        notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
        action = notebook.get_data()['snippets'][0]

        name = '%s-%s' % (self.data['type'].split('-')[0], self.data['id'][:4])
        self.data['properties']['shell_command'] = action['properties']['command_path']
        self.data['properties']['env_var'] = [{'value': prop} for prop in action['properties']['env_var']]
        self.data['properties']['capture_output'] = action['properties']['capture_output']
        self.data['properties']['arguments'] = [{'value': prop} for prop in action['properties']['arguments']]

        self.data['properties']['files'] = [{'value': prop.get('path', prop)} for prop in action['properties']['files']]
        self.data['properties']['archives'] = [{'value': prop} for prop in action['properties']['archives']]

      # Auto ship the script if it was forgotten
      shell_command = self.data['properties']['shell_command']
      if '/' in shell_command and not [f for f in self.data['properties']['files'] if shell_command in f['value']]:
        self.data['properties']['files'].append({'value': shell_command})
        self.data['properties']['shell_command'] = Hdfs.basename(shell_command)


    elif self.data['type'] == MapReduceDocumentAction.TYPE:
      notebook = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=self.data['properties']['uuid']))
      action = notebook.get_data()['snippets'][0]

      name = '%s-%s' % (self.data['type'].split('-')[0], self.data['id'][:4])
      self.data['properties']['app_jar'] = action['properties']['app_jar']
      self.data['properties']['arguments'] = []
      self.data['properties']['parameters'] = []

      job_properties = []
      for prop in action['properties']['hadoopProperties']:
        name, value = prop.split('=', 1)
        job_properties.append({'name': name, 'value': value})
      self.data['properties']['job_properties'] = job_properties

      self.data['properties']['files'] = [{'value': prop} for prop in action['properties']['files']]
      self.data['properties']['archives'] = [{'value': prop} for prop in action['properties']['archives']]

    elif self.data['type'] == ImpalaAction.TYPE or self.data['type'] == ImpalaDocumentAction.TYPE:
      shell_command_name = self.data['name'] + '.sh'
      self.data['properties']['shell_command'] = shell_command_name
      self.data['properties']['env_var'] = []
      self.data['properties']['capture_output'] = False
      self.data['properties']['arguments'] = []

      if self.data['type'] == ImpalaAction.TYPE:
        script_path = self.data['properties'].get('script_path')
      else:
        script_path = self.data['name'] + '.sql'

      files = [{'value': shell_command_name}, {'value': script_path}]
      if self.data['properties']['key_tab_path']:
        files.append({'value': self.data['properties']['key_tab_path']})

      self.data['properties']['files'] = files
      self.data['properties']['archives'] = []


    data = {
      'node': self.data,
      'mapping': mapping,
      'node_mapping': node_mapping,
      'workflow_mapping': workflow_mapping
    }

    if mapping.get('auto-cluster'):
      pass
#       if self.data['type'] == StartNode.TYPE:
#         self.data['altus_action'] = {
#           'properties': {
#             'credentials': {},
#             'retry_max': {},
#             'retry_interval': {},
#             'prepares': {},
#             'job_xml': {},
#             'job_properties': {},
#             'shell_command': '',
#             'arguments': [],
#             'env_var': [],
#             'files': [],
#             'archives': [],
#             'capture_output': True
#             #       <ok to="${ node_mapping[node['children'][0]['to']].name }"/>
# 
#             #  Node(dict(AltusAction().get_fields()))
#           }
#         }
#         self.data['properties']['auto-cluster'] = mapping['auto-cluster']
#       if self.data['type'] == EndNode.TYPE or self.data['type'] == KillAction.TYPE:
#         self.data['properties']['auto-cluster'] = mapping['auto-cluster']
    elif mapping.get('send_email'):
      if self.data['type'] == KillAction.TYPE and not self.data['properties'].get('enableMail'):
        self.data['properties']['enableMail'] = True
        self.data['properties']['to'] = self.user.email
        self.data['properties']['subject'] = _("${wf:name()} execution failure")
        self.data['properties']['body'] = _("Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]")

      if self.data['type'] == EndNode.TYPE:
        self.data['properties']['enableMail'] = True
        self.data['properties']['to'] = self.user.email
        self.data['properties']['subject'] = _("${wf:name()} execution successful")

      if mapping.get('send_result_path'):
        if self.data['type'] == EndNode.TYPE:
          self.data['properties']['body'] = 'View result file at %(send_result_browse_url)s' % mapping

    return django_mako.render_to_string(self.get_template_name(mapping), data)

  @property
  def id(self):
    return self.data['id']

  @property
  def name(self):
    return self.data['name']

  @property
  def sla_enabled(self):
    return 'sla' in self.data['properties'] and self.data['properties']['sla'] and self.data['properties']['sla'][0].get('value')

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
    if 'sla' not in self.data['properties']:
      self.data['properties']['sla'] = WorkflowConfiguration.SLA_DEFAULT
    if 'retry_max' not in self.data['properties']:
      self.data['properties']['retry_max'] = []
    if 'retry_interval' not in self.data['properties']:
      self.data['properties']['retry_interval'] = []

    # Backward compatibility
    _upgrade_older_node(self.data)

  def get_template_name(self, mapping=None):
    if mapping is None:
      mapping = {}

    node_type = self.data['type']
    if self.data['type'] == JavaDocumentAction.TYPE:
      node_type = JavaAction.TYPE
    elif self.data['type'] == ImpalaAction.TYPE or self.data['type'] == ImpalaDocumentAction.TYPE:
      node_type = ShellAction.TYPE
    elif self.data['type'] == AltusAction.TYPE:
      node_type = ShellAction.TYPE
    elif mapping.get('cluster') and 'document' in node_type: # Workflow
      node_type = ShellAction.TYPE
    elif mapping.get('auto-cluster') and 'document' in node_type: # Scheduled workflow
      node_type = ShellAction.TYPE

    return 'editor2/gen/workflow-%s.xml.mako' % node_type

  def find_parameters(self):
    return find_parameters(self) + (find_parameters(self, ['sla']) if self.sla_enabled else [])


def _upgrade_older_node(node):
  if node['type'] in ('sqoop', 'sqoop-widget') and 'arguments' not in node['properties']:
    node['properties']['arguments'] = node['properties']['parameters']

  if node['type'] in ('kill', 'kill-widget') and 'to' not in node['properties']:
    node['properties']['enableMail'] = False
    node['properties']['to'] = ''
    node['properties']['cc'] = ''
    node['properties']['subject'] = ''
    node['properties']['body'] = ''

  if node['type'] in ('end', 'end-widget') and 'to' not in node['properties']:
    node['properties']['enableMail'] = False
    node['properties']['to'] = ''
    node['properties']['cc'] = ''
    node['properties']['subject'] = ''
    node['properties']['body'] = ''
    node['properties']['content_type'] = 'text/plain'
    node['properties']['attachment'] = ''

  if node['type'] == 'email-widget' and 'bcc' not in node['properties']:
    node['properties']['bcc'] = ''
    node['properties']['content_type'] = 'text/plain'
    node['properties']['attachment'] = ''

  if node['type'] == 'spark-widget' and 'files' not in node['properties']:
    node['properties']['files'] = []

  if (node['type'] == 'hive2-widget' or node['type'] == 'hive-document-widget') and 'arguments' not in node['properties']:
    node['properties']['arguments'] = []


class Action(object):

  @classmethod
  def get_fields(cls):
    credentials = [cls.DEFAULT_CREDENTIALS] if hasattr(cls, 'DEFAULT_CREDENTIALS') and cls.DEFAULT_CREDENTIALS else []
    return [(f['name'], f['value']) for f in cls.FIELDS.itervalues()] + [('sla', WorkflowConfiguration.SLA_DEFAULT), ('credentials', credentials)]


class StartNode(Action):
  TYPE = 'start'
  FIELDS = {}


class EndNode(Action):
  TYPE = 'end'
  FIELDS = {}


class PigAction(Action):
  TYPE = 'pig'
  FIELDS = {
     'script_path': {
          'name': 'script_path',
          'label': _('Script'),
          'value': '',
          'help_text': _('Path to the script on HDFS.'),
          'type': ''
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The Pig parameters of the script without -param. e.g. INPUT=${inputDir}'),
          'type': ''
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('The Pig parameters of the script as is. e.g. -param, INPUT=${inputDir}'),
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
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
          'help_text': _('Path to the jar on HDFS.'),
          'type': ''
     },
     'main_class': {
          'name': 'main_class',
          'label': _('Main class'),
          'value': '',
          'help_text': _('Java class. e.g. org.apache.hadoop.examples.Grep'),
          'type': 'text'
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('Arguments of the main method. The value of each arg element is considered a single argument '
                         'and they are passed to the main method in the same order.'),
          'type': ''
     },
     'java_opts': {
          'name': 'java_opts',
          'label': _('Java options'),
          'value': [],
          'help_text': _('Parameters for the JVM, e.g. -Dprop1=a -Dprop2=b'),
          'type': ''
     },
     'capture_output': {
          'name': 'capture_output',
          'label': _('Capture output'),
          'value': False,
          'help_text': _('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                         'command output must be in Java Properties file format and it must not exceed 2KB. '
                         'From within the workflow definition, the output of an %(program)s action node is accessible '
                         'via the String action:output(String node, String key) function') % {'program': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['jar_path'], cls.FIELDS['main_class']]


class HiveAction(Action):
  TYPE = 'hive'
  DEFAULT_CREDENTIALS = 'hcat'
  FIELDS = {
     'script_path': {
          'name': 'script_path',
          'label': _('Script'),
          'value': '',
          'help_text': _('Path to the script on HDFS.'),
          'type': ''
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'hive_xml': {
          'name': 'hive_xml',
          'label': _('Hive XML'),
          'value': '',
          'help_text': _('Refer to a hive-site.xml for connecting to Hive'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['script_path'], cls.FIELDS['hive_xml']]


def _get_hiveserver2_url():
  try:
    from beeswax.hive_site import hiveserver2_jdbc_url
    return hiveserver2_jdbc_url()
  except Exception, e:
    # Might fail is Hive is disabled
    LOG.exception('Could not guess HiveServer2 URL: %s' % smart_str(e))
    return 'jdbc:hive2://localhost:10000/default'


class HiveServer2Action(Action):
  TYPE = 'hive2'
  DEFAULT_CREDENTIALS = 'hive2'
  FIELDS = {
     'script_path': {
          'name': 'script_path',
          'label': _('Script'),
          'value': '',
          'help_text': _('Path to the script on HDFS.'),
          'type': ''
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('Arguments for beeline. E.g. --showHeader=true, -Djavax.net.ssl.trustStore=/etc/cdep-ssl-conf/CA_STANDARD/truststore.jks'),
          'type': []
     },
     'jdbc_url': {
          'name': 'jdbc_url',
          'label': _('HiveServer2 URL'),
          'value': "",
          'help_text': _('e.g. jdbc:hive2://localhost:10000/default. JDBC URL for the Hive Server 2.'),
          'type': ''
     },
     'password': {
          'name': 'password',
          'label': _('Password'),
          'value': '',
          'help_text': _('The password element must contain the password of the current user. However, the password is only used if Hive Server 2 is backed by '
                         'something requiring a password (e.g. LDAP); non-secured Hive Server 2 or Kerberized Hive Server 2 don\'t require a password.'),
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['script_path']]


def _get_impala_url():
  try:
    from impala.dbms import get_query_server_config
    return get_query_server_config()['server_host']
  except Exception, e:
    # Might fail is Impala is disabled
    LOG.exception('Could not get Impalad URL: %s' % smart_str(e))
    return 'localhost'


class ImpalaAction(HiveServer2Action):
  # Executed as shell action until Oozie supports an Impala Action
  TYPE = 'impala'
  DEFAULT_CREDENTIALS = '' # None at this time, need to upload user keytab

  FIELDS = HiveServer2Action.FIELDS.copy()
  del FIELDS['jdbc_url']
  del FIELDS['password']
  FIELDS['impalad_host'] = {
      'name': 'impalad_host',
      'label': _('Impalad hostname'),
      'value': "",
      'help_text': _('e.g. impalad-001.cluster.com. The hostname of the Impalad to send the query to.'),
      'type': ''
  }
  FIELDS['key_tab_path'] = {
      'name': 'key_tab_path',
      'label': _('Keytab path'),
      'value': '${key_tab_path}' if SECURITY_ENABLED.get() else '',
      'help_text': _('Path to the keytab to use when on a secure cluster, e.g. /user/joe/joe.keytab.'),
      'type': ''
  }
  FIELDS['user_principal'] = {
      'name': 'user_principal',
      'label': _('User principal'),
      'value': '${user_principal}' if SECURITY_ENABLED.get() else '',
      'help_text': _('Name of the principal to use in the kinit, e.g.: kinit -k -t /home/joe/joe.keytab joe@PROD.EDH.'),
      'type': ''
  }


class SubWorkflowAction(Action):
  TYPE = 'subworkflow'
  FIELDS = {
     'workflow': {
          'name': 'workflow',
          'label': _('Sub-workflow'),
          'value': None,
          'help_text': _('The sub-workflow application to include. You must own all the sub-workflows'),
          'type': 'workflow'
     },
     'propagate_configuration': {
          'name': 'propagate_configuration',
          'label': _('Propagate configuration'),
          'value': True,
          'help_text': _('If the workflow job configuration should be propagated to the child workflow.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('Can be used to specify the job properties that are required to run the child workflow job.'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['workflow']]


class SqoopAction(Action):
  TYPE = 'sqoop'
  FIELDS = {
     'command': {
          'name': 'command',
          'label': _('Sqoop command'),
          'value': 'import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1',
          'help_text': _('The full %(type)s command. Either put it here or split it by spaces and insert the parts as multiple parameters below.') % {'type': TYPE},
          'type': 'textarea'
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('If no command is specified, split the command by spaces and insert the %(type)s parameters '
                         'here e.g. import, --connect, jdbc:hsqldb:file:db.hsqldb, ...') % {'type': TYPE},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['command']]


class MapReduceAction(Action):
  TYPE = 'mapreduce'
  FIELDS = {
     'jar_path': {
          'name': 'jar_path',
          'label': _('Jar name'),
          'value': '',
          'help_text': _('Path to the jar on HDFS.'),
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['jar_path']]


class ShellAction(Action):
  TYPE = 'shell'
  FIELDS = {
     'shell_command': {
          'name': 'shell_command',
          'label': _('Shell command'),
          'value': '',
          'help_text': _('Shell command to execute, e.g script.sh'),
          'type': ''
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('One arg, e.g. -l, --help'),
          'type': ''
     },
     'env_var': {
          'name': 'env_var',
          'label': _('Environment variables'),
          'value': [],
          'help_text': _('e.g. MAX=10 or PATH=$PATH:mypath'),
          'type': ''
     },
     'capture_output': {
          'name': 'capture_output',
          'label': _('Capture output'),
          'value': True,
          'help_text': _('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                         'command output must be in Java Properties file format and it must not exceed 2KB. '
                         'From within the workflow definition, the output of an %(program)s action node is accessible '
                         'via the String action:output(String node, String key) function') % {'program': TYPE},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['shell_command']]


class SshAction(Action):
  TYPE = 'ssh'
  FIELDS = {
     'host': {
          'name': 'host',
          'label': _('User and Host'),
          'value': 'user@host.com',
          'help_text': _('Where the shell will be executed.'),
          'type': 'text'
     },
     'ssh_command': {
          'name': 'ssh_command',
          'label': _('Ssh command'),
          'value': 'ls',
          'help_text': _('The path of the Shell command to execute.'),
          'type': 'textarea'
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('One arg, e.g. -l, --help'),
          'type': ''
     },
     'capture_output': {
          'name': 'capture_output',
          'label': _('Capture output'),
          'value': True,
          'help_text': _('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                         'command output must be in Java Properties file format and it must not exceed 2KB. '
                         'From within the workflow definition, the output of an %(program)s action node is accessible '
                         'via the String action:output(String node, String key) function') % {'program': TYPE},
          'type': ''
     },
     # Common
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['host'], cls.FIELDS['ssh_command']]


class FsAction(Action):
  TYPE = 'fs'
  FIELDS = {
     'deletes': {
          'name': 'deletes',
          'label': _('Delete path'),
          'value': [],
          'help_text': _('Deletes recursively all content.'),
          'type': ''
     },
     'mkdirs': {
          'name': 'mkdirs',
          'label': _('Create directory'),
          'value': [],
          'help_text': _('Sub directories are created if needed.'),
          'type': ''
     },
     'moves': {
          'name': 'moves',
          'label': _('Move file or directory'),
          'value': [],
          'help_text': _('Destination.'),
          'type': ''
     },
     'chmods': {
          'name': 'chmods',
          'label': _('Change permissions'),
          'value': [],
          'help_text': _('File or directory.'),
          'type': ''
     },
     'touchzs': {
          'name': 'touchzs',
          'label': _('Create or touch a file'),
          'value': [],
          'help_text': _('Or update its modification date.'),
          'type': ''
     },
     'chgrps': {
          'name': 'chgrps',
          'label': _('Change the group'),
          'value': [],
          'help_text': _('File or directory.'),
          'type': ''
     },
     # Common
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return []


class EmailAction(Action):
  TYPE = 'email'
  FIELDS = {
     'to': {
          'name': 'to',
          'label': _('To addresses'),
          'value': '',
          'help_text': _('Comma-separated values'),
          'type': 'text'
     },
     'cc': {
          'name': 'cc',
          'label': _('cc'),
          'value': '',
          'help_text': _('Comma-separated values'),
          'type': 'text'
     },
     'bcc': {
          'name': 'bcc',
          'label': _('bcc'),
          'value': '',
          'help_text': _('Comma-separated values'),
          'type': 'text'
     },
     'subject': {
          'name': 'subject',
          'label': _('Subject'),
          'value': '',
          'help_text': _('Plain-text'),
          'type': 'text'
     },
     'body': {
          'name': 'body',
          'label': _('Body'),
          'value': '',
          'help_text': _('Plain-text'),
          'type': 'textarea'
     },
     'attachment': {
          'name': 'attachment',
          'label': _('Attachment'),
          'value': '',
          'help_text': _('Comma separated list of HDFS files.'),
          'type': ''
     },
     'content_type': {
          'name': 'content_type',
          'label': _('Content-type'),
          'value': 'text/plain',
          'help_text': _('Default is text/plain'),
          'type': 'text'
     },
     # Common
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['to'], cls.FIELDS['subject'], cls.FIELDS['body']]


class StreamingAction(Action):
  TYPE = 'streaming'
  FIELDS = {
     'mapper': {
          'name': 'mapper',
          'label': _('Mapper'),
          'value': '',
          'help_text': _('The executable/script to be used as mapper.'),
          'type': ''
     },
     'reducer': {
          'name': 'reducer',
          'label': _('Reducer'),
          'value': '',
          'help_text': _('The executable/script to be used as reducer.'),
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.')
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.')
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production')
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.')
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml')
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['mapper'], cls.FIELDS['reducer']]


class DistCpAction(Action):
  TYPE = 'distcp'
  FIELDS = {
     'distcp_parameters': {
          'name': 'distcp_parameters',
          'label': _('Arguments'),
          'value': [{'value': ''}, {'value': ''}],
          'help_text': _('Options first, then source / destination paths'),
          'type': 'distcp'
     },
      # Common
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.')
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production')
     },
     'java_opts': {
          'name': 'java_opts',
          'label': _('Java options'),
          'value': '',
          'help_text': _('Parameters for the JVM, e.g. -Dprop1=a -Dprop2=b')
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['distcp_parameters']]


class SparkAction(Action):
  TYPE = 'spark'
  FIELDS = {
     'spark_master': {
          'name': 'spark_master',
          'label': _('Spark Master'),
          'value': 'yarn',
          'help_text': _('Ex: spark://host:port, mesos://host:port, yarn, or local.'),
          'type': ''
     },
     'mode': {
          'name': 'mode',
          'label': _('Mode'),
          'value': 'client',
          'help_text': _('e.g. Client cluster'),
          'type': ''
     },
     'app_name': {
          'name': 'app_name',
          'label': _('App name'),
          'value': 'MySpark',
          'help_text': _('The name of the spark application'),
          'type': ''
     },
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Path to file to put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'class': {
          'name': 'class',
          'label': _('Main class'),
          'value': '',
          'help_text': _("Only if using jars, e.g. org.apache.spark.examples.mllib.JavaALS"),
          'type': 'text'
     },
     'jars': {
          'name': 'jars',
          'label': _('Jar/py name'),
          'value': '',
          'help_text': _('Name of main file added in Files.'),
          'type': 'text'
     },
     'spark_opts': {
          'name': 'spark_opts',
          'label': _('Options list'),
          'value': '',
          'help_text': _('Ex: --executor-memory 20G --num-executors 50'),
          'type': ''
     },
     'spark_arguments': {
          'name': 'spark_arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('Arguments, one by one, e.g. 1000, /path/a.')
     },
     # Common
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production')
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.')
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['files'], cls.FIELDS['jars']]



class AltusAction(Action):
  TYPE = 'altus'
  FIELDS = {
     'service': {
          'name': 'service',
          'label': _('Service'),
          'value': '',
          'help_text': _('e.g. dataeng, iam, dataware...'),
          'type': ''
     },
     'command': {
          'name': 'command',
          'label': _('Command'),
          'value': '',
          'help_text': _('e.g. listClusters, listJobs...'),
          'type': ''
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('List of parameters provided to the command. e.g. jobId=xxx'),
     },
     'capture_output': {
          'name': 'capture_output',
          'label': _('Capture output'),
          'value': True,
          'help_text': _('Capture output of the stdout of the command execution.'),
          'type': ''
     },
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['service'], cls.FIELDS['command']]


class KillAction(Action):
  TYPE = 'kill'
  FIELDS = {
     'message': {
          'name': 'message',
          'label': _('Message'),
          'value': _('Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]'),
          'help_text': _('Message to display when the workflow fails. Can contain some EL functions.'),
          'type': 'textarea'
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


class GenericAction(Action):
  TYPE = 'generic'
  FIELDS = {
     'xml': {
          'name': 'xml',
          'label': _('XML of the action'),
          'value': '<my_action>\n</my_action>',
          'help_text': _('Insert verbatim the XML of the action to insert into the workflow.'),
          'type': 'textarea'
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['xml']]


class ForkNode(Action):
  TYPE = 'fork'
  FIELDS = {}

  @classmethod
  def get_mandatory_fields(cls):
    return []


class HiveDocumentAction(Action):
  TYPE = 'hive-document'
  DEFAULT_CREDENTIALS = 'hive2'
  FIELDS = {
     'uuid': {
          'name': 'uuid',
          'label': _('Hive query'),
          'value': '',
          'help_text': _('Select a saved Hive query you want to schedule.'),
          'type': 'hive'
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The parameters of the script. E.g. N=5, INPUT=${inputDir}'),
          'type': ''
     },
     # Common
     'jdbc_url': {
          'name': 'jdbc_url',
          'label': _('HiveServer2 URL'),
          'value': "",
          'help_text': _('e.g. jdbc:hive2://localhost:10000/default. JDBC URL for the Hive Server 2.'),
          'type': ''
     },
     'password': {
          'name': 'password',
          'label': _('Password'),
          'value': '',
          'help_text': _('The password element must contain the password of the current user. However, the password is only used if Hive Server 2 is backed by '
                         'something requiring a password (e.g. LDAP); non-secured Hive Server 2 or Kerberized Hive Server 2 don\'t require a password.'),
          'type': ''
     },
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class ImpalaDocumentAction(HiveDocumentAction):
  TYPE = 'impala-document'
  DEFAULT_CREDENTIALS = '' # None at this time, need to upload user keytab

  FIELDS = HiveServer2Action.FIELDS.copy()
  del FIELDS['jdbc_url']
  del FIELDS['password']

  FIELDS['impalad_host'] = {
      'name': 'impalad_host',
      'label': _('Impalad hostname'),
      'value': "",
      'help_text': _('e.g. impalad-001.cluster.com (optional)'),
      'type': ''
  }
  FIELDS['key_tab_path'] = {
      'name': 'key_tab_path',
      'label': _('Keytab path'),
      'value': '${key_tab_path}' if SECURITY_ENABLED.get() else '',
      'help_text': _('Path to the keytab to use when on a secure cluster, e.g. /user/joe/joe.keytab.'),
      'type': ''
  }
  FIELDS['user_principal'] = {
      'name': 'user_principal',
      'label': _('User principal'),
      'value': '${user_principal}' if SECURITY_ENABLED.get() else '',
      'help_text': _('Name of the principal to use in the kinit, e.g.: kinit -k -t /home/joe/joe.keytab joe@PROD.EDH.'),
      'type': ''
  }
  FIELDS['uuid'] = {
      'name': 'uuid',
      'label': _('Impala query'),
      'value': '',
      'help_text': _('Select a saved Impala query you want to schedule.'),
      'type': 'impala'
  }


class JavaDocumentAction(Action):
  TYPE = 'java-document'
  FIELDS = {
     'uuid': {
          'name': 'uuid',
          'label': _('Java program'),
          'value': '',
          'help_text': _('Select a saved Java program you want to schedule.'),
          'type': 'java'
     },
     'arguments': {
          'name': 'arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('Arguments of the main method. The value of each arg element is considered a single argument '
                         'and they are passed to the main method in the same order.'),
          'type': ''
     },
     'java_opts': {
          'name': 'java_opts',
          'label': _('Java options'),
          'value': [],
          'help_text': _('Parameters for the JVM, e.g. -Dprop1=a -Dprop2=b'),
          'type': ''
     },
     'capture_output': {
          'name': 'capture_output',
          'label': _('Capture output'),
          'value': False,
          'help_text': _('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                         'command output must be in Java Properties file format and it must not exceed 2KB. '
                         'From within the workflow definition, the output of an %(program)s action node is accessible '
                         'via the String action:output(String node, String key) function') % {'program': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class SparkDocumentAction(Action):
  TYPE = 'spark2-document'
  FIELDS = {
    'uuid': {
        'name': 'uuid',
        'label': _('Spark program'),
        'value': '',
        'help_text': _('Select a saved Spark program you want to schedule.'),
        'type': 'spark'
     },
     'spark_master': {
          'name': 'spark_master',
          'label': _('Spark Master'),
          'value': 'yarn',
          'help_text': _('Ex: spark://host:port, mesos://host:port, yarn, or local.'),
          'type': ''
     },
     'mode': {
          'name': 'mode',
          'label': _('Mode'),
          'value': 'client',
          'help_text': _('e.g. Client cluster'),
          'type': ''
     },
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Path to file to put in the running directory.'),
          'type': ''
     },
     'spark_arguments': {
          'name': 'spark_arguments',
          'label': _('Arguments'),
          'value': [],
          'help_text': _('Arguments, one by one, e.g. 1000, /path/a.')
     },
     'parameters': { # For Oozie Action Document
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     # Common
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production')
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.')
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class PigDocumentAction(Action):
  TYPE = 'pig-document'
  FIELDS = {
    'uuid': {
        'name': 'uuid',
        'label': _('Pig script'),
        'value': '',
        'help_text': _('Select a saved Spark program you want to schedule.'),
        'type': 'pig'
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': [],
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class SqoopDocumentAction(Action):
  TYPE = 'sqoop-document'
  FIELDS = {
    'uuid': {
        'name': 'uuid',
        'label': _('Sqoop command'),
        'value': '',
        'help_text': _('Select a saved Sqoop program you want to schedule.'),
        'type': 'sqoop'
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class DistCpDocumentAction(Action):
  TYPE = 'distcp-document'
  FIELDS = {
    'uuid': {
        'name': 'uuid',
        'label': _('DistCp program'),
        'value': '',
        'help_text': _('Select a saved DistCp program you want to schedule.'),
        'type': 'distcp-doc'
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
      # Common
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.')
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production')
     },
     'java_opts': {
          'name': 'java_opts',
          'label': _('Java options'),
          'value': '',
          'help_text': _('Parameters for the JVM, e.g. -Dprop1=a -Dprop2=b')
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class ShellDocumentAction(Action):
  TYPE = 'shell-document'
  FIELDS = {
    'uuid': {
        'name': 'uuid',
        'label': _('Shell program'),
        'value': '',
        'help_text': _('Select a saved Shell program you want to schedule.'),
        'type': 'shell-doc'
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class MapReduceDocumentAction(Action):
  TYPE = 'mapreduce-document'
  FIELDS = {
    'uuid': {
        'name': 'uuid',
        'label': _('MapReduce program'),
        'value': '',
        'help_text': _('Select a saved MapReduce program you want to schedule.'),
        'type': 'mapreduce-doc'
     },
     'parameters': {
          'name': 'parameters',
          'label': _('Parameters'),
          'value': [],
          'help_text': _('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': TYPE.title()},
          'type': ''
     },
     # Common
     'files': {
          'name': 'files',
          'label': _('Files'),
          'value': [],
          'help_text': _('Files put in the running directory.'),
          'type': ''
     },
     'archives': {
          'name': 'archives',
          'label': _('Archives'),
          'value': [],
          'help_text': _('zip, tar and tgz/tar.gz uncompressed into the running directory.'),
          'type': ''
     },
     'job_properties': {
          'name': 'job_properties',
          'label': _('Hadoop job properties'),
          'value': [],
          'help_text': _('value, e.g. production'),
          'type': ''
     },
     'prepares': {
          'name': 'prepares',
          'label': _('Prepares'),
          'value': [],
          'help_text': _('Path to manipulate before starting the application.'),
          'type': ''
     },
     'job_xml': {
          'name': 'job_xml',
          'label': _('Job XML'),
          'value': '',
          'help_text': _('Refer to a Hadoop JobConf job.xml'),
          'type': ''
     },
     'retry_max': {
          'name': 'retry_max',
          'label': _('Max retry'),
          'value': [],
          'help_text': _('Number of times, default is 3'),
          'type': ''
     },
     'retry_interval': {
          'name': 'retry_interval',
          'label': _('Retry interval'),
          'value': [],
          'help_text': _('Wait time in minutes, default is 10'),
          'type': ''
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['uuid']]


class DecisionNode(Action):
  TYPE = 'decision'
  FIELDS = {}

  @classmethod
  def get_mandatory_fields(cls):
    return []


NODES = {
  'start-widget': StartNode,
  'end-widget': EndNode,
  'pig-widget': PigAction,
  'java-widget': JavaAction,
  'hive-widget': HiveAction,
  'hive2-widget': HiveServer2Action,
  'impala-widget': ImpalaAction,
  'sqoop-widget': SqoopAction,
  'mapreduce-widget': MapReduceAction,
  'subworkflow-widget': SubWorkflowAction,
  'shell-widget': ShellAction,
  'ssh-widget': SshAction,
  'fs-widget': FsAction,
  'email-widget': EmailAction,
  'streaming-widget': StreamingAction,
  'distcp-widget': DistCpAction,
  'altus-widget': AltusAction,
  'kill-widget': KillAction,
  'join-widget': JoinAction,
  'fork-widget': ForkNode,
  'decision-widget': DecisionNode,
  'spark-widget': SparkAction,
  'generic-widget': GenericAction,
  'hive-document-widget': HiveDocumentAction,
  'impala-document-widget': ImpalaDocumentAction,
  'java-document-widget': JavaDocumentAction,
  'spark-document-widget': SparkDocumentAction,
  'pig-document-widget': PigDocumentAction,
  'sqoop-document-widget': SqoopDocumentAction,
  'distcp-document-widget': DistCpDocumentAction,
  'shell-document-widget': ShellDocumentAction,
  'mapreduce-document-widget': MapReduceDocumentAction
}


WORKFLOW_NODE_PROPERTIES = {}
for node in NODES.itervalues():
  WORKFLOW_NODE_PROPERTIES.update(node.FIELDS)



def find_parameters(instance, fields=None):
  """Find parameters in the given fields"""
  if fields is None:
    fields = NODES['%s-widget' % instance.data['type']].FIELDS.keys()

  params = []
  for field in fields:
    data = instance.data['properties'][field]
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

def find_dollar_variables(text):
  return re.findall('[^\n\\\\]\$([^\{ \'\"\-;\(\)]+)', text, re.MULTILINE)

def find_dollar_braced_variables(text):
  vars = set()

  for var in re.findall('\$\{([A-Za-z0-9:_-]+)\}', text, re.MULTILINE):
    if ':' in var:
      var = var.split(':', 1)[1]
    vars.add(var)

  return list(vars)


def import_workflow_from_hue_3_7(old_wf):
  """
  Example of data to transform

  [<Start: start>, <Pig: Pig>, [<Kill: kill>], [<End: end>]]
  [<Start: start>, <Java: TeraGenWorkflow>, <Java: TeraSort>, [<Kill: kill>], [<End: end>]]
  [<Start: start>, [<Fork: fork-34>, [[<Mapreduce: Sleep-1>, <Mapreduce: Sleep-10>], [<Mapreduce: Sleep-5>, [<Fork: fork-38>, [[<Mapreduce: Sleep-3>], [<Mapreduce: Sleep-4>]], <Join: join-39>]]], <Join: join-35>], [<Kill: kill>], [<End: end>]]
  """

  uuids = {}

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
  data['workflow']['properties']['description'] = old_wf.description
  data['workflow']['properties']['sla'] = old_wf.sla
  data['workflow']['properties']['sla_enabled'] = old_wf.sla_enabled
  data['workflow']['properties']['imported'] = True
  data['workflow']['properties']['wf1_id'] = old_wf.id

  # Layout
  rows = data['layout'][0]['rows']

  def _create_layout(nodes, size=12):
    wf_rows = []

    for node in nodes:
      if type(node) == list and len(node) == 1:
        node = node[0]
      if type(node) != list:
        wf_rows.append({"widgets":[{"size":size, "name": node.name.title(), "id":  uuids[node.id], "widgetType": "%s-widget" % node.node_type, "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size, "columns":[]}]})
      else:
        if node[0].node_type == 'fork':
          wf_rows.append({"widgets":[{"size":size, "name": 'Fork', "id":  uuids[node[0].id], "widgetType": "%s-widget" % node[0].node_type, "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size, "columns":[]}]})

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
                        "widgets": c['widgets'],
                        "columns":[]
                      }
                    for c in col] if type(col) == list else [{
                        "id": str(uuid.uuid4()),
                        "widgets": col['widgets'],
                        "columns":[]
                      }
                   ]
                  ,
                  "klass":"card card-home card-column span%s" % (size / len(node[1]))
               }
               for col in _create_layout(node[1], size)
            ]
          })

          wf_rows.append({"widgets":[{"size":size, "name": 'Join', "id":  uuids[node[2].id], "widgetType": "%s-widget" % node[2].node_type, "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span%s" % size, "columns":[]}]})
        else:
          wf_rows.append(_create_layout(node, size))

    return wf_rows

  wf_rows = _create_layout(old_nodes)

  if wf_rows:
    data['layout'][0]['rows'] = [data['layout'][0]['rows'][0]] + wf_rows + [data['layout'][0]['rows'][-1]]


  # Content
  def _dig_nodes(nodes):
    for node in nodes:
      if type(node) != list:
        properties = {}
        if '%s-widget' % node.node_type in NODES:
          properties = dict(NODES['%s-widget' % node.node_type].get_fields())

        if node.node_type == 'pig':
          properties['script_path'] = node.script_path
          properties['parameters'] = [param for param in json.loads(node.params) if param['value'] != '-param']
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['job_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'hive':
          properties['script_path'] = node.script_path
          properties['parameters'] = [param for param in json.loads(node.params) if param['value'] != '-param']
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['hive_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'java':
          properties['jar_path'] = node.jar_path
          properties['main_class'] = node.main_class
          properties['arguments'] = [{'value': arg} for arg in node.args.split(' ')]
          properties['java_opts'] = node.java_opts
          properties['capture_output'] = node.capture_output
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['job_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'sqoop':
          properties['command'] = node.script_path
          properties['parameters'] = json.loads(node.params)
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['job_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'mapreduce':
          properties['jar_path'] = node.jar_path
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['job_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'shell':
          properties['shell_command'] = node.command
          properties['arguments'] = json.loads(node.params)
          properties['capture_output'] = node.capture_output
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['job_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'ssh':
          properties['user'] = '%s@%s' % (node.user, node.host)
          properties['ssh_command'] = node.command
          properties['params'] = json.loads(node.params)
          properties['capture_output'] = node.capture_output
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'fs':
          properties['deletes'] = [{'value': f['name']} for f in json.loads(node.deletes)]
          properties['mkdirs'] = [{'value': f['name']} for f in json.loads(node.mkdirs)]
          properties['moves'] = json.loads(node.moves)
          chmods = json.loads(node.chmods)
          for c in chmods:
            c['value'] = c['path']
            c['dir_files'] = False
          properties['chmods'] = chmods
          properties['touchzs'] = [{'value': f['name']} for f in json.loads(node.touchzs)]
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'email':
          properties['to'] = node.to
          properties['cc'] = node.cc
          properties['subject'] = node.subject
          properties['body'] = node.body
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'streaming':
          properties['mapper'] = node.mapper
          properties['reducer'] = node.reducer
          properties['files'] = [{'value': f} for f in json.loads(node.files)]
          properties['archives'] = json.loads(node.archives)
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['job_xml'] = node.job_xml
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled
        elif node.node_type == 'distcp':
          properties['distcp_parameters'] = json.loads(node.params)
          properties['java_opts'] = node.job_xml
          properties['job_properties'] = json.loads(node.job_properties)
          properties['prepares'] = json.loads(node.prepares)
          properties['description'] = node.description
          properties['sla'] = node.sla
          properties['sla_enabled'] = node.sla_enabled

        wf_nodes.append({
            "id": uuids[node.id],
            "name": '%s-%s' % (node.node_type.split('-')[0], uuids[node.id][:4]),
            "type": "%s-widget" % node.node_type,
            "properties": properties,
            "children":[{('to' if link.name in ('ok', 'start') else link.name): uuids[link.child.get_full_node().id]} for link in node.get_children_links()]
        })
      else:
        _dig_nodes(node)

  _dig_nodes(old_nodes)

  data['workflow']['nodes'] = wf_nodes

  return Workflow(data=json.dumps(data))



class Coordinator(Job):
  XML_FILE_NAME = 'coordinator.xml'
  PROPERTY_APP_PATH = 'oozie.coord.application.path'
  HUE_ID = 'hue-id-c'

  def __init__(self, data=None, json_data=None, document=None):
    self.document = document

    if document is not None:
      self._data = json.loads(document.data)
    elif json_data is not None:
      self._data = json.loads(json_data)
    elif data is not None:
      self._data = data
    else:
      self._data = {
          'id': None,
          'uuid': None,
          'name': 'My Schedule',
          'variables': [], # Aka workflow parameters
          'properties': {
              'description': '',
              'deployment_dir': '',
              'schema_version': 'uri:oozie:coordinator:0.2',
              'frequency_number': 1,
              'frequency_unit': 'days',
              'cron_frequency': '0 0 * * *',
              'cron_advanced': False,
              'timezone': '',
              'start': '${start_date}',
              'end': '${end_date}',
              'workflow': None,
              'document': None,
              'timeout': None,
              'concurrency': None,
              'execution': None,
              'throttle': None,
              'job_xml': '',
              'credentials': [],
              'parameters': [
                  {'name': 'oozie.use.system.libpath', 'value': True},
                  {'name': 'start_date', 'value':  datetime.today().strftime('%Y-%m-%dT%H:%M')},
                  {'name': 'end_date', 'value': (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')}
              ],
              'sla': WorkflowConfiguration.SLA_DEFAULT
          }
      }

  @property
  def id(self):
    return self.document.id

  @property
  def uuid(self):
    return self.document.uuid

  def get_data_for_json(self):
    _data = self.data.copy()

    start_date = filter(lambda a: a['name'] == 'start_date', self._data['properties']['parameters'])
    if start_date and type(start_date[0]['value']) == datetime:
      start_date[0]['value'] = start_date[0]['value'].strftime('%Y-%m-%dT%H:%M:%S')

    end_date = filter(lambda a: a['name'] == 'end_date', self._data['properties']['parameters'])
    if end_date and type(end_date[0]['value']) == datetime:
      end_date[0]['value'] = end_date[0]['value'].strftime('%Y-%m-%dT%H:%M:%S')

    return _data

  def to_json(self):
    return json.dumps(self.get_data_for_json())

  def to_json_for_html(self):
    return json.dumps(self.get_data_for_json(), cls=JSONEncoderForHTML)

  @property
  def data(self):
    if type(self._data['properties']['start']) != datetime and not '$' in self._data['properties']['start']:
      self._data['properties']['start'] = parse(self._data['properties']['start'])

    if type(self._data['properties']['end']) != datetime and not '$' in self._data['properties']['end']:
      self._data['properties']['end'] = parse(self._data['properties']['end'])

    if self.document is not None:
      self._data['id'] = self.document.id

    if 'document' not in self._data['properties']:
      self._data['properties']['document'] = None

    return self._data

  @property
  def name(self):
    from notebook.connectors.oozie_batch import OozieApi # Import dependency

    if self.data['properties']['document']:
      return _("%s for %s") % (OozieApi.SCHEDULE_JOB_PREFIX, self.data['name'] or self.data['type'])
    else:
      return self.data['name']

  def set_workspace(self, user):
    self.data['properties']['deployment_dir'] = Job.get_workspace(user)

  @property
  def deployment_dir(self):
    return self.data['properties']['deployment_dir']

  def find_parameters(self):
    params = set()

    for param in find_dollar_braced_variables(self.name):
      params.add(param)

    for param in find_json_parameters([self.data['properties']]):
      params.add(param)

    for param in find_json_parameters(self.data['variables']):
      if param not in ('MINUTE', 'HOUR', 'DAY', 'MONTH', 'YEAR') and not param.startswith('coord:'):
        params.add(param)

    if self.sla_enabled:
      for param in find_json_parameters(self.sla):
        params.add(param)

    # Get missed params from workflow
    for prop in self.workflow.find_parameters():
      if not prop in params:
        params.add(prop)

    # Remove the ones filled up by coordinator
    removable_names = [ds['workflow_variable'] for ds in self.data['variables']]

    return dict([(param, '') for param in list(params) if param not in removable_names])

  @property
  def sla_enabled(self):
    return self.data['properties']['sla'][0].get('value')

  @property
  def sla(self):
    return self.data['properties']['sla']

  @property
  def parameters(self):
    return self.data['properties']['parameters']

  @property
  def datasets(self):
    return self.inputDatasets + self.outputDatasets

  @property
  def inputDatasets(self):
    return [Dataset(dataset, self) for dataset in self.data['variables'] if dataset['dataset_type'] == 'input_path']

  @property
  def outputDatasets(self):
    return [Dataset(dataset, self) for dataset in self.data['variables'] if dataset['dataset_type'] == 'output_path']

  @property
  def start_server_tz(self):
    return self.data['properties']['start']

  @property
  def end_server_tz(self):
    return self.data['properties']['end']

  @property
  def frequency(self):
    return '${coord:%(unit)s(%(number)d)}' % {'unit': self.data['properties']['frequency_unit'], 'number': self.data['properties']['frequency_number']}

  @property
  def cron_frequency(self):
    data_dict = self.data['properties']

    if 'cron_frequency' in data_dict:
      return data_dict['cron_frequency']
    else:
      # Backward compatibility
      freq = '0 0 * * *'
      if data_dict['frequency_number'] == 1:
        if data_dict['frequency_unit'] == 'minutes':
          freq = '* * * * *'
        elif data_dict['frequency_unit'] == 'hours':
          freq = '0 * * * *'
        elif data_dict['frequency_unit'] == 'days':
          freq = '0 0 * * *'
        elif data_dict['frequency_unit'] == 'months':
          freq = '0 0 0 * *'
      return {'frequency': freq, 'isAdvancedCron': False}

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}

    tmpl = "editor2/gen/coordinator.xml.mako"
    return re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'coord': self, 'mapping': mapping})).encode('utf-8', 'xmlcharrefreplace')

  def clear_workflow_params(self):
    # Repopulated in the config properties
    self.data['variables'] = [dataset for dataset in self.data['variables'] if dataset['dataset_type'] != 'parameter']

  @property
  def properties(self):
    props = [{'name': dataset['workflow_variable'], 'value': dataset['dataset_variable']} for dataset in self.data['variables'] if dataset['dataset_type'] == 'parameter']
    props += self.data['properties']['parameters']
    return props

  @property
  def workflow(self):
    if self.document is None:
      raise PopupException(_('Cannot return workflow since document attribute is None.'))

    # Integrated scheduler
    if self.data['properties']['document']:
      document = Document2.objects.get_by_uuid(user=self.document.owner, uuid=self.data['properties']['document'])
      wf_doc = WorkflowBuilder().create_workflow(document=document, user=self.document.owner, managed=True)
      wf = Workflow(data=wf_doc.data,user=self.document.owner)
      wf_doc.delete()
      return wf
    else:
      wf_doc = Document2.objects.get_by_uuid(user=self.document.owner, uuid=self.data['properties']['workflow'])
      return Workflow(document=wf_doc,user=self.document.owner)

  def get_absolute_url(self):
    return reverse('oozie:edit_coordinator') + '?coordinator=%s' % self.id

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.coord.application.path'


class Dataset():

  def __init__(self, data, coordinator):
    self._data = data
    self.coordinator = coordinator

  @property
  def data(self):
    self._data['name'] = self._data['workflow_variable']

    return self._data

  @property
  def frequency(self):
    if self.data['same_frequency']:
      if self.coordinator.cron_frequency == '* * * * *':
        frequency_unit = 'minutes'
      elif self.coordinator.cron_frequency == '0 * * * *':
        frequency_unit = 'hours'
      elif self.coordinator.cron_frequency == '0 0 * * *':
        frequency_unit = 'days'
      elif self.coordinator.cron_frequency == '0 0 0 * *':
        frequency_unit = 'months'
      else:
        raise PopupException(_('The frequency of the workflow parameter "%s" cannot be guessed from the frequency of the coordinator.'
                               ' It so needs to be specified manually.') % self.data['name'])
      frequency_number = 1
    else:
      frequency_unit = self.data['frequency_unit']
      frequency_number = self.data['frequency_number']

    return '${coord:%(unit)s(%(number)s)}' % {'unit': frequency_unit, 'number': frequency_number}

  @property
  def start_server_tz(self):
    if self.data['same_start']:
      return self.coordinator.start_server_tz
    else:
      return convert_to_server_timezone(self.data['start'], self.data['timezone'])

  @property
  def timezone(self):
    if self.data['same_timezone']:
      return self.coordinator.data['properties']['timezone']
    else:
      return self.data['timezone']

  @property
  def start_instance(self):
    if not self.is_advanced_start_instance:
      return int(self.data['advanced_start_instance'])
    else:
      return 0

  @property
  def is_advanced_start_instance(self):
    return not self.is_int(self.data['advanced_start_instance'])

  def is_int(self, text):
    try:
      int(text)
      return True
    except ValueError:
      return False

  @property
  def end_instance(self):
    if not self.is_advanced_end_instance:
      return int(self.data['advanced_end_instance'])
    else:
      return 0

  @property
  def is_advanced_end_instance(self):
    return not self.is_int(self.data['advanced_end_instance'])



class Bundle(Job):
  XML_FILE_NAME = 'bundle.xml'
  PROPERTY_APP_PATH = 'oozie.bundle.application.path'
  HUE_ID = 'hue-id-b'

  def __init__(self, data=None, json_data=None, document=None):
    self.document = document

    if document is not None:
      self._data = json.loads(document.data)
    elif json_data is not None:
      self._data = json.loads(json_data)
    elif data is not None:
      self._data = data
    else:
      self._data = {
          'id': None,
          'uuid': None,
          'name': 'My Bundle',
          'coordinators': [],
          'properties': {
              'description': '',
              'deployment_dir': '',
              'schema_version': 'uri:oozie:bundle:0.2',
              'kickoff': datetime.today(),
              'parameters': [{'name': 'oozie.use.system.libpath', 'value': 'true'}]
          }
      }

  @property
  def id(self):
    return self.document.id

  @property
  def uuid(self):
    return self.document.uuid

  def get_data_for_json(self):
    _data = self.data.copy()

    _data['properties']['kickoff'] = _data['properties']['kickoff'].strftime('%Y-%m-%dT%H:%M:%S')

    return _data

  def to_json(self):
    return json.dumps(self.get_data_for_json())

  def to_json_for_html(self):
    return json.dumps(self.get_data_for_json(), cls=JSONEncoderForHTML)

  @property
  def data(self):
    if type(self._data['properties']['kickoff']) == unicode:
      self._data['properties']['kickoff'] = parse(self._data['properties']['kickoff'])

    if self.document is not None:
      self._data['id'] = self.document.id

    return self._data

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}

    mapping.update(dict(list(self.get_coordinator_docs().values('uuid', 'name'))))
    tmpl = "editor2/gen/bundle.xml.mako"
    return force_unicode(
              re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {
                'bundle': self,
                'mapping': mapping
           })))

  def get_coordinator_docs(self):
    coordinator_ids = [coordinator['coordinator'] for coordinator in self.data['coordinators']]
    return Document2.objects.filter(type='oozie-coordinator2', uuid__in=coordinator_ids)

  def get_coordinator_objects(self):
    return [Coordinator(document=doc) for doc in self.get_coordinator_docs()]

  @property
  def name(self):
    return self.data['name']

  @property
  def parameters(self):
    return self.data['properties']['parameters']

  @property
  def kick_off_time_utc(self):
    return utc_datetime_format(self.data['properties']['kickoff'])

  def set_workspace(self, user):
    self.data['properties']['deployment_dir'] = Job.get_workspace(user)

  @property
  def deployment_dir(self):
    return self.data['properties']['deployment_dir']

  def find_parameters(self):
    params = set()

    for param in find_dollar_braced_variables(self.name):
      params.add(param)

    for coord in self.get_coordinator_objects():
      params.update(coord.find_parameters())

    for param in find_json_parameters([self.data['properties']]):
      params.add(param)

    # Remove the ones filled up by bundle
    removable_names = [p['name']  for coord in self.data['coordinators'] for p in coord['properties']]

    return dict([(param, '') for param in list(params) if param not in removable_names])

  def get_absolute_url(self):
    return reverse('oozie:edit_bundle') + '?bundle=%s' % self.id

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.bundle.application.path'


class History(object):

  @classmethod
  def get_workflow_from_config(self, conf_dict):
    try:
      doc = Document2.objects.get(type='oozie-workflow2', id=conf_dict.get(Workflow.HUE_ID))
      return Workflow(document=doc)
    except Document2.DoesNotExist:
      pass

  @classmethod
  def get_coordinator_from_config(self, conf_dict):
    try:
      doc = Document2.objects.get(type='oozie-coordinator2', id=conf_dict.get(Coordinator.HUE_ID))
      return Coordinator(document=doc)
    except Document2.DoesNotExist:
      pass

  @classmethod
  def get_bundle_from_config(self, conf_dict):
    try:
      doc = Document2.objects.get(type='oozie-bundle2', id=conf_dict.get(Bundle.HUE_ID))
      return Bundle(document=doc)
    except Document2.DoesNotExist:
      pass


def _import_workspace(fs, user, job):
  source_workspace_dir = job.deployment_dir

  job.set_workspace(user)
  job.check_workspace(fs, user)
  job.import_workspace(fs, source_workspace_dir, user)


def _save_workflow(workflow, layout, user, fs=None):
  if workflow.get('id'):
    workflow_doc = Document2.objects.get(id=workflow['id'])
  else:
    workflow_doc = Document2.objects.create(name=workflow['name'], uuid=workflow['uuid'], type='oozie-workflow2', owner=user, description=workflow['properties']['description'])
    Document.objects.link(workflow_doc, owner=workflow_doc.owner, name=workflow_doc.name, description=workflow_doc.description, extra='workflow2')

  # Excludes all the sub-workflow and Hive dependencies. Contains list of history and coordinator dependencies.
  workflow_doc.dependencies = workflow_doc.dependencies.exclude(Q(is_history=False) & Q(type__in=['oozie-workflow2', 'query-hive', 'query-java']))

  dependencies = \
      [node['properties']['workflow'] for node in workflow['nodes'] if node['type'] == 'subworkflow-widget'] + \
      [node['properties']['uuid'] for node in workflow['nodes'] if 'document-widget' in node['type'] and node['properties'].get('uuid')]
  if dependencies:
    dependency_docs = Document2.objects.filter(uuid__in=dependencies)
    workflow_doc.dependencies.add(*dependency_docs)

  if workflow['properties'].get('imported'): # We convert from and old workflow format (3.8 <) to the latest
    workflow['properties']['imported'] = False
    workflow_instance = Workflow(workflow=workflow, user=user)
    _import_workspace(fs, user, workflow_instance)
    workflow['properties']['deployment_dir'] = workflow_instance.deployment_dir

  workflow_doc.update_data({'workflow': workflow})
  workflow_doc.update_data({'layout': layout})
  workflow_doc1 = workflow_doc.doc.get()
  workflow_doc.name = workflow_doc1.name = workflow['name']
  workflow_doc.description = workflow_doc1.description = workflow['properties']['description']
  workflow_doc.save()
  workflow_doc1.save()

  return workflow_doc


class WorkflowBuilder():
  """
  Building a workflow that has saved Documents for nodes (e.g Saved Hive query, saved Pig script...).
  """

  def create_workflow(self, user, document=None, name=None, managed=False):
    nodes = []
    documents = [document]

    if name is None:
      name = _('Task of ') + ','.join([document.name or document.type for document in documents])

    for document in documents:
      if document.type == 'query-java':
        node = self.get_java_document_node(document)
      elif document.type == 'query-hive':
        node = self.get_hive_document_node(document, user)
      elif document.type == 'query-impala':
        node = self.get_impala_document_node(document, user)
      elif document.type == 'query-spark2':
        node = self.get_spark_document_node(document, user)
      elif document.type == 'query-pig':
        node = self.get_pig_document_node(document, user)
      elif document.type == 'query-sqoop1':
        node = self.get_sqoop_document_node(document, user)
      elif document.type == 'query-distcp':
        node = self.get_distcp_document_node(document, user)
      elif document.type == 'query-shell':
        node = self.get_shell_document_node(document, user)
      elif document.type == 'query-mapreduce':
        node = self.get_mapreduce_document_node(document, user)
      else:
        raise PopupException(_('Snippet type %s is not supported in batch execution.') % document.type)

      nodes.append(node)

    workflow_doc = self.get_workflow(nodes, name, document.uuid, user, managed=managed)
    workflow_doc.dependencies.add(*documents)

    return workflow_doc


  def create_notebook_workflow(self, user, notebook=None, name=None, managed=False):
    nodes = []

    if name is None:
      name = _('Task of ') + ','.join([snippet['name'] or snippet['type'] for snippet in notebook['snippets']])

    for snippet in notebook['snippets']:
      if snippet['type'] == 'java':
        node = self.get_java_snippet_node(snippet)
      elif snippet['type'] == 'hive':
        node = self.get_hive_snippet_node(snippet, user)
      elif snippet['type'] == 'impala':
        node = self.get_impala_snippet_node(snippet, user)
      elif snippet['type'] == 'spark':
        node = self.get_spark_snippet_node(snippet, user)
      elif snippet['type'] == 'shell':
        node = self.get_shell_snippet_node(snippet)
      else:
        raise PopupException(_('Snippet type %s is not supported in batch execution.') % snippet)

      nodes.append(node)

    workflow_doc = self.get_workflow(nodes, name, notebook['uuid'], user, managed=managed) # TODO optionally save

    return workflow_doc

  def get_document_parameters(self, document):
    notebook = Notebook(document=document)
    parameters = find_dollar_braced_variables(notebook.get_str())

    return [{u'value': u'%s=${%s}' % (p, p)} for p in parameters]

  def _get_hive_node(self, node_id, user, is_document_node=False):
    api = get_oozie(user)

    credentials = [HiveDocumentAction.DEFAULT_CREDENTIALS] if api.security_enabled else []

    return {
        u'id': node_id,
        u'name': u'hive-%s' % node_id[:4],
        u"type": u"hive-document-widget", # if is_document_node else u"hive2-widget",
        u'properties': {
            u'files': [],
            u'job_xml': u'',
            u'retry_interval': [],
            u'retry_max': [],
            u'job_properties': [],
            u'arguments': [],
            u'parameters': [],
            u'sla': [
                {u'key': u'enabled', u'value': False},
                {u'key': u'nominal-time', u'value': u'${nominal_time}'},
                {u'key': u'should-start', u'value': u''},
                {u'key': u'should-end', u'value': u'${30 * MINUTES}'},
                {u'key': u'max-duration', u'value': u''},
                {u'key': u'alert-events', u'value': u''},
                {u'key': u'alert-contact', u'value': u''},
                {u'key': u'notification-msg', u'value': u''},
                {u'key': u'upstream-apps', u'value': u''},
            ],
            u'archives': [],
            u'prepares': [],
            u'credentials': credentials,
            u'password': u'',
            u'jdbc_url': u'',
        },
        u'children': [
            {u'to': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a'},
            {u'error': u'17c9c895-5a16-7443-bb81-f34b30b21548'}
        ],
        u'actionParameters': [],
    }

  def get_hive_snippet_node(self, snippet, user):
    node = self._get_hive_node(snippet['id'], user)

    node['properties']['parameters'] = [{'value': '%(name)s=%(value)s' % v} for v in snippet['variables']]
    node['properties']['statements'] = 'USE %s;\n\n%s' % (snippet['database'], snippet['statement_raw'])

    return node

  def get_hive_document_node(self, document, user):
    node = self._get_hive_node(document.uuid, user, is_document_node=True)

    notebook = Notebook(document=document)
    node['properties']['parameters'] = [{'value': '%(name)s=%(value)s' % v} for v in notebook.get_data()['snippets'][0]['variables']]
    node['properties']['uuid'] = document.uuid

    return node

  def _get_impala_node(self, node_id, user, is_document_node=False):
    credentials = []

    return {
        u'id': node_id,
        u'name': u'impala-%s' % node_id[:4],
        u"type": u"impala-document-widget",
        u'properties': {
            u'files': [],
            u'job_xml': u'',
            u'retry_interval': [],
            u'retry_max': [],
            u'job_properties': [],
            u'arguments': [],
            u'parameters': [],
            u'sla': [
                {u'key': u'enabled', u'value': False},
                {u'key': u'nominal-time', u'value': u'${nominal_time}'},
                {u'key': u'should-start', u'value': u''},
                {u'key': u'should-end', u'value': u'${30 * MINUTES}'},
                {u'key': u'max-duration', u'value': u''},
                {u'key': u'alert-events', u'value': u''},
                {u'key': u'alert-contact', u'value': u''},
                {u'key': u'notification-msg', u'value': u''},
                {u'key': u'upstream-apps', u'value': u''},
            ],
            u'archives': [],
            u'prepares': [],
            u'credentials': credentials,
            u'impalad_host': u'',
            u'key_tab_path': u'',
            u'user_principal': u''
        },
        u'children': [
            {u'to': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a'},
            {u'error': u'17c9c895-5a16-7443-bb81-f34b30b21548'}
        ],
        u'actionParameters': [],
    }

  def get_impala_snippet_node(self, snippet, user):
    node = self._get_impala_node(snippet['id'], user)

    node['properties']['parameters'] = [{'value': '%(name)s=%(value)s' % v} for v in snippet['variables']]
    node['properties']['statements'] = 'USE %s;\n\n%s' % (snippet['database'], snippet['statement_raw'])

    return node

  def get_impala_document_node(self, document, user):
    node = self._get_impala_node(document.uuid, user, is_document_node=True)

    notebook = Notebook(document=document)
    node['properties']['parameters'] = [{'value': '%(name)s=%(value)s' % v} for v in notebook.get_data()['snippets'][0]['variables']]
    node['properties']['uuid'] = document.uuid

    return node

  def _get_spark_node(self, node_id, user, is_document_node=False):
    credentials = []

    return {
        u'id': node_id,
        u'name': u'spark2-%s' % node_id[:4],
        u"type": u"spark2-document-widget" if is_document_node else u"spark-widget",
        u'properties': {
            u'files': [],
            u'job_xml': u'',
            u'retry_interval': [],
            u'retry_max': [],
            u'job_properties': [],
            u'sla': [
                {u'key': u'enabled', u'value': False},
                {u'key': u'nominal-time', u'value': u'${nominal_time}'},
                {u'key': u'should-start', u'value': u''},
                {u'key': u'should-end', u'value': u'${30 * MINUTES}'},
                {u'key': u'max-duration', u'value': u''},
                {u'key': u'alert-events', u'value': u''},
                {u'key': u'alert-contact', u'value': u''},
                {u'key': u'notification-msg', u'value': u''},
                {u'key': u'upstream-apps', u'value': u''},
            ],
            u'archives': [],
            u'prepares': [],
            u'credentials': credentials,
            u'spark_master': u'yarn',
            u'mode': u'client',
            u'app_name': u'BatchSpark2'
        },
        u'children': [
            {u'to': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a'},
            {u'error': u'17c9c895-5a16-7443-bb81-f34b30b21548'}
        ],
        u'actionParameters': [],
    }

  def get_spark_snippet_node(self, snippet, user):
    node_id = snippet.get('id', str(uuid.uuid4()))

    node = self._get_spark_node(node_id, user)
    node['properties']['class'] = snippet['properties']['class']
    node['properties']['jars'] = snippet['properties']['app_jar'] # Not used, submission add it to oozie.libpath instead
    node['properties']['files'] = [{'value': f['path']} for f in snippet['properties']['files']]
    node['properties']['spark_opts'] = snippet['properties']['spark_opts']
    node['properties']['spark_arguments'] = [{'value': f} for f in snippet['properties']['arguments']]

    return node

  def get_spark_document_node(self, document, user):
    node = self._get_spark_node(document.uuid, user, is_document_node=True)

    node['properties']['uuid'] = document.uuid

    return node

  def get_sqoop_document_node(self, document, user):
    node = self._get_sqoop_node(document.uuid, is_document_node=True)

    node['properties']['uuid'] = document.uuid

    return node

  def _get_sqoop_node(self, node_id, credentials=None, is_document_node=False):
    if credentials is None:
      credentials = []

    return {
        "id": node_id,
        'name': 'sqoop-%s' % node_id[:4],
        "type": "sqoop-document-widget",
        "properties":{
              "statement": "",
              "arguments": [],
              "retry_max": [],
              "retry_interval": [],
              "job_properties": [],
              "prepares": [],
              "credentials": credentials,
              "sla": [{"value":False, "key":"enabled"}, {"value":"${nominal_time}", "key":"nominal-time"}, {"value":"", "key":"should-start"}, {"value":"${30 * MINUTES}", "key":"should-end"}, {"value":"", "key":"max-duration"}, {"value":"", "key":"alert-events"}, {"value":"", "key":"alert-contact"}, {"value":"", "key":"notification-msg"}, {"value":"", "key":"upstream-apps"}],
              "archives": [],
              "files": []
        },
        "children": [
            {"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"},
            {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}
        ],
        "actionParameters": [],
        "actionParametersFetched": False
    }

  def get_distcp_document_node(self, document, user):
    node = self._get_distcp_node(document.uuid, is_document_node=True)

    node['properties']['uuid'] = document.uuid
    node['properties']['distcp_parameters'] = document.data_dict['snippets'][0]['properties'].get('distcp_parameters', [])

    return node

  def _get_distcp_node(self, node_id, credentials=None, is_document_node=False):
    if credentials is None:
      credentials = []

    return {
        "id": node_id,
        'name': 'distcp-%s' % node_id[:4],
        "type": "distcp-document-widget",
        "properties":{
              "source_path": "",
              "destination_path": "",
              "arguments": [],
              "java_opts": [],
              "retry_max": [],
              "retry_interval": [],
              "job_properties": [],
              "prepares": [],
              "distcp_parameters": [],
              "credentials": credentials,
              "sla": [{"value":False, "key":"enabled"}, {"value":"${nominal_time}", "key":"nominal-time"}, {"value":"", "key":"should-start"}, {"value":"${30 * MINUTES}", "key":"should-end"}, {"value":"", "key":"max-duration"}, {"value":"", "key":"alert-events"}, {"value":"", "key":"alert-contact"}, {"value":"", "key":"notification-msg"}, {"value":"", "key":"upstream-apps"}],
              "archives": []
        },
        "children": [
            {"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"},
            {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}
        ],
        "actionParameters": [],
        "actionParametersFetched": False
    }

  def get_shell_document_node(self, document, user):
    node = self._get_shell_node(document.uuid)

    node['properties']['uuid'] = document.uuid

    notebook = Notebook(document=document)
    node['properties']['capture_output'] = notebook.get_data()['snippets'][0]['properties']['capture_output']

    return node

  def get_shell_snippet_node(self, snippet):
    node = self._get_shell_node(snippet['id'])

    node['properties']['shell_command'] = snippet['properties'].get('shell_command')
    node['properties']['arguments'] = snippet['properties'].get('arguments')
    node['properties']['archives'] = snippet['properties'].get('archives')
    node['properties']['files'] = snippet['properties'].get('files')
    node['properties']['env_var'] = snippet['properties'].get('env_var')
    node['properties']['capture_output'] = snippet['properties'].get('capture_output')

    return node

  def _get_shell_node(self, node_id, credentials=None, is_snippet_node=False):
    if credentials is None:
      credentials = []

    return {
        "id": node_id,
        'name': 'shell-%s' % node_id[:4],
        "type": "shell-document-widget",
        "properties":{
              "command_path": "",
              "env_var": [],
              "arguments": [],
              "java_opts": [],
              "retry_max": [],
              "retry_interval": [],
              "job_properties": [],
              "capture_output": False,
              "prepares": [],
              "credentials": credentials,
              "sla": [{"value":False, "key":"enabled"}, {"value":"${nominal_time}", "key":"nominal-time"}, {"value":"", "key":"should-start"}, {"value":"${30 * MINUTES}", "key":"should-end"}, {"value":"", "key":"max-duration"}, {"value":"", "key":"alert-events"}, {"value":"", "key":"alert-contact"}, {"value":"", "key":"notification-msg"}, {"value":"", "key":"upstream-apps"}],
              "archives": []
        },
        "children": [
            {"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"},
            {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}
        ],
        "actionParameters": [],
        "actionParametersFetched": False
    }

  def get_mapreduce_document_node(self, document, user):
    node = self._get_mapreduce_node(document.uuid, is_document_node=True)

    node['properties']['uuid'] = document.uuid

    return node

  def _get_mapreduce_node(self, node_id, credentials=None, is_document_node=False):
    if credentials is None:
      credentials = []

    return {
        "id": node_id,
        'name': 'mapreduce-%s' % node_id[:4],
        "type": "mapreduce-document-widget",
        "properties":{
              "jar_path": "",
              "arguments": [],
              "java_opts": [],
              "retry_max": [],
              "retry_interval": [],
              "job_properties": [],
              "prepares": [],
              "credentials": credentials,
              "sla": [{"value":False, "key":"enabled"}, {"value":"${nominal_time}", "key":"nominal-time"}, {"value":"", "key":"should-start"}, {"value":"${30 * MINUTES}", "key":"should-end"}, {"value":"", "key":"max-duration"}, {"value":"", "key":"alert-events"}, {"value":"", "key":"alert-contact"}, {"value":"", "key":"notification-msg"}, {"value":"", "key":"upstream-apps"}],
              "archives": []
        },
        "children": [
            {"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"},
            {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}
        ],
        "actionParameters": [],
        "actionParametersFetched": False
    }

  def get_pig_document_node(self, document, user):
    statement = json.loads(document.data)['snippets'][0]['statement']
    credentials = []
    if self._use_hcatalog(statement) and SECURITY_ENABLED.get():
      credentials.append('hcat')

    node = self._get_pig_node(document.uuid, credentials=credentials, is_document_node=True)

    node['properties']['uuid'] = document.uuid

    return node

  def _use_hcatalog(self, statement):
    return ('org.apache.hcatalog.pig.HCatStorer' in statement or 'org.apache.hcatalog.pig.HCatLoader' in statement) or \
           ('org.apache.hive.hcatalog.pig.HCatLoader' in statement or 'org.apache.hive.hcatalog.pig.HCatStorer' in statement)

  def _get_pig_node(self, node_id, credentials=None, is_document_node=False):
    if credentials is None:
      credentials = []

    return {
        "id": node_id,
        'name': 'pig-%s' % node_id[:4],
        "type": "pig-document-widget",
        "properties":{
              "job_xml": [],
              "jar_path": "",
              "java_opts": [],
              "retry_max": [],
              "retry_interval": [],
              "job_properties": [],
              "prepares": [],
              "credentials": credentials,
              "sla": [{"value":False, "key":"enabled"}, {"value":"${nominal_time}", "key":"nominal-time"}, {"value":"", "key":"should-start"}, {"value":"${30 * MINUTES}", "key":"should-end"}, {"value":"", "key":"max-duration"}, {"value":"", "key":"alert-events"}, {"value":"", "key":"alert-contact"}, {"value":"", "key":"notification-msg"}, {"value":"", "key":"upstream-apps"}],
              "archives": []
        },
        "children": [
            {"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"},
            {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}
        ],
        "actionParameters": [],
        "actionParametersFetched": False
    }

  def _get_java_node(self, node_id, credentials=None, is_document_node=False):
    if credentials is None:
      credentials = []

    return {
        "id": node_id,
        'name': 'java-%s' % node_id[:4],
        "type": "java-document-widget" if is_document_node else "java-widget",
        "properties":{
              "job_xml": [],
              "jar_path": "",
              "java_opts": [],
              "retry_max": [],
              "retry_interval": [],
              "job_properties": [],
              "capture_output": False,
              "prepares": [],
              "credentials": credentials,
              "sla": [{"value":False, "key":"enabled"}, {"value":"${nominal_time}", "key":"nominal-time"}, {"value":"", "key":"should-start"}, {"value":"${30 * MINUTES}", "key":"should-end"}, {"value":"", "key":"max-duration"}, {"value":"", "key":"alert-events"}, {"value":"", "key":"alert-contact"}, {"value":"", "key":"notification-msg"}, {"value":"", "key":"upstream-apps"}],
              "archives": []
        },
        "children": [
            {"to": "33430f0f-ebfa-c3ec-f237-3e77efa03d0a"},
            {"error": "17c9c895-5a16-7443-bb81-f34b30b21548"}
        ],
        "actionParameters": [],
        "actionParametersFetched": False
    }

  def get_java_snippet_node(self, snippet):
    credentials = []

    node_id = snippet.get('id', str(uuid.uuid4()))

    node = self._get_java_node(node_id, credentials)
    node['properties']['main_class'] = snippet['properties']['class']
    node['properties']['app_jar'] = snippet['properties']['app_jar'] # Not used, submission add it to oozie.libpath instead
    node['properties']['files'] = [{'value': f['path']} for f in snippet['properties']['files']]
    node['properties']['arguments'] = [{'value': f} for f in snippet['properties']['arguments']]

    return node

  def get_java_document_node(self, document):
    credentials = []

    node = self._get_java_node(document.uuid, credentials, is_document_node=True)
    node['uuid'] = document.uuid

    return node

  def get_workflow(self, nodes, name, doc_uuid, user, managed=False):
    parameters = []

    data = {
      u'workflow': {
      u'name': name,
      u'nodes': [{
          u'name': u'Start',
          u'properties': {},
          u'actionParametersFetched': False,
          u'id': u'3f107997-04cc-8733-60a9-a4bb62cebffc',
          u'type': u'start-widget',
          u'children': [{u'to': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a'}],
          u'actionParameters': [],
        }, {
          u'name': u'End',
          u'properties': {
              u'body': u'',
              u'cc': u'',
              u'to': u'',
              u'enableMail': False,
              u'message': u'Workflow ${wf:id()} finished',
              u'subject': u'',
              u'attachment': u''
          },
          u'actionParametersFetched': False,
          u'id': u'33430f0f-ebfa-c3ec-f237-3e77efa03d0a',
          u'type': u'end-widget',
          u'children': [],
          u'actionParameters': [],
        }, {
          u'name': u'Kill',
          u'properties': {
              u'body': u'',
              u'cc': u'',
              u'to': u'',
              u'enableMail': False,
              u'message': u'Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]',
              u'subject': u'',
              u'attachment': u''
          },
          u'actionParametersFetched': False,
          u'id': u'17c9c895-5a16-7443-bb81-f34b30b21548',
          u'type': u'kill-widget',
          u'children': [],
          u'actionParameters': [],
        }
      ],
      u'properties': {
          u'job_xml': u'',
          u'description': u'',
          u'wf1_id': None,
          u'sla_enabled': False,
          u'deployment_dir': Job.get_workspace(user),
          u'schema_version': u'uri:oozie:workflow:0.5',
          u'sla': [
              {u'key': u'enabled', u'value': False},
              {u'key': u'nominal-time', u'value': u'${nominal_time}'},
              {u'key': u'should-start', u'value': u''},
              {u'key': u'should-end', u'value': u'${30 * MINUTES}'},
              {u'key': u'max-duration', u'value': u''},
              {u'key': u'alert-events', u'value': u''},
              {u'key': u'alert-contact', u'value': u''},
              {u'key': u'notification-msg', u'value': u''},
              {u'key': u'upstream-apps', u'value': u''},
              ],
          u'show_arrows': True,
          u'parameters': parameters,
          u'properties': [],
          },
      u'uuid': str(uuid.uuid4()),
      }
    }

    _prev_node = data['workflow']['nodes'][0]

    for node in nodes:
      data['workflow']['nodes'].append(node)

      _prev_node['children'][0]['to'] = node['id'] # We link nodes
      _prev_node = node

    workflow_doc = _save_workflow(data['workflow'], {}, user)
    workflow_doc.is_managed = managed
    workflow_doc.save()

    return workflow_doc
