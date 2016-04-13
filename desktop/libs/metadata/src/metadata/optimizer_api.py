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

import json
import logging
import random

from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from desktop.models import Document2
from notebook.models import Notebook

from metadata.optimizer_client import OptimizerApi
from metadata.conf import OPTIMIZER


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Http404, e:
      raise e
    except Exception, e:
      LOG.exception(e)
      response = {
        'status': -1,
        'message': force_unicode(str(e))
      }
    return JsonResponse(response, status=500)
  return decorator


@require_POST
@error_handler
def top_tables(request):
  response = {'status': -1}

  database = request.POST.get('database', 'default')
  len = request.POST.get('len', 1000)

  if OPTIMIZER.MOCKING.get():
    from beeswax.server import dbms
    from beeswax.server.dbms import get_query_server_config
    db = dbms.get(request.user)
    tables = [
      {'name': table, 'popularity': random.randint(1, 100) , 'column_count': random.randint(1, 100), 'is_fact': bool(random.getrandbits(1))}
      for table in db.get_tables(database=database)
    ][:len]
  else:
    """
    Get back:
    # u'details': [{u'columnCount': 28, u'name': u'date_dim', u'patternCount': 136, u'workloadPercent': 89, u'total': 92, u'type': u'Dimension', u'eid': u'19'},
    """
    api = OptimizerApi()
    data = api.top_tables()

    tables = [{
        'eid': table['eid'],
        'name': table['name'],
        'popularity': table['workloadPercent'],
        'column_count': table['columnCount'],
        'patternCount': table['patternCount'],
        'total': table['total'],
        'is_fact': table['type'] != 'Dimension'
        } for table in data['details']
    ]

  response['top_tables'] = tables
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def table_details(request):
  response = {'status': -1}

  table_name = request.POST.get('tableName')

  api = OptimizerApi()

  data = api.table_details(table_name=table_name)

  if data['status'] == 'success':
    response['status'] = 0
    response['details'] = data['details']
  else:
    response['message'] = 'Optimizer: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def query_compatibility(request):
  response = {'status': -1}

  source_platform = request.POST.get('sourcePlatform')
  target_platform = request.POST.get('targetPlatform')
  query = request.POST.get('query')

  api = OptimizerApi()

  data = api.query_compatibility(source_platform=source_platform, target_platform=target_platform, query=query)

  if data['status'] == 'success':
    response['status'] = 0
    response['query_compatibility'] = json.loads(data['details'])
  else:
    response['message'] = 'Optimizer: %s' % data['details']

  return JsonResponse(response)


