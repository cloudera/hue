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
import os
import shutil
import subprocess

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from libsolr.api import SolrApi
from search.conf import SOLR_URL, SECURITY_ENABLED

from indexer import conf, utils


LOG = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024 # 100 MB
ALLOWED_FIELD_ATTRIBUTES = set(['name', 'type', 'indexed', 'stored'])
FLAGS = [('I', 'indexed'), ('T', 'tokenized'), ('S', 'stored')]


def get_solrctl_path():
  solrctl_path = conf.SOLRCTL_PATH.get()
  if solrctl_path is None:
    LOG.error("Could not find solrctl executable")
    raise PopupException(_('Could not find solrctl executable'))

  return solrctl_path


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

  def is_solr_cloud_mode(self):
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if not hasattr(self, '_solr_cloud_mode'):
      try:
        api.collections()
        setattr(self, '_solr_cloud_mode', True)
      except Exception, e:
        LOG.info('Non SolrCloud server: %s' % e)
        setattr(self, '_solr_cloud_mode', False)
    return getattr(self, '_solr_cloud_mode')

  def collection_exists(self, collection):
    return collection in self.get_collections()

  def get_collections(self):
    try:
      api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())

      if self.is_solr_cloud_mode():
        solr_collections = api.collections()
        for name in solr_collections:
          solr_collections[name]['isCoreOnly'] = False
      else:
        solr_collections = {}

      solr_cores = api.cores()
      for name in solr_cores:
        solr_cores[name]['isCoreOnly'] = True

      solr_aliases = api.aliases()
      for name in solr_aliases:
        solr_aliases[name] = {
            'isCoreOnly': False,
            'isAlias': True,
            'collections': solr_aliases[name]
        }
    except Exception, e:
      LOG.warn('No Zookeeper servlet running on Solr server: %s' % e)
      solr_collections = {}
      solr_cores = {}
      solr_aliases = {}

    solr_cores.update(solr_collections)
    solr_cores.update(solr_aliases)
    return solr_cores

  def get_fields(self, collection_or_core_name):
    try:
      field_data = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).fields(collection_or_core_name)
      fields = self._format_flags(field_data['schema']['fields'])
    except:
      LOG.exception(_('Could not fetch fields for collection %s.') % collection_or_core_name)
      raise PopupException(_('Could not fetch fields for collection %s. See logs for more info.') % collection_or_core_name)

    try:
      uniquekey = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).uniquekey(collection_or_core_name)
    except:
      LOG.exception(_('Could not fetch unique key for collection %s.') % collection_or_core_name)
      raise PopupException(_('Could not fetch unique key for collection %s. See logs for more info.') % collection_or_core_name)

    return uniquekey, fields

  def create_collection(self, name, fields, unique_key_field='id', df='text'):
    """
    Create solr collection or core and instance dir.
    Create schema.xml file so that we can set UniqueKey field.
    """
    if self.is_solr_cloud_mode():
      # solrcloud mode

      # Need to remove path afterwards
      tmp_path, solr_config_path = utils.copy_configs(fields, unique_key_field, df, True)

      # Create instance directory.
      solrctl_path = get_solrctl_path()

      process = subprocess.Popen([solrctl_path, "instancedir", "--create", name, solr_config_path],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env={
                                   'SOLR_ZK_ENSEMBLE': conf.SOLR_ZK_ENSEMBLE.get()
                                 })
      status = process.wait()

      # Don't want directories laying around
      shutil.rmtree(tmp_path)

      if status != 0:
        LOG.error("Could not create instance directory.\nOutput: %s\nError: %s" % process.communicate())
        raise PopupException(_('Could not create instance directory. '
                               'Check if solr_zk_ensemble and solrctl_path are correct in Hue config [indexer].'))

      api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
      if not api.create_collection(name):
        # Delete instance directory if we couldn't create a collection.
        process = subprocess.Popen([solrctl_path, "instancedir", "--delete", name],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env={
                                     'SOLR_ZK_ENSEMBLE': conf.SOLR_ZK_ENSEMBLE.get()
                                   })
        if process.wait() != 0:
          LOG.error("Cloud not delete collection.\nOutput: %s\nError: %s" % process.communicate())
        raise PopupException(_('Could not create collection. Check error logs for more info.'))
    else:
      # Non-solrcloud mode
      # Create instance directory locally.
      instancedir = os.path.join(conf.CORE_INSTANCE_DIR.get(), name)
      if os.path.exists(instancedir):
        raise PopupException(_("Instance directory %s already exists! Please remove it from the file system.") % instancedir)
      tmp_path, solr_config_path = utils.copy_configs(fields, unique_key_field, df, False)
      shutil.move(solr_config_path, instancedir)
      shutil.rmtree(tmp_path)

      api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
      if not api.create_core(name, instancedir):
        # Delete instance directory if we couldn't create a collection.
        shutil.rmtree(instancedir)
        raise PopupException(_('Could not create collection. Check error logs for more info.'))

  def delete_collection(self, name, core):
    """
    Delete solr collection/core and instance dir
    """
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if core:
      raise PopupException(_('Cannot remove Solr cores.'))

    if api.remove_collection(name):
      # Delete instance directory.
      solrctl_path = get_solrctl_path()

      process = subprocess.Popen([solrctl_path, "instancedir", "--delete", name],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env={
                                   'SOLR_ZK_ENSEMBLE': conf.SOLR_ZK_ENSEMBLE.get()
                                 })
      if process.wait() != 0:
        LOG.error("Cloud not delete instance directory.\nOutput stream: %s\nError stream: %s" % process.communicate())
        raise PopupException(_('Could not create instance directory. Check error logs for more info.'))
    else:
      raise PopupException(_('Could not remove collection. Check error logs for more info.'))

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

  def update_data_from_hdfs(self, fs, collection_or_core_name, fields, path, data_type='separated', indexing_strategy='upload', **kwargs):
    """
    Add hdfs path contents to index
    """
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())

    if indexing_strategy == 'upload':
      stats = fs.stats(path)
      if stats.size > MAX_UPLOAD_SIZE:
        raise PopupException(_('File size is too large to handle!'))
      else:
        # Get fields for filtering
        unique_key, fields = self.get_fields(collection_or_core_name)
        fields = [{'name': field, 'type': fields[field]['type']} for field in fields]

        fh = fs.open(path)
        if data_type == 'log':
          # Transform to JSON then update
          data = json.dumps([value for value in utils.field_values_from_log(fh, fields)])
          content_type = 'json'
        elif data_type == 'separated':
          data = json.dumps([value for value in utils.field_values_from_separated_file(fh, kwargs.get('separator', ','), kwargs.get('quote_character', '"'), fields)], indent=2)
          content_type = 'json'
        else:
          raise PopupException(_('Could not update index. Unknown type %s') % data_type)
        fh.close()
      if not api.update(collection_or_core_name, data, content_type=content_type):
        raise PopupException(_('Could not update index. Check error logs for more info.'))
    else:
      raise PopupException(_('Could not update index. Indexing strategy %s not supported.') % indexing_strategy)

  def update_data_from_hive(self, db, collection_or_core_name, database, table, columns, indexing_strategy='upload'):
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

        if not api.update(collection_or_core_name, dataset.csv, content_type='csv'):
          raise PopupException(_('Could not update index. Check error logs for more info.'))
      else:
        raise PopupException(_('Could not update index. Could not fetch any data from Hive.'))
    else:
      raise PopupException(_('Could not update index. Indexing strategy %s not supported.') % indexing_strategy)
