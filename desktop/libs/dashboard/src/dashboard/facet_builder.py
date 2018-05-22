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
from math import ceil
from math import log
from time import mktime

from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)

MS = 1
SECOND_MS = 1000 * MS
MINUTE_MS = SECOND_MS * 60
HOUR_MS = MINUTE_MS * 60
DAY_MS = HOUR_MS * 24
WEEK_MS = DAY_MS * 7
MONTH_MS = DAY_MS * 30.5
YEAR_MS = DAY_MS * 365
TIME_INTERVALS = [
  {'ms': SECOND_MS * 1, 'coeff': '1', 'unit': 'SECONDS'},
  {'ms': SECOND_MS * 2, 'coeff': '2', 'unit': 'SECONDS'},
  {'ms': SECOND_MS * 5, 'coeff': '5', 'unit': 'SECONDS'},
  {'ms': SECOND_MS * 10, 'coeff': '10', 'unit': 'SECONDS'},
  {'ms': SECOND_MS * 15, 'coeff': '15', 'unit': 'SECONDS'},
  {'ms': SECOND_MS * 30, 'coeff': '30', 'unit': 'SECONDS'},
  {'ms': MINUTE_MS * 1, 'coeff': '1', 'unit': 'MINUTES'},
  {'ms': MINUTE_MS * 2, 'coeff': '2', 'unit': 'MINUTES'},
  {'ms': MINUTE_MS * 5, 'coeff': '5', 'unit': 'MINUTES'},
  {'ms': MINUTE_MS * 10, 'coeff': '10', 'unit': 'MINUTES'},
  {'ms': MINUTE_MS * 15, 'coeff': '15', 'unit': 'MINUTES'},
  {'ms': MINUTE_MS * 30, 'coeff': '30', 'unit': 'MINUTES'},
  {'ms': HOUR_MS * 1, 'coeff': '1', 'unit': 'HOURS'},
  {'ms': HOUR_MS * 2, 'coeff': '2', 'unit': 'HOURS'},
  {'ms': HOUR_MS * 4, 'coeff': '4', 'unit': 'HOURS'},
  {'ms': HOUR_MS * 6, 'coeff': '6', 'unit': 'HOURS'},
  {'ms': HOUR_MS * 8, 'coeff': '8', 'unit': 'HOURS'},
  {'ms': HOUR_MS * 12, 'coeff': '12', 'unit': 'HOURS'},
  {'ms': DAY_MS * 1, 'coeff': '1', 'unit': 'DAYS'},
  {'ms': DAY_MS * 2, 'coeff': '2', 'unit': 'MONTHS'},
  {'ms': WEEK_MS * 1, 'coeff': '7', 'unit': 'DAYS'},
  {'ms': WEEK_MS * 2, 'coeff': '14', 'unit': 'DAYS'},
  {'ms': MONTH_MS * 1, 'coeff': '1', 'unit': 'MONTHS'},
  {'ms': MONTH_MS * 2, 'coeff': '2', 'unit': 'MONTHS'},
  {'ms': MONTH_MS * 3, 'coeff': '3', 'unit': 'MONTHS'},
  {'ms': MONTH_MS * 6, 'coeff': '6', 'unit': 'MONTHS'},
  {'ms': YEAR_MS * 1, 'coeff': '1', 'unit': 'YEARS'}];
TIME_INTERVALS_MS = {
  'SECONDS': SECOND_MS,
  'MINUTES': MINUTE_MS,
  'HOURS': HOUR_MS,
  'DAYS': DAY_MS,
  'WEEKS': WEEK_MS,
  'MONTHS': MONTH_MS,
  'YEARS': YEAR_MS
}

def utf_quoter(what):
  return urllib.quote(unicode(what).encode('utf-8'), safe='~@#$&()*!+=:;,.?/\'')


def _guess_range_facet(widget_type, solr_api, collection, facet_field, properties, start=None, end=None, gap=None, window_size=None, slot = 0):
  try:
    stats_json = solr_api.stats(collection['name'], [facet_field])
    stat_facet = stats_json['stats']['stats_fields'][facet_field]

    _compute_range_facet(widget_type, stat_facet, properties, start, end, gap, window_size = window_size, SLOTS = slot)
  except Exception, e:
    print e
    LOG.info('Stats not supported on all the fields, like text: %s' % e)


