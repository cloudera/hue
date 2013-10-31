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
import posixpath

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document as Doc
from hadoop.fs.hadoopfs import Hdfs


class SparkScript(models.Model):
  _ATTRIBUTES = ['script', 'name', 'properties', 'job_id', 'parameters', 'resources', 'hadoopProperties', 'type']

  data = models.TextField(default=json.dumps({
      'script': '',
      'name': '',
      'properties': [],
      'job_id': None,
      'parameters': [],
      'resources': [],
      'hadoopProperties': [],
      'type': 'python',
  }))

  doc = generic.GenericRelation(Doc, related_name='spark_doc')

  def update_from_dict(self, attrs):
    data_dict = self.dict

    for attr in SparkScript._ATTRIBUTES:
      if attrs.get(attr) is not None:
        data_dict[attr] = attrs[attr]

    if 'name' in attrs:
      self.doc.update(name=attrs['name'])

    self.data = json.dumps(data_dict)

  @property
  def dict(self):
    return json.loads(self.data)

  def get_absolute_url(self):
    return reverse('spark:index') + '#edit/%s' % self.id


def create_or_update_script(id, name, script, user, parameters, resources, hadoopProperties, is_design=True):
  try:
    spark_script = SparkScript.objects.get(id=id)
    spark_script.doc.get().can_read_or_exception(user)
  except SparkScript.DoesNotExist:
    spark_script = SparkScript.objects.create()
    Doc.objects.link(spark_script, owner=user, name=name)
    if not is_design:
      spark_script.doc.get().add_to_history()

  spark_script.update_from_dict({
      'name': name,
      'script': script,
      'parameters': parameters,
      'resources': resources,
      'hadoopProperties': hadoopProperties
  })

  return spark_script


def get_scripts(user, is_design=None):
  scripts = []
  data = Doc.objects.available(SparkScript, user)

  if is_design is not None:
    data = [job for job in data if not job.doc.get().is_historic()]

  for script in data:
    data = script.dict
    massaged_script = {
      'id': script.id,
      'name': data['name'],
      'script': data['script'],
      'parameters': data['parameters'],
      'resources': data['resources'],
      'hadoopProperties': data.get('hadoopProperties', []),
      'isDesign': not script.doc.get().is_historic(),
    }
    scripts.append(massaged_script)

  return scripts


def get_workflow_output(oozie_workflow, fs):
  # TODO: guess from the Input(s):/Output(s)
  output = None

  if 'workflowRoot' in oozie_workflow.conf_dict:
    output = oozie_workflow.conf_dict.get('workflowRoot')
    if output and not fs.exists(output):
      output = None

  return output


def hdfs_link(url):
  if url:
    path = Hdfs.urlsplit(url)[2]
    if path:
      if path.startswith(posixpath.sep):
        return "/filebrowser/view" + path
      else:
        return "/filebrowser/home_relative_view/" + path
    else:
      return url
  else:
    return url
