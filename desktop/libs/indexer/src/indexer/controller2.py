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
import os
import shutil

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from indexer.conf import CORE_INSTANCE_DIR
from indexer.utils import copy_configs
from libsolr.api import SolrApi
from libzookeeper.conf import ENSEMBLE
from libzookeeper.models import ZookeeperClient
from search.conf import SOLR_URL, SECURITY_ENABLED


LOG = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024 # 100 MB
ALLOWED_FIELD_ATTRIBUTES = set(['name', 'type', 'indexed', 'stored'])
FLAGS = [('I', 'indexed'), ('T', 'tokenized'), ('S', 'stored'), ('M', 'multivalued')]
ZK_SOLR_CONFIG_NAMESPACE = 'configs'


def get_solr_ensemble():
  return '%s/solr' % ENSEMBLE.get()


class IndexControllerException(Exception):
  pass


class IndexController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user
    self.api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())


  def is_solr_cloud_mode(self):
    if not hasattr(self, '_solr_cloud_mode'):
      try:
        self.api.collections()
        setattr(self, '_solr_cloud_mode', True)
      except Exception, e:
        LOG.info('Non SolrCloud server: %s' % e)
        setattr(self, '_solr_cloud_mode', False)
    return getattr(self, '_solr_cloud_mode')

#  def collection_exists(self, collection):
#    return collection in self.get_collections()

  def get_indexes(self):
    indexes = []

    try:
      if self.is_solr_cloud_mode():
        collections = self.api.collections2()
        for name in collections:
          indexes.append({'name': name, 'type': 'collection', 'collections': []})

      solr_cores = self.api.cores()
      for name in solr_cores:
        indexes.append({'name': name, 'type': 'core', 'collections': []})

      solr_aliases = self.api.aliases()
      for name in solr_aliases:
        collections = solr_aliases[name].split()
        indexes.append({'name': name, 'type': 'alias', 'collections': collections})

    except Exception, e:
      msg = _('Solr server could not be contacted properly: %s') % e
      LOG.warn(msg)
      raise PopupException(msg, detail=smart_str(e))

    return indexes


  def create_index(self, name, fields, unique_key_field='id', df='text'):
    """
    Create solr collection or core and instance dir.
    Create schema.xml file so that we can set UniqueKey field.
    """
    if self.is_solr_cloud_mode():
      self._create_solr_cloud_index(name, fields, unique_key_field, df)

    else:  # Non-solrcloud mode
      self._create_non_solr_cloud_index(name, fields, unique_key_field, df)

    return name

  def _create_solr_cloud_index(self, name, fields, unique_key_field, df):
    with ZookeeperClient(hosts=get_solr_ensemble(), read_only=False) as zc:
      tmp_path, solr_config_path = copy_configs(fields, unique_key_field, df, True)

      try:
        root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
        config_root_path = '%s/%s' % (solr_config_path, 'conf')
        zc.copy_path(root_node, config_root_path)

        if not self.api.create_collection(name):
          raise Exception('Failed to create collection: %s' % name)
      except Exception, e:
        if zc.path_exists(root_node):
          # Remove the root node from Zookeeper
          zc.delete_path(root_node)
        raise PopupException(_('Could not create index. Check error logs for more info.'), detail=e)
      finally:
        # Remove tmp config directory
        shutil.rmtree(tmp_path)


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
      # Delete instance directory if we couldn't create the core.
      shutil.rmtree(instancedir)
#

  def delete_index(self, name):
    """
    Delete solr collection/core and instance dir
    """
    # TODO: Implement deletion of local Solr cores
    if not self.is_solr_cloud_mode():
      raise PopupException(_('Cannot remove non-Solr cloud cores.'))

    if self.api.remove_collection(name):
      # Delete instance directory.
      try:
        root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
        with ZookeeperClient(hosts=get_solr_ensemble(), read_only=False) as zc:
          zc.delete_path(root_node)
      except Exception, e:
        # Re-create collection so that we don't have an orphan config
        self.api.add_collection(name)
        raise PopupException(_('Error in deleting Solr configurations.'), detail=e)
    else:
      raise PopupException(_('Could not remove collection. Check error logs for more info.'))


  def get_index_schema(self, index_name):
    """
    Returns a tuple of the unique key and schema fields for a given index
    """
    try:
      field_data = self.api.fields(index_name)
      fields = self._format_flags(field_data['schema']['fields'])
      uniquekey = self.api.uniquekey(index_name)
      return uniquekey, fields
    except Exception, e:
      LOG.exception(e.message)
      raise IndexControllerException(_("Error in getting schema information for index '%s'" % index_name))


  def delete_alias(self, name):
    return self.api.delete_alias(name)


  def _format_flags(self, fields):
    for name, properties in fields.items():
      for (code, value) in FLAGS:
        if code in properties['flags']:
          properties[value] = True  # Add a new key-value boolean for the decoded flag
    return fields
