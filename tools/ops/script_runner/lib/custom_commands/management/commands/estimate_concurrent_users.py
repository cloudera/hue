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

import os
import re
import sys
import logging
import heapq
import datetime
import time
import subprocess
from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError

import desktop.conf
from desktop.conf import TIME_ZONE
from search.conf import SOLR_URL, SECURITY_ENABLED as SOLR_SECURITY_ENABLED
from liboozie.conf import OOZIE_URL, SECURITY_ENABLED as OOZIE_SECURITY_ENABLED
from hadoop import conf as hdfs_conf
from hadoop import cluster

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

DEFAULT_LOG_DIR = 'logs'
log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)

class Command(BaseCommand):
  """
  Handler for renaming duplicate User objects
  """

  try:
    from optparse import make_option
    option_list = BaseCommand.option_list + (
      make_option("--today", help=_t("Estimate users for today."),
                  action="store_true", default=False, dest='today'),
      make_option("--logdir", help=_t("Specify directory to process access logs."),
                  action="store", default=log_dir, dest='logdir'),
      make_option("--increment", help=_t("Increments to count users, hour, min10, day"),
                  action="store", default="day", dest='increment'),
      make_option("--date", help=_t("Estimate users for date.  In form of YYYY-MM-DD"),
                  action="store", default=False, dest='date'),
      make_option("--last10", help=_t("Process logs for last 10 minutes."),
                  action="store_true", default=False, dest='last10'),
      make_option("--last1h", help=_t("Process logs for last hour."),
                  action="store_true", default=False, dest='last1h'),
      make_option("--includejb", help=_t("Include Jobbrowser entries."),
                  action="store_true", default=False, dest='includejb'),
      make_option("--verbose", help=_t("Verbose."),
                  action="store_true", default=False, dest='verbose'),
    )

  except AttributeError, e:
    baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
    if baseoption_test:
      def add_arguments(self, parser):
        parser.add_argument("--today", help=_t("Estimate users for today."),
                    action="store_true", default=False, dest='today'),
        parser.add_argument("--logdir", help=_t("Specify directory to process access logs."),
                    action="store", default=log_dir, dest='logdir'),
        parser.add_argument("--increment", help=_t("Increments to count users, hour, min10, day"),
                    action="store", default="day", dest='increment'),
        parser.add_argument("--date", help=_t("Estimate users for date.  In form of YYYY-MM-DD"),
                    action="store", default=False, dest='date'),
        parser.add_argument("--last10", help=_t("Process logs for last 10 minutes."),
                    action="store_true", default=False, dest='last10'),
        parser.add_argument("--last1h", help=_t("Process logs for last hour."),
                    action="store_true", default=False, dest='last1h'),
        parser.add_argument("--includejb", help=_t("Include Jobbrowser entries."),
                    action="store_true", default=False, dest='includejb'),
        parser.add_argument("--verbose", help=_t("Verbose."),
                    action="store_true", default=False, dest='verbose')
    else:
      logging.warn(str(e))
      sys.exit(1)

  def handle(self, *args, **options):
    if options['date']:
      now = datetime.datetime.strptime(options['date'], '%Y-%m-%d')
    else:
      now = datetime.datetime.now()
      minus10 = now - datetime.timedelta(minutes=10)
      minus1h = now - datetime.timedelta(minutes=60)

    date = now - datetime.timedelta(days=1999)
    previous_date = now - datetime.timedelta(days=2000)
    totalconcurrent = 0
    userlist = []
    numlist = []

    regex = re.compile(
      # Example line
      # [20/Jun/2017 04:40:07 -0700] DEBUG    172.31.112.36 -anon- - "HEAD /desktop/debug/is_alive HTTP/1.1"
      r'\['
      r'(?P<date>'
      r'\d{2}/\w{3}/\d{4} '  # Parse Date in form of '25/Oct/2015'
      r'\d{2}:\d{2}:\d{2}'  # Parse Time in form of '12:34:56'
      r') '
      r'[-+]?\d{4}'  # Ignore the timezone
      r'\] '
      r'(?P<level>\w+) +'
      r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) '
      r'(?P<user>\w+) '
      r'\S+ "'  # Ignore unknown
      r'(?P<method>\w+) '
      r'(?P<url>\S+) '
    )

    for filename in sorted(os.listdir(options['logdir']), reverse=True):
      if not filename.startswith("access"):
        continue  # Only process access log files

      for line in open(options['logdir'] + "/" + filename).xreadlines():
        if not line.startswith("["):
          continue  # Only process lines that start with a date

        # Make sure this log entry is a user access
        m = regex.match(line)
        if m:
          previous_date = date
          date = datetime.datetime.strptime(m.group('date'), '%d/%b/%Y %H:%M:%S')

          if not options['includejb']:
            if re.match(m.group('url'), '/jobbrowser/jobs/$'):
              continue

          if options['today']:
            if \
                    date.year != now.year or \
                            date.month != now.month or \
                            date.day != now.day:
              continue

          if options['last10']:
            # Skip anything older than 10 mins ago
            if date < minus10:
              continue

          if options['last1h']:
            # Skip anything older than 1 hour ago
            if date < minus1h:
              continue

          user = m.group('user')

          if previous_date.day == date.day:
            if not user == "-anon-":
              userlist.append(user)
          else:
            newuserlist = list(OrderedDict.fromkeys(userlist))
            userlist = []
            totalconcurrent = len(newuserlist)
            numlist.append(totalconcurrent)

    newuserlist = list(OrderedDict.fromkeys(userlist))
    totalconcurrent = len(newuserlist)
    numlist.append(totalconcurrent)
    # Sort the list and remove any unique values
    numlist = sorted(set(numlist))
    # Print the top 10 most concurrent counts
    logging.warn("largest: %s" % heapq.nlargest(10, numlist))
    # print "newuserlist: %s" % newuserlist
    # print "userlist: %s" % userlist
