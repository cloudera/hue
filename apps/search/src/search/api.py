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
import numbers
import urllib
import re

from datetime import datetime, timedelta
from math import log
from time import mktime

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import RestException
from django.utils.translation import ugettext as _

from libsolr.api import SolrApi as BaseSolrApi

from search.conf import EMPTY_QUERY, SECURITY_ENABLED


LOG = logging.getLogger(__name__)

DEFAULT_USER = 'hue'


def utf_quoter(what):
  return urllib.quote(unicode(what).encode('utf-8'), safe='~@#$&()*!+=:;,.?/\'')

def _guess_range_facet(widget_type, solr_api, collection, facet_field, properties, start=None, end=None, gap=None):
  try:
    if widget_type == 'pie-widget':
      SLOTS = 5
    elif widget_type == 'facet-widget':
      SLOTS = 10
    else:
      SLOTS = 100
      
    stats_json = solr_api.stats(collection['name'], [facet_field])
    stat_facet = stats_json['stats']['stats_fields'][facet_field]
    
    # to refactor
    if isinstance(stat_facet['min'], numbers.Number):
      stats_min = int(stat_facet['min']) # Cast floats to int currently
      stats_max = int(stat_facet['max'])
      if start is None:
        if widget_type == 'line-widget':
          start, _ = _round_thousand_range(stats_min)
        else:        
          start, _ =  _round_number_range(stats_min)
      else:
        start = int(start)
      if end is None:
        if widget_type == 'line-widget':
          _, end = _round_thousand_range(stats_max)
        else:
          _, end = _round_number_range(stats_max)        
      else:
        end = int(end)

      if gap is None:
        gap = int((end - start) / SLOTS)      
      if gap < 1:
        gap = 1
    elif 'T' in stat_facet['min']:
      stats_min = stat_facet['min']
      stats_max = stat_facet['max']
      if start is None:
        start = stats_min 
      start = re.sub('\.\d\d?\d?Z$', 'Z', start)
      start_ts = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
      start_ts, _ = _round_date_range(start_ts)
      start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      if end is None:
        end = stats_max
      end = re.sub('\.\d\d?\d?Z$', 'Z', end)
      end_ts = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
      _, end_ts = _round_date_range(end_ts)
      end = end_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      difference = (
          mktime(end_ts.timetuple()) - 
          mktime(start_ts.timetuple())
      ) / SLOTS

      if difference < 1:
        gap = '+1SECONDS'
      elif difference < 100:
        gap = '+1MINUTES'
      elif difference < 60 * 5:
        gap = '+5MINUTES'
      elif difference < 60 * 10:
        gap = '+10MINUTES'
      elif difference < 60 * 30:
        gap = '+30MINUTES'                
      elif difference < 3600:
        gap = '+1HOURS'
      elif difference < 3600 * 3:
        gap = '+3HOURS'
      elif difference < 3600 * 12:
        gap = '+12HOURS'
      elif difference < 3600 * 24:
        gap = '+1DAYS'
      elif difference < 3600 * 24 * 7:
        gap = '+7DAYS'        
      elif difference < 3600 * 24 * 30:
        gap = '+1MONTHS'        
      else:
        gap = '+1YEARS'      

    properties.update({
      'min': stats_min,
      'max': stats_max,
      'start': start,
      'end': end,
      'gap': gap,
      'canRange': True,
    })
  except Exception, e:
    print e
    # stats not supported on all the fields, like text
    pass

def _round_date_range(tm):
  start = tm - timedelta(minutes=tm.minute, seconds=tm.second, microseconds=tm.microsecond)
  end = start + timedelta(minutes=60)  
  return start, end

def _round_number_range(n):
  if n <= 10:
    return n, n + 1
  else:
    i = int(log(n, 10))
    end = round(n, -i)
    start = end - 10 ** i
    return start, end 

def _round_thousand_range(n):
  if n <= 10:
    return 0, 0
  else:
    i = int(log(n, 10))
    start = 10 ** i
    end = 10 ** (i + 1)
    return start, end 

def _guess_gap(solr_api, collection, facet, start=None, end=None):
  properties = {}
  _guess_range_facet(facet['widgetType'], solr_api, collection, facet['field'], properties, start=start, end=end)
  return properties


def _new_range_facet(solr_api, collection, facet_field, widget_type):
  properties = {}
  _guess_range_facet(widget_type, solr_api, collection, facet_field, properties)
  return properties


def _zoom_range_facet(solr_api, collection, facet, direction='out'):
  properties = {}
  _guess_range_facet(facet['widgetType'], solr_api, collection, facet['field'], properties)
  return properties


