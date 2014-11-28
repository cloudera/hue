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

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from desktop.context_processors import get_app_name
from desktop.lib.django_util import render
from django.shortcuts import redirect

from beeswax import models as beeswax_models
from beeswax.views import safe_get_design

from spark.job_server_api import get_api
from spark.forms import UploadApp
from desktop.lib.exceptions import StructuredException
from spark.api import design_to_dict

from spark.decorators import view_error_handler


LOG = logging.getLogger(__name__)


@view_error_handler
def editor(request):
  return render('editor.mako', request, {})

@view_error_handler
def list_jobs(request):
  api = get_api(request.user)
  jobs = api.jobs()

  return render('list_jobs.mako', request, {
    'jobs': jobs,
    'jobs_json': json.dumps(jobs)
  })

@view_error_handler
def list_contexts(request):
  api = get_api(request.user)
  contexts = api.contexts()

  return render('list_contexts.mako', request, {
    'contexts': contexts,
    'contexts_json': json.dumps(contexts)
  })

@view_error_handler
def delete_contexts(request):
  if request.method == 'POST':
    api = get_api(request.user)
    ids = request.POST.getlist('contexts_selection')
    for name in ids:
      api.delete_context(name)
    return redirect(reverse('spark:list_contexts'))
  else:
    return render('confirm.mako', request, {'url': request.path, 'title': _('Delete context(s)?')})

@view_error_handler
def list_applications(request):
  api = get_api(request.user)
  applications = api.jars()

  return render('list_applications.mako', request, {
    'applications': applications,
    'applications_json': json.dumps([applications])
  })


def upload_app(request):
  if request.method != 'POST':
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Requires a POST'))
  response = {
    'status': -1
  }

  form = UploadApp(request.POST, request.FILES)

  if form.is_valid():
    app_name = form.cleaned_data['app_name']
    try:
      data = form.cleaned_data['jar_file'].read()
      api = get_api(request.user)
      response['status'] = 0
      response['results'] = api.upload_jar(app_name, data)
    except ValueError:
      # No json is returned
      pass
  else:
    response['results'] = form.errors

  return redirect(request.META['HTTP_REFERER'])

@view_error_handler
def download_result(request, job_id):
  api = get_api(request.user)
  result = api.job(job_id)

  mimetype = 'application/json'
  gen = json.dumps(result['result'])

  resp = HttpResponse(gen, mimetype=mimetype)
  resp['Content-Disposition'] = 'attachment; filename=query_result.%s' % format

  return resp