# Mocked
@require_POST
@error_handler
def query_complexity(request):
  response = {'status': -1}

  snippet = json.loads(request.POST.get('snippet'))

  if 'select * from tsqc_date t join atd_au_dtl a on (t.date = a.date)' in snippet['statement'].lower():
    comment = 'Large join is happening'
  elif 'large' in snippet['statement'].lower():
    comment = 'Previously failed 5 times in a row'
  elif 'partition' in snippet['statement'].lower():
    comment = 'Has 50k partitions'
  else:
    comment = ''

  response['query_complexity'] = {
    'level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
    'comment': comment
  }
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def simiar_queries(request):
  response = {'status': -1}

  source_platform = request.POST.get('sourcePlatform')
  query = request.POST.get('query')

  api = OptimizerApi()

  data = api.similar_queries(source_platform=source_platform, query=query)

  if data['status'] == 'success':
    response['status'] = 0
    response['similar_queries'] = json.loads(data['details']['similarQueries'])
  else:
    response['message'] = 'Optimizer: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def popular_values(request):
  response = {'status': -1}

  table_name = request.POST.get('tableName')
  column_name = request.POST.get('columnName')

  if OPTIMIZER.MOCKING.get():
    if column_name:
      values = [
          {
            "values": [
              "1",
              "(6,0)"
            ],
            "columnName": "d_dow",
            "tableName": "date_dim"
          }
      ]
    else:
      values = [
          {
            "values": [
              "('2001q1','2001q2','2001q3')",
              "'2001q1'"
            ],
            "columnName": "d_quarter_name",
            "tableName": "date_dim"
          },
          {
            "values": [
              "1",
              "2",
              "4"
            ],
            "columnName": "d_qoy",
            "tableName": "date_dim"
          },
          {
            "values": [
              "Subquery"
            ],
            "columnName": "d_week_seq",
            "tableName": "date_dim"
          },
          {
            "values": [
              "(cast('1998-08-14' as date) + interval '30' day)",
              "(cast ('1998-03-08' as date) + interval '30' day)",
              "d1.d_date + 5",
              "cast('1998-08-14' as date)",
              "cast('1999-04-26' as date)",
              "'2002-4-01'",
              "(cast('2000-02-02' as date) + interval '90' day)",
              "(cast('2002-4-01' as date) + interval '60' day)",
              "(cast('2002-01-18' as date) + 60 + interval '60' day)",
              "('1999-04-17','1999-10-04','1999-11-10')",
              "(cast('1999-04-26' as date) + 30 + interval '30' day)",
              "(cast('1999-06-03' as date) + interval '30' day)",
              "cast('1998-01-06' as date)",
              "(cast('2000-2-01' as date) + interval '60' day)",
              "(cast('2002-04-01' as date) + interval '30' day)",
              "( cast('2000-03-22' as date ) + interval '90' day )",
              "cast('2001-08-21' as date)",
              "(cast ('1998-03-08' as date) - interval '30' day)",
              "'2000-03-22'",
              "(cast('2001-08-21' as date) + interval '14' day)",
              "( cast('1999-08-25' as date) + interval '30' day )",
              "Subquery",
              "'2000-3-01'",
              "cast('2002-01-18' as date)",
              "(cast ('2001-03-14' as date) - interval '30' day)",
              "'2000-02-02'",
              "cast('2002-04-01' as date)",
              "'2002-03-09'",
              "(cast('2000-3-01' as date) + interval '60' day)",
              "cast('1999-06-03' as date)",
              "cast('1999-08-25' as date)",
              "(cast ('2001-03-14' as date) + interval '30' day)",
              "'2000-2-01'",
              "(cast('1998-01-06' as date) + interval '60' day)"
            ],
            "columnName": "d_date",
            "tableName": "date_dim"
          },
          {
            "values": [
              "1223",
              "1200",
              "1202",
              "1214+11",
              "(select distinct date_dim.d_month_seq+1 from date_dim where date_dim.d_year = 2001 and date_dim.d_moy = 5)",
              "1181+11",
              "1199",
              "1191",
              "(1206,1206+1,1206+2,1206+3,1206+4,1206+5,1206+6,1206+7,1206+8,1206+9,1206+10,1206+11)",
              "1211 + 11",
              "1199 + 11",
              "1212",
              "(select distinct date_dim.d_month_seq+3 from date_dim where date_dim.d_year = 2001 and date_dim.d_moy = 5)",
              "1211",
              "1214",
              "Subquery",
              "(1195,1195+1,1195+2,1195+3,1195+4,1195+5,1195+6,1195+7,1195+8,1195+9,1195+10,1195+11)",
              "1200+11",
              "1212 + 11",
              "1223+11",
              "1183 + 11",
              "1183",
              "1181",
              "1191 + 11",
              "1202 + 11"
            ],
            "columnName": "d_month_seq",
            "tableName": "date_dim"
          },
          {
            "values": [
              "11",
              "4 + 3",
              "12",
              "3+2",
              "2+3",
              "1",
              "3",
              "2",
              "5",
              "4",
              "6",
              "8",
              "10"
            ],
            "columnName": "d_moy",
            "tableName": "date_dim"
          },
          {
            "values": [
              "25",
              "16",
              "28",
              "1",
              "3",
              "2"
            ],
            "columnName": "d_dom",
            "tableName": "date_dim"
          },
          {
            "values": [
              "(1998,1998+1)",
              "2000 + 1",
              "2000 + 2",
              "(2000,2000+1,2000+2)",
              "(1999,1999+1,1999+2)",
              "2000-1",
              "2001+1",
              "1999 + 2",
              "2000+1",
              "2000+2",
              "1999+1",
              "(2002)",
              "( 1999, 1999 + 1, 1999 + 2, 1999 + 3 )",
              "1999-1",
              "( 1998, 1998 + 1, 1998 + 2 )",
              "1999",
              "1998",
              "(1998,1998+1,1998+2)",
              "2002",
              "2000",
              "2001",
              "2004"
            ],
            "columnName": "d_year",
            "tableName": "date_dim"
          },
          {
            "values": [
              "1",
              "(6,0)"
            ],
            "columnName": "d_dow",
            "tableName": "date_dim"
          }
        ]
  else:
    api = OptimizerApi()
    data = api.popular_filter_values(table_name=table_name, column_name=column_name)

    if data['status'] == 'success':
      if 'status' in data['details']:
        response['values'] = [] # Bug in Opt API
      else:
        response['values'] = data['details']
        response['status'] = 0
    else:
      response['message'] = 'Optimizer: %s' % data['details']

  return JsonResponse(response)


@require_POST
@error_handler
def upload_history(request):
  response = {'status': -1}

  query_type = 'hive'

  queries = [
      (doc.uuid, 1000, Notebook(document=doc).get_data()['snippets'][0]['statement'])
      for doc in Document2.objects.get_history(doc_type='query-%s' % query_type, user=request.user)[:25]
  ]

  api = OptimizerApi()

  response['upload_history'] = api.upload(queries=queries, source_platform=query_type)
  response['status'] = 0

  return JsonResponse(response)
