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
import csv
import logging
import json
import os
import sys
import pwd

from django.core.management.base import BaseCommand

from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import USE_NEW_EDITOR
from desktop.models import Directory, Document2, Document2Permission
from hadoop import cluster
from notebook.models import import_saved_beeswax_query, make_notebook, MockRequest, _get_example_directory
from useradmin.models import get_default_user_group, install_sample_user, User

from beeswax.design import hql_query
from beeswax.conf import LOCAL_EXAMPLES_DATA_DIR
from beeswax.hive_site import has_concurrency_support
from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS
from beeswax.server import dbms

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

LOG = logging.getLogger()


class InstallException(Exception):
  pass


class Command(BaseCommand):
  args = '<hive|impala> <db_name>'
  help = 'Install examples but do not overwrite them.'

  def handle(self, *args, **options):
    if args:
      dialect = args[0]
      db_name = args[1] if len(args) > 1 else 'default'
      user = User.objects.get(username=pwd.getpwuid(os.getuid()).pw_name)
      request = None
      self.queries = None
      self.tables = None
      interpreter = None
    else:
      dialect = options['dialect']
      db_name = options.get('db_name', 'default')
      interpreter = options.get('interpreter')  # Only when connectors are enabled. Later will deprecate `dialect`.
      user = options['user']
      request = options.get('request', MockRequest(user=user))
      self.queries = options.get('queries')
      self.tables = options.get('tables')  # Optional whitelist of table names

    tables = \
        'tables.json' if dialect not in ('hive', 'impala') else (
        'tables_transactional.json' if has_concurrency_support() else
        'tables_standard.json'
    )
    exception = None

    LOG.info('Installing %s samples %s in DB %s owned by user %s' % (dialect, tables, db_name, user))

    self.successes = []
    self.errors = []
    try:
      sample_user = install_sample_user(user)  # Documents will belong to the sample user but we run the SQL as the current user
      self.install_queries(sample_user, dialect, interpreter=interpreter)
      self.install_tables(user, dialect, db_name, tables, interpreter=interpreter, request=request)
    except Exception as ex:
      LOG.exception('Dialect %s sample install' % dialect)
      exception = ex

    if exception is not None:
      pretty_msg = None

      if "Permission denied" in str(exception):
        pretty_msg = _("Permission denied. Please check with your system administrator.")

      if pretty_msg is not None:
        raise PopupException(pretty_msg)
      else:
        raise exception

    return self.successes, self.errors


  def install_tables(self, django_user, dialect, db_name, tables, interpreter=None, request=None):
    data_dir = LOCAL_EXAMPLES_DATA_DIR.get()
    table_file = open(os.path.join(data_dir, tables))
    table_list = json.load(table_file)
    table_file.close()

    table_list = [table_dict for table_dict in table_list if dialect in table_dict.get('dialects', [dialect])]

    if not table_list:
      self.successes.append(_('No %s tables are available as samples') % dialect)
      return

    for table_dict in table_list:
      if self.tables is None or table_dict['table_name'] in self.tables:
        full_name = '%s.%s' % (db_name, table_dict['table_name'])
        try:
          table = SampleTable(table_dict, dialect, db_name, interpreter=interpreter, request=request)
          if table.install(django_user):
            self.successes.append(_('Table %s installed.') % full_name)
        except Exception as ex:
          msg = str(ex)
          LOG.error(msg)
          self.errors.append(_('Could not install table %s: %s') % (full_name, msg))


  def install_queries(self, django_user, dialect, interpreter=None):
    design_file = open(os.path.join(LOCAL_EXAMPLES_DATA_DIR.get(), 'queries.json'))
    design_list = json.load(design_file)
    design_file.close()

    # Filter query list to HiveServer2 vs other interfaces
    app_type = HQL if dialect == 'hive' else IMPALA if dialect == 'impala' else RDBMS
    design_list = [d for d in design_list if int(d['type']) == app_type]

    if app_type == RDBMS:
      design_list = [d for d in design_list if dialect in d['dialects']]

    if not self.queries:  # Manual install
      design_list = [d for d in design_list if not d.get('auto_load_only')]

    if self.queries:  # Automated install
      design_list = [d for d in design_list if d['name'] in self.queries]

    if not design_list:
      self.successes.append(_('No %s queries are available as samples') % dialect)
      return

    for design_dict in design_list:
      design = SampleQuery(design_dict)
      try:
        design.install(django_user, interpreter=interpreter)
        self.successes.append(_('Query %s %s installed.') % (design_dict['name'], dialect))
      except Exception as ex:
        msg = str(ex)
        LOG.error(msg)
        self.errors.append(_('Could not install %s query: %s') % (dialect, msg))


