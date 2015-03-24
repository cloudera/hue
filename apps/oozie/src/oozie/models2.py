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

from datetime import datetime, timedelta
from dateutil.parser import parse
from string import Template

from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2

from hadoop.fs.hadoopfs import Hdfs
from liboozie.submission2 import Submission
from liboozie.submission2 import create_directories

from oozie.conf import REMOTE_SAMPLE_DIR
from oozie.utils import utc_datetime_format
from hadoop.fs.exceptions import WebHdfsException


LOG = logging.getLogger(__name__)


class Job(object):

  def find_all_parameters(self, with_lib_path=True):
    params = self.find_parameters()

    for param in self.parameters:
      params[param['name'].strip()] = param['value']

    return  [{'name': name, 'value': value} for name, value in params.iteritems() if with_lib_path or name != 'oozie.use.system.libpath']

  @classmethod
  def get_workspace(cls, user):
    return (REMOTE_SAMPLE_DIR.get() + '/hue-oozie-$TIME').replace('$USER', user.username).replace('$TIME', str(time.time()))

  @property
  def validated_name(self):
    good_name = []

    for c in self.name[:40]:
      if not good_name:
        if not re.match('[a-zA-Z_\{\$\}]', c):
          c = '_'
      else:
        if not re.match('[\-_a-zA-Z0-9\{\$\}]', c):
          c = '_'
      good_name.append(c)

    return ''.join(good_name)

  def __str__(self):
    return '%s' % force_unicode(self.name)


