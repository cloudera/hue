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

  response['apps'] = get_api(request.user, interface).apps()
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def job(request):
  response = {'status': -1}

  interface = json.loads(request.POST.get('interface'))
  appid = json.loads(request.POST.get('appid'))

  response['app'] = get_api(request.user, interface).app(appid)
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def kill(request): return {}


@api_error_handler
def progress(request): return {'progress': 0}


@api_error_handler
def tasks(request): return []


@api_error_handler
def logs(request): return {'stderr': '', 'stdout': ''}


@api_error_handler
def profile(request): return {}

