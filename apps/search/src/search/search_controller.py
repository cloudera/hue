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

from desktop.lib.exceptions_renderable import PopupException

from search.api import SolrApi
from search.conf import SOLR_URL
from search.models import Collection
from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class SearchController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user

  def get_new_collections(self):
    try:
      solr_collections = SolrApi(SOLR_URL.get(), self.user).collections()
      for name in Collection.objects.values_list('name', flat=True):
        solr_collections.pop(name, None)
    except Exception, e:
      LOG.warn('No Zookeeper servlet running on Solr server: %s' % e)
      solr_collections = []

    return solr_collections

  def get_new_cores(self):
    try:
      solr_cores = SolrApi(SOLR_URL.get(), self.user).cores()
      for name in Collection.objects.values_list('name', flat=True):
        solr_cores.pop(name, None)
    except Exception, e:
      solr_cores = []
      LOG.warn('No Single core setup on Solr server: %s' % e)

    return solr_cores

  def add_new_collection(self, attrs):
    if attrs['type'] == 'collection':
      collections = self.get_new_collections()
      collection = collections[attrs['name']]

      hue_collection, created = Collection.objects.get_or_create(name=attrs['name'], solr_properties=collection, is_enabled=True, user=self.user)
      return hue_collection
    elif attrs['type'] == 'core':
      cores = self.get_new_cores()
      core = cores[attrs['name']]

      hue_collection, created = Collection.objects.get_or_create(name=attrs['name'], solr_properties=core, is_enabled=True, is_core_only=True, user=self.user)
      return hue_collection
    else:
      raise PopupException(_('Collection type does not exit: %s') % attrs)

  def delete_collection(self, collection_id):
    id = collection_id
    try:
      Collection.objects.get(id=collection_id).delete()
    except Exception, e:
      LOG.warn('Error deleting collection: %s' % e)
      id = -1

    return id

  def copy_collection(self, collection_id):
    id = -1

    try:
      copy = Collection.objects.get(id=collection_id)
      copy.label += _(' (Copy)')
      copy.id = copy.pk = None
      copy.save()

      facets = copy.facets
      facets.id = None
      facets.save()
      copy.facets = facets

      result = copy.result
      result.id = None
      result.save()
      copy.result = result


      sorting = copy.sorting
      sorting.id = None
      sorting.save()
      copy.sorting = sorting

      copy.save()

      id = copy.id
    except Exception, e:
      LOG.warn('Error copying collection: %s' % e)

  def is_collection(self, collection_name):
    solr_collections = SolrApi(SOLR_URL.get(), self.user).collections()
    return collection_name in solr_collections

  def is_core(self, core_name):
    solr_cores = SolrApi(SOLR_URL.get(), self.user).cores()
    return core_name in solr_cores
