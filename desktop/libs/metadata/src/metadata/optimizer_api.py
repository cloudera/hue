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

  len = request.POST.get('len', 500)

  api = OptimizerApi()

  response['top_tables'] = api.top_tables() if not OPTIMIZER.MOCKING.get() else [
      {'name': 'customers', 'popularity': random.randint(1, 100) , 'column_count': random.randint(1, 100), 'is_fact': bool(random.getrandbits(1))}
    for i in xrange(0, len)
  ]
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def table_details(request):
  response = {'status': -1}

  table_name = request.POST.get('tableName')

  api = OptimizerApi()

  response['table_details'] = api.table_details(table_name=table_name)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def query_compatibility(request):
  response = {'status': -1}

  source_platform = request.POST.get('sourcePlatform')
  target_platform = request.POST.get('target_platform')
  query = request.POST.get('query')

  api = OptimizerApi()

  response['table_details'] = api.query_compatibility(source_platform=source_platform, target_platform=target_platform, query=query)
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@error_handler
def query_complexity(request):
  response = {'status': -1}

  snippet = json.loads(request.POST.get('snippet'))

  if 'join' in snippet['statement'].lower():
    comment = 'Large join is happening'
  elif 'large' in snippet['statement'].lower():
    comment = 'Previously failed 5 times in a row'
  elif 'partition' in snippet['statement'].lower():
    comment = 'Has 50k partitions'
  else:
    comment = ''

  response['query_complexity'] = {
    'level': randome.choice(['LOW', 'MEDIUM', 'HIGH']),
    'comment': comment
  }
  response['status'] = 0

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
