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

from django.contrib.auth.models import User
from django.core import management
from django.core.management.base import NoArgsCommand
from django.db import transaction
from django.utils.translation import ugettext as _

from hadoop import cluster
from hadoop.fs.hadoopfs import Hdfs
from liboozie.conf import REMOTE_DEPLOYMENT_DIR

from oozie.conf import LOCAL_SAMPLE_DATA_DIR, LOCAL_SAMPLE_DIR, REMOTE_SAMPLE_DIR


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):
  def handle_noargs(self, **options):
    fs = cluster.get_hdfs()
    remote_dir = create_directories(fs)

    # Copy examples binaries
    for name in os.listdir(LOCAL_SAMPLE_DIR.get()):
      local_dir = fs.join(LOCAL_SAMPLE_DIR.get(), name)
      remote_data_dir = fs.join(remote_dir, name)
      LOG.info(_('Copying examples %(local_dir)s to %(remote_data_dir)s\n') % {
                  'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
      fs.do_as_user(fs.DEFAULT_USER, fs.copyFromLocal, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = LOCAL_SAMPLE_DATA_DIR.get()
    remote_data_dir = fs.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    fs.do_as_user(fs.DEFAULT_USER, fs.copyFromLocal, local_dir, remote_data_dir)

    # Load jobs
    USERNAME = 'sample'
    try:
      sample_user = User.objects.get(username=USERNAME)
    except User.DoesNotExist:
      sample_user = User.objects.create(username=USERNAME, password='!', is_active=False, is_superuser=False, id=1100713, pk=1100713)
    management.call_command('loaddata', 'initial_oozie_examples.json', verbosity=2)


def create_directories(fs):
  # If needed, create the remote home, deployment and data directories
  directories = (REMOTE_DEPLOYMENT_DIR.get(), REMOTE_SAMPLE_DIR.get())

  for directory in directories:
    if not fs.do_as_user(fs.DEFAULT_USER, fs.exists, directory):
      remote_home_dir = Hdfs.join('/user', fs.DEFAULT_USER)
      if directory.startswith(remote_home_dir):
        # Home is 755
        fs.do_as_user(fs.DEFAULT_USER, fs.create_home_dir, remote_home_dir)
      # Shared by all the users
      fs.do_as_user(fs.DEFAULT_USER, fs.mkdir, directory, 01777)
      fs.do_as_user(fs.DEFAULT_USER, fs.chmod, directory, 01777) # To remove after https://issues.apache.org/jira/browse/HDFS-3491

  return REMOTE_SAMPLE_DIR.get()
