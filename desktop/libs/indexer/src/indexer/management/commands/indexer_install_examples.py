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

    twitter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../examples/twitter/index_data.csv'))

    LOG.info(_("Installing twitter collection"))
    self._setup_collection_from_csv({
      'name': 'twitter_example',
      'fields': self._parse_fields(twitter_path),
      'uniqueKeyField': 'id'
    }, twitter_path)
    LOG.info(_("Twitter collection successfully installed"))

  def _setup_collection_from_csv(self, collection, path, separator=',', quote_character='"'):
    searcher = controller.CollectionManagerController(self.user)

    # Create instance directory, collection, and add fields
    searcher.create_collection(collection['name'], collection['fields'], collection['uniqueKeyField'])

    try:
      hdfs_path = '/tmp/%s' % uuid.uuid4()

      # Put in HDFS
      with open(path) as fh:
        if self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.exists, hdfs_path):
          overwrite = True
        else:
          overwrite = False
        self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.create, hdfs_path, data=fh.read(), overwrite=overwrite)

      # Index data
      searcher.update_data_from_hdfs(self.fs,
                                     collection['name'],
                                     collection['fields'],
                                     hdfs_path,
                                     'separated',
                                     separator=separator,
                                     quote_character=quote_character)

    except:
      searcher.delete_collection(collection['name'])
      raise
    finally:
      # Remove HDFS file
      if self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.exists, hdfs_path):
        self.fs.remove(hdfs_path, skip_trash=True)

  def _parse_fields(self, path, separator=',', quote_character='"'):
    with open(path) as fh:
      field_generator = utils.field_values_from_separated_file(fh, separator, quote_character)
      row = next(field_generator)
      field_names = row.keys()
      field_types = utils.get_field_types(row.values())
      return [{'name': field[0], 'type': field[1]} for field in zip(field_names, field_types)]
