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
import urllib

from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie

from desktop.lib.django_util import JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import RestException
from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS
from desktop.models import Document

from oozie.views.dashboard import show_oozie_error, check_job_access_permission,\
                                  check_job_edition_permission

from pig import api
from pig.management.commands import pig_setup
from pig.models import get_workflow_output, hdfs_link, PigScript,\
  create_or_update_script, get_scripts


LOG = logging.getLogger(__name__)

@ensure_csrf_cookie
def app(request):
  autocomplete_base_url = ''
  try:
    autocomplete_base_url = reverse('beeswax:api_autocomplete_databases', kwargs={}) + '/'
  except:
    LOG.exception('failed to find autocomplete base url')

  return render('app.mako', request, {
    'autocomplete_base_url': autocomplete_base_url
  })


def scripts(request):
  return JsonResponse(get_scripts(request.user, is_design=True), safe=False)


@show_oozie_error
def dashboard(request):
  pig_api = api.get(request.fs, request.jt, request.user)

  jobs = pig_api.get_jobs()
  hue_jobs = Document.objects.available(PigScript, request.user, with_history=True)
  massaged_jobs = pig_api.massaged_jobs_for_json(request, jobs, hue_jobs)

  return JsonResponse(massaged_jobs, safe=False)


def save(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  attrs = {
    'id': request.POST.get('id'),
    'name': request.POST.get('name'),
    'script': request.POST.get('script'),
    'user': request.user,
    'parameters': json.loads(request.POST.get('parameters')),
    'resources': json.loads(request.POST.get('resources')),
    'hadoopProperties': json.loads(request.POST.get('hadoopProperties')),
  }
  pig_script = create_or_update_script(**attrs)
  pig_script.is_design = True
  pig_script.save()

  response = {
    'id': pig_script.id,
    'docId': pig_script.doc.get().id
  }

  return JsonResponse(response, content_type="text/plain")


@show_oozie_error
def stop(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  pig_script = PigScript.objects.get(id=request.POST.get('id'))
  job_id = pig_script.dict['job_id']

  job = check_job_access_permission(request, job_id)
  check_job_edition_permission(job, request.user)

  try:
    api.get(request.fs, request.jt, request.user).stop(job_id)
  except RestException, e:
    raise PopupException(_("Error stopping Pig script.") % e.message)

  return watch(request, job_id)


@show_oozie_error
def run(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  attrs = {
    'id': request.POST.get('id'),
    'name': request.POST.get('name'),
    'script': request.POST.get('script'),
    'user': request.user,
    'parameters': json.loads(request.POST.get('parameters')),
    'resources': json.loads(request.POST.get('resources')),
    'hadoopProperties': json.loads(request.POST.get('hadoopProperties')),
    'is_design': False
  }

  pig_script = create_or_update_script(**attrs)

  params = request.POST.get('submissionVariables')
  oozie_id = api.get(request.fs, request.jt, request.user).submit(pig_script, params)

  pig_script.update_from_dict({'job_id': oozie_id})
  pig_script.save()

  response = {
    'id': pig_script.id,
    'watchUrl': reverse('pig:watch', kwargs={'job_id': oozie_id}) + '?format=python'
  }

  return JsonResponse(response, content_type="text/plain")


def copy(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  pig_script = PigScript.objects.get(id=request.POST.get('id'))
  doc = pig_script.doc.get()

  try:
    doc.can_read_or_exception(request.user)
  except Exception, e:
    raise PopupException(e)

  existing_script_data = pig_script.dict

  owner = request.user
  name = existing_script_data["name"] + _(' (Copy)')
  script = existing_script_data["script"]
  parameters = existing_script_data["parameters"]
  resources = existing_script_data["resources"]
  hadoopProperties = existing_script_data["hadoopProperties"]

  script_copy = PigScript.objects.create(owner=owner)
  script_copy.update_from_dict({
      'name': name,
      'script': script,
      'parameters': parameters,
      'resources': resources,
      'hadoopProperties': hadoopProperties
  })
  script_copy.save()

  copy_doc = doc.copy(content_object=script_copy, name=name, owner=owner)

  response = {
    'id': script_copy.id,
    'docId': copy_doc.id,
    'name': name,
    'script': script,
    'parameters': parameters,
    'resources': resources,
    'hadoopProperties': hadoopProperties
  }

  return JsonResponse(response, content_type="text/plain")


def delete(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  ids = request.POST.get('ids').split(",")

  for script_id in ids:
    try:
      pig_script = PigScript.objects.get(id=script_id)
      pig_script.can_edit_or_exception(request.user)
      pig_script.doc.all().delete()
      pig_script.delete()
    except:
      LOG.exception('failed to delete pig script')
      None

  response = {
    'ids': ids,
  }

  return JsonResponse(response, content_type="text/plain")


@show_oozie_error
def watch(request, job_id):
  oozie_workflow = check_job_access_permission(request, job_id)
  logs, workflow_actions, is_really_done = api.get(request.fs, request.jt, request.user).get_log(request, oozie_workflow)
  output = get_workflow_output(oozie_workflow, request.fs)

  workflow = {
    'job_id': oozie_workflow.id,
    'status': oozie_workflow.status,
    'progress': oozie_workflow.get_progress(),
    'isRunning': oozie_workflow.is_running(),
    'killUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id': oozie_workflow.id, 'action': 'kill'}),
    'rerunUrl': reverse('oozie:rerun_oozie_job', kwargs={'job_id': oozie_workflow.id, 'app_path': urllib.quote(oozie_workflow.appPath.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)}),
    'actions': workflow_actions
  }

  response = {
    'workflow': workflow,
    'logs': logs,
    'isReallyDone': is_really_done,
    'output': hdfs_link(output)
  }

  return JsonResponse(response, content_type="text/plain")


def install_examples(request):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      pig_setup.Command().handle()
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
