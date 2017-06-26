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

from libsolr.api import SolrApi

from search.conf import SOLR_URL


LOG = logging.getLogger(__name__)


class SearchController(object):

  def __init__(self, user):
    self.user = user
  
  def is_collection(self, collection_name):
    return collection_name in self.get_solr_collections()

  def is_core(self, core_name):
    solr_cores = SolrApi(SOLR_URL.get(), self.user).cores()
    return core_name in solr_cores

  def get_solr_collections(self):
    return SolrApi(SOLR_URL.get(), self.user).collections()

  def get_all_indexes(self, show_all=False):
    indexes = []
    try:
      indexes = self.get_solr_collections().keys()
    except:
      LOG.exception('failed to get indexes')

    try:
      indexes += SolrApi(SOLR_URL.get(), self.user).aliases().keys()
    except:
      LOG.exception('failed to get index aliases')

    if show_all or not indexes:
      return indexes + SolrApi(SOLR_URL.get(), self.user).cores().keys()
    else:
      return indexes
