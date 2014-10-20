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
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render
from desktop.models import Document2

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
