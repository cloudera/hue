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

"""
Install sample table data and designs.

Expects 2 files in the beeswax.conf.LOCAL_EXAMPLES_DATA_DIR:
  - tables.json: Describes the list of tables to create. Each item in the list has
    the key-value pairs:
      * table_name: the table name
      * data_file: path of the data file, relative to LOCAL_EXAMPLES_DATA_DIR
      * create_hql: the hql to create this table
  - designs.json: Describes the list of designs to populate. Each item in the list
    has key-value pairs:
      * name: design name
      * desc: design description
      * type: REPORT/HQL design type
      * data: the json design data
"""

import logging
import os
import pwd
import simplejson

from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User

import beeswax.conf
import beeswax.design
from beeswax import db_utils, models
from beeswaxd import BeeswaxService
from beeswaxd.ttypes import BeeswaxException

import hive_metastore.ttypes

LOG = logging.getLogger(__name__)
DEFAULT_INSTALL_USER = 'hue'

def get_install_user():
  """Use the DEFAULT_INSTALL_USER if it exists, else try the current user"""
  try:
    pwd.getpwnam(DEFAULT_INSTALL_USER)
    return DEFAULT_INSTALL_USER
  except KeyError:
    pw_struct = pwd.getpwuid(os.geteuid())
    LOG.info("Default sample installation user '%s' does not exist. Using '%s'"
             % (DEFAULT_INSTALL_USER, pw_struct.pw_name))
    return pw_struct.pw_name


class InstallException(Exception):
  pass


class Command(NoArgsCommand):
  """
  The handler for the sample installation action.
  """

  def handle_noargs(self, **options):
    """Main entry point to install examples. May raise InstallException"""
    if self._check_installed():
      msg = 'Beeswax examples already installed'
      LOG.error(msg)
      raise InstallException(msg)

    try:
      user = self._install_user()
      self._install_tables(user)
      self._install_reports(user)
      self._set_installed()
      LOG.info('Beeswax examples installed')
    except Exception, ex:
      LOG.exception(ex)
      LOG.error('Beeswax examples installation failed: %s' % (ex,))
      raise InstallException(ex)


  def _check_installed(self):
    """_check_installed() -> True/False whether examples have been installed"""
    model = models.MetaInstall.get()
    return model.installed_example

  def _set_installed(self):
    """_set_installed() -> Set that the examples have been installed"""
    model = models.MetaInstall.get()
    model.installed_example = True
    model.save()


  def _install_user(self):
    """
    Setup the sample user
    """
    USERNAME = 'sample'
    try:
      user = User.objects.get(username=USERNAME)
    except User.DoesNotExist:
      user = User(username=USERNAME, password='!', is_active=False, is_superuser=False)
      user.save()
      LOG.info('Installed a user called "%s"' % (USERNAME,))
    return user

  def _install_tables(self, django_user):
    """
    Install the tables into HDFS and create them in Hive.
    """
    data_dir = beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get()
    table_file = file(os.path.join(data_dir, 'tables.json'))
    table_list = simplejson.load(table_file)
    table_file.close()

    for table_dict in table_list:
      table = SampleTable(table_dict)
      table.install(django_user)
    LOG.info('Successfully created sample tables with data')

  def _install_reports(self, django_user):
    """
    Install design designs.
    """
    design_file = file(os.path.join(beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get(), 'designs.json'))
    design_list = simplejson.load(design_file)
    design_file.close()

    for design_dict in design_list:
      design = SampleDesign(design_dict)
      design.install(django_user)
    LOG.info('Successfully installed all sample queries')


def _make_query_msg(hql):
  """
  Make a thrift Query object.
  Need to run query as a valid hadoop user. Use hue:supergroup
  """
  query_msg = BeeswaxService.Query(query=hql, configuration=[])
  query_msg.hadoop_user = get_install_user()
  return query_msg


class SampleTable(object):
  """
  Represents a table loaded from the tables.json file
  """
  def __init__(self, data_dict):
    self.name = data_dict['table_name']
    self.filename = data_dict['data_file']
    self.hql = data_dict['create_hql']

    # Sanity check
    self._data_dir = beeswax.conf.LOCAL_EXAMPLES_DATA_DIR.get()
    self._contents_file = os.path.join(self._data_dir, self.filename)
    if not os.path.isfile(self._contents_file):
      msg = 'Cannot find table data in "%s"' % (self._contents_file,)
      LOG.error(msg)
      raise ValueError(msg)

  def install(self, django_user):
    self.create(django_user)
    self.load(django_user)

  def create(self, django_user):
    """
    Create in Hive. Raise InstallException on failure.
    """
    # Create table
    LOG.info('Creating table "%s"' % (self.name,))
    try:
      # Already exists?
      tables = db_utils.meta_client().get_table("default", self.name)
      msg = 'Table "%s" already exists' % (self.name,)
      LOG.error(msg)
      raise InstallException(msg)
    except hive_metastore.ttypes.NoSuchObjectException:
      query_msg = _make_query_msg(self.hql)
      try:
        results = db_utils.execute_and_wait(django_user, query_msg)
        if not results:
          msg = 'Error creating table %s: Operation timeout' % (self.name,)
          LOG.error(msg)
          raise InstallException(msg)
      except BeeswaxException, ex:
        msg = 'Error creating table %s: %s' % (self.name, ex)
        LOG.error(msg)
        raise InstallException(msg)

  def load(self, django_user):
    """
    Load data into table. Raise InstallException on failure.
    """
    LOAD_HQL = \
      """
      LOAD DATA local INPATH
      '%(filename)s' OVERWRITE INTO TABLE %(tablename)s
      """

    LOG.info('Loading data into table "%s"' % (self.name,))
    hql = LOAD_HQL % dict(tablename=self.name, filename=self._contents_file)
    query_msg = _make_query_msg(hql)
    try:
      results = db_utils.execute_and_wait(django_user, query_msg)
      if not results:
        msg = 'Error loading table %s: Operation timeout' % (self.name,)
        LOG.error(msg)
        raise InstallException(msg)
    except BeeswaxException, ex:
      msg = 'Error loading table %s: %s' % (self.name, ex)
      LOG.error(msg)
      raise InstallException(msg)


class SampleDesign(object):
  """Represents a design loaded from the designs.json file"""
  def __init__(self, data_dict):
    self.name = data_dict['name']
    self.desc = data_dict['desc']
    self.type = int(data_dict['type'])
    self.data = data_dict['data']

  def install(self, django_user):
    """
    Install design. Raise InstallException on failure.
    """
    LOG.info('Installing sample design: %s' % (self.name,))
    try:
      # Don't overwrite
      model = models.SavedQuery.objects.get(owner=django_user, name=self.name)
      msg = 'Sample design %s already exists' % (self.name,)
      LOG.error(msg)
      raise InstallException(msg)
    except models.SavedQuery.DoesNotExist:
      model = models.SavedQuery(owner=django_user, name=self.name)
      model.type = self.type
      # The data field needs to be a string. The sample file writes it
      # as json (without encoding into a string) for readability.
      model.data = simplejson.dumps(self.data)
      model.desc = self.desc
      model.save()
      LOG.info('Successfully installed sample design: %s' % (self.name,))
