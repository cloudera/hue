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

try:
  import json
except ImportError:
  import simplejson as json
import logging
import time

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from desktop.lib.django_util import render, encode_json_for_js
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.view_util import format_duration_in_millis
from liboozie.oozie_api import get_oozie
from oozie.views.dashboard import show_oozie_error, check_job_access_permission

from pig.api import Api
from pig.models import get_workflow_output, hdfs_link, PigScript


LOG = logging.getLogger(__name__)

def app(request):
  return render('app.mako', request, {
    'scripts': json.dumps(get_scripts())
    }
  )

def scripts(request):
  return HttpResponse(json.dumps(get_scripts()), mimetype="application/json")


def get_scripts():
  scripts = []

  for script in PigScript.objects.filter(is_history=False):
    data = json.loads(script.data)
    massaged_script = {
      'id': script.id,
      'name': data["name"],
      'script': data["script"]
    }
    scripts.append(massaged_script)

  return scripts

@show_oozie_error
def dashboard(request):
  kwargs = {'cnt': 100,}
  kwargs['user'] = request.user.username
  kwargs['name'] = Api.WORKFLOW_NAME

  jobs = get_oozie().get_workflows(**kwargs).jobs
  return HttpResponse(json.dumps(massaged_oozie_jobs_for_json(jobs, request.user)), mimetype="application/json")


def udfs(request):
  return render('udfs.mako', request, {})


@require_http_methods(["POST"])
def save(request):
  # TODO security
  pig_script = create_or_update_script(request.POST.get('id'), request.POST.get('name'), request.POST.get('script'), request.user)
  
  response = {
    'id': pig_script.id,
  }

  return HttpResponse(json.dumps(response), content_type="text/plain")


@require_http_methods(["POST"])
@show_oozie_error
def run(request):
  # TODO security
  pig_script = create_or_update_script(request.POST.get('id'), request.POST.get('name'), request.POST.get('script'), request.user)

  # Todo, will come from script properties later
  mapping = {
    'oozie.use.system.libpath':  'true',
  }  

  oozie_id = Api(request.fs, request.user).submit(pig_script, mapping)

  response = {
    'id': pig_script.id,
    'watchUrl': reverse('pig:watch', kwargs={'job_id': oozie_id}) + '?format=python'
  }

  return HttpResponse(json.dumps(response), content_type="text/plain")

@require_http_methods(["POST"])
def copy(request):
  # TODO security
  existing_script_data = json.loads((PigScript.objects.get(id=request.POST.get('id'))).data)
  name = existing_script_data["name"] + _(' (Copy)')
  script = existing_script_data["script"]

  pig_script = PigScript.objects.create(owner=request.user)
  pig_script.update_from_dict({'name': name, 'script': script})
  pig_script.save()

  response = {
    'id': pig_script.id,
    'name': name,
    'script': script
    }

  return HttpResponse(json.dumps(response), content_type="text/plain")

@require_http_methods(["POST"])
def delete(request):
  # TODO security
  ids = request.POST.get('ids').split(",")

  for script_id in ids:
    try:
      pig_script = PigScript.objects.get(id=script_id)
      pig_script.delete()
    except:
      None

  response = {
    'ids': ids,
  }

  return HttpResponse(json.dumps(response), content_type="text/plain")


def create_or_update_script(id, name, script, user):
  try:
    pig_script = PigScript.objects.get(id=id)
  except:
    pig_script = PigScript.objects.create(owner=user)

  pig_script.update_from_dict({'name': name, 'script': script})
  pig_script.save()

  return pig_script

@show_oozie_error
def watch(request, job_id):
  oozie_workflow = check_job_access_permission(request, job_id) 
  logs, workflow_actions = Api(request, job_id).get_log(request, oozie_workflow)
  output = get_workflow_output(oozie_workflow, request.fs)

  workflow = {
    'job_id': oozie_workflow.id,
    'status': oozie_workflow.status,
    'progress': oozie_workflow.get_progress(),
    'isRunning': oozie_workflow.is_running(),
    'killUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id': oozie_workflow.id, 'action': 'kill'}),
    'rerunUrl': reverse('oozie:rerun_oozie_job', kwargs={'job_id': oozie_workflow.id, 'app_path': oozie_workflow.appPath}),
    'actions': workflow_actions
  }

  response = {
    'workflow': workflow,
    'logs': logs,
    'output': hdfs_link(output)
  }
  
  return HttpResponse(json.dumps(response), content_type="text/plain")


def format_time(st_time):
  if st_time is None:
    return '-'
  else:
    return time.strftime("%a, %d %b %Y %H:%M:%S", st_time)

def has_job_edition_permission(oozie_job, user):
  return user.is_superuser or oozie_job.user == user.username

def has_dashboard_jobs_access(user):
  return user.is_superuser or user.has_hue_permission(action="dashboard_jobs_access", app=DJANGO_APPS[0])

def massaged_oozie_jobs_for_json(oozie_jobs, user):
  jobs = []

  for job in oozie_jobs:
    if job.is_running():
      if job.type == 'Workflow':
        job = get_oozie().get_job(job.id)
      elif job.type == 'Coordinator':
        job = get_oozie().get_coordinator(job.id)
      else:
        job = get_oozie().get_bundle(job.id)

    massaged_job = {
      'id': job.id,
      'lastModTime': hasattr(job, 'lastModTime') and job.lastModTime and format_time(job.lastModTime) or None,
      'kickoffTime': hasattr(job, 'kickoffTime') and job.kickoffTime or None,
      'timeOut': hasattr(job, 'timeOut') and job.timeOut or None,
      'endTime': job.endTime and format_time(job.endTime) or None,
      'status': job.status,
      'isRunning': job.is_running(),
      'duration': job.endTime and job.startTime and format_duration_in_millis(( time.mktime(job.endTime) - time.mktime(job.startTime) ) * 1000) or None,
      'appName': job.appName,
      'progress': job.get_progress(),
      'user': job.user,
      'absoluteUrl': job.get_absolute_url(),
      'canEdit': has_job_edition_permission(job, user),
      'killUrl': reverse('oozie:manage_oozie_jobs', kwargs={'job_id':job.id, 'action':'kill'}),
      'created': hasattr(job, 'createdTime') and job.createdTime and job.createdTime and ((job.type == 'Bundle' and job.createdTime) or format_time(job.createdTime)),
      'startTime': hasattr(job, 'startTime') and format_time(job.startTime) or None,
      'run': hasattr(job, 'run') and job.run or 0,
      'frequency': hasattr(job, 'frequency') and job.frequency or None,
      'timeUnit': hasattr(job, 'timeUnit') and job.timeUnit or None,
      }
    jobs.append(massaged_job)

  return jobs