class SampleTable(object):
  """
  Represents a table loaded from the tables.json file
  """
  def __init__(self, data_dict, dialect, db_name='default', interpreter=None, request=None):
    self.name = data_dict['table_name']
    if 'partition_files' in data_dict:
      self.partition_files = data_dict['partition_files']
    else:
      self.partition_files = None
      self.filename = data_dict['data_file']
    self._contents_file = None
    self.create_sql = data_dict['create_sql'].strip()
    self.insert_sql = data_dict.get('insert_sql')
    self.dialect = dialect
    self.db_name = db_name
    self.interpreter = interpreter
    self.request = request
    self.columns = data_dict.get('columns')
    self.is_transactional = data_dict.get('transactional')
    self.is_multi_inserts = data_dict.get('is_multi_inserts')

    # Sanity check
    self._data_dir = LOCAL_EXAMPLES_DATA_DIR.get()
    if self.partition_files:
      for partition_spec, filename in list(self.partition_files.items()):
        filepath = os.path.join(self._data_dir, filename)
        self.partition_files[partition_spec] = filepath
        self._check_file_contents(filepath)
    elif self.filename:
      self._contents_file = os.path.join(self._data_dir, self.filename)
      self._check_file_contents(self._contents_file)


  def install(self, django_user):
    if self.dialect in ('hive', 'impala'):
      if has_concurrency_support() and not self.is_transactional:
        LOG.info('Skipping table %s as non transactional' % self.name)
        return
      if not (has_concurrency_support() and self.is_transactional) and not cluster.get_hdfs():
        raise PopupException('Requiring a File System to load its data')

    self.create(django_user)

    if self.partition_files:
      for partition_spec, filepath in list(self.partition_files.items()):
        self.load_partition(django_user, partition_spec, filepath, columns=self.columns)
    elif self._contents_file:
      self.load(django_user)

    return True


  def create(self, django_user):
    """
    Create SQL sample table.
    """
    LOG.info('Creating table "%s"' % self.name)

    try:
      job = make_notebook(
          name=_('Create sample table %s') % self.name,
          editor_type=self.interpreter['type'] if self.interpreter else self.dialect,  # Backward compatibility without connectors
          statement=self.create_sql,
          status='ready',
          database=self.db_name,
          on_success_url='assist.db.refresh',
          last_executed=int(self.request.ts * 1000) if self.request else -1,
          is_task=False,
      )

      job.execute_and_wait(self.request)
    except Exception as ex:
      exception_string = str(ex)
      if 'already exists' in exception_string or 'AlreadyExistsException' in exception_string:
        raise PopupException('already exists')
      else:
        raise ex


  def load(self, django_user):
    inserts = []

    if (self.dialect not in ('hive', 'impala') or has_concurrency_support()) and self.is_transactional:
      with open(self._contents_file) as f:
        if self.insert_sql:
          sql_insert = self.insert_sql
        else:
          sql_insert = """
            INSERT INTO TABLE %(tablename)s
            VALUES %(values)s
            """
        values = self._get_sql_insert_values(f)
        for value in values:
          inserts.append(
            sql_insert % {
              'tablename': self.name,
              'values': value
            }
          )
    else:
      # Upload data to HDFS home of user then load (aka move) it into the Hive table (in the Hive metastore in HDFS).
      hdfs_root_destination = self._get_hdfs_root_destination(django_user)
      hdfs_file_destination = self._upload_to_hdfs(django_user, self._contents_file, hdfs_root_destination)
      hql = """
        LOAD DATA INPATH
        '%(filename)s' OVERWRITE INTO TABLE %(tablename)s
        """ % {
          'tablename': self.name,
          'filename': hdfs_file_destination
        }
      inserts.append(hql)

    for insert in inserts:
      self._load_data_to_table(django_user, insert)


  def load_partition(self, django_user, partition_spec, filepath, columns):
    if (self.dialect not in ('hive', 'impala') or has_concurrency_support()) and self.is_transactional:
      with open(filepath) as f:
        hql = \
          """
          INSERT INTO TABLE %(tablename)s
          PARTITION (%(partition_spec)s)
          VALUES %(values)s
          """ % {
            'tablename': self.name,
            'partition_spec': partition_spec,
            'values': ''.join(self._get_sql_insert_values(f, columns))
          }
    else:
      # Upload data found at filepath to HDFS home of user, the load intto a specific partition
      LOAD_PARTITION_HQL = \
        """
        ALTER TABLE %(tablename)s ADD PARTITION(%(partition_spec)s) LOCATION '%(filepath)s'
        """

      partition_dir = self._get_partition_dir(partition_spec)
      hdfs_root_destination = self._get_hdfs_root_destination(django_user, subdir=partition_dir)
      filename = filepath.split('/')[-1]
      hdfs_file_destination = self._upload_to_hdfs(django_user, filepath, hdfs_root_destination, filename)

      hql = LOAD_PARTITION_HQL % {'tablename': self.name, 'partition_spec': partition_spec, 'filepath': hdfs_root_destination}

    self._load_data_to_table(django_user, hql)


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
    hdfs_root_destination = None
    can_impersonate_hdfs = False

    if self.dialect == 'impala':
      # Impala can support impersonation, so use home instead of a public destination for the upload
      from impala.conf import IMPERSONATION_ENABLED
      can_impersonate_hdfs = IMPERSONATION_ENABLED.get()

    if can_impersonate_hdfs:
      hdfs_root_destination = fs.do_as_user(django_user, fs.get_home_dir)
      if subdir:
        hdfs_root_destination += '/%s' % subdir
        fs.do_as_user(django_user, fs.mkdir, hdfs_root_destination, '0777')
    else:
      tmp_public = '/tmp/public_hue_examples'
      if subdir:
        tmp_public += '/%s' % subdir
      fs.do_as_user(django_user, fs.mkdir, tmp_public, '0777')
      hdfs_root_destination = tmp_public

    return hdfs_root_destination


  def _upload_to_hdfs(self, django_user, local_filepath, hdfs_root_destination, filename=None):
    fs = cluster.get_hdfs()

    if filename is None:
      filename = self.name
    hdfs_destination = '%s/%s' % (hdfs_root_destination, filename)

    LOG.info('Uploading local data %s to HDFS path "%s"' % (self.name, hdfs_destination))
    fs.do_as_user(django_user, fs.copyFromLocal, local_filepath, hdfs_destination)

    return hdfs_destination


  def _load_data_to_table(self, django_user, hql):
    LOG.info('Loading data into table "%s"' % (self.name,))

    job = make_notebook(
        name=_('Insert data in sample table %s') % self.name,
        editor_type=self.interpreter['type'] if self.interpreter else self.dialect,
        statement=hql,
        status='ready',
        database=self.db_name,
        on_success_url='assist.db.refresh',
        last_executed=int(self.request.ts * 1000) if self.request and hasattr(self.request, 'ts') else -1,
        is_task=False,
    )
    job.execute_and_wait(self.request)


  def _get_sql_insert_values(self, f, columns=None):
    data = f.read()
    dialect = csv.Sniffer().sniff(data)
    reader = csv.reader(data.splitlines(), delimiter=dialect.delimiter)

    rows = [
      '(%s)' % ', '.join(
        col if is_number(col, i, columns) else "'%s'" % col.replace("'", "\\'")
        for i, col in enumerate(row)
      )
      for row in reader
    ]

    return rows if self.is_multi_inserts else [', '.join(rows)]


