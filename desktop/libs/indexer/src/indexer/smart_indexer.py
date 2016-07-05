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
import os
import logging

from mako.lookup import TemplateLookup
from mako.template import Template

from liboozie.oozie_api import get_oozie
from oozie.models2 import Job
from liboozie.submission2 import Submission

from indexer.fields import Field, FIELD_TYPES
from indexer.operations import get_checked_args
from indexer.file_format import get_file_format_instance
from indexer.conf import CONFIG_INDEXING_TEMPLATES_PATH
from indexer.conf import CONFIG_INDEXER_LIBS_PATH
from indexer.conf import zkensemble

from collections import deque

LOG = logging.getLogger(__name__)

class Indexer(object):
  def __init__(self, username, fs):
    self.fs = fs
    self.username = username

  # TODO: This oozie job code shouldn't be in the indexer. What's a better spot for it?
  def _upload_workspace(self, morphline):
    hdfs_workspace_path = Job.get_workspace(self.username)
    hdfs_morphline_path = os.path.join(hdfs_workspace_path, "morphline.conf")
    hdfs_workflow_path = os.path.join(hdfs_workspace_path, "workflow.xml")
    hdfs_log4j_properties_path = os.path.join(hdfs_workspace_path, "log4j.properties")

    workflow_template_path = os.path.join(CONFIG_INDEXING_TEMPLATES_PATH.get(), "workflow.xml")
    log4j_template_path = os.path.join(CONFIG_INDEXING_TEMPLATES_PATH.get(), "log4j.properties")

    # create workspace on hdfs
    self.fs.do_as_user(self.username, self.fs.mkdir, hdfs_workspace_path)

    self.fs.do_as_user(self.username, self.fs.create, hdfs_morphline_path, data=morphline)
    self.fs.do_as_user(self.username, self.fs.create, hdfs_workflow_path, data=open(workflow_template_path).read())
    self.fs.do_as_user(self.username, self.fs.create, hdfs_log4j_properties_path, data=open(log4j_template_path).read())

    return hdfs_workspace_path

  def _schedule_oozie_job(self, workspace_path, collection_name, input_path):
    oozie = get_oozie(self.username)

    properties = {
      "dryrun": "False",
      "zkHost":  zkensemble(),
      # these libs can be installed from here:
      # https://drive.google.com/a/cloudera.com/folderview?id=0B1gZoK8Ae1xXc0sxSkpENWJ3WUU&usp=sharing
      "oozie.libpath": CONFIG_INDEXER_LIBS_PATH.get(),
      "security_enabled": "False",
      "collectionName": collection_name,
      "filePath": input_path,
      "outputDir": "/user/%s/indexer" % self.username,
      "workspacePath": workspace_path,
      'oozie.wf.application.path': "${nameNode}%s" % workspace_path,
      'user.name': self.username
    }

    submission = Submission(self.username, fs=self.fs, properties=properties)
    job_id = submission.run(workspace_path)

    return job_id

  def run_morphline(self, collection_name, morphline, input_path):
    workspace_path = self._upload_workspace(morphline)

    job_id = self._schedule_oozie_job(workspace_path, collection_name, input_path)
    return job_id

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

  def get_uuid_name(self, format_):
    base_name = "_uuid"

    field_names = set([column['name'] for column in format_['columns']])

    while base_name in field_names:
      base_name = '_' + base_name

    return base_name

  @staticmethod
  def _format_character(string):
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    string = string.replace('\t', '\\t')
    string = string.replace('\n', '\\n')

    return string

  @staticmethod
  def _get_regex_for_type(type_):
    matches = filter(lambda field_type: field_type.name == type_, FIELD_TYPES)

    return matches[0].regex.replace('\\', '\\\\')

  def generate_morphline_config(self, collection_name, data, uuid_name):
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
      "format_character":Indexer._format_character,
      "uuid_name" : uuid_name,
      "get_regex":Indexer._get_regex_for_type,
      "format":data['format'],
      "get_kept_args": get_checked_args,
      "grok_dictionaries_location" : grok_dicts_loc if self.fs.exists(geolite_loc) else None,
      "geolite_db_location" : geolite_loc if self.fs.exists(geolite_loc) else None,
      "zk_host": zkensemble()
    }

    oozie_workspace = CONFIG_INDEXING_TEMPLATES_PATH.get()

    lookup = TemplateLookup(directories=[oozie_workspace])
    morphline = lookup.get_template("morphline_template.conf").render(**properties)

    return morphline

