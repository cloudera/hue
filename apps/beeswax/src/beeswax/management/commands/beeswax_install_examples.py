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

from builtins import object
import logging
import os
import pwd
import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import USE_NEW_EDITOR
from desktop.models import Directory, Document, Document2, Document2Permission
from hadoop import cluster
from notebook.models import import_saved_beeswax_query
from useradmin.models import get_default_user_group, install_sample_user

import beeswax.conf
from beeswax.models import SavedQuery, HQL, IMPALA
from beeswax.design import hql_query
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config, QueryServerException


LOG = logging.getLogger(__name__)


class InstallException(Exception):
  pass


class Command(BaseCommand):
  args = '<beeswax|impala> <db_name>'
  help = 'Install examples but do not overwrite them.'

  def handle(self, *args, **options):
    if args:
      app_name = args[0]
      db_name = args[1] if len(args) > 1 else 'default'
      user = User.objects.get(username=pwd.getpwuid(os.getuid()).pw_name)
    else:
      app_name = options['app_name']
      db_name = options.get('db_name', 'default')
      user = options['user']

    tables = options['tables'] if 'tables' in options else 'tables.json'

    exception = None

    # Documents will belong to this user but we run the install as the current user
    try:
      sample_user = install_sample_user()
      self._install_queries(sample_user, app_name)
      self._install_tables(user, app_name, db_name, tables)
    except Exception as ex:
      exception = ex

    Document.objects.sync()

    if exception is not None:
      pretty_msg = None
      
      if "AlreadyExistsException" in exception.message:
        pretty_msg = _("SQL table examples already installed.")
      if "Permission denied" in exception.message:
        pretty_msg = _("Permission denied. Please check with your system administrator.")

      if pretty_msg is not None:
        raise PopupException(pretty_msg)
      else: 
        raise exception

  def _install_tables(self, django_user, app_name, db_name, tables):
    data_dir = beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get()
    table_file = file(os.path.join(data_dir, tables))
    table_list = json.load(table_file)
    table_file.close()

    for table_dict in table_list:
      table = SampleTable(table_dict, app_name, db_name)
      try:
        table.install(django_user)
      except Exception as ex:
        raise InstallException(_('Could not install table: %s') % ex)

  def _install_queries(self, django_user, app_name):
    design_file = file(os.path.join(beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get(), 'designs.json'))
    design_list = json.load(design_file)
    design_file.close()

    # Filter design list to app-specific designs
    app_type = HQL if app_name == 'beeswax' else IMPALA
    design_list = [d for d in design_list if int(d['type']) == app_type]

    for design_dict in design_list:
      design = SampleQuery(design_dict)
      try:
        design.install(django_user)
      except Exception as ex:
        raise InstallException(_('Could not install query: %s') % ex)


