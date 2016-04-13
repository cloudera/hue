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
import uuid
import os

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from hadoop import cluster

from useradmin.models import install_sample_user
from indexer import utils, controller


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):
  """
  Install examples but do not overwrite them.
  """
  def handle_noargs(self, **options):
    self.user = install_sample_user()
    self.fs = cluster.get_hdfs()
    self.searcher = controller.CollectionManagerController(self.user)

    LOG.info(_("Installing twitter collection"))
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../apps/search/examples/collections/solr_configs_twitter_demo/index_data.csv'))
    self._setup_collection_from_csv({
      'name': 'twitter_demo',
      'fields': self._parse_fields(path),
      'uniqueKeyField': 'id',
      'df': 'text'
    }, path)
    LOG.info(_("Twitter collection successfully installed"))

    LOG.info(_("Installing yelp collection"))
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../apps/search/examples/collections/solr_configs_yelp_demo/index_data.csv'))
    self._setup_collection_from_csv({
      'name': 'yelp_demo',
      'fields': self._parse_fields(path),
      'uniqueKeyField': 'id',
      'df': 'text'
    }, path)
    LOG.info(_("Yelp collection successfully installed"))

    LOG.info(_("Installing logs collection"))
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../apps/search/examples/collections/solr_configs_log_analytics_demo/index_data.csv'))
    self._setup_collection_from_csv({
      'name': 'log_analytics_demo',
      'fields': self._parse_fields(path, fieldtypes={
        'region_code': 'string',
        'referer': 'string'
      }),
      'uniqueKeyField': 'id',
      'df': 'record'
    }, path)
    LOG.info(_("Logs collection successfully installed"))

  def _setup_collection_from_csv(self, collection, path, separator=',', quote_character='"'):
    if not self.searcher.collection_exists(collection['name']):
      self.searcher.create_collection(collection['name'], collection['fields'], collection['uniqueKeyField'], collection['df'])

    try:
      hdfs_path = '/tmp/%s' % uuid.uuid4()

      with open(path) as fh:
        self.fs.do_as_user(self.user.username, self.fs.create, hdfs_path, data=fh.read())

      self.searcher.update_data_from_hdfs(
          self.fs,
          collection['name'],
          collection['fields'],
          hdfs_path,
          'separated',
          separator=separator,
          quote_character=quote_character
      )
    finally:
      if self.fs.do_as_user(self.user.username, self.fs.exists, hdfs_path):
        self.fs.do_as_user(self.user.username, self.fs.remove, hdfs_path, skip_trash=True)

  def _parse_fields(self, path, separator=',', quote_character='"', fieldtypes={}):
    with open(path) as fh:
      field_generator = utils.field_values_from_separated_file(fh, separator, quote_character)
      row = next(field_generator)
      field_names = row.keys()
      field_types = utils.get_field_types((row.values() for row in itertools.chain([row], field_generator)), iterations=51)
      return [{'name': field[0], 'type': field[0] in fieldtypes and fieldtypes[field[0]] or field[1]} for field in zip(field_names, field_types)]
