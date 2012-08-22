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
import os
import posixpath

from django.core import management
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from hadoop import cluster
from hadoop.fs.hadoopfs import Hdfs

from oozie.conf import LOCAL_SAMPLE_DATA_DIR, LOCAL_SAMPLE_DIR, REMOTE_DEPLOYMENT_DIR, REMOTE_SAMPLE_DIR


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):
  def handle_noargs(self, **options):
    fs = cluster.get_hdfs()
    remote_dir = create_data_dir(fs)

    # Copy examples binaries
    for name in os.listdir(LOCAL_SAMPLE_DIR.get()):
      local_dir = posixpath.join(LOCAL_SAMPLE_DIR.get(), name)
      remote_data_dir = posixpath.join(remote_dir, name)
      LOG.info(_('Copying examples %(local_dir)s to %(remote_data_dir)s\n') % {
                  'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
      copy_dir(fs, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = LOCAL_SAMPLE_DATA_DIR.get()
    remote_data_dir = posixpath.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    copy_dir(fs, local_dir, remote_data_dir)

    # Load jobs
    management.call_command('loaddata', 'apps/oozie/src/oozie/fixtures/initial_data.json', verbosity=2)



# This should probably be refactored and some parts moved to the HDFS lib. Jobsub could be updated to.

def copy_dir(fs, local_dir, remote_dir, mode=0755):
  fs.do_as_user(fs.DEFAULT_USER, fs.mkdir, remote_dir, mode=mode)

  for f in os.listdir(local_dir):
    local_src = os.path.join(local_dir, f)
    remote_dst = posixpath.join(remote_dir, f)
    print f, local_src, remote_dst
    if os.path.isdir(remote_dst):
      copy_dir(fs, local_src, remote_dst, mode)
    else:
      copy_file(fs, local_src, remote_dst)


CHUNK_SIZE = 1024 * 1024

def copy_file(fs, local_src, remote_dst):
  if fs.exists(remote_dst):
    LOG.info(_('%(remote_dst)s already exists.  Skipping.') % {'remote_dst': remote_dst})
    return
  else:
    LOG.info(_('%(remote_dst)s does not exist. Trying to copy') % {'remote_dst': remote_dst})

  if os.path.isfile(local_src):
    src = file(local_src)
    try:
      try:
        fs.do_as_user(fs.DEFAULT_USER, fs.create, remote_dst, permission=01755)
        chunk = src.read(CHUNK_SIZE)
        while chunk:
          fs.do_as_user(fs.DEFAULT_USER, fs.append, remote_dst, chunk)
          chunk = src.read(CHUNK_SIZE)
        LOG.info(_('Copied %s -> %s') % (local_src, remote_dst))
      except:
        LOG.error(_('Copying %s -> %s failed') % (local_src, remote_dst))
        raise
    finally:
      src.close()
  else:
    LOG.info(_('Skipping %s (not a file)') % local_src)


def create_data_dir(fs):
  # If needed, create the remote home, deployment and data directories
  directories = (REMOTE_DEPLOYMENT_DIR.get(), REMOTE_SAMPLE_DIR.get())
  user = fs.user

  try:
    fs.setuser(fs.DEFAULT_USER)
    for directory in directories:
      if not fs.exists(directory):
        remote_home_dir = Hdfs.join('/user', fs.user)
        if directory.startswith(remote_home_dir):
          # Home is 755
          fs.create_home_dir(remote_home_dir)
        # Shared by all the users
        fs.mkdir(directory, 01777)
        fs.chmod(directory, 01777) # To remove after https://issues.apache.org/jira/browse/HDFS-3491
  finally:
    fs.setuser(user)

  return REMOTE_SAMPLE_DIR.get()
