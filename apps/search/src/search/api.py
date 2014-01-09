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
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource
from search.conf import EMPTY_QUERY, SECURITY_ENABLED
from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)

DEFAULT_USER = 'hue'


class SolrApi(object):
  """
  http://wiki.apache.org/solr/CoreAdmin#CoreAdminHandler
  """
  def __init__(self, solr_url, user):
    self._url = solr_url
    self._user = user
    self._client = HttpClient(self._url, logger=LOG)
    self.security_enabled = SECURITY_ENABLED.get()
    if self.security_enabled:
      self._client.set_kerberos_auth()
    self._root = resource.Resource(self._client)

  def _get_params(self):
    if self.security_enabled:
      return (('doAs', self._user ),)
    return (('user.name', DEFAULT_USER), ('doAs', self._user),)

  def query(self, solr_query, hue_core):
    try:
      params = self._get_params() + (
          ('q', solr_query['q'] or EMPTY_QUERY.get()),
          ('wt', 'json'),
          ('rows', solr_query['rows']),
          ('start', solr_query['start']),
      )

      params += hue_core.get_query(solr_query)

      fqs = solr_query['fq'].split('|')
      for fq in fqs:
        if fq:
          params += (('fq', fq),)

      response = self._root.get('%(collection)s/select' % solr_query, params)

      if type(response) != dict:
        # Got 'plain/text' mimetype instead of 'application/json'
        try:
          response = json.loads(response)
        except ValueError, e:
          # Got some null bytes in the response
          LOG.error('%s: %s' % (unicode(e), repr(response)))
          response = json.loads(response.replace('\x00', ''))
      return response
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def suggest(self, solr_query, hue_core):
    try:
      params = self._get_params() + (
          ('q', solr_query['q']),
          ('wt', 'json'),
      )
      response = self._root.get('%(collection)s/suggest' % solr_query, params)
      if type(response) != dict:
        response = json.loads(response)
      return response
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def collections(self):
    try:
      params = self._get_params() + (
          ('detail', 'true'),
          ('path', '/clusterstate.json'),
      )
      response = self._root.get('zookeeper', params=params)
      return json.loads(response['znode']['data'])
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def collection_or_core(self, hue_collection):
    if hue_collection.is_core_only:
      return self.core(hue_collection.name)
    else:
      return self.collection(hue_collection.name)

  def collection(self, name):
    try:
      collections = self.collections()
      return collections[name]
    except Exception, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def cores(self):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      return self._root.get('admin/cores', params=params)['status']
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def core(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('core', core),
      )
      return self._root.get('admin/cores', params=params)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def schema(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('file', 'schema.xml'),
      )
      return self._root.get('%(core)s/admin/file' % {'core': core}, params=params)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
