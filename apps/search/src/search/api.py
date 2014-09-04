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
import numbers
import urllib
import re

from datetime import datetime, timedelta
from math import log
from time import mktime

from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)


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
    is_date = False

    if isinstance(stat_facet['min'], numbers.Number):
      stats_min = int(stat_facet['min']) # Cast floats to int currently
      stats_max = int(stat_facet['max'])
      if start is None:
        if widget_type == 'line-widget':
          start, _ = _round_thousand_range(stats_min)
        else:
          start, _ = _round_number_range(stats_min)
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
      is_date = True
      stats_min = stat_facet['min']
      stats_max = stat_facet['max']
      if start is None:
        start = stats_min
      start = re.sub('\.\d\d?\d?Z$', 'Z', start)
      try:
        start_ts = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
      except Exception, e:
        LOG.error('Bad date: %s' % e)
        start_ts = datetime.strptime('1970-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
      start_ts, _ = _round_date_range(start_ts)
      start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      stats_min = min(stats_min, start)
      if end is None:
        end = stats_max
      end = re.sub('\.\d\d?\d?Z$', 'Z', end)
      try:
        end_ts = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
      except Exception, e:
        LOG.error('Bad date: %s' % e)
        end_ts = datetime.strptime('2050-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
      _, end_ts = _round_date_range(end_ts)
      end = end_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      stats_max = max(stats_max, end)
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
      elif difference < 3600 * 24 * 40:
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
      'isDate': is_date,
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
