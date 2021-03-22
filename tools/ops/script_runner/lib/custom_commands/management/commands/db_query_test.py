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
import sys
import time
import datetime
import re
import logging

from django.core.management.base import BaseCommand, CommandError
from django.db.backends.oracle.base import Oracle_datetime
from django.db import connection

import desktop.conf

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
  """
  Handler for running queries from Hue log with database_logging queries
  """

  try:
      from optparse import make_option
      option_list = BaseCommand.option_list + (
          make_option("--read-log-file", help=_t("Log file to scan for queries to be run "
                                                 "from database_logging = true."),
                      action="store",
                      default='/var/log/hue/runcpserver.log'),
          make_option("--start-url", help=_t("NOT WORKING: Hue URL to search for in the logs as a starting"
                                             "point, uses the most recent instance. Requires --end-url"),
                      action="store"),
          make_option("--end-url", help=_t("NOT WORKING: Hue URL to search for in the logs as an ending"
                                           "point, uses the most recent instance. Requires --start-url"),
                      action="store"),
          make_option("--start-time", help=_t("Start time to search for queries in log, format:"
                                              '%d/%b/%Y %H:%M:%S IE: 01/Jan/2018 00:00:00: This is'
                                              'standard Hue log format'),
                      action="store",
                      default=(datetime.datetime.now() - datetime.timedelta(minutes=2))),
          make_option("--end-time", help=_t("End time to search for queries in log, format:"
                                            '%d/%b/%Y %H:%M:%S IE: 01/Jan/2018 00:00:00: This is'
                                            'standard Hue log format'),
                      action="store",
                      default=(datetime.datetime.now())),
      )

  except AttributeError, e:
      baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
      if baseoption_test:
          def add_arguments(self, parser):
              parser.add_argument("--read-log-file", help=_t("Log file to scan for queries to be run "
                                                 "from database_logging = true."),
                      action="store",
                      default='/var/log/hue/runcpserver.log'),
              parser.add_argument("--start-url", help=_t("NOT WORKING: Hue URL to search for in the logs as a starting"
                                             "point, uses the most recent instance. Requires --end-url"),
                      action="store"),
              parser.add_argument("--end-url", help=_t("NOT WORKING: Hue URL to search for in the logs as an ending"
                                           "point, uses the most recent instance. Requires --start-url"),
                      action="store"),
              parser.add_argument("--start-time", help=_t("Start time to search for queries in log, format:"
                                              '%d/%b/%Y %H:%M:%S IE: 01/Jan/2018 00:00:00: This is'
                                              'standard Hue log format'),
                      action="store",
                      default=(datetime.datetime.now() - datetime.timedelta(minutes=2))),
              parser.add_argument("--end-time", help=_t("End time to search for queries in log, format:"
                                            '%d/%b/%Y %H:%M:%S IE: 01/Jan/2018 00:00:00: This is'
                                            'standard Hue log format'),
                      action="store",
                      default=(datetime.datetime.now()))
      else:
          LOG.exception(str(e))
          sys.exit(1)

  def handle(self, *args, **options):
    LOG.warn("Running database queries in file: %s: starting from: %s" % (options['read_log_file'], options['start_time']))

    start = time.time()

    oracleDatetimeRegex = re.compile(r"Oracle_datetime\([0-9,\ ]*\)")
    paramsFixRegex = re.compile(r",\ ")
    trueFixRegex = re.compile(r"True")
    falseFixRegex = re.compile(r"False")

    count = 1
    with open(options['read_log_file'], 'rU') as f:
      for line in f:
         if "QUERY" in line:
           junk, dateTemp = line.split('[')
           dateTemp = dateTemp.split(" ")
           if isinstance(options['start_time'], basestring):
             start_time = datetime.datetime.strptime(options['start_time'], "%d/%b/%Y %H:%M:%S")
           else:
             start_time = options['start_time']
           if isinstance(options['end_time'], basestring):
             end_time = datetime.datetime.strptime(options['end_time'], "%d/%b/%Y %H:%M:%S")
           else:
             end_time = options['end_time']
           log_time = datetime.datetime.strptime(dateTemp[0] + " " + dateTemp[1], "%d/%b/%Y %H:%M:%S")
           if start_time <= log_time <= end_time:
             queryStart = time.time()
             line = oracleDatetimeRegex.sub("PLACEHOLDER", line)
             junk, query = line.split("QUERY = u'")
             query, param_base = query.split("' - PARAMS = (")
             params, junk = param_base.split(");")

             if params.endswith(','):
               params = params[:-1]

             params = paramsFixRegex.sub(",", params)
             params = params.split(',')

             loopCount = len(params) - 1
             while(loopCount >= 0):
               i = loopCount
               loopCount = loopCount - 1
               updateArgsRegex = re.compile(r":arg%d" % i)
               if params[i] == "PLACEHOLDER":
                 query = updateArgsRegex.sub("'%s'" % Oracle_datetime.from_datetime(datetime.datetime.now()), query)
               else:
                 if "oracle" in desktop.conf.DATABASE.ENGINE.get():
                   params[i] = trueFixRegex.sub("1", params[i], re.IGNORECASE)
                   params[i] = falseFixRegex.sub("0", params[i], re.IGNORECASE)
               query = updateArgsRegex.sub(params[i], query)

             cursor = connection.cursor()
             cursor.execute(query)
             try:
               row = cursor.fetchone()
             except:
               LOG.warn("EXCEPTION: fetchone failed for query: %s" % query)

#              FETCH MANY MAY BE NEEDED
#              rows = cursor.fetchmany(GET_ITERATOR_CHUNK_SIZE)
#              while rows:
#                  rows = cursor.fetchmany(GET_ITERATOR_CHUNK_SIZE)

             count = count + 1
             queryEnd = time.time()
             queryElapsed = (queryEnd - queryStart)
             LOG.debug("Query time elapsed (seconds): %s: query: %s" % (queryElapsed, query))
             LOG.debug("")

    end = time.time()
    elapsed = (end - start)
    LOG.debug("Total queries: %s: time elapsed (seconds): %.2f" % (count, elapsed))
