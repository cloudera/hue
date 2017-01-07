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
import logging
import os

from django.core import management
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from hadoop import cluster

from desktop.conf import USE_NEW_EDITOR
from desktop.lib import paths
from desktop.models import Directory, Document, Document2, Document2Permission
from liboozie.submittion import create_directories
from pig.conf import LOCAL_SAMPLE_DIR, REMOTE_SAMPLE_DIR
from useradmin.models import get_default_user_group, install_sample_user

LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):

  def handle_noargs(self, **options):
    fs = cluster.get_hdfs()
    create_directories(fs, [REMOTE_SAMPLE_DIR.get()])
    remote_dir = REMOTE_SAMPLE_DIR.get()

    # Copy examples binaries
    for name in os.listdir(LOCAL_SAMPLE_DIR.get()):
      local_dir = fs.join(LOCAL_SAMPLE_DIR.get(), name)
      remote_data_dir = fs.join(remote_dir, name)
      LOG.info(_('Copying examples %(local_dir)s to %(remote_data_dir)s\n') % {
                  'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
      fs.do_as_user(fs.DEFAULT_USER, fs.copyFromLocal, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = paths.get_thirdparty_root("sample_data")
    remote_data_dir = fs.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    fs.do_as_user(fs.DEFAULT_USER, fs.copyFromLocal, local_dir, remote_data_dir)

    # Load jobs
    sample_user = install_sample_user()
    management.call_command('loaddata', 'initial_pig_examples.json', verbosity=2)
    Document.objects.sync()

    if USE_NEW_EDITOR.get():
      # Get or create sample user directories
      home_dir = Directory.objects.get_home_directory(sample_user)
      examples_dir, created = Directory.objects.get_or_create(
        parent_directory=home_dir,
        owner=sample_user,
        name=Document2.EXAMPLES_DIR)

      try:
        # Don't overwrite
        doc = Document.objects.get(object_id=1100713)
        doc2 = Document2.objects.get(owner=sample_user, name=doc.name, type='link-pigscript')
        # If document exists but has been trashed, recover from Trash
        if doc2.parent_directory != examples_dir:
          doc2.parent_directory = examples_dir
          doc2.save()
      except Document.DoesNotExist:
        LOG.warn('Sample pig script document not found.')
      except Document2.DoesNotExist:
        if doc.content_object:
          data = doc.content_object.dict
          data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
          data = json.dumps(data)

          doc2 = Document2.objects.create(
            owner=sample_user,
            parent_directory=examples_dir,
            name=doc.name,
            type='link-pigscript',
            description=doc.description,
            data=data)
          LOG.info('Successfully installed sample link to pig script: %s' % (doc2.name,))

      # Share with default group
      examples_dir.share(sample_user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
