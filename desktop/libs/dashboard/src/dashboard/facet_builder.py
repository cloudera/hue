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
from dateutil.relativedelta import *

from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)

MS = 1
SECOND_MS = 1000 * MS
MINUTE_MS = SECOND_MS * 60
HOUR_MS = MINUTE_MS * 60
DAY_MS = HOUR_MS * 24
WEEK_MS = DAY_MS * 7
MONTH_MS = DAY_MS * 30
YEAR_MS = DAY_MS * 365
TIME_INTERVALS_MS = {
  'MICROSECONDS': MS,
  'SECONDS': SECOND_MS,
  'MINUTES': MINUTE_MS,
  'HOURS': HOUR_MS,
  'DAYS': DAY_MS,
  'WEEKS': WEEK_MS,
  'MONTHS': MONTH_MS,
  'YEARS': YEAR_MS
}
TIME_INTERVALS_STARTING_VALUE = {
  'microsecond': 0,
  'second': 0,
  'minute': 0,
  'hour': 0,
  'day': 1,
  'month': 1,
  'year': 0
}
TIME_INTERVAL_SORTED = ['microsecond', 'second', 'minute', 'hour', 'day', 'month']
TIME_INTERVALS = [
  {'coeff': 1, 'unit': 'SECONDS'},
  {'coeff': 2, 'unit': 'SECONDS'},
  {'coeff': 5, 'unit': 'SECONDS'},
  {'coeff': 10, 'unit': 'SECONDS'},
  {'coeff': 15, 'unit': 'SECONDS'},
  {'coeff': 30, 'unit': 'SECONDS'},
  {'coeff': 1, 'unit': 'MINUTES'},
  {'coeff': 2, 'unit': 'MINUTES'},
  {'coeff': 5, 'unit': 'MINUTES'},
  {'coeff': 10, 'unit': 'MINUTES'},
  {'coeff': 15, 'unit': 'MINUTES'},
  {'coeff': 30, 'unit': 'MINUTES'},
  {'coeff': 1, 'unit': 'HOURS'},
  {'coeff': 2, 'unit': 'HOURS'},
  {'coeff': 4, 'unit': 'HOURS'},
  {'coeff': 6, 'unit': 'HOURS'},
  {'coeff': 8, 'unit': 'HOURS'},
  {'coeff': 12, 'unit': 'HOURS'},
  {'coeff': 1, 'unit': 'DAYS'},
  {'coeff': 2, 'unit': 'DAYS'},
  {'coeff': 7, 'unit': 'DAYS', 'start_relative': 'WEEKS'},
  {'coeff': 14, 'unit': 'DAYS', 'start_relative': 'WEEKS'},
  {'coeff': 1, 'unit': 'MONTHS'},
  {'coeff': 3, 'unit': 'MONTHS'},
  {'coeff': 6, 'unit': 'MONTHS'},
  {'coeff': 1, 'unit': 'YEARS'}];
for interval in TIME_INTERVALS:
  interval['ms'] = TIME_INTERVALS_MS[interval['unit']] * interval['coeff']

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
    coeff = min(ceil(domain_ms / SLOTS), 100) # If we go over 100 years, something has gone wrong.
    return {'ms': YEAR_MS * coeff, 'coeff': coeff, 'unit': 'YEARS'}

  for i in range(len(TIME_INTERVALS) - 2, 0, -1):
    slots = domain_ms / TIME_INTERVALS[i]['ms']
    if slots > SLOTS:
      return TIME_INTERVALS[i + 1]

  return TIME_INTERVALS[0]

def _format_interval(interval):
  return '+' + str(interval['coeff']) + interval['unit']

def _get_interval_duration(text):
  regex = re.search('.*-(\d*)(.*)', text)

  if regex:
    groups = regex.groups()
    if TIME_INTERVALS_MS[groups[1]]:
      return TIME_INTERVALS_MS[groups[1]] * int(groups[0])
  return 0

def _clamp_date(interval, time):
  gap_duration_lower = interval['unit'].lower()
  gap_duration_lowers = gap_duration_lower[:-1]  # Removes 's'
  for time_interval in TIME_INTERVAL_SORTED:
    if time_interval != gap_duration_lowers:
      kwargs = {time_interval: TIME_INTERVALS_STARTING_VALUE[time_interval]}
      time = time.replace(**kwargs)
    else:
      break
  return time

def _get_next_interval(interval, start_time, do_at_least_once):
  time = start_time
  if interval.get('start_relative'):
    time = time + relativedelta(weekday=MO)
  else:
    gap_duration_lower = interval['unit'].lower()
    gap_duration_lowers = gap_duration_lower[:-1]  # Removes 's'
    gap_duration = int(interval['coeff'])
    while (getattr(time, gap_duration_lowers) - TIME_INTERVALS_STARTING_VALUE[gap_duration_lowers]) % gap_duration or (do_at_least_once and time == start_time): # Do while
      kwargs = {gap_duration_lower: 1}
      time = time + relativedelta(**kwargs)

  return time

def _remove_duration(interval, nb_slot, time):
  gap_duration_lower = interval['unit'].lower()
  gap_duration = int(interval['coeff']) * nb_slot
  kwargs = {gap_duration_lower: -1 * gap_duration}
  return time + relativedelta(**kwargs)

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
      start_was_none = False
      if start is None:
        start_was_none = True
        start = stats_min
      start = re.sub('\.\d\d?\d?Z$', 'Z', start)
      try:
        start_ts = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
        start_ts.strftime('%Y-%m-%dT%H:%M:%SZ') # Check for dates before 1900
      except Exception, e:
        LOG.error('Bad date: %s' % e)
        start_ts = datetime.strptime('1970-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')

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
      domain_ms = (mktime(end_ts.timetuple()) - mktime(start_ts.timetuple())) * 1000
      interval = _get_interval(domain_ms, SLOTS)
      start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      gap = _format_interval(interval)
      if start_was_none:
        start_ts = _clamp_date(interval, start_ts)
        start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
        stats_max = end
        stats_min = start
      else:
        start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif stat_facet['max'] == 'NOW':
      is_date = True
      domain_ms = _get_interval_duration(stat_facet['min'])
      interval = _get_interval(domain_ms, SLOTS)
      nb_slot = domain_ms / interval['ms']
      gap = _format_interval(interval)
      end_ts = datetime.utcnow()
      end_ts_clamped = _clamp_date(interval, end_ts)
      end_ts = _get_next_interval(interval, end_ts_clamped, end_ts_clamped != end_ts)
      start_ts = _remove_duration(interval, nb_slot, end_ts)
      stats_max = end = end_ts.strftime('%Y-%m-%dT%H:%M:%SZ')
      stats_min = start = start_ts.strftime('%Y-%m-%dT%H:%M:%SZ')

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
    end = int(round(n, -i))
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
