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

from collections import deque

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from mako.lookup import TemplateLookup

from desktop.models import Document2
from notebook.connectors.base import get_api
from notebook.models import Notebook, make_notebook

from indexer.conf import CONFIG_INDEXING_TEMPLATES_PATH
from indexer.conf import CONFIG_INDEXER_LIBS_PATH
from indexer.conf import zkensemble
from indexer.fields import get_field_type
from indexer.file_format import get_file_format_instance, get_file_format_class
from indexer.operations import get_checked_args


LOG = logging.getLogger(__name__)


class Indexer(object):

  def __init__(self, username, fs=None, jt=None):
    self.fs = fs
    self.jt = jt
    self.username = username
    self.user = User.objects.get(username=username) # To clean

  def _upload_workspace(self, morphline):
    from oozie.models2 import Job

    hdfs_workspace_path = Job.get_workspace(self.username)
    hdfs_morphline_path = os.path.join(hdfs_workspace_path, "morphline.conf")
    hdfs_log4j_properties_path = os.path.join(hdfs_workspace_path, "log4j.properties")

    log4j_template_path = os.path.join(CONFIG_INDEXING_TEMPLATES_PATH.get(), "log4j.properties")

    # Create workspace on hdfs
    self.fs.do_as_user(self.username, self.fs.mkdir, hdfs_workspace_path)

    self.fs.do_as_user(self.username, self.fs.create, hdfs_morphline_path, data=morphline)
    self.fs.do_as_user(self.username, self.fs.create, hdfs_log4j_properties_path, data=open(log4j_template_path).read())

    return hdfs_workspace_path

  def run_morphline(self, request, collection_name, morphline, input_path, query=None):
    workspace_path = self._upload_workspace(morphline)
# 
    task = Notebook(
        name='Indexer job for %s' % collection_name,
        isManaged=True
    )
#     task = make_notebook(
#       name=_('Indexer job for %s') % collection_name,
#       editor_type='notebook',
#       on_success_url=reverse('search:browse', kwargs={'name': collection_name}),
#       is_task=True
#     )

    if query:
      q = Notebook(document=Document2.objects.get_by_uuid(user=self.user, uuid=query))
      notebook_data = q.get_data()
      snippet = notebook_data['snippets'][0]

      api = get_api(request, snippet)

      destination = '__hue_%s' % notebook_data['uuid'][:4]
      location = '/user/%s/__hue-%s' % (request.user,  notebook_data['uuid'][:4])
      sql, success_url = api.export_data_as_table(notebook_data, snippet, destination, is_temporary=True, location=location)
      input_path = '${nameNode}%s' % location

      task.add_hive_snippet(snippet['database'], sql)

    task.add_java_snippet(
      clazz='org.apache.solr.hadoop.MapReduceIndexerTool',
      app_jar=CONFIG_INDEXER_LIBS_PATH.get(),
      arguments=[
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
      files=[
          {u'path': u'%s/log4j.properties' % workspace_path, u'type': u'file'},
          {u'path': u'%s/morphline.conf' % workspace_path, u'type': u'file'}
      ]
    )

    return task.execute(request, batch=True)

  def guess_format(self, data):
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
    geolite_loc = os.path.join(CONFIG_INDEXER_LIBS_PATH.get(), "GeoLite2-City.mmdb")
    grok_dicts_loc = os.path.join(CONFIG_INDEXER_LIBS_PATH.get(), "grok_dictionaries")

    properties = {
      "collection_name": collection_name,
      "fields": self.get_field_list(data['columns']),
      "num_base_fields": len(data['columns']),
      "uuid_name" : uuid_name,
      "get_regex": Indexer._get_regex_for_type,
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
