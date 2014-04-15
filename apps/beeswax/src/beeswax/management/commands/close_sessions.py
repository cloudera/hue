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

from beeswax.models import Session
from beeswax.server import dbms


class Command(BaseCommand):
  """
  Close old HiveServer2 and Impala sessions.

  e.g.
  build/env/bin/hue close_sessions 7 all
  Closing (all=True) queries older than 7 days...
  0 queries closed.
  """
  args = '<age_in_days> <hive,impala,all> (default is 7 and hive)'
  help = 'Close finished Hive queries older than 7 days. If \'all\' is specified, also close the Impala ones.'

  def handle(self, *args, **options):
    days = int(args[0]) if len(args) >= 1 else 7
    query_type = args[1] if len(args) >= 2 else None
    if query_type == 'hive' or query_type is None:
      query_type = 'beeswax'

    self.stdout.write('Closing (all=%s) HiveServer2/Impala sessions older than %s days...\n' % (query_type, days))

    n = 0
    sessions = Session.objects.all()

    if query_type != 'all':
      sessions = sessions.filter(application=query_type)

    sessions = sessions.filter(last_used__lte=datetime.today() - timedelta(days=days))

    for session in sessions:
      try:
          resp = dbms.get(user=session.owner).close_session(session)
          if not 'Session does not exist!' in str(resp):
            self.stdout.write('Error: %s\n' % resp)
            n += 1
      except Exception, e:
        if not 'Session does not exist!' in str(e):
          self.stdout.write('Error: %s\n' % e)

    self.stdout.write('%s sessions closed.\n' % n)
