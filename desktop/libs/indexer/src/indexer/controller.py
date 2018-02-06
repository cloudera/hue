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
import numbers
import os
import shutil

from django.utils.translation import ugettext as _
import tablib

from desktop.lib.exceptions_renderable import PopupException
from dashboard.models import Collection2
from libsolr.api import SolrApi
from libzookeeper.models import ZookeeperClient
from search.conf import SOLR_URL, SECURITY_ENABLED

from indexer.conf import CORE_INSTANCE_DIR
from indexer.utils import copy_configs, field_values_from_log, field_values_from_separated_file
from indexer.solr_client import SolrClient


LOG = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024 # 100 MB
ALLOWED_FIELD_ATTRIBUTES = set(['name', 'type', 'indexed', 'stored'])
FLAGS = [('I', 'indexed'), ('T', 'tokenized'), ('S', 'stored')]
ZK_SOLR_CONFIG_NAMESPACE = 'configs'


class CollectionManagerController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user

  def _format_flags(self, fields):
    for name, properties in fields.items():
      for (code, value) in FLAGS:
        if code in properties['flags']:
          properties[value] = True  # Add a new key-value boolean for the decoded flag
    return fields

  def is_solr_cloud_mode(self):
    client = SolrClient(self.user)
    return client.is_solr_cloud_mode()

  def collection_exists(self, collection):
    return collection in self.get_collections()

  def get_collections(self):
    solr_collections = {}
    solr_aliases = {}
    solr_cores = {}

    try:
      api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())

      if self.is_solr_cloud_mode():
        solr_collections = api.collections()
        for name in solr_collections:
          solr_collections[name]['isCoreOnly'] = False

        solr_aliases = api.aliases()
        for name in solr_aliases:
          solr_aliases[name] = {
              'isCoreOnly': False,
              'isAlias': True,
              'collections': solr_aliases[name]
          }

      solr_cores = api.cores()
      for name in solr_cores:
        solr_cores[name]['isCoreOnly'] = True
    except Exception, e:
      LOG.warn('No Zookeeper servlet running on Solr server: %s' % e)

    solr_cores.update(solr_collections)
    solr_cores.update(solr_aliases)
    return solr_cores

  def get_autocomplete(self):
    autocomplete = {}
    try:
      api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
      autocomplete['collections'] = api.collections2()
      autocomplete['configs'] = api.configs()

    except Exception, e:
      LOG.warn('No Zookeeper servlet running on Solr server: %s' % e)

    return autocomplete

  def get_fields(self, collection_or_core_name):
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())

    try:
      field_data = api.fields(collection_or_core_name)
      fields = self._format_flags(field_data['schema']['fields'])
    except Exception, e:
      LOG.warn('/luke call did not succeed: %s' % e)
      try:
        fields = api.schema_fields(collection_or_core_name)
        fields = Collection2._make_luke_from_schema_fields(fields)
      except:
        LOG.exception(_('Could not fetch fields for collection %s.') % collection_or_core_name)
        raise PopupException(_('Could not fetch fields for collection %s. See logs for more info.') % collection_or_core_name)

    try:
      uniquekey = api.uniquekey(collection_or_core_name)
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
      self._create_solr_cloud_collection(name, fields, unique_key_field, df)
    else:
      self._create_non_solr_cloud_collection(name, fields, unique_key_field, df)

  def _create_solr_cloud_collection(self, name, fields, unique_key_field, df):
    client = SolrClient(self.user)

    with ZookeeperClient(hosts=client.get_zookeeper_host(), read_only=False) as zc:
      root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)

      tmp_path, solr_config_path = copy_configs(
          fields=fields,
          unique_key_field=unique_key_field,
          df=df,
          solr_cloud_mode=client.is_solr_cloud_mode(),
          is_solr_six_or_more=client.is_solr_six_or_more(),
          is_solr_hdfs_mode=client.is_solr_with_hdfs()
      )
      try:
        config_root_path = '%s/%s' % (solr_config_path, 'conf')
        try:
          zc.copy_path(root_node, config_root_path)

        except Exception, e:
          zc.delete_path(root_node)
          raise PopupException(_('Error in copying Solr configurations: %s') % e)
      finally:
        # Don't want directories laying around
        shutil.rmtree(tmp_path)

      api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
      if not api.create_collection(name):
        # Delete instance directory if we couldn't create a collection.
        try:
          zc.delete_path(root_node)
        except Exception, e:
          raise PopupException(_('Error in deleting Solr configurations.'), detail=e)
        raise PopupException(_('Could not create collection. Check error logs for more info.'))

  def _create_non_solr_cloud_collection(self, name, fields, unique_key_field, df):
    # Non-solrcloud mode
    # Create instance directory locally.
    instancedir = os.path.join(CORE_INSTANCE_DIR.get(), name)
    if os.path.exists(instancedir):
      raise PopupException(_("Instance directory %s already exists! Please remove it from the file system.") % instancedir)

    tmp_path, solr_config_path = copy_configs(fields, unique_key_field, df, False)
    try:
      shutil.move(solr_config_path, instancedir)
    finally:
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
    client = SolrClient(self.user)

    if core:
      raise PopupException(_('Cannot remove Solr cores.'))

    if api.remove_collection(name):
      # Delete instance directory.
      try:
        root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
        with ZookeeperClient(hosts=client.get_zookeeper_host(), read_only=False) as zc:
          zc.delete_path(root_node)
      except Exception, e:
        # Re-create collection so that we don't have an orphan config
        api.add_collection(name)
        raise PopupException(_('Error in deleting Solr configurations.'), detail=e)
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
          data = json.dumps([value for value in field_values_from_log(fh, fields)])
          content_type = 'json'
        elif data_type == 'separated':
          data = json.dumps([value for value in field_values_from_separated_file(fh, kwargs.get('separator', ','), kwargs.get('quote_character', '"'), fields)], indent=2)
          content_type = 'json'
        else:
          raise PopupException(_('Could not update index. Unknown type %s') % data_type)
        fh.close()

      if not api.update(collection_or_core_name, data, content_type=content_type):
        raise PopupException(_('Could not update index. Check error logs for more info.'))
    else:
      raise PopupException(_('Could not update index. Indexing strategy %s not supported.') % indexing_strategy)

  def update_data_from_hive(self, collection_or_core_name, columns, fetch_handle, indexing_options=None):
    MAX_ROWS = 10000
    FETCH_BATCH = 1000

    row_count = 0
    has_more = True
    if indexing_options is None:
      indexing_options = {}

    client = SolrClient(self.user)

    try:
      while row_count < MAX_ROWS and has_more:
        result = fetch_handle(FETCH_BATCH, row_count == 0)
        has_more = result['has_more']

        if result['data']:
          dataset = tablib.Dataset()
          dataset.append(columns)
          for i, row in enumerate(result['data']):
            dataset.append([cell if cell else (0 if isinstance(cell, numbers.Number) else '') for cell in row])

          if not client.index(name=collection_or_core_name, data=dataset.csv, **indexing_options):
            raise PopupException(_('Could not index the data. Check error logs for more info.'))

        row_count += len(dataset)
    except Exception, e:
      raise PopupException(_('Could not update index: %s') % e)

    return row_count
