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

from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from desktop.lib.rest.http_client import RestException
from desktop.models import Document2

from liboozie.submission2 import Submission

from oozie.forms import ParameterForm
from oozie.models2 import Workflow


LOG = logging.getLogger(__name__)



def list_editor_workflows(request):
  workflows = Document2.objects.filter(type='oozie-workflow2', owner=request.user)

  return render('editor/list_editor_workflows.mako', request, {
      'workflows': workflows
  })


def edit_workflow(request):

  workflow_id = request.GET.get('workflow')
  
  if workflow_id:
    workflow = Workflow(document=Document2.objects.get(id=workflow_id)) # Todo perms
  else:
    workflow = Workflow()
  
  workflow_data = workflow.get_data()

  return render('editor/workflow_editor.mako', request, {
      'layout_json': json.dumps(workflow_data['layout']),
      'workflow_json': json.dumps(workflow_data['workflow'])
  })


def new_workflow(request):
  return edit_workflow(request)


def save_workflow(request):
  response = {'status': -1}

  workflow = json.loads(request.POST.get('workflow', '{}')) # TODO perms
  layout = json.loads(request.POST.get('layout', '{}'))

  name = 'test'

  if workflow.get('id'):
    workflow_doc = Document2.objects.get(id=workflow['id'])
  else:      
    workflow_doc = Document2.objects.create(name=name, type='oozie-workflow2', owner=request.user)

  workflow_doc.update_data({'workflow': workflow})
  workflow_doc.update_data({'layout': layout})
  workflow_doc.name = name
  workflow_doc.save()
  
  workflow_instance = Workflow(document=workflow_doc)
  workflow_instance.check_workspace(request.fs)
  
  response['status'] = 0
  response['id'] = workflow_doc.id
  response['message'] = _('Page saved !')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def gen_xml_workflow(request):
  response = {'status': -1}

  try:
    workflow_json = json.loads(request.POST.get('workflow', '{}')) # TODO perms
  
    workflow = Workflow(workflow=workflow_json)
  
    response['status'] = 0
    response['xml'] = workflow.to_xml()
  except Exception, e:
    response['message'] = str(e)
    
  return HttpResponse(json.dumps(response), mimetype="application/json") 


def submit_workflow(request, doc_id):
  workflow = Workflow(document=Document2.objects.get(id=doc_id)) # Todo perms
  ParametersFormSet = formset_factory(ParameterForm, extra=0)

  if request.method == 'POST':
    params_form = ParametersFormSet(request.POST)    

    if params_form.is_valid():
      mapping = dict([(param['name'], param['value']) for param in params_form.cleaned_data])

      job_id = _submit_workflow(request.user, request.fs, request.jt, workflow, mapping)

      request.info(_('Workflow submitted'))
      return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))
    else:
      request.error(_('Invalid submission form: %s' % params_form.errors))
  else:
    parameters = workflow.find_all_parameters()
    initial_params = ParameterForm.get_initial_params(dict([(param['name'], param['value']) for param in parameters]))
    params_form = ParametersFormSet(initial=initial_params)

  popup = render('editor/submit_job_popup.mako', request, {
                   'params_form': params_form,
                   'action': reverse('oozie:editor_submit_workflow', kwargs={'doc_id': workflow.id})
                 }, force_template=True).content
  return HttpResponse(json.dumps(popup), mimetype="application/json")


def _submit_workflow(user, fs, jt, workflow, mapping):
  try:
    submission = Submission(user, workflow, fs, jt, mapping)
    job_id = submission.run()
    return job_id
  except RestException, ex:
    detail = ex._headers.get('oozie-error-message', ex)
    if 'Max retries exceeded with url' in str(detail):
      detail = '%s: %s' % (_('The Oozie server is not running'), detail)
    LOG.error(smart_str(detail))
    raise PopupException(_("Error submitting workflow %s") % (workflow,), detail=detail)

  return redirect(reverse('oozie:list_oozie_workflow', kwargs={'job_id': job_id}))