class SolrApi(BaseSolrApi):
  """
  http://wiki.apache.org/solr/CoreAdmin#CoreAdminHandler
  """
  def __init__(self, solr_url, user):
    super(SolrApi, self).__init__(solr_url, user, SECURITY_ENABLED.get())

  def _get_params(self):
    if self.security_enabled:
      return (('doAs', self._user ),)
    return (('user.name', DEFAULT_USER), ('doAs', self._user),)

  #@demo_handler
  def query(self, collection, query):
    solr_query = {}      
    
    solr_query['collection'] = collection['name']
    solr_query['rows'] = min(int(collection['template']['rows'] or 10), 1000)
    solr_query['start'] = min(int(query['start']), 10000)
    
    q_template = '(%s)' if len(query['qs']) >= 2 else '%s'
          
    params = self._get_params() + (
        ('q', 'OR'.join([q_template % (q['q'] or EMPTY_QUERY.get()) for q in query['qs']])),
        ('wt', 'json'),
        ('rows', solr_query['rows']),
        ('start', solr_query['start']),
    )

    if any(collection['facets']):
      params += (
        ('facet', 'true'),
        ('facet.mincount', 0),
        ('facet.limit', 10),
      )
      for facet in collection['facets']:
        if facet['type'] == 'query':
          params += (('facet.query', '%s' % facet['field']),)          
        elif facet['type'] == 'range':
          params += tuple([
             ('facet.range', '{!ex=%s}%s' % (facet['field'], facet['field'])),
             ('f.%s.facet.range.start' % facet['field'], facet['properties']['start']),
             ('f.%s.facet.range.end' % facet['field'], facet['properties']['end']),
             ('f.%s.facet.range.gap' % facet['field'], facet['properties']['gap']),
             ('f.%s.facet.mincount' % facet['field'], facet['properties']['mincount']),]
          )          
        elif facet['type'] == 'field':
          params += (
              ('facet.field', '{!ex=%s}%s' % (facet['field'], facet['field'])),
              ('f.%s.facet.limit' % facet['field'], int(facet['properties'].get('limit', 10)) + 1),
              ('f.%s.facet.mincount' % facet['field'], int(facet['properties']['mincount'])),
          )

    for fq in query['fqs']:
      if fq['type'] == 'field':
        # This does not work if spaces in Solr: 
        # params += (('fq', ' '.join([urllib.unquote(utf_quoter('{!tag=%s}{!field f=%s}%s' % (fq['field'], fq['field'], _filter))) for _filter in fq['filter']])),)
        f = []
        for _filter in fq['filter']:          
          if _filter is not None and ' ' in _filter:
            f.append('%s:"%s"' % (fq['field'], _filter))
          else:
            f.append('{!field f=%s}%s' % (fq['field'], _filter))
        params += (('fq', urllib.unquote(utf_quoter('{!tag=%s}' % fq['field'] + ' '.join(f)))),)
      elif fq['type'] == 'range':
        params += (('fq', '{!tag=%s}' % fq['field'] + ' '.join([urllib.unquote(utf_quoter('%s:[%s TO %s}' % (fq['field'], f['from'], f['to']))) for f in fq['properties']])),)

    if collection['template']['fieldsSelected'] and collection['template']['isGridLayout']:
      fields = collection['template']['fieldsSelected'] + [collection['idField']] if collection['idField'] else []
      params += (('fl', urllib.unquote(utf_quoter(','.join(fields)))),)
    else:
      params += (('fl', '*'),)

    params += (
      ('hl', 'true'),
      ('hl.fl', '*'),
      ('hl.snippets', 3)
    )

    if collection['template']['fieldsSelected']:
      fields = []
      for field in collection['template']['fieldsSelected']:
        attribute_field = filter(lambda attribute: field == attribute['name'], collection['template']['fieldsAttributes'])
        if attribute_field:
          if attribute_field[0]['sort']['direction']:
            fields.append('%s %s' % (field, attribute_field[0]['sort']['direction']))
      if fields:
        params += (         
          ('sort', ','.join(fields)),
        )

    response = self._root.get('%(collection)s/select' % solr_query, params)

    return self._get_json(response)


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
      return json.loads(response['znode'].get('data', '{}'))
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

  def fields(self, core, dynamic=False):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
          ('fl', '*'),
      )
      if not dynamic:
        params += (('show', 'schema'),)
      response = self._root.get('%(core)s/admin/luke' % {'core': core}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def luke(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%(core)s/admin/luke' % {'core': core}, params=params)
      return self._get_json(response)    
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def schema_fields(self, core):
    try:
      params = self._get_params() + (
          ('wt', 'json'),
      )
      response = self._root.get('%(core)s/schema/fields' % {'core': core}, params=params)
      return self._get_json(response)    
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
    
  def stats(self, core, fields):
    try:
      params = (
          ('q', EMPTY_QUERY.get()),
          ('wt', 'json'),
          ('rows', 0),
          ('stats', 'true'),
      )      
      params += tuple([('stats.field', field) for field in fields])
      response = self._root.get('%(core)s/select' % {'core': core}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))

  def get(self, core, doc_id):
    try:
      params = (
          ('id', doc_id),
          ('wt', 'json'),
      )      
      response = self._root.get('%(core)s/get' % {'core': core}, params=params)
      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
