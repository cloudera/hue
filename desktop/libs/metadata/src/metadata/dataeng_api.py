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
import json

from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode

from notebook.connectors.altus import DataEngApi


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Exception, e:
      LOG.exception(e)
      response = {
        'status': -1,
        'message': force_unicode(e)
      }
    return JsonResponse(response, status=500)
  return decorator


@require_POST
@error_handler
def create_cluster(request):
  response = {'status': -1}

  cluster_name = request.POST.get('cluster_name')
  cdh_version = request.POST.get('cdh_version')
  public_key = request.POST.get('public_key')
  instance_type = request.POST.get('instance_type', "workers_group_size"'')
  environment_name = request.POST.get('environment_name')
  workers_group_size = request.POST.get('workers_group_size', '3')
  namespace_name = request.POST.get('namespace_name', 'null')

  api = DataEngApi(request.user)
  data = api.create_cluster(
      cloud_provider='aws',
      cluster_name=cluster_name,
      cdh_version=cdh_version,
      public_key=public_key,
      instance_type=instance_type,
      environment_name=environment_name,
      namespace_name=namespace_name,
      workers_group_size=workers_group_size
  )

  if data:
    response['status'] = 0
    response['data'] = data
  else:
    response['message'] = 'Data Engineering: %s' % data['details']

  return JsonResponse(response)