def _get_interval(domain_ms, SLOTS):
  biggest_interval = TIME_INTERVALS[len(TIME_INTERVALS) - 1]
  biggest_interval_is_too_small = domain_ms / biggest_interval['ms'] > SLOTS
  if biggest_interval_is_too_small:
    coeff = ceil(domain_ms / SLOTS)
    return '+' + coeff + 'YEARS'

  for i in range(len(TIME_INTERVALS) - 2, 0, -1):
    slots = domain_ms / TIME_INTERVALS[i]['ms']
    if slots > SLOTS:
      return '+' + TIME_INTERVALS[i + 1]['coeff'] + TIME_INTERVALS[i + 1]['unit']

  return '+' + TIME_INTERVALS[0]['coeff'] + TIME_INTERVALS[0]['unit'];

def _get_interval_duration(text):
  regex = re.search('.*-(\d*)(.*)', text)

  if regex:
    groups = regex.groups()
    if TIME_INTERVALS_MS[groups[1]]:
      return TIME_INTERVALS_MS[groups[1]] * int(groups[0])
  return 0

def _compute_range_facet(widget_type, stat_facet, properties, start=None, end=None, gap=None, SLOTS=0, window_size=None):
    if SLOTS == 0:
      if widget_type == 'pie-widget' or widget_type == 'pie2-widget':
        SLOTS = 5
      elif widget_type == 'facet-widget' or widget_type == 'text-facet-widget' or widget_type == 'histogram-widget' or widget_type == 'bar-widget' or widget_type == 'bucket-widget' or widget_type == 'timeline-widget':
        if window_size:
          SLOTS = int(window_size) / 75 # Value is determined as the thinnest space required to display a timestamp on x axis
        else:
          SLOTS = 10
      else:
        SLOTS = 100

    is_date = widget_type == 'timeline-widget'

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

      end = max(end, stats_max)
    elif re.match('\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d\d?\d?)?Z', stat_facet['min']):
      is_date = True
      stats_min = stat_facet['min']
      stats_max = stat_facet['max']
      if start is None:
        start = stats_min
      start = re.sub('\.\d\d?\d?Z$', 'Z', start)
      try:
        start_ts = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
        start_ts.strftime('%Y-%m-%dT%H:%M:%SZ') # Check for dates before 1900
      except Exception, e:
        LOG.error('Bad date: %s' % e)
        start_ts = datetime.strptime('1970-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
      start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      stats_min = min(stats_min, start)
      if end is None:
        end = stats_max
      end = re.sub('\.\d\d?\d?Z$', 'Z', end)
      try:
        end_ts = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
        end_ts.strftime('%Y-%m-%dT%H:%M:%SZ') # Check for dates before 1900
      except Exception, e:
        LOG.error('Bad date: %s' % e)
        end_ts = datetime.strptime('2050-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
      end = end_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      stats_max = max(stats_max, end)
      domain_ms = (mktime(end_ts.timetuple()) - mktime(start_ts.timetuple())) * 1000

      gap = _get_interval(domain_ms, SLOTS)
    elif stat_facet['max'] == 'NOW':
      is_date = True
      domain_ms = _get_interval_duration(stat_facet['min'])
      start = stat_facet['min']
      end = stat_facet['max']
      stats_min = start
      stats_max = end
      gap = _get_interval(domain_ms, SLOTS)

    properties.update({
      'min': stats_min,
      'max': stats_max,
      'start': start,
      'end': end,
      'gap': gap,
      'slot': SLOTS,
      'canRange': True,
      'isDate': is_date,
    })

    if widget_type == 'histogram-widget':
      properties.update({
        'timelineChartType': 'bar',
        'enableSelection': True
      })


def _round_date_range(tm):
  start = tm - timedelta(seconds=tm.second, microseconds=tm.microsecond)
  end = start + timedelta(seconds=60)
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
  _guess_range_facet(facet['widgetType'], solr_api, collection, facet['field'], properties, start=start, end=end, slot = facet.get('properties', facet)['slot'])
  return properties


def _new_range_facet(solr_api, collection, facet_field, widget_type, window_size):
  properties = {}
  _guess_range_facet(widget_type, solr_api, collection, facet_field, properties, window_size = window_size)
  return properties


def _zoom_range_facet(solr_api, collection, facet, direction='out'):
  properties = {}
  _guess_range_facet(facet['widgetType'], solr_api, collection, facet['field'], properties)
  return properties
