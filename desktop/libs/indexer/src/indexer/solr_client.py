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

import logging
import json
import os
import shutil

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from libsolr.api import SolrApi
from libzookeeper.models import ZookeeperClient

from indexer.conf import CORE_INSTANCE_DIR, get_solr_ensemble
from indexer.utils import copy_configs


LOG = logging.getLogger(__name__)


MAX_UPLOAD_SIZE = 100 * 1024 * 1024 # 100 MB
ALLOWED_FIELD_ATTRIBUTES = set(['name', 'type', 'indexed', 'stored'])
FLAGS = [('I', 'indexed'), ('T', 'tokenized'), ('S', 'stored'), ('M', 'multivalued')]
ZK_SOLR_CONFIG_NAMESPACE = 'configs'

_IS_SOLR_CLOUD = None
_IS_SOLR_6_OR_MORE = None
_IS_SOLR_WITH_HDFS = None
_ZOOKEEPER_HOST = None
_IS_SENTRY_PROTECTED = None


class SolrClientException(Exception):
  pass


class SolrClient(object):

  def __init__(self, user, api=None):
    self.user = user
    self.api = api if api is not None else SolrApi(user=self.user)


  def get_indexes(self, include_cores=False):
    indexes = []

    try:
      if self.is_solr_cloud_mode():
        collections = self.api.collections2()
        for name in collections:
          indexes.append({'name': name, 'type': 'collection', 'collections': []})

      if self.is_solr_cloud_mode():
        try:
          if self.is_solr_six_or_more():
            solr_aliases = self.api.list_aliases()
          else:
            solr_aliases = self.api.aliases()
          for name in solr_aliases:
            collections = solr_aliases[name].split()
            indexes.append({'name': name, 'type': 'alias', 'collections': collections})
        except Exception:
          LOG.exception('Aliases could not be retrieved')

      if not self.is_solr_cloud_mode() or include_cores:
        solr_cores = self.api.cores()
        for name in solr_cores:
          indexes.append({'name': name, 'type': 'core', 'collections': []})

    except Exception, e:
      msg = _('Solr server could not be contacted properly: %s') % e
      LOG.warn(msg)
      raise PopupException(msg, detail=smart_str(e))

    return sorted(indexes, key=lambda index: index['name'])


  def create_index(self, name, fields, config_name=None, unique_key_field=None, df=None, shards=1, replication=1):
    if self.is_solr_cloud_mode():
      if self.is_solr_six_or_more():
        config_sets = self.list_configs()
        if not config_sets:
          raise PopupException(_('Solr does not have any predefined (secure: %s) configSets: %s') % (self.is_sentry_protected(), self.list_configs()))

        if not config_name or config_name not in config_sets:
          config_name_target = 'managedTemplate'
          if config_name_target in config_sets:
            config_name = config_name_target
          elif '_default' in config_sets:
            config_name = '_default'
          else:
            config_name = config_sets[0]

        # Note: uniqueKey is always 'id'
        self.api.create_config(name, config_name, immutable=False)

        self.api.create_collection2(name, config_name=name, shards=shards, replication=replication)

        fields = [{
            'name': field['name'],
            'type': SolrClient._port_field_types(field)['type'],
            'stored': field.get('stored', True),
            'multiValued': field.get('multiValued', False)
          } for field in fields if field['name'] != 'id'
        ]
        self.api.add_fields(name, fields)

        if df:
          self.api.update_config(name, {
            'update-requesthandler': {
              "name": "/select",
              "class": "solr.SearchHandler",
              "defaults": {"df": df},
            }
          })

        if self.is_solr_six_or_more():
          self.api.update_config(name, {
            'add-updateprocessor': {
              "name" : "tolerant",
              "class": "solr.TolerantUpdateProcessorFactory",
              "maxErrors": "100"
            }
          })
      else:
        self._create_cloud_config(name, fields, unique_key_field, df)
        self.api.create_collection2(name, config_name=config_name, shards=shards, replication=replication)
    else:
      self._create_non_solr_cloud_index(name, fields, unique_key_field, df)


  def create_alias(self, name, collections):
    return self.api.create_alias(name, collections)


  def index(self, name, data, content_type='csv', version=None, **kwargs):
    """
    e.g. Parameters: separator = ',', fieldnames = 'a,b,c', header=true, skip 'a,b', encapsulator="
      escape=\, map, split, overwrite=true, rowid=id
    """
    return self.api.update(name, data, content_type=content_type, version=version, **kwargs)


  def exists(self, name):
    try:
      self.api.get_schema(name)
      return True
    except Exception, e:
      LOG.info('Check if index %s existed failed: %s' % (name, e))
      return False


  def delete_index(self, name, keep_config=True):
    if not self.is_solr_cloud_mode():
      raise PopupException(_('Cannot remove non-Solr cloud cores.'))

    result = self.api.delete_collection(name)

    if result['status'] == 0:
      # Delete instance directory.
      if not keep_config:
        if self.is_solr_six_or_more():
          return self.api.delete_config(name)
        else:
          try:
            root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
            with ZookeeperClient(hosts=self.get_zookeeper_host(), read_only=False) as zc:
              zc.delete_path(root_node)
          except Exception, e:
            # Re-create collection so that we don't have an orphan config
            self.api.add_collection(name)
            raise PopupException(_('Error in deleting Solr configurations.'), detail=e)
    else:
      if not 'Cannot unload non-existent core' in json.dumps(result):
        raise PopupException(_('Could not remove collection: %(message)s') % result)


  def sample_index(self, collection, rows=100):
    return self.api.select(collection, rows=min(rows, 1000))


  def get_config(self, collection):
    return self.api.config(collection)


  def list_configs(self):
    return self.api.configs()


  def list_schema(self, index_name):
    return self.api.get_schema(index_name)


  def delete_alias(self, name):
    return self.api.delete_alias(name)


  def update_config(self, name, properties):
    return self.api.update_config(name, properties)


  def is_solr_cloud_mode(self):
    global _IS_SOLR_CLOUD

    if _IS_SOLR_CLOUD is None:
      self._fillup_properties()

    return _IS_SOLR_CLOUD


  def is_solr_six_or_more(self):
    global _IS_SOLR_6_OR_MORE

    if _IS_SOLR_6_OR_MORE is None:
      self._fillup_properties()

    return _IS_SOLR_6_OR_MORE


  def is_solr_with_hdfs(self):
    global _IS_SOLR_WITH_HDFS

    if _IS_SOLR_WITH_HDFS is None:
      self._fillup_properties()

    return _IS_SOLR_WITH_HDFS


  def is_sentry_protected(self):
    global _IS_SENTRY_PROTECTED

    if _IS_SENTRY_PROTECTED is None:
      self._fillup_properties()

    return _IS_SENTRY_PROTECTED


  def get_zookeeper_host(self):
    global _ZOOKEEPER_HOST

    if _ZOOKEEPER_HOST is None:
      self._fillup_properties()

    return _ZOOKEEPER_HOST


  # Deprecated
  def _create_cloud_config(self, name, fields, unique_key_field, df):
    with ZookeeperClient(hosts=self.get_zookeeper_host(), read_only=False) as zc:
      tmp_path, solr_config_path = copy_configs(
          fields=fields,
          unique_key_field=unique_key_field,
          df=df,
          solr_cloud_mode=True,
          is_solr_six_or_more=self.is_solr_six_or_more(),
          is_solr_hdfs_mode=self.is_solr_with_hdfs(),
          is_sentry_protected=self.is_sentry_protected()
      )

      try:
        root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
        config_root_path = '%s/%s' % (solr_config_path, 'conf')
        if not zc.path_exists(root_node):
          zc.copy_path(root_node, config_root_path)
        else:
          LOG.warn('Config %s already existing.' % name)
      except Exception, e:
        if zc.path_exists(root_node):
          zc.delete_path(root_node)
        raise PopupException(_('Could not create index: %s') % e)
      finally:
        shutil.rmtree(tmp_path)


  # Deprecated
  def _create_non_solr_cloud_index(self, name, fields, unique_key_field, df):
    # Create instance directory locally.
    instancedir = os.path.join(CORE_INSTANCE_DIR.get(), name)

    if os.path.exists(instancedir):
      raise PopupException(_("Instance directory %s already exists! Please remove it from the file system.") % instancedir)

    try:
      tmp_path, solr_config_path = copy_configs(fields, unique_key_field, df, False)
      try:
        shutil.move(solr_config_path, instancedir)
      finally:
        shutil.rmtree(tmp_path)

      if not self.api.create_core(name, instancedir):
        raise Exception('Failed to create core: %s' % name)
    except Exception, e:
      raise PopupException(_('Could not create index. Check error logs for more info.'), detail=e)
    finally:
      shutil.rmtree(instancedir)


  def _fillup_properties(self):
    global _IS_SOLR_CLOUD
    global _IS_SOLR_6_OR_MORE
    global _IS_SOLR_WITH_HDFS
    global _ZOOKEEPER_HOST
    global _IS_SENTRY_PROTECTED

    properties = self.api.info_system()

    _IS_SOLR_CLOUD = properties.get('mode', 'solrcloud') == 'solrcloud'
    _IS_SOLR_6_OR_MORE = not str(properties.get('lucene', {}).get('solr-spec-version')).startswith('4.')
    _IS_SOLR_WITH_HDFS = False
    _ZOOKEEPER_HOST = properties.get('zkHost', get_solr_ensemble())

    command_line_args = properties.get('jvm', {}).get('jmx', {}).get('commandLineArgs', [])
    for command_line_arg in command_line_args:
      if not _IS_SOLR_WITH_HDFS and 'solr.hdfs.home' in command_line_arg:
        _IS_SOLR_WITH_HDFS = True
      if '-DzkHost=' in command_line_arg:
        _ZOOKEEPER_HOST = command_line_arg.split('-DzkHost=', 1)[1]
      if '-Dsolr.authorization.sentry.site' in command_line_arg:
        _IS_SENTRY_PROTECTED = True


  @staticmethod
  def _port_field_types(field):
    if not field['type'].startswith('p'): # Check for automatically converting to new default Solr types
      field['type'] = field['type'].replace('long', 'plong').replace('double', 'pdouble').replace('date', 'pdate')
    return field


  @staticmethod
  def _reset_properties():
    global _IS_SOLR_CLOUD
    global _IS_SOLR_6_OR_MORE
    global _IS_SOLR_WITH_HDFS
    global _ZOOKEEPER_HOST
    global _IS_SENTRY_PROTECTED

    _IS_SOLR_CLOUD = _IS_SOLR_6_OR_MORE = _IS_SOLR_6_OR_MORE = _IS_SOLR_WITH_HDFS = _ZOOKEEPER_HOST = _IS_SENTRY_PROTECTED = None


  # Used by morphline indexer
  def get_index_schema(self, index_name):
    try:
      field_data = self.api.fields(index_name)
      fields = self._format_flags(field_data['schema']['fields'])
      uniquekey = self.api.uniquekey(index_name)
      return uniquekey, fields
    except Exception, e:
      LOG.exception(e.message)
      raise SolrClientException(_("Error in getting schema information for index '%s'" % index_name))
