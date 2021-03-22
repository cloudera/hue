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
import logging
import datetime
import time

from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User

import desktop.conf

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

logging.basicConfig()
LOG = logging.getLogger(__name__)

class Command(BaseCommand):
  """
  Handler for renaming duplicate User objects
  """

  try:
    from optparse import make_option
    option_list = BaseCommand.option_list + (
      make_option("--hive", help=_t("Run Hive query."),
                  action="store_true", default=False, dest='runhive'),
      make_option("--impala", help=_t("Run Impala query."),
                  action="store_true", default=True, dest='runimpala'),
      make_option("--username", help=_t("User to run query as."),
                  action="store", default="admin", dest='username'),
      make_option("--query", help=_t("Query to run."),
                  action="store", default="select * from default.sample_07;", dest='query'),
    )

  except AttributeError, e:
    baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
    if baseoption_test:
      def add_arguments(self, parser):
        parser.add_argument("--hive", help=_t("Run Hive query."),
                    action="store_true", default=False, dest='runhive'),
        parser.add_argument("--impala", help=_t("Run Impala query."),
                    action="store_true", default=True, dest='runimpala'),
        parser.add_argument("--username", help=_t("User to run query as."),
                    action="store", default="admin", dest='username'),
        parser.add_argument("--query", help=_t("Query to run."),
                    action="store", default="select * from default.sample_07;", dest='query')

    else:
      LOG.exception(str(e))
      sys.exit(1)


  def handle(self, *args, **options):
    hue, created = User.objects.get_or_create(username=options['username'])
    if options['runhive']:
      query_backend = 'hive'
      from beeswax.server import dbms
      from beeswax.conf import HIVE_SERVER_HOST
      SERVER_HOST = HIVE_SERVER_HOST
      db = dbms.get(hue)
    else:
      query_backend = 'impala'
      from impala import conf
      from impala import dbms
      from beeswax.server import dbms as beeswax_dbms
      SERVER_HOST = conf.SERVER_HOST.get()
      query_server = dbms.get_query_server_config()
      db = beeswax_dbms.get(hue, query_server=query_server)

    LOG.info("QUERY_BACKEND: %s" % query_backend)
    LOG.info("QUERY_USER: %s" % options['username'])
    LOG.info("QUERY: %s" % options['query'])
    LOG.info("QUERY_HOST: %s" % SERVER_HOST)

    start = time.time()

    db.get_tables()

    executequery = options['query']
    query = db.execute_statement(executequery)

    LOG.info(db.get_log(query.get_handle()))

    while True:
      ret = db.get_state(query.get_handle())
      try:
        LOG.info("ret.key: %s" % ret.key)
        LOG.info("ret: %s" % ret)
        if ret.key != 'running':
          break
      except AttributeError:
#    submitted = 0
#    running = 1
#    available = 2
#    failed = 3
#    expired = 4
        LOG.info("ret: %s" % ret.value)
        if ret.value != 1:
          break
        pass
      time.sleep(1)
      LOG.info("Waiting for query execution")

    result = db.fetch(query.get_handle())

    i = 0
    for row in result.rows():
      LOG.info("row: %s" % row)
      if i > 100:
        break
      i += 1

    LOG.info(db.get_log(query.get_handle()))
    end = time.time()
    elapsed = (end - start) / 60
    LOG.info("Time elapsed (minutes): %.2f" % elapsed)
