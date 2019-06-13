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
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import ugettext as _

from desktop.conf import USE_NEW_EDITOR
from desktop.models import Directory, Document, Document2, Document2Permission
from hadoop import cluster
from liboozie.submittion import create_directories
from notebook.models import make_notebook

from useradmin.models import get_default_user_group, install_sample_user

from oozie.conf import LOCAL_SAMPLE_DATA_DIR, LOCAL_SAMPLE_DIR, REMOTE_SAMPLE_DIR, ENABLE_V2
from oozie.models import Workflow, Coordinator, Bundle
from oozie.importlib.workflows import import_workflow_root
from oozie.importlib.coordinators import import_coordinator_root
from oozie.importlib.bundles import import_bundle_root


LOG = logging.getLogger(__name__)


class Command(BaseCommand):

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


  def _install_mapreduce_example(self):
    doc2 = None
    name = _('MapReduce Sleep Job')

    if Document2.objects.filter(owner=self.user, name=name, type='query-mapreduce', is_history=False).exists():
      LOG.info("Sample mapreduce editor job already installed.")
      doc2 = Document2.objects.get(owner=self.user, name=name, type='query-mapreduce', is_history=False)
    else:
      snippet_properties = {
        'app_jar': '/user/hue/oozie/workspaces/lib/hadoop-examples.jar',
        'hadoopProperties': ['mapred.mapper.class=org.apache.hadoop.examples.SleepJob',
          'mapred.reducer.class=org.apache.hadoop.examples.SleepJob',
          'mapred.mapoutput.key.class=org.apache.hadoop.io.IntWritable',
          'mapred.mapoutput.value.class=org.apache.hadoop.io.NullWritable',
          'mapred.output.format.class=org.apache.hadoop.mapred.lib.NullOutputFormat',
          'mapred.input.format.class=org.apache.hadoop.examples.SleepJob$SleepInputFormat',
          'mapred.partitioner.class=org.apache.hadoop.examples.SleepJob',
          'sleep.job.map.sleep.time=5', 'sleep.job.reduce.sleep.time=10'],
        'archives': [],
        'jars': []
      }

      notebook = make_notebook(
        name=name,
        description=_('Sleep: Example MapReduce job'),
        editor_type='mapreduce',
        statement='',
        status='ready',
        snippet_properties=snippet_properties,
        is_saved=True
      )

      # Remove files, functions, settings from snippet properties
      data = notebook.get_data()
      data['snippets'][0]['properties'].pop('functions')
      data['snippets'][0]['properties'].pop('settings')

      try:
        with transaction.atomic():
          doc2 = Document2.objects.create(
            owner=self.user,
            name=data['name'],
            type='query-mapreduce',
            description=data['description'],
            data=json.dumps(data)
          )
      except Exception, e:
        LOG.exception("Failed to create sample mapreduce job document: %s" % e)
        # Just to be sure we delete Doc2 object incase of exception.
        # Possible when there are mixed InnoDB and MyISAM tables
        if doc2 and Document2.objects.filter(id=doc2.id).exists():
          doc2.delete()

    return doc2

  def _install_java_example(self):
    doc2 = None
    name = _('Java TeraGen Job')

    if Document2.objects.filter(owner=self.user, name=name, type='query-java', is_history=False).exists():
      LOG.info("Sample Java editor job already installed.")
      doc2 = Document2.objects.get(owner=self.user, name=name, type='query-java', is_history=False)
    else:
      snippet_properties = {
        'app_jar': '/user/hue/oozie/workspaces/lib/hadoop-examples.jar',
        'class': 'org.apache.hadoop.examples.terasort.TeraGen',
        'java_opts': '',
        'hadoopProperties': [],
        'archives': [],
        'files': [],
        'arguments': ['10000', 'output_dir/teragen'],
        'capture_output': False
      }

      notebook = make_notebook(
        name=name,
        description=_('TeraGen: Generates N rows of random data to a directory.'),
        editor_type='java',
        statement='',
        status='ready',
        snippet_properties=snippet_properties,
        is_saved=True
      )

      # Remove files, functions, settings from snippet properties
      data = notebook.get_data()
      data['snippets'][0]['properties'].pop('functions')
      data['snippets'][0]['properties'].pop('settings')

      try:
        with transaction.atomic():
          doc2 = Document2.objects.create(
            owner=self.user,
            name=data['name'],
            type='query-java',
            description=data['description'],
            data=json.dumps(data)
          )
      except Exception, e:
        LOG.exception("Failed to create sample Java job document: %s" % e)
        # Just to be sure we delete Doc2 object incase of exception.
        # Possible when there are mixed InnoDB and MyISAM tables
        if doc2 and Document2.objects.filter(id=doc2.id).exists():
          doc2.delete()

    return doc2

  def _install_spark_example(self):
    doc2 = None
    name = _('Spark File Copy Job')

    if Document2.objects.filter(owner=self.user, name=name, type='query-spark2', is_history=False).exists():
      LOG.info("Sample Spark editor job already installed.")
      doc2 = Document2.objects.get(owner=self.user, name=name, type='query-spark2', is_history=False)
    else:
      snippet_properties = {
        'jars': ['/user/hue/oozie/workspaces/workflows/spark-scala/lib/oozie-examples.jar'],
        'class': 'org.apache.oozie.example.SparkFileCopy',
        'app_name': '',
        'spark_opts': [],
        'spark_arguments': [
          "/user/hue/oozie/workspaces/data/sonnets.txt",
          "sonnets"
        ],
        'files': []
      }

      notebook = make_notebook(
        name=name,
        description=_('File Copy: Example Spark job'),
        editor_type='spark2',
        statement='',
        status='ready',
        snippet_properties=snippet_properties,
        is_saved=True
      )

      # Remove files, functions, settings from snippet properties
      data = notebook.get_data()
      data['snippets'][0]['properties'].pop('functions')
      data['snippets'][0]['properties'].pop('settings')

      try:
        with transaction.atomic():
          doc2 = Document2.objects.create(
            owner=self.user,
            name=data['name'],
            type='query-spark2',
            description=data['description'],
            data=json.dumps(data)
          )
      except Exception, e:
        LOG.exception("Failed to create sample Spark job document: %s" % e)
        # Just to be sure we delete Doc2 object incase of exception.
        # Possible when there are mixed InnoDB and MyISAM tables
        if doc2 and Document2.objects.filter(id=doc2.id).exists():
          doc2.delete()

    return doc2


  def _install_pyspark_example(self):
    doc2 = None
    name = _('PySpark Pi Estimator Job')

    if Document2.objects.filter(owner=self.user, name=name, type='query-spark2', is_history=False).exists():
      LOG.info("Sample pyspark editor job already installed.")
      doc2 = Document2.objects.get(owner=self.user, name=name, type='query-spark2', is_history=False)
    else:
      snippet_properties = {
        'jars': ['/user/hue/oozie/workspaces/lib/pi.py'],
        'class': '',
        'app_name': '',
        'spark_opts': [],
        'spark_arguments': [],
        'files': []
      }

      notebook = make_notebook(
        name=name,
        description=_('Pi Estimator: Example PySpark job'),
        editor_type='spark2',
        statement='',
        status='ready',
        snippet_properties=snippet_properties,
        is_saved=True
      )

      # Remove files, functions, settings from snippet properties
      data = notebook.get_data()
      data['snippets'][0]['properties'].pop('functions')
      data['snippets'][0]['properties'].pop('settings')

      try:
        with transaction.atomic():
          doc2 = Document2.objects.create(
            owner=self.user,
            name=data['name'],
            type='query-spark2',
            description=data['description'],
            data=json.dumps(data)
          )
      except Exception, e:
        LOG.exception("Failed to create sample PySpark job document: %s" % e)
        # Just to be sure we delete Doc2 object incase of exception.
        # Possible when there are mixed InnoDB and MyISAM tables
        if doc2 and Document2.objects.filter(id=doc2.id).exists():
          doc2.delete()

    return doc2

  def install_examples(self):
    data_dir = LOCAL_SAMPLE_DIR.get()

    unmanaged_dir = os.path.join(data_dir, 'unmanaged')
    self._import_workflows(unmanaged_dir, managed=False)


  def handle(self, *args, **options):
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
      self.fs.do_as_user(self.user.username, self.fs.copyFromLocal, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = LOCAL_SAMPLE_DATA_DIR.get()
    remote_data_dir = self.fs.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    self.fs.do_as_user(self.user.username, self.fs.copyFromLocal, local_dir, remote_data_dir)

    # Get or create sample user directories
    home_dir = Directory.objects.get_home_directory(self.user)
    examples_dir, created = Directory.objects.get_or_create(
      parent_directory=home_dir,
      owner=self.user,
      name=Document2.EXAMPLES_DIR
    )

    # Load jobs
    LOG.info(_("Installing examples..."))

    if ENABLE_V2.get():
      with transaction.atomic():
        management.call_command('loaddata', 'initial_oozie_examples.json', verbosity=2, commit=False)

    # Install editor oozie examples without doc1 link
    LOG.info("Using Hue 4, will install oozie editor samples.")

    example_jobs = []
    example_jobs.append(self._install_mapreduce_example())
    example_jobs.append(self._install_java_example())
    example_jobs.append(self._install_spark_example())
    example_jobs.append(self._install_pyspark_example())

    # If documents exist but have been trashed, recover from Trash
    for doc in example_jobs:
      if doc is not None and doc.parent_directory != examples_dir:
        doc.parent_directory = examples_dir
        doc.save()

    # Share oozie examples with default group
    oozie_examples = Document2.objects.filter(
      type__in=['oozie-workflow2', 'oozie-coordinator2', 'oozie-bundle2'],
      owner=self.user,
      parent_directory=None
    )
    oozie_examples.update(parent_directory=examples_dir)
    examples_dir.share(self.user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
