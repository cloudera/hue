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
"""Utilities for views (text and number formatting, etc)"""

import math
import datetime

def big_filesizeformat(bytes):
  if bytes is None or bytes is "":
    return "N/A"

  assert bytes >= 0

  # Special case small numbers (including 0), because they're exact.
  if bytes < 1024:
    return "%d B" % bytes

  units = ["B", "KB", "MB", "GB", "TB", "PB"]
  index = int(math.floor(math.log(bytes, 1024)))
  index = min(len(units) - 1, index)

  return( "%.1f %s" % (bytes / math.pow(1024, index), units[index]) )

def format_time_diff(start=None, end=None):
  """
    formats the difference between two times as Xd:Xh:Xm:Xs
  """
  if (end is None):
    end = datetime.datetime.now()
  diff = end - start
  minutes, seconds = divmod(diff.seconds, 60)
  hours, minutes = divmod(minutes, 60)
  days = diff.days
  output = []
  written = False
  if days:
    written = True
    output.append("%dd" % days)
  if written or hours:
    written = True
    output.append("%dh" % hours)
  if written or minutes:
    output.append("%dm" % minutes)
  output.append("%ds" % seconds)
  return ":".join(output)

def format_duration_in_millis(duration=0):
    """
      formats the difference between two times in millis as Xd:Xh:Xm:Xs
    """
    seconds, millis = divmod(duration, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    output = []
    written = False
    if days:
        written = True
        output.append("%dd" % days)
    if written or hours:
        written = True
        output.append("%dh" % hours)
    if written or minutes:
        output.append("%dm" % minutes)
    output.append("%ds" % seconds)
    return ":".join(output)