class Workflow(Job):
  XML_FILE_NAME = 'workflow.xml'
  PROPERTY_APP_PATH = 'oozie.wf.application.path'
  SLA_DEFAULT = [
      {'key': 'enabled', 'value': False}, # Always first element
      {'key': 'nominal-time', 'value': '${nominal_time}'},
      {'key': 'should-start', 'value': ''},
      {'key': 'should-end', 'value': '${30 * MINUTES}'},
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
                  {"widgets":[{"size":12, "name":"End", "id":"33430f0f-ebfa-c3ec-f237-3e77efa03d0a", "widgetType":"end-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]},
                  {"widgets":[{"size":12, "name":"Kill", "id":"17c9c895-5a16-7443-bb81-f34b30b21548", "widgetType":"kill-widget", "properties":{}, "offset":0, "isLoading":False, "klass":"card card-widget span12"}]}
              ],
              "drops":[ "temp"],
              "klass":"card card-home card-column span12"
          }],
          'workflow': workflow if workflow is not None else {
              "id": None,
              "uuid": None,
              "name": "My Workflow",
              "properties": {
                  "description": "",
                  "job_xml": "",
                  "sla_enabled": False,
                  "schema_version": "uri:oozie:workflow:0.5",
                  "properties": [],
                  "sla": Workflow.SLA_DEFAULT,
                  "show_arrows": True,
                  "wf1_id": None
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
  def uuid(self):
    return self.document.uuid

  def get_json(self):
    _data = self.get_data()

    return json.dumps(_data)

  def get_data(self):
    _data = json.loads(self.data)

    if self.document is not None:
      _data['workflow']['id'] = self.document.id
      _data['workflow']['dependencies'] = list(self.document.dependencies.values('uuid',))
    else:
      _data['workflow']['dependencies'] = []

    if 'parameters' not in _data['workflow']['properties']:
      _data['workflow']['properties']['parameters'] = [
          {'name': 'oozie.use.system.libpath', 'value': True},
      ]
    if 'show_arrows' not in _data['workflow']['properties']:
      _data['workflow']['properties']['show_arrows'] = True

    return _data

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = 'editor2/gen/workflow.xml.mako'

    data = self.get_data()
    nodes = [node for node in self.nodes if node.name != 'End'] + [node for node in self.nodes if node.name == 'End'] # End at the end
    node_mapping = dict([(node.id, node) for node in nodes])

    sub_wfs_ids = [node.data['properties']['workflow'] for node in nodes if node.data['type'] == 'subworkflow']
    workflow_mapping = dict([(workflow.uuid, Workflow(document=workflow)) for workflow in Document2.objects.filter(uuid__in=sub_wfs_ids)])

    xml = re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {
              'wf': self,
              'workflow': data['workflow'],
              'nodes': nodes,
              'mapping': mapping,
              'node_mapping': node_mapping,
              'workflow_mapping': workflow_mapping
          }))
    return force_unicode(xml)

  @property
  def name(self):
    _data = self.get_data()
    return _data['workflow']['name']

  def update_name(self, name):
    _data = self.get_data()
    _data['workflow']['name'] = name
    self.data = json.dumps(_data)

  @property
  def deployment_dir(self):
    _data = self.get_data()
    return _data['workflow']['properties']['deployment_dir']

  @property
  def parameters(self):
    _data = self.get_data()
    return _data['workflow']['properties']['parameters']

  def override_subworkflow_id(self, sub_wf_action, workflow_id):
    _data = self.get_data()

    action = [_action for _action in _data['workflow']['nodes'] if _action['id'] == sub_wf_action.id]
    if action:
      action[0]['properties']['job_properties'].append({'name': Workflow.HUE_ID, 'value': workflow_id})

    self.data = json.dumps(_data)

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
    return [Node(node) for node in _data['workflow']['nodes']]

  def find_parameters(self):
    params = set()

    for param in find_dollar_braced_variables(self.name):
      params.add(param)

    if self.sla_enabled:
      for param in find_json_parameters(self.sla):
        params.add(param)

    for node in self.nodes:
      params.update(node.find_parameters())

    return dict([(param, '') for param in list(params)])

  def set_workspace(self, user):
    _data = json.loads(self.data)

    _data['workflow']['properties']['deployment_dir'] = Job.get_workspace(user)

    self.data = json.dumps(_data)

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

  def gen_status_graph(self, oozie_workflow):
    return ''

  def get_absolute_url(self):
    return reverse('oozie:edit_workflow') + '?workflow=%s' % self.id

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.wf.application.path'


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

    if self.data['type'] == 'hive2' and not self.data['properties']['jdbc_url']:
      self.data['properties']['jdbc_url'] = _get_hiveserver2_url()

    data = {
      'node': self.data,
      'mapping': mapping,
      'node_mapping': node_mapping,
      'workflow_mapping': workflow_mapping
    }

    return django_mako.render_to_string(self.get_template_name(), data)

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
      self.data['properties']['sla'] = Workflow.SLA_DEFAULT

  def get_template_name(self):
    return 'editor2/gen/workflow-%s.xml.mako' % self.data['type']

  def find_parameters(self):
    return find_parameters(self) + (find_parameters(self, ['sla']) if self.sla_enabled else [])


class Action(object):

  @classmethod
  def get_fields(cls):
    return [(f['name'], f['value']) for f in cls.FIELDS.itervalues()] + [('sla', Workflow.SLA_DEFAULT), ('credentials', [])]


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
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['script_path'], cls.FIELDS['hive_xml']]


def _get_hiveserver2_url():
  try:
    from beeswax.conf import HIVE_SERVER_HOST, HIVE_SERVER_PORT
    return 'jdbc:hive2://%s:%s/default' % (HIVE_SERVER_HOST.get(), HIVE_SERVER_PORT.get())
  except Exception, e:
    # Might fail is Hive is disabled
    LOG.warn('Could not guess HiveServer2 URL: %s' % smart_str(e))
    return 'jdbc:hive2://localhost:10000/default'


