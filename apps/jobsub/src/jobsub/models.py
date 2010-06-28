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

from django.db import models
from django.core import urlresolvers
from django.contrib.auth.models import User

from desktop.lib.djangothrift import ThriftField
from desktop.lib.thrift_util import simpler_string

from jobsub.server_models import *

import jobsubd.ttypes
from jobsubd.ttypes import SubmissionHandle

class TSubmissionPlan(jobsubd.ttypes.SubmissionPlan):
  """Wrapped submission class with simpler stringification."""
  def __str__(self):
    return simpler_string(self)

class JobDesign(models.Model):
  """
  Contains CMS information for "job designs".
  """
  owner = models.ForeignKey(User)
  name = models.CharField(max_length=40)
  description = models.CharField(max_length=1024)
  last_modified = models.DateTimeField(auto_now=True)
  # Type corresponds to a JobSubForm that gets registered in jobsub.forms.interface.registry
  type = models.CharField(max_length=128)
  # Data is serialized via JobSubFormInterface.serialize_[to|from]_string
  data = models.CharField(max_length=4096)

  def edit_url(self):
    return urlresolvers.reverse("jobsub.views.edit_design", kwargs=dict(id=self.id))

  def clone_url(self):
    return urlresolvers.reverse("jobsub.views.clone_design", kwargs=dict(id=self.id))
  
  def delete_url(self):
    return urlresolvers.reverse("jobsub.views.delete_design", kwargs=dict(id=self.id))

  def submit_url(self):
    return urlresolvers.reverse("jobsub.views.submit_design", kwargs=dict(id=self.id))

  def clone(self):
    clone_kwargs = dict([(field.name, getattr(self, field.name)) for field in self._meta.fields if field.name != 'id']);
    return self.__class__.objects.create(**clone_kwargs)

  def to_jsonable(self):
    return {
      'owner': self.owner.username,
      'name': self.name,
      'last_modified': str(self.last_modified),
      'type': self.type,
      'data': repr(self.data)
    }

class Submission(models.Model):
  """
  Holds informations on submissions from the web app to the daemon.
  The daemon should not update this directly.
  """
  owner = models.ForeignKey(User)
  submission_date = models.DateTimeField(auto_now_add=True)
  name = models.CharField(max_length=40, editable=False)
  submission_plan = ThriftField(TSubmissionPlan, editable=False)
  submission_handle = ThriftField(SubmissionHandle)
  last_seen_state = models.IntegerField(db_index=True)

  def last_seen_state_as_string(self):
    return jobsubd.ttypes.State._VALUES_TO_NAMES.get(self.last_seen_state)

  def watch_url(self):
    return urlresolvers.reverse("jobsub.views.watch_submission", kwargs=dict(id=self.id))

class CheckForSetup(models.Model):
  """
  A model which should have at most one row, indicating
  whether jobsub_setup has run succesfully.
  """
  setup_run = models.BooleanField()
