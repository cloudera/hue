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
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import ugettext as _

from desktop.conf import USE_NEW_EDITOR
from desktop.lib import paths
from desktop.models import Directory, Document, Document2, Document2Permission
from hadoop import cluster
from liboozie.submittion import create_directories
from notebook.models import make_notebook

from useradmin.models import get_default_user_group, install_sample_user

from pig.conf import LOCAL_SAMPLE_DIR, REMOTE_SAMPLE_DIR


LOG = logging.getLogger(__name__)


class Command(BaseCommand):

  def install_pig_script(self, sample_user):
    doc2 = None
    name = _('UpperText')

    if Document2.objects.filter(owner=sample_user, name=name, type='query-pig', is_history=False).exists():
      LOG.info("Sample pig editor script already installed.")
      doc2 = Document2.objects.get(owner=sample_user, name=name, type='query-pig', is_history=False)
    else:
      statement = """REGISTER hdfs://{}/piggybank.jar;

data = LOAD '{}/data/midsummer.txt' as (text:CHARARRAY);

upper_case = FOREACH data GENERATE org.apache.pig.piggybank.evaluation.string.UPPER(text);

STORE upper_case INTO '$output';
""".format(REMOTE_SAMPLE_DIR.get(), REMOTE_SAMPLE_DIR.get())
      snippet_properties = {
        'hadoopProperties': [],
        'parameters': [],
        'resources': []
      }

      notebook = make_notebook(
        name=name,
        description=_('UpperText: Example Pig script'),
        editor_type='pig',
        statement=statement,
        status='ready',
        snippet_properties=snippet_properties,
        is_saved=True
      )

      # Remove files, functions, settings from snippet properties
      data = notebook.get_data()
      data['snippets'][0]['properties'].pop('files')
      data['snippets'][0]['properties'].pop('functions')
      data['snippets'][0]['properties'].pop('settings')

      try:
        with transaction.atomic():
          doc2 = Document2.objects.create(
            owner=sample_user,
            name=data['name'],
            type='query-pig',
            description=data['description'],
            data=json.dumps(data)
          )
      except Exception, e:
        LOG.exception("Failed to create sample pig script document: %s" % e)
        # Just to be sure we delete Doc2 object incase of exception.
        # Possible when there are mixed InnoDB and MyISAM tables
        if doc2 and Document2.objects.filter(id=doc2.id).exists():
          doc2.delete()

    return doc2


  def handle(self, *args, **options):
    fs = cluster.get_hdfs()
    create_directories(fs, [REMOTE_SAMPLE_DIR.get()])
    remote_dir = REMOTE_SAMPLE_DIR.get()
    sample_user = install_sample_user()

    # Copy examples binaries
    for name in os.listdir(LOCAL_SAMPLE_DIR.get()):
      local_dir = fs.join(LOCAL_SAMPLE_DIR.get(), name)
      remote_data_dir = fs.join(remote_dir, name)
      LOG.info(_('Copying examples %(local_dir)s to %(remote_data_dir)s\n') % {
                  'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
      fs.do_as_user(sample_user.username, fs.copyFromLocal, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = paths.get_thirdparty_root("sample_data")
    remote_data_dir = fs.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    fs.do_as_user(sample_user.username, fs.copyFromLocal, local_dir, remote_data_dir)

    # Initialize doc2, whether editor script or link
    doc2 = None

    # Install editor pig script without doc1 link
    LOG.info("Using Hue 4, will install pig editor sample.")
    doc2 = self.install_pig_script(sample_user)

    if USE_NEW_EDITOR.get():
      # Get or create sample user directories
      LOG.info("Creating sample user directories.")

      home_dir = Directory.objects.get_home_directory(sample_user)
      examples_dir, created = Directory.objects.get_or_create(
        parent_directory=home_dir,
        owner=sample_user,
        name=Document2.EXAMPLES_DIR)

      # If document exists but has been trashed, recover from Trash
      if doc2 and doc2.parent_directory != examples_dir:
        doc2.parent_directory = examples_dir
        doc2.save()

      # Share with default group
      examples_dir.share(sample_user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
