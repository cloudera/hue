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

try:
  import json
except ImportError:
  import simplejson as json

import logging

from desktop.lib.exceptions_renderable import PopupException

from search.api import SolrApi
from search.conf import SOLR_URL
from search.models import Collection


LOG = logging.getLogger(__name__)


class SearchController(object):
  """
  Glue the models to the views.
  """
  def __init__(self):
    pass

  def get_new_collections(self):
    solr_collections = SolrApi(SOLR_URL.get()).collections()
    for name in Collection.objects.values_list('name', flat=True):
      solr_collections.pop(name)

    return solr_collections

  def get_new_cores(self):
    # TODO
    solr_cores = []

    return solr_cores

  def add_new_collection(self, attrs):
    if attrs['type'] == 'collection':
      collections = self.get_new_collections()
      collection = collections[attrs['name']]

      hue_collection, created = Collection.objects.get_or_create(name=attrs['name'], solr_properties=collection, is_enabled=True)
      return hue_collection
    else:
      raise PopupException(_('Collection type does not exit: %s') % attrs)
