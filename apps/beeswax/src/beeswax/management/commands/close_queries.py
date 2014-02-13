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

from django.core.management.base import BaseCommand

from datetime import datetime,  timedelta

from beeswax.models import QueryHistory, HiveServerQueryHistory
from beeswax.server import dbms


class Command(BaseCommand):
  """
  Close old HiveServer2 and Impala queries.

  e.g.
  build/env/bin/hue close_queries 7 all
  Closing (all=True) queries older than 7 days...
  0 queries closed.
  """
  args = '<age_in_days> <all> (default is 7)'
  help = 'Close finished Hive queries older than 7 days. If \'all\' is specified, also close the Impala ones.'

  def handle(self, *args, **options):
    days = int(args[0]) if len(args) >= 1 else 7
    close_all = args[1] == 'all' if len(args) >= 2 else False

    self.stdout.write('Closing (all=%s) HiveServer2/Impala queries older than %s days...\n' % (close_all, days))

    n = 0
    queries = HiveServerQueryHistory.objects.filter(last_state__in=[QueryHistory.STATE.expired.index, QueryHistory.STATE.failed.index, QueryHistory.STATE.available.index])

    if close_all:
      queries = HiveServerQueryHistory.objects.all()

    queries = queries.filter(submission_date__lte=datetime.today() - timedelta(days=days))

    for query in queries:
      try:
        query_history = HiveServerQueryHistory.objects.get(id=query.id)
        if query_history.server_id is not None:
          handle = query_history.get_handle()
          dbms.get(user=query_history.owner).close_operation(handle)
          n += 1
        query.last_state = QueryHistory.STATE.expired.index
        query.save()
      except Exception, e:
        if 'Invalid OperationHandle' in str(e):
          query.last_state = QueryHistory.STATE.expired.index
          query.save()
        else:
          self.stdout.write('Error: %s\n' % e)

    self.stdout.write('%s queries closed.\n' % n)
