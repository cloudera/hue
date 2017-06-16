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

import logging

from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET, require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import smart_unicode

from libsolr.api import SolrApi


LOG = logging.getLogger(__name__)


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}

    try:
      return func(*args, **kwargs)
    except Exception, e:
      LOG.exception('Error running %s' % func)
      response['status'] = -1
      response['message'] = smart_unicode(e)
    finally:
      if response:
        return JsonResponse(response)

  return decorator


@require_POST
@api_error_handler
def list_collections(request):
  response = {'status': -1}

  api = SolrApi(user=request.user)

  response['collections'] = [{'isCoreOnly': False, 'isAlias': False, 'collections': [], 'name': name} for name in api.collections2()]
  response['status'] = 0

  return JsonResponse(response)


@require_POST
@api_error_handler
def delete_collections(request):
  response = {'status': -1}

  names = request.POST.get_list('name')

  api = SolrApi(user=request.user)

  response['statuses'] = [api.remove_collection(name) for name in names]
  response['status'] = 0

  return JsonResponse(response)