class HiveServer2Action(Action):
  TYPE = 'hive2'
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
     'parameters': {
          'name': 'parameters',
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
          'label': _('Cc addresses (optional)'),
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
          'value': 'local[*]',
          'help_text': _('Ex: spark://host:port, mesos://host:port, yarn, or local.'),
          'type': ''
     },
     'mode': {
          'name': 'mode',
          'label': _('Mode'),
          'value': 'client',
          'help_text': _('e.g. client,cluster'),
          'type': ''
     },
     'app_name': {
          'name': 'app_name',
          'label': _('App name'),
          'value': 'MySpark',
          'help_text': _('The name of the spark application'),
          'type': ''
     },
    'class': {
          'name': 'class',
          'label': _('Main class'),
          'value': '',
          'help_text': _("e.g. org.apache.spark.examples.mllib.JavaALS."),
          'type': 'text'
     },
     'jars': {
          'name': 'jars',
          'label': _('Jars/py files'),
          'value': '',
          'help_text': _('Comma separated list of jars or python HDFS files.'),
          'type': ''
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
     }
  }

  @classmethod
  def get_mandatory_fields(cls):
    return [cls.FIELDS['spark_master'], cls.FIELDS['mode'], cls.FIELDS['jars'], cls.FIELDS['class']]


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


class ForkNode(Action):
  TYPE = 'fork'
  FIELDS = {}

  @classmethod
  def get_mandatory_fields(cls):
    return []


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
  'sqoop-widget': SqoopAction,
  'mapreduce-widget': MapReduceAction,
  'subworkflow-widget': SubWorkflowAction,
  'shell-widget': ShellAction,
  'ssh-widget': SshAction,
  'fs-widget': FsAction,
  'email-widget': EmailAction,
  'streaming-widget': StreamingAction,
  'distcp-widget': DistCpAction,
  'kill-widget': KillAction,
  'join-widget': JoinAction,
  'fork-widget': ForkNode,
  'decision-widget': DecisionNode,
  'spark-widget': SparkAction
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

  for var in re.findall('\$\{(.+)\}', text, re.MULTILINE):
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
          'name': 'My Coordinator',
          'variables': [], # Aka workflow parameters
          'properties': {
              'description': '',
              'deployment_dir': '',
              'schema_version': 'uri:oozie:coordinator:0.2',
              'frequency_number': 1,
              'frequency_unit': 'days',
              'cron_frequency': '0 0 * * *',
              'cron_advanced': False,
              'timezone': 'America/Los_Angeles',
              'start': '${start_date}',
              'end': '${end_date}',
              'workflow': None,
              'timeout': None,
              'concurrency': None,
              'execution': None,
              'throttle': None,
              'job_xml': '',
              'credentials': [],
              'parameters': [
                  {'name': 'oozie.use.system.libpath', 'value': True},
                  {'name': 'start_date', 'value':  datetime.today().strftime('%Y-%m-%dT%H:%MZ')},
                  {'name': 'end_date', 'value': (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%MZ')}
              ],
              'sla': Workflow.SLA_DEFAULT
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
      start_date[0]['value'] = start_date[0]['value'].strftime('%Y-%m-%dT%H:%M:%SZ')

    end_date = filter(lambda a: a['name'] == 'end_date', self._data['properties']['parameters'])
    if end_date and type(end_date[0]['value']) == datetime:
      end_date[0]['value'] = end_date[0]['value'].strftime('%Y-%m-%dT%H:%M:%SZ')

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

    return self._data

  @property
  def name(self):
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
  def start_utc(self):
    return self.data['properties']['start']

  @property
  def end_utc(self):
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

  @property
  def properties(self):
    props = [{'name': dataset['workflow_variable'], 'value': dataset['dataset_variable']} for dataset in self.data['variables'] if dataset['dataset_type'] == 'parameter']
    props += self.data['properties']['parameters']
    return props

  @property
  def workflow(self):
    wf_doc = Document2.objects.get(uuid=self.data['properties']['workflow'])
    return Workflow(document=wf_doc)

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
    if type(self._data['start']) == unicode:
      self._data['start'] = parse(self._data['start'])

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
        raise PopupException(_('The frequency of the workflow parameter %s cannot be guessed from the frequency of the coordinator.'
                               ' It so needs to be specified manually.'))
      frequency_number = 1
    else:
      frequency_unit = self.data['frequency_unit']
      frequency_number = self.data['frequency_number']

    return '${coord:%(unit)s(%(number)s)}' % {'unit': frequency_unit, 'number': frequency_number}

  @property
  def start_utc(self):
    if self.data['same_start']:
      return self.coordinator.start_utc
    else:
      return utc_datetime_format(self.data['start'])

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
