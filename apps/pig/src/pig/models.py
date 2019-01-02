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
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document as Doc, SAMPLE_USER_ID
from hadoop.fs.hadoopfs import Hdfs
from desktop.auth.backend import is_admin


class Document(models.Model):
  owner = models.ForeignKey(User, db_index=True, verbose_name=_t('Owner'), help_text=_t('User who can modify the job.'))
  is_design = models.BooleanField(default=True, db_index=True, verbose_name=_t('Is a user document, not a document submission.'),
                                     help_text=_t('If the document is not a submitted job but a real query, script, workflow.'))

  def is_editable(self, user): # Deprecated
    return is_admin(user) or self.owner == user

  def can_edit_or_exception(self, user, exception_class=PopupException): # Deprecated
    if self.is_editable(user):
      return True
    else:
      raise exception_class(_('Only superusers and %s are allowed to modify this document.') % user)


class PigScript(Document):
  _ATTRIBUTES = ['script', 'name', 'properties', 'job_id', 'parameters', 'resources', 'hadoopProperties']

  data = models.TextField(default=json.dumps({
      'script': '',
      'name': '',
      'properties': [],
      'job_id': None,
      'parameters': [],
      'resources': [],
      'hadoopProperties': []
  }))

  doc = GenericRelation(Doc, related_query_name='pig_doc')

  isV2 = False

  def update_from_dict(self, attrs):
    data_dict = self.dict

    for attr in PigScript._ATTRIBUTES:
      if attrs.get(attr) is not None:
        data_dict[attr] = attrs[attr]

    if 'name' in attrs:
      self.doc.update(name=attrs['name'])

    self.data = json.dumps(data_dict)

  @property
  def dict(self):
    return json.loads(self.data)

  def get_absolute_url(self):
    return reverse('pig:index') + '#edit/%s' % self.id

  @property
  def use_hcatalog(self):
    script = self.dict['script']
    return ('org.apache.hcatalog.pig.HCatStorer' in script or 'org.apache.hcatalog.pig.HCatLoader' in script) or \
        ('org.apache.hive.hcatalog.pig.HCatLoader' in script or 'org.apache.hive.hcatalog.pig.HCatStorer' in script) # New classes

  @property
  def use_hbase(self):
    script = self.dict['script']
    return 'org.apache.pig.backend.hadoop.hbase.HBaseStorage' in script


class PigScript2(object):
  isV2 = True     # V2 is for the Notebook app

  def __init__(self, attrs=None):
    self.data = json.dumps({
        'script': '',
        'name': '',
        'properties': [],
        'job_id': None,
        'parameters': [],
        'resources': [],
        'hadoopProperties': []
    })

    if attrs:
      self.update_from_dict(attrs)

  def update_from_dict(self, attrs):
    data_dict = self.dict

    data_dict.update(attrs)

    self.data = json.dumps(data_dict)

  @property
  def dict(self):
    return json.loads(self.data)

  @property
  def use_hcatalog(self):
    script = self.dict['script']

    return ('org.apache.hcatalog.pig.HCatStorer' in script or 'org.apache.hcatalog.pig.HCatLoader' in script) or \
        ('org.apache.hive.hcatalog.pig.HCatLoader' in script or 'org.apache.hive.hcatalog.pig.HCatStorer' in script) # New classes

  @property
  def use_hbase(self):
    script = self.dict['script']

    return 'org.apache.pig.backend.hadoop.hbase.HBaseStorage' in script


def create_or_update_script(id, name, script, user, parameters, resources, hadoopProperties, is_design=True):
  try:
    pig_script = PigScript.objects.get(id=id)
    if id == str(SAMPLE_USER_ID): # Special case for the Example, just create an history
      is_design = False
      raise PigScript.DoesNotExist()
    pig_script.doc.get().can_write_or_exception(user)
  except PigScript.DoesNotExist:
    pig_script = PigScript.objects.create(owner=user, is_design=is_design)
    Doc.objects.link(pig_script, owner=pig_script.owner, name=name)
    if not is_design:
      pig_script.doc.get().add_to_history()

  # A user decided eventually to save an unsaved script after execution:
  if is_design and pig_script.doc.get().is_historic():
    pig_script.doc.get().remove_from_history()

  pig_script.update_from_dict({
      'name': name,
      'script': script,
      'parameters': parameters,
      'resources': resources,
      'hadoopProperties': hadoopProperties
  })

  return pig_script


def get_scripts(user, is_design=None):
  scripts = []
  data = Doc.objects.available(PigScript, user)

  if is_design is not None:
    data = [job for job in data if job.is_design]

  for script in data:
    data = script.dict
    massaged_script = {
      'id': script.id,
      'docId': script.doc.get().id,
      'name': data['name'],
      'script': data['script'],
      'parameters': data['parameters'],
      'resources': data['resources'],
      'hadoopProperties': data.get('hadoopProperties', []),
      'isDesign': script.is_design,
      'can_write': script.doc.get().can_write(user)
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
        return "/filebrowser/view=" + path
      else:
        return "/filebrowser/home_relative_view=/" + path
    else:
      return url
  else:
    return url