class SampleTable(object):
  """
  Represents a table loaded from the tables.json file
  """
  def __init__(self, data_dict, app_name, db_name='default'):
    self.name = data_dict['table_name']
    if 'partition_files' in data_dict:
      self.partition_files = data_dict['partition_files']
    else:
      self.partition_files = None
      self.filename = data_dict['data_file']
    self.hql = data_dict['create_hql']
    self.query_server = get_query_server_config(app_name)
    self.app_name = app_name
    self.db_name = db_name

    # Sanity check
    self._data_dir = beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get()
    if self.partition_files:
      for partition_spec, filename in list(self.partition_files.items()):
        filepath = os.path.join(self._data_dir, filename)
        self.partition_files[partition_spec] = filepath
        self._check_file_contents(filepath)
    else:
      self._contents_file = os.path.join(self._data_dir, self.filename)
      self._check_file_contents(self._contents_file)


  def install(self, django_user):
    if self.create(django_user):
      if self.partition_files:
        for partition_spec, filepath in list(self.partition_files.items()):
          self.load_partition(django_user, partition_spec, filepath)
      else:
        self.load(django_user)

  def create(self, django_user):
    """
    Create table in the Hive Metastore.
    """
    LOG.info('Creating table "%s"' % (self.name,))
    db = dbms.get(django_user, self.query_server)

    try:
      # Already exists?
      if self.app_name == 'impala':
        db.invalidate(database=self.db_name, flush_all=False)
      db.get_table(self.db_name, self.name)
      msg = _('Table "%(table)s" already exists.') % {'table': self.name}
      LOG.error(msg)
      return False
    except Exception:
      query = hql_query(self.hql)
      try:
        db.use(self.db_name)
        results = db.execute_and_wait(query)
        if not results:
          msg = _('Error creating table %(table)s: Operation timeout.') % {'table': self.name}
          LOG.error(msg)
          raise InstallException(msg)
        return True
      except Exception as ex:
        msg = _('Error creating table %(table)s: %(error)s.') % {'table': self.name, 'error': ex}
        LOG.error(msg)
        raise InstallException(msg)

  def load_partition(self, django_user, partition_spec, filepath):
    """
    Upload data found at filepath to HDFS home of user, the load intto a specific partition
    """
    LOAD_PARTITION_HQL = \
      """
      ALTER TABLE %(tablename)s ADD PARTITION(%(partition_spec)s) LOCATION '%(filepath)s'
      """

    partition_dir = self._get_partition_dir(partition_spec)
    hdfs_root_destination = self._get_hdfs_root_destination(django_user, subdir=partition_dir)
    filename = filepath.split('/')[-1]
    hdfs_file_destination = self._upload_to_hdfs(django_user, filepath, hdfs_root_destination, filename)

    hql = LOAD_PARTITION_HQL % {'tablename': self.name, 'partition_spec': partition_spec, 'filepath': hdfs_root_destination}
    LOG.info('Running load query: %s' % hql)
    self._load_data_to_table(django_user, hql, hdfs_file_destination)


  def load(self, django_user):
    """
    Upload data to HDFS home of user then load (aka move) it into the Hive table (in the Hive metastore in HDFS).
    """
    LOAD_HQL = \
      """
      LOAD DATA INPATH
      '%(filename)s' OVERWRITE INTO TABLE %(tablename)s
      """

    hdfs_root_destination = self._get_hdfs_root_destination(django_user)
    hdfs_file_destination = self._upload_to_hdfs(django_user, self._contents_file, hdfs_root_destination)

    hql = LOAD_HQL % {'tablename': self.name, 'filename': hdfs_file_destination}
    LOG.info('Running load query: %s' % hql)
    self._load_data_to_table(django_user, hql, hdfs_file_destination)


  def _check_file_contents(self, filepath):
    if not os.path.isfile(filepath):
      msg = _('Cannot find table data in "%(file)s".') % {'file': filepath}
      LOG.error(msg)
      raise ValueError(msg)


  def _get_partition_dir(self, partition_spec):
    parts = partition_spec.split(',')
    last_part = parts[-1]
    part_value = last_part.split('=')[-1]
    part_dir = part_value.strip("'").replace('-', '_')
    return part_dir


  def _get_hdfs_root_destination(self, django_user, subdir=None):
    fs = cluster.get_hdfs()

    if self.app_name == 'impala':
      # Because Impala does not have impersonation on by default, we use a public destination for the upload.
      from impala.conf import IMPERSONATION_ENABLED
      if not IMPERSONATION_ENABLED.get():
        tmp_public = '/tmp/public_hue_examples'
        if subdir:
          tmp_public += '/%s' % subdir
        fs.do_as_user(django_user, fs.mkdir, tmp_public, '0777')
        hdfs_root_destination = tmp_public
    else:
      hdfs_root_destination = fs.do_as_user(django_user, fs.get_home_dir)
      if subdir:
        hdfs_root_destination += '/%s' % subdir
        fs.do_as_user(django_user, fs.mkdir, hdfs_root_destination, '0777')

    return hdfs_root_destination


  def _upload_to_hdfs(self, django_user, local_filepath, hdfs_root_destination, filename=None):
    fs = cluster.get_hdfs()

    if filename is None:
      filename = self.name
    hdfs_destination = '%s/%s' % (hdfs_root_destination, filename)

    LOG.info('Uploading local data %s to HDFS path "%s"' % (self.name, hdfs_destination))
    fs.do_as_user(django_user, fs.copyFromLocal, local_filepath, hdfs_destination)

    return hdfs_destination


  def _load_data_to_table(self, django_user, hql, hdfs_destination):
    LOG.info('Loading data into table "%s"' % (self.name,))
    query = hql_query(hql)

    try:
      results = dbms.get(django_user, self.query_server).execute_and_wait(query)
      if not results:
        msg = _('Error loading table %(table)s: Operation timeout.') % {'table': self.name}
        LOG.error(msg)
        raise InstallException(msg)
    except QueryServerException as ex:
      msg = _('Error loading table %(table)s: %(error)s.') % {'table': self.name, 'error': ex}
      LOG.error(msg)
      raise InstallException(msg)


class SampleQuery(object):

  """Represents a query loaded from the designs.json file"""
  def __init__(self, data_dict):
    self.name = data_dict['name']
    self.desc = data_dict['desc']
    self.type = int(data_dict['type'])
    self.data = data_dict['data']


  def install(self, django_user):
    """
    Install queries. Raise InstallException on failure.
    """
    LOG.info('Installing sample query: %s' % (self.name,))

    try:
      # Don't overwrite
      query = SavedQuery.objects.get(owner=django_user, name=self.name, type=self.type)
    except SavedQuery.DoesNotExist:
      query = SavedQuery(owner=django_user, name=self.name, type=self.type, desc=self.desc)
      # The data field needs to be a string. The sample file writes it
      # as json (without encoding into a string) for readability.
      query.data = json.dumps(self.data)
      query.save()
      LOG.info('Successfully installed sample design: %s' % (self.name,))

    if USE_NEW_EDITOR.get():
      # Get or create sample user directories
      home_dir = Directory.objects.get_home_directory(django_user)
      examples_dir, created = Directory.objects.get_or_create(
        parent_directory=home_dir,
        owner=django_user,
        name=Document2.EXAMPLES_DIR
      )

      try:
        # Don't overwrite
        doc2 = Document2.objects.get(owner=django_user, name=self.name, type=self._document_type(self.type), is_history=False)
        # If document exists but has been trashed, recover from Trash
        if doc2.parent_directory != examples_dir:
          doc2.parent_directory = examples_dir
          doc2.save()
      except Document2.DoesNotExist:
        # Create document from saved query
        notebook = import_saved_beeswax_query(query)
        data = notebook.get_data()
        data['isSaved'] = True
        uuid = data.get('uuid')
        data = json.dumps(data)

        doc2 = Document2.objects.create(
          uuid=uuid,
          owner=django_user,
          parent_directory=examples_dir,
          name=self.name,
          type=self._document_type(self.type),
          description=self.desc,
          data=data
        )

      # Share with default group
      examples_dir.share(django_user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
      LOG.info('Successfully installed sample query: %s' % (self.name,))


  def _document_type(self, type):
    if type == HQL:
      return 'query-hive'
    elif type == IMPALA:
      return 'query-impala'
    else:
      return None
