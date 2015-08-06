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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from libsolr.api import SolrApi
from libzookeeper.conf import ENSEMBLE
from search.conf import SOLR_URL, SECURITY_ENABLED

from desktop.lib.i18n import smart_str


LOG = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024 # 100 MB
ALLOWED_FIELD_ATTRIBUTES = set(['name', 'type', 'indexed', 'stored'])
FLAGS = [('I', 'indexed'), ('T', 'tokenized'), ('S', 'stored')]
ZK_SOLR_CONFIG_NAMESPACE = 'configs'


def get_solr_ensemble():
  return '%s/solr' % ENSEMBLE.get()


class CollectionController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user
    self.api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())

#  def _format_flags(self, fields):
#    for field_name, field in fields.items():
#      for index in range(0, len(FLAGS)):
#        flags = FLAGS[index]
#        field[flags[1]] = field['flags'][index] == FLAGS[index][0]
#    return fields
#
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
          indexes.append({'name': name, 'type': 'collection', 'collections': ''})

      solr_cores = self.api.cores()
      for name in solr_cores:
        indexes.append({'name': name, 'type': 'core', 'collections': ''})

      solr_aliases = self.api.aliases()
      for name in solr_aliases:
        indexes.append({'name': name, 'type': 'alias', 'collections': solr_aliases[name]})

    except Exception, e:
      msg = _('Solr server could not be contacted properly: %s') % e
      LOG.warn(msg)
      raise PopupException(msg, detail=smart_str(e))

    return indexes

#  def get_fields(self, collection_or_core_name):
#    try:
#      field_data = self.api.fields(collection_or_core_name)
#      fields = self._format_flags(field_data['schema']['fields'])
#    except:
#      LOG.exception(_('Could not fetch fields for collection %s.') % collection_or_core_name)
#      raise PopupException(_('Could not fetch fields for collection %s. See logs for more info.') % collection_or_core_name)
#
#    try:
#      uniquekey = self.api.uniquekey(collection_or_core_name)
#    except:
#      LOG.exception(_('Could not fetch unique key for collection %s.') % collection_or_core_name)
#      raise PopupException(_('Could not fetch unique key for collection %s. See logs for more info.') % collection_or_core_name)
#
#    return uniquekey, fields
#
#  def create_collection(self, name, fields, unique_key_field='id', df='text'):
#    """
#    Create solr collection or core and instance dir.
#    Create schema.xml file so that we can set UniqueKey field.
#    """
#    if self.is_solr_cloud_mode():
#      # solrcloud mode
#
#      # Need to remove path afterwards
#      tmp_path, solr_config_path = copy_configs(fields, unique_key_field, df, True)
#
#      zc = ZookeeperClient(hosts=get_solr_ensemble(), read_only=False)
#      root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
#      config_root_path = '%s/%s' % (solr_config_path, 'conf')
#      try:
#        zc.copy_path(root_node, config_root_path)
#      except Exception, e:
#        zc.delete_path(root_node)
#        raise PopupException(_('Error in copying Solr configurations.'), detail=e)
#
#      # Don't want directories laying around
#      shutil.rmtree(tmp_path)
#
#      if not self.api.create_collection(name):
#        # Delete instance directory if we couldn't create a collection.
#        try:
#          zc.delete_path(root_node)
#        except Exception, e:
#          raise PopupException(_('Error in deleting Solr configurations.'), detail=e)
#    else:
#      # Non-solrcloud mode
#      # Create instance directory locally.
#      instancedir = os.path.join(CORE_INSTANCE_DIR.get(), name)
#      if os.path.exists(instancedir):
#        raise PopupException(_("Instance directory %s already exists! Please remove it from the file system.") % instancedir)
#      tmp_path, solr_config_path = copy_configs(fields, unique_key_field, df, False)
#      shutil.move(solr_config_path, instancedir)
#      shutil.rmtree(tmp_path)
#
#      if not self.api.create_core(name, instancedir):
#        # Delete instance directory if we couldn't create a collection.
#        shutil.rmtree(instancedir)
#        raise PopupException(_('Could not create collection. Check error logs for more info.'))
#
#  def delete_collection(self, name, core):
#    if core:
#      raise PopupException(_('Cannot remove Solr cores.'))
#
#    if self.api.remove_collection(name):
#      # Delete instance directory.
#      try:
#        root_node = '%s/%s' % (ZK_SOLR_CONFIG_NAMESPACE, name)
#        zc = ZookeeperClient(hosts=get_solr_ensemble(), read_only=False)
#        zc.delete_path(root_node)
#      except Exception, e:
#        # Re-create collection so that we don't have an orphan config
#        self.api.add_collection(name)
#        raise PopupException(_('Error in deleting Solr configurations.'), detail=e)
#    else:
#      raise PopupException(_('Could not remove collection. Check error logs for more info.'))
