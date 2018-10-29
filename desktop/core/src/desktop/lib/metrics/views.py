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

import datetime
import logging
import json

from django.views.decorators.http import require_GET

from desktop.lib.django_util import JsonResponse, login_notrequired, render
from desktop.lib.metrics.registry import global_registry


LOG = logging.getLogger(__name__)


@login_notrequired
@require_GET
def index(request):
  if request.GET.get('pretty') == 'true':
    indent = 2
  else:
    indent = None

  rep = {
      'timestamp': datetime.datetime.utcnow().isoformat(),
      'metric': global_registry().dump_metrics(),
  }

  if request.is_ajax():
    return JsonResponse(rep, json_dumps_params={'indent': indent})
  else:
    return render("metrics.mako", request, {'metrics': json.dumps(rep['metric']), 'is_embeddable': request.GET.get('is_embeddable', False)})
