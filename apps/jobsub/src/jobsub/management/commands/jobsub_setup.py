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
#
# Copies a handful of files over to the remote filesystem.
# The source for this operation ought to be part of the
# build process; this is currently a bit ad-hoc.

import os
import posixpath
import logging
import shutil

import django.core
from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User

from hadoop import cluster
import jobsub.conf
from jobsub.submit import Submission

from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)


# The setup_level value for the CheckForSetup table
JOBSUB_SETUP_LEVEL = 200        # Stands for Hue 2.0.0


class Command(NoArgsCommand):
  """Creates file system for testing."""
  def handle_noargs(self, **options):
    remote_fs = cluster.get_hdfs()
    if hasattr(remote_fs, "setuser"):
      remote_fs.setuser(remote_fs.DEFAULT_USER)
    LOG.info("Using remote fs: %s" % str(remote_fs))

    # Create remote data directory if needed
    remote_data_dir = Submission.create_data_dir(remote_fs)

    # Copy over examples/
    for dirname in ("examples",):
      local_dir = os.path.join(jobsub.conf.LOCAL_DATA_DIR.get(), dirname)
      remote_dir = posixpath.join(remote_data_dir, dirname)
      copy_dir(local_dir, remote_fs, remote_dir)

    # Copy over sample_data/
    copy_dir(jobsub.conf.SAMPLE_DATA_DIR.get(),
      remote_fs,
      posixpath.join(remote_data_dir, "sample_data"))

    # Write out the models too
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "example_data.xml")
    examples = django.core.serializers.deserialize("xml", open(fixture_path))
    sample_user = None
    sample_oozie_designs = []
    sample_oozie_abstract_actions = {}      # pk -> object
    sample_oozie_concrete_actions = {}      # oozieaction_ptr_id -> object

    for example in examples:
      if isinstance(example.object, User):
        sample_user = example
      elif isinstance(example.object, jobsub.models.OozieDesign):
        sample_oozie_designs.append(example)
      elif type(example.object) in (jobsub.models.OozieMapreduceAction,
                                    jobsub.models.OozieJavaAction,
                                    jobsub.models.OozieStreamingAction):
        key = example.object.oozieaction_ptr_id
        sample_oozie_concrete_actions[key] = example
      elif type(example.object) is jobsub.models.OozieAction:
        key = example.object.pk
        sample_oozie_abstract_actions[key] = example
      else:
        raise Exception(_("Unexpected fixture type."))

    if sample_user is None:
      raise Exception(_("Expected sample user fixture."))

    # Create the sample user if it doesn't exist
    USERNAME = 'sample'
    try:
      sample_user.object = User.objects.get(username=USERNAME)
    except User.DoesNotExist:
      sample_user.object = User.objects.create(username=USERNAME, password='!', is_active=False, is_superuser=False, id=1100713, pk=1100713)

    # Create the designs
    for d in sample_oozie_designs:
      #
      # OozieDesign          ----many-to-one--->  OozieAction
      #
      # OozieMapreduceAction -----one-to-one--->  OozieAction
      # OozieStreamingAction -----one-to-one--->  OozieAction
      # OozieJavaAction      -----one-to-one--->  OozieAction
      #
      # We find the OozieAction pk and link everything back together
      #
      abstract_action_id = d.object.root_action_id
      abstract_action = sample_oozie_abstract_actions[abstract_action_id]
      concrete_action = sample_oozie_concrete_actions[str(abstract_action_id)]

      concrete_action.object.action_type = abstract_action.object.action_type
      concrete_action.object.pk = None
      concrete_action.object.id = None
      concrete_action.object.save()

      d.object.id = None
      d.object.pk = None
      d.object.owner_id = sample_user.object.id
      d.object.root_action = concrete_action.object
      d.object.save()

    # Upon success, write to the database
    try:
      entry = jobsub.models.CheckForSetup.objects.get(id=1)
    except jobsub.models.CheckForSetup.DoesNotExist:
      entry = jobsub.models.CheckForSetup(id=1)
    entry.setup_run = True
    entry.setup_level = JOBSUB_SETUP_LEVEL
    entry.save()

  def has_been_setup(self):
    """
    Returns true if we think job sub examples have been setup.
    """
    try:
      entry = jobsub.models.CheckForSetup.objects.get(id=1)
    except jobsub.models.CheckForSetup.DoesNotExist:
      return False
    return entry.setup_run and entry.setup_level >= JOBSUB_SETUP_LEVEL


def copy_dir(local_dir, remote_fs, remote_dir):
  # Hadoop mkdir is always recursive.
  remote_fs.mkdir(remote_dir)
  for f in os.listdir(local_dir):
    local_src = os.path.join(local_dir, f)
    remote_dst = posixpath.join(remote_dir, f)
    copy_file(local_src, remote_fs, remote_dst)


CHUNK_SIZE = 65536

def copy_file(local_src, remote_fs, remote_dst):
  if remote_fs.exists(remote_dst):
    LOG.info("%s already exists.  Skipping." % remote_dst)
    return
  else:
    LOG.info("%s does not exist. trying to copy" % remote_dst)

  if os.path.isfile(local_src):
    src = file(local_src)
    try:
      dst = remote_fs.open(remote_dst, "w")
      try:
        shutil.copyfileobj(src, dst, CHUNK_SIZE)
        LOG.info("Copied %s -> %s" % (local_src, remote_dst))
      finally:
        dst.close()
    finally:
      src.close()
  else:
    LOG.info("Skipping %s (not a file)" % local_src)
