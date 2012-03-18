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
try:
  import json
except ImportException:
  import simplejson

from django.db import models
from django.core import urlresolvers
from django.contrib.auth.models import User

LOG = logging.getLogger(__name__)


class JobDesign(models.Model):
  """
  DEPRECATED!!!
      This is the old Hue 1.x job design model. In Hue 2, the design is modelled
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

class CheckForSetup(models.Model):
  """
  A model which should have at most one row, indicating
  whether jobsub_setup has run succesfully.
  """
  # Pre-Hue2 setup
  setup_run = models.BooleanField()
  # What kind of setup have we done?
  setup_level = models.IntegerField(default=0)


################################## New Models ################################

PATH_MAX = 512


class OozieAction(models.Model):
  """
  The OozieAction model is an abstract base class. All concrete actions
  derive from it. And it provides something for the OozieWorkflow to
  reference. See
  https://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance
  """
  # This allows the code to easily figure out which subclass to access
  action_type = models.CharField(max_length=64, blank=False)


class OozieWorkflow(models.Model):
  """
  Contains information on MapReduce job types
  """
  # Generic stuff
  owner = models.ForeignKey(User)
  name = models.CharField(max_length=64, blank=False,
      help_text='Name of the design, which must be unique per user')
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


class OozieMapreduceAction(OozieAction):
  """
  Stores MR actions
  """
  ACTION_TYPE = "mapreduce"

  # For the distributed cache. JSON arrays.
  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text='List of paths to files to be added to the distributed cache')
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text='List of paths to archives to be added to the distributed cache')
  # For the job configuration. JSON dict. Required (e.g. mapred.mapper.class).
  job_properties = models.CharField(max_length=32768, default="[]")
  # Location of the jar in hdfs
  jar_path = models.CharField(max_length=PATH_MAX,
      help_text='Path to jar files on HDFS')


class OozieStreamingAction(OozieAction):
  """
  This is still an MR action from Oozie's perspective. But the data modeling is
  slightly different.

  Note that we don't inherit from OozieMapreduceAction because we want the data
  to be in one place.
  """
  ACTION_TYPE = "streaming"

  # For the distributed cache. JSON arrays.
  files = models.CharField(max_length=PATH_MAX, default="[]")
  archives = models.CharField(max_length=PATH_MAX, default="[]")
  # For the job configuration. JSON dict. Required (e.g. mapred.input.dir).
  job_properties = models.CharField(max_length=32768, default="[]")
  # Scripts/commands (paths in hdfs)
  mapper = models.CharField(max_length=PATH_MAX, blank=False)
  reducer = models.CharField(max_length=PATH_MAX, blank=False)


class OozieJavaAction(OozieAction):
  """
  Definition of Java actions
  """
  ACTION_TYPE = "java"

  # For the distributed cache. JSON arrays.
  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text='List of paths to files to be added to the distributed cache')
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text='List of paths to archives to be added to the distributed cache')
  # Location of the jar in hdfs
  jar_path = models.CharField(max_length=PATH_MAX, blank=False)
  main_class = models.CharField(max_length=256, blank=False)
  args = models.CharField(max_length=4096, blank=True)
  java_opts = models.CharField(max_length=256, blank=True)
  # For the job configuration. JSON dict.
  job_properties = models.CharField(max_length=32768, default="[]")


class JobHistory(models.Model):
  """
  Contains informatin on submitted jobs/workflows.
  """
  owner = models.ForeignKey(User)
  submission_date = models.DateTimeField(auto_now=True)
  job_id = models.CharField(max_length=128)
  workflow = models.ForeignKey(OozieWorkflow)


def hue1_to_hue2_data_migration():
  """
  Data migration from the JobDesign table to the new Oozie-based models.

  The migration could be incomplete:
  - Jar types, for which the main class wasn't specified.

  We add an `(incomplete)' marker to the design name to alert the user.
  """
  jd_list = JobDesign.objects.all()

  for jd in jd_list:
    if jd.type == 'jar':
      _job_design_migration_for_jar(jd)
    elif jd.type == 'streaming':
      _job_design_migration_for_streaming(jd)
    else:
      LOG.warn("Unknown JobDesign type '%s' in the old table. Row id: %s" %
               (jd.type, jd.id))


def _job_design_migration_for_jar(jd):
  """Migrate one jar type design"""
  data = json.loads(jd.data)
  action = OozieJavaAction(action_type=OozieJavaAction.ACTION_TYPE,
                           jar_path=data['jarfile'],
                           main_class="please.specify.in.the.job.design",
                           args=data['arguments'])
  action.save()

  wf = OozieWorkflow(owner=jd.owner,
                     name=jd.name + ' (incomplete)',
                     description=jd.description,
                     root_action=action)
  wf.save()


def _job_design_migration_for_streaming(jd):
  """Migrate one streaming type design"""
  data = json.loads(jd.data)

  files = json.dumps(data['cache_files'])
  archives = json.dumps(data['cache_archives'])
  properties = data['hadoop_properties']

  def add_property(key, value):
    if value:
      properties[key] = value

  add_property('mapred.input.dir', ','.join(data['input']))
  add_property('mapred.output.dir', data['output'])
  add_property('mapred.combiner.class', data['combiner_class'])
  add_property('mapred.mapper.class', data['mapper_class'])
  add_property('mapred.reducer.class', data['reducer_class'])
  add_property('mapred.partitioner.class', data['partitioner_class'])
  add_property('mapred.input.format.class', data['inputformat_class'])
  add_property('mapred.output.format.class', data['outputformat_class'])
  add_property('mapred.reduce.tasks', data['num_reduce_tasks'])


  action = OozieStreamingAction(action_type=OozieStreamingAction.ACTION_TYPE,
                                mapper=data['mapper_cmd'],
                                reducer=data['reducer_cmd'],
                                files=files,
                                archives=archives,
                                job_properties=properties)
  action.save()

  wf = OozieWorkflow(owner=jd.owner,
                     name=jd.name,
                     description=jd.description,
                     root_action=action)
  wf.save()
