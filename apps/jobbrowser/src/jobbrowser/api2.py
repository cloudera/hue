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

from django.utils.translation import ugettext as _
from desktop.lib.i18n import smart_unicode
from desktop.lib.django_util import JsonResponse

from jobbrowser.apis.base_api import get_api


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


@api_error_handler
def jobs(request):
  response = {'status': -1}

  interface = json.loads(request.POST.get('interface'))
  filters = dict([(key, value) for _filter in json.loads(request.POST.get('filters', '[]')) for key, value in _filter.items() if value])

  jobs = get_api(request.user, interface).apps(filters)

  response['apps'] = jobs['apps']
  response['total'] = jobs.get('total')
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def job(request):
  response = {'status': -1}

  interface = json.loads(request.POST.get('interface'))
  app_id = json.loads(request.POST.get('app_id'))

  response['app'] = get_api(request.user, interface).app(app_id)
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def action(request):
  response = {'status': -1, 'message': ''}

  interface = json.loads(request.POST.get('interface'))
  app_ids = json.loads(request.POST.get('app_ids'))
  operation = json.loads(request.POST.get('operation'))

  response['operation'] = operation
  response.update(get_api(request.user, interface).action(app_ids, operation))

  return JsonResponse(response)


@api_error_handler
def logs(request):
  response = {'status': -1}

  interface = json.loads(request.POST.get('interface'))
  app_id = json.loads(request.POST.get('app_id'))
  app_type = json.loads(request.POST.get('type'))
  log_name = json.loads(request.POST.get('name'))

  response['logs'] = get_api(request.user, interface).logs(app_id, app_type, log_name)
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def profile(request):
  response = {'status': -1}

  interface = json.loads(request.POST.get('interface'))
  app_id = json.loads(request.POST.get('app_id'))
  app_type = json.loads(request.POST.get('app_type'))
  app_property = json.loads(request.POST.get('app_property'))
  app_filters = dict([(key, value) for _filter in json.loads(request.POST.get('app_filters', '[]')) for key, value in _filter.items() if value])

  api = get_api(request.user, interface)
  api._set_request(request) # For YARN

  response[app_property] = api.profile(app_id, app_type, app_property, app_filters)
  response['status'] = 0

  return JsonResponse(response)
