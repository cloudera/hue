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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from liboozie.oozie_api import get_oozie
from oozie.views.dashboard import show_oozie_error, check_job_access_permission

from pig.api import Api
from pig.models import get_workflow_output, hdfs_link, PigScript


LOG = logging.getLogger(__name__)


def editor(request):
  pig_script_json = {}
  return render('editor.mako', request, {
                  'pig_script_json': json.dumps(pig_script_json)
                  }
                )

@show_oozie_error
def dashboard(request):
  kwargs = {'cnt': 100,}
  kwargs['user'] = request.user.username
  kwargs['name'] = Api.WORKFLOW_NAME

  workflows = get_oozie().get_workflows(**kwargs)
    
  return render('dashboard.mako', request, {
                    'workflows': workflows
                  }
                )

def scripts(request):
  
  return render('scripts.mako', request, {
                    'scripts': PigScript.objects.filter(is_history=False)
                  }
                )


def udfs(request):
  
  return render('udfs.mako', request, {
                  }
                )


def load_script(request, doc_id):

  ko_repo = {
    'id': doc_id,
    'name': 'Run',
    'description': 'Outputs and MR jobs',
    'submitUrl': reverse('pig:submit', args=[doc_id]),
    'saveUrl': reverse('pig:save', args=[doc_id])
    }

  response = {
    'apps': [ko_repo],
    'repo_id': 1,
  }

  return HttpResponse(json.dumps(response), content_type="text/plain")


@require_http_methods(["POST"])
def save(request, doc_id=None):
  # TODO security
  if doc_id is None:
    script = request.POST.get('script')
    pig_script = PigScript.objects.create(owner=request.user)
  pig_script.update_from_dict({'script': script})
  pig_script.save()
  
  response = {
    'doc_id': pig_script.id,
  }

  return HttpResponse(json.dumps(response), content_type="text/plain")


@require_http_methods(["POST"])
@show_oozie_error
def submit(request, doc_id):
  # TODO security
  script = request.POST.get('script')
  pig_script = PigScript.objects.create(owner=request.user, is_history=True)
  pig_script.update_from_dict({'script': script})
  pig_script.save()
  
  # Todo, will come from script properties later
  mapping = {
    'oozie.use.system.libpath':  'true',
  }  

  oozie_id = Api(request.fs, request.user).submit(pig_script, mapping)

  response = {
    'demoId': doc_id,
    'jobId': pig_script.id,
    'watchUrl': reverse('pig:watch', kwargs={'doc_id': doc_id, 'job_id': oozie_id}) + '?format=python'
  }

  return HttpResponse(json.dumps(response), content_type="text/plain")


@show_oozie_error
def watch(request, doc_id, job_id):
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

