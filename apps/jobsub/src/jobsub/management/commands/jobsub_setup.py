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
import hadoop.conf
import jobsub.conf

class Command(NoArgsCommand):
  """Creates file system for testing."""
  def handle_noargs(self, **options):
    remote_fs = cluster.get_hdfs()
    if hasattr(remote_fs, "setuser"):
      remote_fs.setuser("hue", ["supergroup"])
    logging.info("Using remote fs: %s" % str(remote_fs))

    # Copy over examples/ and script_templates/ directories
    for dirname in ("examples", "script_templates"):
      local_dir = os.path.join(jobsub.conf.LOCAL_DATA_DIR.get(), dirname)
      remote_dir = posixpath.join(jobsub.conf.REMOTE_DATA_DIR.get(), dirname)
      copy_dir(local_dir, remote_fs, remote_dir)

    # Copy over sample data
    copy_dir(jobsub.conf.SAMPLE_DATA_DIR.get(),
      remote_fs,
      posixpath.join(jobsub.conf.REMOTE_DATA_DIR.get(), "sample_data"))

    # Also copy over Hadoop examples and streaming jars
    local_src = hadoop.conf.HADOOP_EXAMPLES_JAR.get()
    if local_src is None:
      raise Exception('Failed to locate the Hadoop example jar')
    remote_dst = posixpath.join(jobsub.conf.REMOTE_DATA_DIR.get(), "examples", "hadoop-examples.jar")
    copy_file(local_src, remote_fs, remote_dst)

    # Write out the models too
    fixture_path = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "example_data.xml")
    examples = django.core.serializers.deserialize("xml", open(fixture_path))
    sample_user = None
    sample_job_designs = []
    for example in examples:
      if isinstance(example.object, User):
        sample_user = example
      elif isinstance(example.object, jobsub.models.JobDesign):
        sample_job_designs.append(example)
      else:
        raise Exception("Unexpected fixture type.")
    if sample_user is None:
      raise Exception("Expected sample user fixture.")
    # Create the sample user if it doesn't exist
    try:
      sample_user.object = User.objects.get(username=sample_user.object.username)
    except User.DoesNotExist:
      sample_user.object.pk = None
      sample_user.object.id = None
      sample_user.save()
    for j in sample_job_designs:
      j.object.id = None
      j.object.pk = None
      j.object.owner_id = sample_user.object.id
      j.save()

    # Upon success, write to the database
    try:
      entry = jobsub.models.CheckForSetup.objects.get(id=1)
    except jobsub.models.CheckForSetup.DoesNotExist:
      entry = jobsub.models.CheckForSetup(id=1)
    entry.setup_run = True
    entry.save()

  def has_been_setup(self):
    """
    Returns true if we think job sub examples have been setup.
    """
    try:
      entry = jobsub.models.CheckForSetup.objects.get(id=1)
    except jobsub.models.CheckForSetup.DoesNotExist:
      return False
    return entry.setup_run

def copy_dir(local_dir, remote_fs, remote_dir):
  # Hadoop mkdir is always recursive.
  remote_fs.mkdir(remote_dir)
  for f in os.listdir(local_dir):
    local_src = os.path.join(local_dir, f)
    remote_dst = posixpath.join(remote_dir, f)
    copy_file(local_src, remote_fs, remote_dst)

def copy_file(local_src, remote_fs, remote_dst):
  if remote_fs.exists(remote_dst):
    logging.info("%s already exists.  Skipping." % remote_dst)
    return
    
  if os.path.isfile(local_src):
    src = file(local_src)
    try:
      dst = remote_fs.open(remote_dst, "w")
      try:
        shutil.copyfileobj(src, dst)
        logging.info("Copied %s -> %s" % (local_src, remote_dst))
      finally:
        dst.close()
    finally:
      src.close()
  else:
    logging.info("Skipping %s (not a file)" % local_src)
