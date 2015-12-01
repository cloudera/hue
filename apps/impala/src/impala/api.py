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


## Main views are inherited from Beeswax.

import logging

from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse

from beeswax.server import dbms as beeswax_dbms

from impala import dbms


LOG = logging.getLogger(__name__)


@require_POST
def invalidate(request, database):
  query_server = dbms.get_query_server_config()
  db = beeswax_dbms.get(request.user, query_server=query_server)

  response = {'status': 0, 'message': ''}

  try:
    flush_all = request.POST.get('flush_all', 'false').lower() == 'true'
    db.invalidate(database, flush_all=flush_all)
    response['message'] = _('Successfully invalidated metadata for `%s`') % database
  except Exception, e:
    response['status'] = -1
    response['message'] = _(str(e))

  return JsonResponse(response)



@require_POST
def refresh_table(request, database, table):
  query_server = dbms.get_query_server_config()
  db = beeswax_dbms.get(request.user, query_server=query_server)

  response = {'status': 0, 'message': ''}

  try:
    db.refresh_table(database, table)
    response['message'] = _('Successfully refreshed metadata for `%s`.`%s`') % (database, table)
  except Exception, e:
    response['status'] = -1
    response['message'] = _(str(e))

  return JsonResponse(response)
