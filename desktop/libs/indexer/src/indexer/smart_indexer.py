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
# limitations under the License.import logging

import logging
import os

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from mako.lookup import TemplateLookup
from mako.template import Template

from collections import deque
from notebook.api import _save_notebook, _execute_notebook
from notebook.models import make_notebook, make_notebook2
from oozie.models2 import Job

from indexer.fields import get_field_type
from indexer.operations import get_checked_args
from indexer.file_format import get_file_format_instance, get_file_format_class
from indexer.conf import CONFIG_INDEXING_TEMPLATES_PATH
from indexer.conf import CONFIG_INDEXER_LIBS_PATH
from indexer.conf import zkensemble


LOG = logging.getLogger(__name__)


class Indexer(object):

  def __init__(self, username, fs=None, jt=None):
    self.fs = fs
    self.jt = jt
    self.username = username
    self.user = User.objects.get(username=username) # To clean

  def _upload_workspace(self, morphline):
    hdfs_workspace_path = Job.get_workspace(self.username)
    hdfs_morphline_path = os.path.join(hdfs_workspace_path, "morphline.conf")
    hdfs_log4j_properties_path = os.path.join(hdfs_workspace_path, "log4j.properties")

    log4j_template_path = os.path.join(CONFIG_INDEXING_TEMPLATES_PATH.get(), "log4j.properties")

    # Create workspace on hdfs
    self.fs.do_as_user(self.username, self.fs.mkdir, hdfs_workspace_path)

    self.fs.do_as_user(self.username, self.fs.create, hdfs_morphline_path, data=morphline)
    self.fs.do_as_user(self.username, self.fs.create, hdfs_log4j_properties_path, data=open(log4j_template_path).read())

    return hdfs_workspace_path

  def run_morphline(self, request, collection_name, morphline, input_path):
    workspace_path = self._upload_workspace(morphline)

#     snippets = [
#       {
#         u'type': u'java',
#         u'files': [
#             {u'path': u'%s/log4j.properties' % workspace_path, u'type': u'file'},
#             {u'path': u'%s/morphline.conf' % workspace_path, u'type': u'file'}
#         ],
#         u'class': u'org.apache.solr.hadoop.MapReduceIndexerTool',
#         u'app_jar': CONFIG_INDEXER_LIBS_PATH.get(),
#         u'arguments': [
#             u'--morphline-file',
#             u'morphline.conf',
#             u'--output-dir',
#             u'${nameNode}/user/%s/indexer' % self.username,
#             u'--log4j',
#             u'log4j.properties',
#             u'--go-live',
#             u'--zk-host',
#             zkensemble(),
#             u'--collection',
#             collection_name,
#             input_path,
#         ],
#         u'archives': [],
#       }
#     ]
#
#     # managed notebook
#     notebook = make_notebook2(name='Indexer job for %s' % collection_name, snippets=snippets).get_data()
#     notebook_doc, created = _save_notebook(notebook, self.user)
#
#     snippet = {'wasBatchExecuted': True}

    snippet_properties =  {
       u'files': [
           {u'path': u'%s/log4j.properties' % workspace_path, u'type': u'file'},
           {u'path': u'%s/morphline.conf' % workspace_path, u'type': u'file'}
       ],
       u'class': u'org.apache.solr.hadoop.MapReduceIndexerTool',
       u'app_jar': CONFIG_INDEXER_LIBS_PATH.get(),
       u'arguments': [
           u'--morphline-file',
           u'morphline.conf',
           u'--output-dir',
           u'${nameNode}/user/%s/indexer' % self.username,
           u'--log4j',
           u'log4j.properties',
           u'--go-live',
           u'--zk-host',
           zkensemble(),
           u'--collection',
           collection_name,
           input_path,
       ],
       u'archives': [],
    }

    notebook = make_notebook(name='Indexer', editor_type='java', snippet_properties=snippet_properties, status='running').get_data()
    notebook_doc, created = _save_notebook(notebook, self.user)

    snippet = {'wasBatchExecuted': True, 'id': notebook['snippets'][0]['id'], 'statement': ''}

    job_handle = _execute_notebook(request, notebook, snippet)

    return job_handle

  def guess_format(self, data):
    """
    Input:
    data: {'type': 'file', 'path': '/user/hue/logs.csv'}
    Output:
    {'format':
      {
        type: 'csv',
        fieldSeparator : ",",
        recordSeparator: '\n',
        quoteChar : "\""
      },
      'columns':
        [
          {name: business_id, type: string},
          {name: cool, type: integer},
          {name: date, type: date}
          ]
    }
    """
    file_format = get_file_format_instance(data['file'])
    return file_format.get_format()

  def guess_field_types(self, data):
    file_format = get_file_format_instance(data['file'], data['format'])
    return file_format.get_fields() if file_format else {'columns':[]}

  # Breadth first ordering of fields
  def get_field_list(self, field_data):
    fields = []

    queue = deque(field_data)

    while len(queue):
      curr_field = queue.popleft()
      fields.append(curr_field)

      for operation in curr_field["operations"]:
        for field in operation["fields"]:
          queue.append(field)

    return fields

  def get_kept_field_list(self, field_data):
    return [field for field in self.get_field_list(field_data) if field['keep']]

  def get_unique_field(self, format_):
    # check for a unique field
    unique_fields = [column['name'] for column in format_['columns'] if column['unique']]

    if unique_fields:
      return unique_fields[0]
    else:
      base_name = "_uuid"
      field_names = set([column['name'] for column in format_['columns']])

      while base_name in field_names:
        base_name = '_' + base_name

      return base_name

  def is_unique_generated(self, format_):
    unique_fields = [column['name'] for column in format_['columns'] if column['unique']]

    return len(unique_fields) == 0

  @staticmethod
  def _get_regex_for_type(type_name):
    field_type = get_field_type(type_name)

    return field_type.regex.replace('\\', '\\\\')

  def generate_morphline_config(self, collection_name, data, uuid_name=None):
    """
    Input:
    data: {
      'type': {'name': 'My New Collection!' format': 'csv', 'columns': [{'name': business_id, 'included': True', 'type': 'string'}, cool, date], fieldSeparator : ",", recordSeparator: '\n', quoteChar : "\""},
      'transformation': [
        'country_code': {'replace': {'FRA': 'FR, 'CAN': 'CA'..}}
        'ip': {'geoIP': }
      ]
    }
    Output:
    Morphline content 'SOLR_LOCATOR : { ...}'
    """

    geolite_loc = os.path.join(CONFIG_INDEXER_LIBS_PATH.get(), "GeoLite2-City.mmdb")
    grok_dicts_loc = os.path.join(CONFIG_INDEXER_LIBS_PATH.get(), "grok_dictionaries")

    properties = {
      "collection_name":collection_name,
      "fields":self.get_field_list(data['columns']),
      "num_base_fields": len(data['columns']),
      "uuid_name" : uuid_name,
      "get_regex":Indexer._get_regex_for_type,
      "format_settings": data['format'],
      "format_class": get_file_format_class(data['format']['type']),
      "get_kept_args": get_checked_args,
      "grok_dictionaries_location" : grok_dicts_loc if self.fs and self.fs.exists(grok_dicts_loc) else None,
      "geolite_db_location" : geolite_loc if self.fs and self.fs.exists(geolite_loc) else None,
      "zk_host": zkensemble()
    }

    oozie_workspace = CONFIG_INDEXING_TEMPLATES_PATH.get()

    lookup = TemplateLookup(directories=[oozie_workspace])
    morphline = lookup.get_template("morphline_template.conf").render(**properties)

    return morphline
