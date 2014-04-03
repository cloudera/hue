#!/usr/bin/env python
# -- coding: utf-8 --
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
import shutil
import subprocess

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from libsolr.api import SolrApi
from search.conf import SOLR_URL, SECURITY_ENABLED

from collectionmanager import conf, utils


LOG = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 1024*1024 # 1 MB
ALLOWED_FIELD_ATTRIBUTES = set(['name', 'type', 'indexed', 'stored'])
FLAGS = [('I', 'indexed'), ('T', 'tokenized'), ('S', 'stored')]


class CollectionManagerController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user

  def _format_flags(self, fields):
    for field_name, field in fields.items():
      for index in range(0, len(FLAGS)):
        flags = FLAGS[index]
        field[flags[1]] = field['flags'][index] == FLAGS[index][0]
    return fields

  def get_collections(self):
    try:
      solr_collections = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).collections()
    except Exception, e:
      LOG.warn('No Zookeeper servlet running on Solr server: %s' % e)
      solr_collections = []

    return solr_collections

  def get_fields(self, collection_or_core):
    try:
      field_data = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).fields(collection_or_core)
      fields = self._format_flags(field_data['schema']['fields'])
    except:
      LOG.exception(_('Could not fetch fields for collection %s.') % collection_or_core)
      raise PopupException(_('Could not fetch fields for collection %s. See logs for more info.') % collection_or_core)

    try:
      uniquekey = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).uniquekey(collection_or_core)
    except:
      LOG.exception(_('Could not fetch unique key for collection %s.') % collection_or_core)
      raise PopupException(_('Could not fetch unique key for collection %s. See logs for more info.') % collection_or_core)

    return uniquekey, fields

  def create_collection(self, name, fields, unique_key_field='id'):
    """
    Create solr collection and instance dir.
    Create schema.xml file so that we can set UniqueKey field.
    """
    # Need to remove path afterwards
    tmp_path, solr_config_path = utils.copy_config_with_fields_and_unique_key(fields, unique_key_field)

    # Create instance directory.
    process = subprocess.Popen([conf.SOLRCTL_PATH.get(), "instancedir", "--create", name, solr_config_path],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               env={
                                 'SOLR_HOME': conf.SOLR_HOME.get(),
                                 'SOLR_ZK_ENSEMBLE': conf.SOLR_ZK_ENSEMBLE.get()
                               })
    status = process.wait()

    # Don't want directories laying around
    shutil.rmtree(tmp_path)

    if status != 0:
      LOG.error("Cloud not create instance directory.\nOutput stream: %s\nError stream: %s" % process.communicate())
      raise PopupException(_('Could not create instance directory. Check error logs for more info.'))

    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if not api.create_collection(name):
      # Delete instance directory.
      process = subprocess.Popen([conf.SOLRCTL_PATH.get(), "instancedir", "--delete", name],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env={
                                   'SOLR_HOME': conf.SOLR_HOME.get(),
                                   'SOLR_ZK_ENSEMBLE': conf.SOLR_ZK_ENSEMBLE.get()
                                 })
      if process.wait() != 0:
        LOG.error("Cloud not delete instance directory.\nOutput stream: %s\nError stream: %s" % process.communicate())
      raise PopupException(_('Could not create collection. Check error logs for more info.'))

  def delete_collection(self, name):
    """
    Delete solr collection and instance dir
    """
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if api.remove_collection(name):
      # Delete instance directory.
      process = subprocess.Popen([conf.SOLRCTL_PATH.get(), "instancedir", "--delete", name],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env={
                                   'SOLR_HOME': conf.SOLR_HOME.get(),
                                   'SOLR_ZK_ENSEMBLE': conf.SOLR_ZK_ENSEMBLE.get()
                                 })
      if process.wait() != 0:
        LOG.error("Cloud not delete instance directory.\nOutput stream: %s\nError stream: %s" % process.communicate())
        raise PopupException(_('Could not create instance directory. Check error logs for more info.'))
    else:
      raise PopupException(_('Could not create collection. Check error logs for more info.'))

  def update_collection(self, name, fields):
    """
    Only create new fields
    """
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    # Create only new fields
    # Fields that already exist, do not overwrite since there is no way to do that, currently.
    old_field_names = api.fields(name)['schema']['fields'].keys()
    new_fields = filter(lambda field: field['name'] not in old_field_names, fields)
    new_fields_filtered = []
    for field in new_fields:
      new_field = {}
      for attribute in filter(lambda attribute: attribute in field, ALLOWED_FIELD_ATTRIBUTES):
        new_field[attribute] = field[attribute]
      new_fields_filtered.append(new_field)

    api.add_fields(name, new_fields_filtered)

  def update_data_from_hdfs(self, fs, collection_or_core, path, data_type='log', indexing_strategy='upload'):
    """
    Add hdfs path contents to index
    """
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if indexing_strategy == 'upload':
      stats = fs.stats(path)
      if stats.size > MAX_UPLOAD_SIZE:
        raise PopupException(_('File size is too large to handle!'))
      else:
        fh = fs.open(path)
        if data_type == 'log':
          # Transform to JSON then update
          data = json.dumps([value for value in utils.field_values_from_log(fh)])
          content_type = 'json'
        else:
          # 'data' first line should be headers.
          data = fh.read()
          content_type = 'csv'
        fh.close()
      if not api.update(collection_or_core, data, content_type=content_type):
        raise PopupException(_('Could not update index. Check error logs for more info.'))
    else:
      raise PopupException(_('Could not update index. Indexing strategy %s not supported.') % indexing_strategy)

  def update_data_from_hive(self, db, collection_or_core, database, table, columns, indexing_strategy='upload'):
    """
    Add hdfs path contents to index
    """
    # Run a custom hive query and post data to collection
    from beeswax.server import dbms
    import tablib

    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if indexing_strategy == 'upload':
      table = db.get_table(database, table)
      hql = "SELECT %s FROM `%s.%s` %s" % (','.join(columns), database, table.name, db._get_browse_limit_clause(table))
      query = dbms.hql_query(hql)
      handle = db.execute_and_wait(query)

      if handle:
        result = db.fetch(handle, rows=100)
        db.close(handle)

        dataset = tablib.Dataset()
        dataset.append(columns)
        for row in result.rows():
          dataset.append(row)

        if not api.update(collection_or_core, dataset.csv, content_type='csv'):
          raise PopupException(_('Could not update index. Check error logs for more info.'))
      else:
        raise PopupException(_('Could not update index. Could not fetch any data from Hive.'))
    else:
      raise PopupException(_('Could not update index. Indexing strategy %s not supported.') % indexing_strategy)
