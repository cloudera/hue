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

from django.db.models import Q

from desktop.conf import USE_NEW_EDITOR
from desktop.models import Document2, Document, SAMPLE_USER_OWNERS

from dashboard.models import Collection2

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


class DashboardController(object):

  def __init__(self, user):
    self.user = user

  def get_search_collections(self):
    if USE_NEW_EDITOR.get():
      return Document2.objects.documents(user=self.user).search_documents(types=['search-dashboard'], order_by='-id')
    else:
      return [d.content_object for d in Document.objects.get_docs(self.user, Document2, extra='search-dashboard').order_by('-id')]

  def get_shared_search_collections(self):
    # Those are the ones appearing in the menu
    if USE_NEW_EDITOR.get():
      return Document2.objects.filter(Q(owner=self.user) | Q(owner__username__in=SAMPLE_USER_OWNERS), type='search-dashboard').order_by('-id')
    else:
      docs = Document.objects.filter(Q(owner=self.user) | Q(owner__username__in=SAMPLE_USER_OWNERS), extra='search-dashboard')
      return [d.content_object for d in docs.order_by('-id')]

  def get_owner_search_collections(self):
    if USE_NEW_EDITOR.get():
      if is_admin(self.user):
        docs = Document2.objects.filter(type='search-dashboard')
      else:
        docs = Document2.objects.filter(type='search-dashboard', owner=self.user)
      return docs
    else:
      if is_admin(self.user):
        docs = Document.objects.filter(extra='search-dashboard')
      else:
        docs = Document.objects.filter(extra='search-dashboard', owner=self.user)
      return [d.content_object for d in docs.order_by('-id')]

  def get_icon(self, name):
    if name == 'Twitter':
      return 'dashboard/art/icon_twitter_48.png'
    elif name == 'Yelp Reviews':
      return 'dashboard/art/icon_yelp_48.png'
    elif name == 'Web Logs':
      return 'dashboard/art/icon_logs_48.png'
    else:
      return 'dashboard/art/icon_search_48.png'

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
          doc2 = Document2.objects.get_by_uuid(user=self.user, uuid=doc2.uuid)
          doc = doc2.doc.get()

          name = doc2.name + '-copy'
          doc2 = doc2.copy(name=name, owner=self.user)

          doc.copy(content_object=doc2, name=name, owner=self.user)

          collection = Collection2(self.user, document=doc2)
          collection.data['collection']['label'] = name

          doc2.update_data({'collection': collection.data['collection']})
          doc2.save()
      result['status'] = 0
    except Exception, e:
      LOG.exception('Error copying collection')
      result['message'] = unicode(str(e), "utf8")

    return result


def can_edit_index(user): # Deprecated by Sentry now
  return True
