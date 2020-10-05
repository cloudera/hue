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

import base64
import json
import logging
import struct

from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.connectors.models import ConnectorNotFoundException
from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode

from metadata.models.base import get_api


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    response = {
      'message': ''
    }
    status = 500
    try:
      return view_fn(*args, **kwargs)
    except ConnectorNotFoundException as e:
      response['message'] = force_unicode(e.message)
      status = 403
    except Exception as e:
      LOG.exception(e)
      response['message'] = force_unicode(e)
    return JsonResponse(response, status=status)
  return decorator


@require_POST
@error_handler
def list_models(request, database=None):
  response = {'status': -1}

  connector_id = request.POST.get('connector')

  api = get_api(request.user, connector_id)

  data = api.list_models(database)

  return JsonResponse({'models': data})


@require_POST
@error_handler
def train(request, model):
  response = {'status': -1}

  connector_id = request.POST.get('connector')
  params = request.POST.copy()
  params['model'] = model

  api = get_api(request.user, connector_id)

  data = api.train(params)

  return JsonResponse({'data': data})


@require_POST
@error_handler
def predict(request, model):
  response = {'status': -1}

  connector_id = request.POST.get('connector')
  params = request.POST.copy()
  params['model'] = model

  api = get_api(request.user, connector_id)

  data = api.predict(params)

  return JsonResponse({'data': data})


@require_POST
@error_handler
def delete_model(request, model):
  response = {'status': -1}

  connector_id = request.POST.get('connector')

  api = get_api(request.user, connector_id)

  data = api.delete_model(model)

  return JsonResponse({'info': data})
