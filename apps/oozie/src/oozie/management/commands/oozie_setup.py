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
from lxml import etree

from django.core import management
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from hadoop import cluster

from desktop.conf import USE_NEW_EDITOR
from desktop.models import Directory, Document, Document2, Document2Permission
from liboozie.submittion import create_directories
from oozie.conf import LOCAL_SAMPLE_DATA_DIR, LOCAL_SAMPLE_DIR, REMOTE_SAMPLE_DIR, ENABLE_V2
from oozie.models import Workflow, Coordinator, Bundle
from oozie.importlib.workflows import import_workflow_root
from oozie.importlib.coordinators import import_coordinator_root
from oozie.importlib.bundles import import_bundle_root
from useradmin.models import get_default_user_group, install_sample_user


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):

  def _import_workflows(self, directory, managed=True):

    for example_directory_name in os.listdir(directory):
      if os.path.isdir(os.path.join(directory, example_directory_name)):
        with open(os.path.join(directory, example_directory_name, 'workflow.zip')) as fp:
          workflow_xml, metadata = Workflow.decompress(fp)

        workflow_root = etree.fromstring(workflow_xml)

        try:
          Workflow.objects.get(name=workflow_root.get('name'), managed=managed)
        except Workflow.DoesNotExist:
          LOG.info(_("Installing workflow %s") % workflow_root.get('name'))
          LOG.debug("Workflow definition:\n%s" % workflow_xml)
          workflow = Workflow.objects.new_workflow(owner=self.user)
          workflow.is_shared = True
          workflow.managed = managed
          workflow.name = workflow_root.get('name')
          workflow.save()
          Workflow.objects.initialize(workflow)
          import_workflow_root(workflow=workflow, workflow_definition_root=workflow_root, metadata=metadata, fs=self.fs)
          workflow.doc.all().delete() # Delete doc as it messes up the example sharing

  def _import_coordinators(self, directory):

    for example_directory_name in os.listdir(directory):
      if os.path.isdir(os.path.join(directory, example_directory_name)):
        with open(os.path.join(directory, example_directory_name, 'coordinator.zip')) as fp:
          coordinator_xml, metadata = Coordinator.decompress(fp)

        coordinator_root = etree.fromstring(coordinator_xml)

        try:
          Coordinator.objects.get(name=coordinator_root.get('name'))
        except Coordinator.DoesNotExist:
          LOG.info(_("Installing coordinator %s") % coordinator_root.get('name'))
          LOG.debug("Coordinator definition:\n%s" % coordinator_xml)
          coordinator = Coordinator(owner=self.user, is_shared=True)
          coordinator.name = coordinator_root.get('name')
          coordinator.save()
          import_coordinator_root(coordinator=coordinator, coordinator_definition_root=coordinator_root, metadata=metadata)

  def _import_bundles(self, directory):

    for example_directory_name in os.listdir(directory):

      if os.path.isdir(os.path.join(directory, example_directory_name)):
        with open(os.path.join(directory, example_directory_name, 'bundle.zip')) as fp:
          bundle_xml, metadata = Bundle.decompress(fp)

        bundle_root = etree.fromstring(bundle_xml)

        try:
          Bundle.objects.get(name=bundle_root.get('name'))
        except Bundle.DoesNotExist:
          LOG.info(_("Installing bundle %s") % bundle_root.get('name'))
          LOG.debug("Bundle definition:\n%s" % bundle_xml)
          bundle = Bundle(owner=self.user, is_shared=True)
          bundle.name = bundle_root.get('name')
          bundle.save()
          import_bundle_root(bundle=bundle, bundle_definition_root=bundle_root, metadata=metadata)

  def install_examples(self):
    data_dir = LOCAL_SAMPLE_DIR.get()

    unmanaged_dir = os.path.join(data_dir, 'unmanaged')
    self._import_workflows(unmanaged_dir, managed=False)

  def handle_noargs(self, **options):
    self.user = install_sample_user()
    self.fs = cluster.get_hdfs()

    LOG.info(_("Creating sample directory '%s' in HDFS") % REMOTE_SAMPLE_DIR.get())
    create_directories(self.fs, [REMOTE_SAMPLE_DIR.get()])
    remote_dir = REMOTE_SAMPLE_DIR.get()

    # Copy examples binaries
    for name in os.listdir(LOCAL_SAMPLE_DIR.get()):
      local_dir = self.fs.join(LOCAL_SAMPLE_DIR.get(), name)
      remote_data_dir = self.fs.join(remote_dir, name)
      LOG.info(_('Copying examples %(local_dir)s to %(remote_data_dir)s\n') % {
                  'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
      self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.copyFromLocal, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = LOCAL_SAMPLE_DATA_DIR.get()
    remote_data_dir = self.fs.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.copyFromLocal, local_dir, remote_data_dir)

    # Load jobs
    LOG.info(_("Installing examples..."))

    if ENABLE_V2.get():
      management.call_command('loaddata', 'initial_oozie_examples.json', verbosity=2)

    # Get or create sample user directories
    home_dir = Directory.objects.get_home_directory(self.user)
    examples_dir, created = Directory.objects.get_or_create(
      parent_directory=home_dir,
      owner=self.user,
      name=Document2.EXAMPLES_DIR
    )

    if USE_NEW_EDITOR.get():
      docs = Document.objects.get_docs(self.user, Workflow).filter(owner=self.user)
      for doc in docs:
        if doc.content_object:
          data = doc.content_object.data_dict
          data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
          data = json.dumps(data)

          doc2 = Document2.objects.create(
            owner=self.user,
            parent_directory=examples_dir,
            name=doc.name,
            type='link-workflow',
            description=doc.description,
            data=data)

          LOG.info('Successfully installed sample link to jobsub: %s' % (doc2.name,))

    # Share oozie examples with default group
    oozie_examples = Document2.objects.filter(
      type__in=['oozie-workflow2', 'oozie-coordinator2', 'oozie-bundle2'],
      owner=self.user,
      parent_directory=None
    )
    oozie_examples.update(parent_directory=examples_dir)
    examples_dir.share(self.user, Document2Permission.READ_PERM, groups=[get_default_user_group()])

    self.install_examples()

    Document.objects.sync()
