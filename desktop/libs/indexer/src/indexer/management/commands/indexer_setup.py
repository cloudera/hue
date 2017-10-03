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

import itertools
import logging
import os

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from useradmin.models import install_sample_user

from indexer import utils
from indexer.solr_client import SolrClient


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  """
  Install examples but do not overwrite them.
  """
  def handle(self, *args, **options):
    self.user = install_sample_user()
    self.client = SolrClient(self.user)

    collection = options['data']

    if collection == 'twitter_demo':
      LOG.info("Installing twitter collection")
      path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../apps/search/examples/collections/solr_configs_twitter_demo/index_data.csv'))
      self._setup_collection_from_csv({
          'name': 'twitter_demo',
          'fields': self._parse_fields(path, fieldtypes={
            'source': 'string',
            'username': 'string',
          }),
          'uniqueKeyField': 'id',
          'df': 'text'
        },
        path
      )
      LOG.info("Twitter collection successfully installed")

    if collection == 'yelp_demo':
      LOG.info("Installing yelp collection")
      path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../apps/search/examples/collections/solr_configs_yelp_demo/index_data.csv'))
      self._setup_collection_from_csv({
          'name': 'yelp_demo',
          'fields': self._parse_fields(path, fieldtypes={
            'name': 'string',
          }),
          'uniqueKeyField': 'id',
          'df': 'text'
        },
        path
      )
      LOG.info("Yelp collection successfully installed")

    if collection == 'log_analytics_demo':
      LOG.info("Installing logs collection")
      path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../apps/search/examples/collections/solr_configs_log_analytics_demo/index_data.csv'))
      self._setup_collection_from_csv({
          'name': 'log_analytics_demo',
          'fields': self._parse_fields(path, fieldtypes={
            'region_code': 'string',
            'referer': 'string',
            'user_agent': 'string'
          }),
          'uniqueKeyField': 'id',
          'df': 'record'
        },
        path
      )
      LOG.info("Logs collection successfully installed")


  def _setup_collection_from_csv(self, collection, path):
    if not self.client.exists(collection['name']):
      self.client.create_index(
          name=collection['name'],
          fields=collection['fields'],
          unique_key_field=collection['uniqueKeyField'],
          df=collection['df']
      )

      with open(path) as fh:
        self.client.index(collection['name'], fh.read())


  def _parse_fields(self, path, separator=',', quote_character='"', fieldtypes={}):
    with open(path) as fh:
      field_generator = utils.field_values_from_separated_file(fh, separator, quote_character)
      row = next(field_generator)
      field_names = row.keys()
      field_types = utils.get_field_types((row.values() for row in itertools.chain([row], field_generator)), iterations=51)
      return [{'name': field[0], 'type': field[0] in fieldtypes and fieldtypes[field[0]] or field[1]} for field in zip(field_names, field_types)]
