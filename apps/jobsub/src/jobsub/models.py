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

import logging

from django.db import models
from django.core import urlresolvers
from django.contrib.auth.models import User
from desktop.lib.parameterization import find_parameters, bind_parameters

from django.utils.translation import ugettext_lazy as _


LOG = logging.getLogger(__name__)


class JobDesign(models.Model):
  """
  DEPRECATED!!!
      This is the old Hue 1.x job design model. In Hue 2, the design is modeled
      after Oozie workflows.

  Contains CMS information for "job designs".
  """
  owner = models.ForeignKey(User)
  name = models.CharField(max_length=40)
  description = models.CharField(max_length=1024)
  last_modified = models.DateTimeField(auto_now=True)
  # Type corresponds to a JobSubForm that gets registered in jobsub.forms.interface.registry
  type = models.CharField(max_length=128)
  # Data is serialized via JobSubFormInterface.serialize_[to|from]_string
  data = models.TextField()

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

class CheckForSetup(models.Model):
  """
  A model which should have at most one row, indicating
  whether jobsub_setup has run succesfully.
  """
  # Pre-Hue2 setup
  setup_run = models.BooleanField(default=False)
  # What kind of setup have we done?
  setup_level = models.IntegerField(default=0)


################################## New Models ################################

PATH_MAX = 512


class OozieAction(models.Model):
  """
  DEPRECATED!!!
      This is the old Hue 2.0/2.1 job design model. In Hue 2.2 and newer,
      Oozie models are used.

  The OozieAction model is an abstract base class. All concrete actions
  derive from it. And it provides something for the OozieDesign to
  reference. See
  https://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance
  """
  PARAM_FIELDS = ( )    # Nothing is parameterized by default

  # This allows the code to easily figure out which subclass to access
  action_type = models.CharField(max_length=64, blank=False)

  def find_parameters(self):
    """Return a list of parameters in the various fields"""
    return find_parameters(self, self.PARAM_FIELDS)

  def bind_parameters(self, mapping):
    """
    Change the values of the model object by replacing the param variables
    with actual values.

    Mapping is a dictionary of variable to value.
    """
    # We're going to alter this object. Disallow saving (for models).
    self.save = None
    bind_parameters(self, mapping, self.PARAM_FIELDS)


class OozieDesign(models.Model):
  """
  DEPRECATED!!!
      This is the old Hue 2.0/2.1 job design model. In Hue 2.2 and newer,
      Oozie models are used.

  Contains information about all (Oozie) designs. Specific action info are
  stored in the Oozie*Action models.
  """
  # Generic stuff
  owner = models.ForeignKey(User)
  name = models.CharField(max_length=64, blank=False,
      help_text=_('Name of the design, which must be unique per user.'))
  description = models.CharField(max_length=1024, blank=True)
  last_modified = models.DateTimeField(auto_now=True)

  # Action. Avoid using `root_action' directly, because it only gives you the
  # intermediate table (i.e. OozieAction). You want to use `get_root_action()'
  # most of the time.
  root_action = models.ForeignKey(OozieAction)

  def get_root_action(self):
    """Return the concrete action object, not just a generic OozieAction"""
    root = self.root_action
    if root is None:
      return None
    if root.action_type == OozieMapreduceAction.ACTION_TYPE:
      return root.ooziemapreduceaction
    elif root.action_type == OozieStreamingAction.ACTION_TYPE:
      return root.ooziestreamingaction
    elif root.action_type == OozieJavaAction.ACTION_TYPE:
      return root.ooziejavaaction

    LOG.error("Oozie action type '%s' is not valid (jobsub_oozieaction.id %s)"
              % (root.action_type, root.id))
    return None

  def clone(self, new_owner=None):
    """Return a newly saved instance."""
    action_copy = self.get_root_action()
    action_copy.pk = None       # Need a new OozieAction (superclass instance)
    action_copy.id = None       # Need a new action instance as well
    action_copy.save()

    copy = self
    copy.pk = None
    copy.root_action = action_copy
    if new_owner is not None:
      copy.owner = new_owner
    copy.save()
    return copy

  def find_parameters(self):
    return self.get_root_action().find_parameters()

  def bind_parameters(self, mapping):
    return self.get_root_action().bind_parameters(mapping)


class OozieMapreduceAction(OozieAction):
  """
  DEPRECATED!!!
      This is the old Hue 2.0/2.1 job design model. In Hue 2.2 and newer,
      Oozie models are used.

  Stores MR actions
  """
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'jar_path')
  ACTION_TYPE = "mapreduce"

  # For the distributed cache. JSON arrays.
  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_('List of paths to files to be added to the distributed cache.'))
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_('List of paths to archives to be added to the distributed cache.'))
  # For the job configuration. JSON dict. Required (e.g. mapred.mapper.class).
  job_properties = models.TextField(default="[]")
  # Location of the jar in hdfs
  jar_path = models.CharField(max_length=PATH_MAX,
      help_text=_('Path to jar files on HDFS.'))


class OozieStreamingAction(OozieAction):
  """
  DEPRECATED!!!
      This is the old Hue 2.0/2.1 job design model. In Hue 2.2 and newer,
      Oozie models are used.

  This is still an MR action from Oozie's perspective. But the data modeling is
  slightly different.

  Note that we don't inherit from OozieMapreduceAction because we want the data
  to be in one place.
  """
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'mapper', 'reducer')
  ACTION_TYPE = "streaming"

  # For the distributed cache. JSON arrays.
  files = models.CharField(max_length=PATH_MAX, default="[]")
  archives = models.CharField(max_length=PATH_MAX, default="[]")
  # For the job configuration. JSON dict. Required (e.g. mapred.input.dir).
  job_properties = models.TextField(default="[]")
  # Scripts/commands (paths in hdfs)
  mapper = models.CharField(max_length=PATH_MAX, blank=False)
  reducer = models.CharField(max_length=PATH_MAX, blank=False)


class OozieJavaAction(OozieAction):
  """
  DEPRECATED!!!
      This is the old Hue 2.0/2.1 job design model. In Hue 2.2 and newer,
      Oozie models are used.

  Definition of Java actions
  """
  PARAM_FIELDS = ('files', 'archives', 'jar_path', 'main_class', 'args',
                  'java_opts', 'job_properties')
  ACTION_TYPE = "java"

  # For the distributed cache. JSON arrays.
  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_('List of paths to files to be added to the distributed cache.'))
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_('List of paths to archives to be added to the distributed cache.'))
  # Location of the jar in hdfs
  jar_path = models.CharField(max_length=PATH_MAX, blank=False)
  main_class = models.CharField(max_length=256, blank=False)
  args = models.TextField(blank=True)
  java_opts = models.CharField(max_length=256, blank=True)
  # For the job configuration. JSON dict.
  job_properties = models.TextField(default="[]")


class JobHistory(models.Model):
  """
  DEPRECATED!!!
      This is the old Hue 2.0/2.1 job design model. In Hue 2.2 and newer,
      Oozie models are used.

  Contains informatin on submitted jobs/workflows.
  """
  owner = models.ForeignKey(User)
  submission_date = models.DateTimeField(auto_now=True)
  job_id = models.CharField(max_length=128)
  design = models.ForeignKey(OozieDesign)
