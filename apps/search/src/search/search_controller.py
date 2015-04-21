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

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext as _

from desktop.models import Document2
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
    if self.user.is_superuser:
      return Document2.objects.filter(type='search-dashboard').order_by('-id')
    else:
      return Document2.objects.filter(type='search-dashboard').filter(owner=self.user).order_by('-id')

  def get_shared_search_collections(self):
    return Document2.objects.filter(type='search-dashboard').filter(Q(owner=self.user) | Q(owner__in=User.objects.filter(is_superuser=True)) | Q(id__in=[20000000, 20000001, 20000002])).order_by('-id')

  def get_owner_search_collections(self):
    if self.user.is_superuser:
      return Document2.objects.filter(type='search-dashboard')
    else:
      return Document2.objects.filter(type='search-dashboard').filter(Q(owner=self.user))

  def get_icon(self, name):
    if name == 'twitter_demo':
      return 'search/art/icon_twitter_48.png'
    elif name == 'yelp_demo':
      return 'search/art/icon_yelp_48.png'
    elif name == 'log_analytics_demo':
      return 'search/art/icon_logs_48.png'
    else:
      return 'search/art/icon_search_48.png'

  def delete_collections(self, collection_ids):
    result = {'status': -1, 'message': ''}
    try:
      # todo
      self.get_owner_search_collections().filter(id__in=collection_ids).delete()
      result['status'] = 0
    except Exception, e:
      LOG.warn('Error deleting collection: %s' % e)
      result['message'] = unicode(str(e), "utf8")

    return result

  def copy_collections(self, collection_ids):
    result = {'status': -1, 'message': ''}
    try:
      for collection in self.get_shared_search_collections().filter(id__in=collection_ids):
        doc2 = Document2.objects.get(type='search-dashboard', id=collection.id)

        name = doc2.name + '-copy'
        copy_doc = doc2.doc.get().copy(name=name, owner=self.user)

        doc2.pk = None
        doc2.id = None
        doc2.uuid = str(uuid.uuid4())
        doc2.name = name
        doc2.owner = self.user
        doc2.save()

        doc2.doc.all().delete()
        doc2.doc.add(copy_doc)
        doc2.save()

        copy = Collection2(document=doc2)
        copy['collection']['label'] = name

        doc2.update_data({'collection': copy['collection']})
        doc2.save()
      result['status'] = 0
    except Exception, e:
      LOG.warn('Error copying collection: %s' % e)
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
      pass

    try:
      indexes += SolrApi(SOLR_URL.get(), self.user).aliases().keys()
    except:
      pass

    if show_all or not indexes:
      return indexes + SolrApi(SOLR_URL.get(), self.user).cores().keys()
    else:
      return indexes
