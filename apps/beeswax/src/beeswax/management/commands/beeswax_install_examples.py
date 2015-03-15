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
import pwd
import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from hadoop import cluster

from desktop.lib.exceptions_renderable import PopupException
from useradmin.models import install_sample_user
from desktop.models import Document

import beeswax.conf

from beeswax.models import SavedQuery, IMPALA
from beeswax.design import hql_query
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config, QueryServerException


LOG = logging.getLogger(__name__)


class InstallException(Exception):
  pass


class Command(BaseCommand):
  args = '<beeswax|impala>'
  help = 'Install examples but do not overwrite them.'

  def handle(self, *args, **options):
    if args:
      app_name = args[0]
      user = User.objects.get(username=pwd.getpwuid(os.getuid()).pw_name)
    else:
      app_name = options['app_name']
      user = options['user']

    tables = options['tables'] if 'tables' in options else 'tables.json'

    exception = None

    # Documents will belong to this user but we run the install as the current user
    try:
      sample_user = install_sample_user()
      self._install_queries(sample_user, app_name)
      self._install_tables(user, app_name, tables)
    except Exception, ex:
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

  def _install_tables(self, django_user, app_name, tables):
    data_dir = beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get()
    table_file = file(os.path.join(data_dir, tables))
    table_list = json.load(table_file)
    table_file.close()

    for table_dict in table_list:
      table = SampleTable(table_dict, app_name)
      try:
        table.install(django_user)
      except Exception, ex:
        raise InstallException(_('Could not install table: %s') % ex)

  def _install_queries(self, django_user, app_name):
    design_file = file(os.path.join(beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get(), 'designs.json'))
    design_list = json.load(design_file)
    design_file.close()

    for design_dict in design_list:
      if app_name == 'impala':
        design_dict['type'] = IMPALA
      design = SampleDesign(design_dict)
      try:
        design.install(django_user)
      except Exception, ex:
        raise InstallException(_('Could not install query: %s') % ex)


class SampleTable(object):
  """
  Represents a table loaded from the tables.json file
  """
  def __init__(self, data_dict, app_name):
    self.name = data_dict['table_name']
    self.filename = data_dict['data_file']
    self.hql = data_dict['create_hql']
    self.query_server = get_query_server_config(app_name)
    self.app_name = app_name

    # Sanity check
    self._data_dir = beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get()
    self._contents_file = os.path.join(self._data_dir, self.filename)
    if not os.path.isfile(self._contents_file):
      msg = _('Cannot find table data in "%(file)s".') % {'file': self._contents_file}
      LOG.error(msg)
      raise ValueError(msg)

  def install(self, django_user):
    if self.create(django_user):
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
        db.invalidate_tables('default', [self.name])
      db.get_table('default', self.name)
      msg = _('Table "%(table)s" already exists.') % {'table': self.name}
      LOG.error(msg)
      return False
    except Exception:
      query = hql_query(self.hql)
      try:
        results = db.execute_and_wait(query)
        if not results:
          msg = _('Error creating table %(table)s: Operation timeout.') % {'table': self.name}
          LOG.error(msg)
          raise InstallException(msg)
        return True
      except Exception, ex:
        msg = _('Error creating table %(table)s: %(error)s.') % {'table': self.name, 'error': ex}
        LOG.error(msg)
        raise InstallException(msg)

  def load(self, django_user):
    """
    Upload data to HDFS home of user then load (aka move) it into the Hive table (in the Hive metastore in HDFS).
    """
    LOAD_HQL = \
      """
      LOAD DATA INPATH
      '%(filename)s' OVERWRITE INTO TABLE %(tablename)s
      """

    fs = cluster.get_hdfs()

    if self.app_name == 'impala':
      # Because Impala does not have impersonation on by default, we use a public destination for the upload.
      from impala.conf import IMPERSONATION_ENABLED
      if not IMPERSONATION_ENABLED.get():
        tmp_public = '/tmp/public_hue_examples'
        fs.do_as_user(django_user, fs.mkdir, tmp_public, '0777')
        hdfs_root_destination = tmp_public
    else:
      hdfs_root_destination = fs.do_as_user(django_user, fs.get_home_dir)

    hdfs_destination = os.path.join(hdfs_root_destination, self.name)

    LOG.info('Uploading local data %s to HDFS table "%s"' % (self.name, hdfs_destination))
    fs.do_as_user(django_user, fs.copyFromLocal, self._contents_file, hdfs_destination)

    LOG.info('Loading data into table "%s"' % (self.name,))
    hql = LOAD_HQL % {'tablename': self.name, 'filename': hdfs_destination}
    query = hql_query(hql)

    try:
      results = dbms.get(django_user, self.query_server).execute_and_wait(query)
      if not results:
        msg = _('Error loading table %(table)s: Operation timeout.') % {'table': self.name}
        LOG.error(msg)
        raise InstallException(msg)
    except QueryServerException, ex:
      msg = _('Error loading table %(table)s: %(error)s.') % {'table': self.name, 'error': ex}
      LOG.error(msg)
      raise InstallException(msg)


class SampleDesign(object):
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
      model = SavedQuery.objects.get(owner=django_user, name=self.name, type=self.type)
    except SavedQuery.DoesNotExist:
      model = SavedQuery(owner=django_user, name=self.name)
      model.type = self.type
      # The data field needs to be a string. The sample file writes it
      # as json (without encoding into a string) for readability.
      model.data = json.dumps(self.data)
      model.desc = self.desc
      model.save()
      LOG.info('Successfully installed sample design: %s' % (self.name,))
