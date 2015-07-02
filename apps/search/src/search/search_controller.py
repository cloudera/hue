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
import uuid

from django.db.models import Q

from desktop.models import Document2, Document, SAMPLE_USERNAME
from libsolr.api import SolrApi

from search.conf import SOLR_URL
from search.models import Collection2


LOG = logging.getLogger(__name__)


class SearchController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user

  def get_search_collections(self):
    return [d.content_object for d in Document.objects.get_docs(self.user, Document2, extra='search-dashboard').order_by('-id')]

  def get_shared_search_collections(self):
    # Those are the ones appearing in the menu
    docs = Document.objects.filter(Q(owner=self.user) | Q(owner__username=SAMPLE_USERNAME), extra='search-dashboard')

    return [d.content_object for d in docs.order_by('-id')]

  def get_owner_search_collections(self):
    if self.user.is_superuser:
      docs = Document.objects.filter(extra='search-dashboard')
    else:
      docs = Document.objects.filter(extra='search-dashboard', owner=self.user)

    return [d.content_object for d in docs.order_by('-id')]

  def get_icon(self, name):
    if name == 'Twitter':
      return 'search/art/icon_twitter_48.png'
    elif name == 'Yelp Reviews':
      return 'search/art/icon_yelp_48.png'
    elif name == 'Web Logs':
      return 'search/art/icon_logs_48.png'
    else:
      return 'search/art/icon_search_48.png'

  def delete_collections(self, collection_ids):
    result = {'status': -1, 'message': ''}
    try:
      for doc2 in self.get_owner_search_collections():
        if doc2.id in collection_ids:
          doc = doc2.doc.get()
          doc.delete()
          doc2.delete()
      result['status'] = 0
    except Exception, e:
      LOG.warn('Error deleting collection: %s' % e)
      result['message'] = unicode(str(e), "utf8")

    return result

  def copy_collections(self, collection_ids):
    result = {'status': -1, 'message': ''}
    try:
      for doc2 in self.get_shared_search_collections():
        if doc2.id in collection_ids:
          doc2 = Document2.objects.get(uuid=notebook['uuid'])
          doc = doc2.doc.get()

          name = doc2.name + '-copy'
          doc2 = doc2.copy(name=name, owner=request.user)

          doc.copy(content_object=doc2, name=name)

          collection = Collection2(self.user, document=doc2)
          collection.data['collection']['label'] = name

          doc2.update_data({'collection': collection.data['collection']})
          doc2.save()
      result['status'] = 0
    except Exception, e:
      LOG.exception('Error copying collection')
      result['message'] = unicode(str(e), "utf8")

    return result

  def is_collection(self, collection_name):
    solr_collections = SolrApi(SOLR_URL.get(), self.user).collections()
    return collection_name in solr_collections

  def is_core(self, core_name):
    solr_cores = SolrApi(SOLR_URL.get(), self.user).cores()
    return core_name in solr_cores

  def get_solr_collection(self):
    return SolrApi(SOLR_URL.get(), self.user).collections()

  def get_all_indexes(self, show_all=False):
    indexes = []
    try:
      indexes = self.get_solr_collection().keys()
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
