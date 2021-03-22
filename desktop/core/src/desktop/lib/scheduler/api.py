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
import sys

from django.forms.formsets import formset_factory
from django.urls import reverse

from desktop.auth.backend import is_admin
from desktop.conf import TASK_SERVER
from desktop.models import Document2
from desktop.lib.django_util import JsonResponse, render
from desktop.lib.i18n import force_unicode
from desktop.lib.scheduler.lib.api import get_api

LOG = logging.getLogger(__name__)

try:
  from oozie.decorators import check_document_access_permission
  from oozie.forms import ParameterForm
  from oozie.views.editor2 import edit_coordinator, new_coordinator, Coordinator
except Exception as e:
  LOG.warning('Oozie application is not enabled: %s' % e)


def list_schedules(request):
  return JsonResponse({})


def new_schedule(request):
  return new_coordinator(request)


def get_schedule(request):
  return edit_coordinator(request)


# To move to lib in case oozie is blacklisted
#@check_document_access_permission()
def submit_schedule(request, doc_id):
  interface = request.GET.get('interface', request.POST.get('interface', 'hive'))

  if doc_id.isdigit():
    coordinator = Coordinator(document=Document2.objects.get(id=doc_id))
  else:
    coordinator = Coordinator(document=Document2.objects.get_by_uuid(user=request.user, uuid=doc_id))

  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])
      mapping['dryrun'] = request.POST.get('dryrun_checkbox') == 'on'
      jsonify = request.POST.get('format') == 'json'
      try:
        job_id = get_api(request, interface).submit_schedule(request, coordinator, mapping)
      except Exception as e:
        message = force_unicode(str(e))
        return JsonResponse({'status': -1, 'message': message}, safe=False)
      if jsonify:
        if interface == 'hive':
          schedule_type = 'schedule-hive'  # Current Job Browser "types"
        elif interface == 'beat':
          schedule_type = 'celery-beat'
        else:
          schedule_type = 'schedule'
        return JsonResponse({'status': 0, 'job_id': job_id, 'type': schedule_type}, safe=False)
      else:
        request.info(_('Schedule submitted.'))
        return redirect(reverse('oozie:list_oozie_coordinator', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s') % params_form.errors)
  else:
    parameters = coordinator.find_all_parameters() if interface == 'oozie' else []
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

  popup = render(
      'scheduler/submit_job_popup.mako',
      request, {
          'params_form': params_form,
          'name': coordinator.name,
          'action': '/scheduler/api/schedule/submit/%s' % coordinator.id,
          'show_dryrun': False,
          'return_json': request.GET.get('format') == 'json',
          'interface': interface
      },
      force_template=True
  ).content

  return JsonResponse(popup.decode("utf-8") if sys.version_info[0] > 2 else popup, safe=False)