def is_number(col, i, columns):
  '''Basic check. For proper check, use columns headers like for the web_logs table.'''
  return columns[i]['type'] != 'string' if columns else col.isdigit() or col == 'NULL'


class SampleQuery(object):

  """Represents a query loaded from the designs.json file"""
  def __init__(self, data_dict):
    self.name = data_dict['name']
    self.desc = data_dict['desc']
    self.type = int(data_dict['type'])
    self.data = data_dict['data']


  def install(self, django_user, interpreter=None):
    """
    Install queries. Raise InstallException on failure.
    """
    LOG.info('Installing sample query: %s' % (self.name,))

    try:
      # Don't overwrite
      query = SavedQuery.objects.get(owner=django_user, name=self.name, type=self.type)
    except SavedQuery.DoesNotExist:
      query = SavedQuery(owner=django_user, name=self.name, type=self.type, desc=self.desc)
      # The data field needs to be a string. The sample file writes it as json (without encoding into a string) for readability.
      query.data = json.dumps(self.data)
      query.save()
      LOG.info('Successfully installed sample design: %s' % (self.name,))

    if USE_NEW_EDITOR.get():
      examples_dir = _get_example_directory(django_user)

      document_type = self._document_type(self.type, interpreter)
      notebook = import_saved_beeswax_query(query, interpreter=interpreter)

      try:
        # Could move PK from a uuid in queries.json at some point to handle name changes without duplicating.
        # And move to a simpler json format at some point.
        doc2 = Document2.objects.get(owner=django_user, name=self.name, type=document_type, is_history=False)

        if doc2.parent_directory != examples_dir:  # Recover from Trash or if moved
          doc2.parent_directory = examples_dir

        data = json.loads(doc2.data)
        data['uuid'] = doc2.uuid
        doc2.data = json.dumps(data)  # Refresh content

        doc2.save()
      except Document2.DoesNotExist:
        # Create new example
        data = notebook.get_data()
        data['isSaved'] = True
        uuid = data.get('uuid')
        data = json.dumps(data)

        doc2 = Document2.objects.create(
          uuid=uuid,  # Must the same as in the notebook data
          owner=django_user,
          parent_directory=examples_dir,
          name=self.name,
          type=document_type,
          description=self.desc,
          data=data
        )

        # TODO: FK to connector object

      # Share with default group
      examples_dir.share(django_user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
      LOG.info('Successfully installed sample query: %s' % doc2)


  def _document_type(self, type, interpreter=None):
    if type == HQL:
      return 'query-hive'
    elif type == IMPALA:
      return 'query-impala'
    elif interpreter:
      return 'query-%(dialect)s' % interpreter
    else:
      return None
