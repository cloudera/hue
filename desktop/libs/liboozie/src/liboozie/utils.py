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

"""
Misc helper functions
"""
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
from past.builtins import basestring

import logging
import re
import sys
import time

from datetime import datetime
from dateutil.parser import parse
from time import strftime
from xml.sax.saxutils import escape

if sys.version_info[0] > 2:
  from io import StringIO as string_io
  new_str = str
else:
  try:
    from cStringIO import StringIO as string_io
  except:
    from StringIO import StringIO as string_io
  new_str = unicode

LOG = logging.getLogger()
_NAME_REGEX = re.compile('^[a-zA-Z][\-_a-zA-Z0-0]*$')


def catch_unicode_time(u_time):
  if type(u_time) == time.struct_time:
    return u_time
  else:
    return datetime.timetuple(parse(u_time))


def parse_timestamp(timestamp, time_format=None):
  """
  parse_timestamp(timestamp, time_format=None) -> struct_time

  Does NOT raise ValueError. Return None on formatting error.
  """
  if time_format is None:
    time_format = '%a, %d %b %Y %H:%M:%S %Z'
  try:
    return time.strptime(timestamp, time_format)
  except ValueError:
    try:
      return time.strptime(re.sub(' \w+$', '', timestamp), time_format.replace(' %Z', ''))
    except ValueError:
      LOG.error("Failed to convert Oozie timestamp: %s" % time_format)
  except Exception:
    LOG.error("Failed to convert Oozie timestamp: %s" % time_format)
  return None


def config_gen(dic):
  """
  config_gen(dic) -> xml for Oozie workflow configuration
  """
  sio = string_io()
  print('<?xml version="1.0" encoding="UTF-8"?>', file=sio)
  print("<configuration>", file=sio)
  # if dic's key contains <,>,& then it will be escaped and if dic's value contains ']]>' then ']]>' will be stripped
  for k, v in sorted(dic.items()):
    print("<property>\n  <name>%s</name>\n  <value><![CDATA[%s]]></value>\n</property>\n" \
        % (escape(k), v.replace(']]>', '') if isinstance(v, basestring) else v), file=sio)
  print("</configuration>", file=sio)
  sio.flush()
  sio.seek(0)
  return sio.read()


def is_valid_node_name(name):
  return _NAME_REGEX.match(name) is not None

def format_time(time, format='%d %b %Y %H:%M:%S'):
  if time is None:
    return ''

  fmt_time = None
  if type(time) == new_str:
    return time
  else:
    try:
      fmt_time = strftime(format, time)
    except:
      fmt_time = None

    if fmt_time is None:
      try:
        fmt_time = strftime(format+" %f", time)
      except:
        fmt_time = None

    return fmt_time
