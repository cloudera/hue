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
"""
Views for JobSubmission.

The typical workflow has a user creating a "job design".
Existing job designs can also be edited and listed.
To "run" the job design, it must be parameterized, and submitted
to the cluster.  A parameterized, submitted job design
is a "job submission".  Submissions can be "watched".
"""

try:
  import json
except ImportError:
  import simplejson as json
import logging


from django.core import urlresolvers
from django.shortcuts import redirect

from desktop.lib.django_util import render, PopupException, extract_field_data
from desktop.log.access import access_warn

from jobsub import models, submit
from jobsub.oozie_lib.oozie_api import get_oozie
import jobsub.forms


LOG = logging.getLogger(__name__)


def oozie_job(request, jobid):
  """View the details about this job."""
  workflow = get_oozie().get_job(jobid)
  _check_permission(request, workflow.user,
                    "Access denied: view job %s" % (jobid,))

  return render('workflow.mako', request, {
    'workflow': workflow,
  })


def list_history(request):
  """
  List the job submission history. Normal users can only look at their
  own submissions.
  """
  history = models.JobHistory.objects

  if not request.user.is_superuser:
    history = history.filter(owner=request.user)
  history = history.order_by('-submission_date')

  return render('list_history.mako', request, {
    'history': history,
  })


def new_design(request, action_type):
  form = jobsub.forms.workflow_form_by_type(action_type)

  if request.method == 'POST':
    form.bind(request.POST)

    if form.is_valid():
      action = form.action.save(commit=False)
      action.action_type = action_type
      action.save()

      workflow = form.wf.save(commit=False)
      workflow.root_action = action
      workflow.owner = request.user
      workflow.save()

      return redirect(urlresolvers.reverse(list_designs))
  else:
    form.bind()

  return _render_design_edit(request, form, action_type, _STD_PROPERTIES_JSON)


def _render_design_edit(request, form, action_type, properties_hint):
  return render('edit_design.mako', request, {
    'form': form,
    'action': request.path,
    'action_type': action_type,
    'properties': extract_field_data(form.action['job_properties']),
    'files': extract_field_data(form.action['files']),
    'archives': extract_field_data(form.action['archives']),
    'properties_hint': properties_hint,
  })


def list_designs(request):
  '''
  List all workflow designs. Result sorted by last modification time.
  Query params:
    owner       - Substring filter by owner field 
    name        - Substring filter by workflow name field
  '''
  data = models.OozieWorkflow.objects
  owner = request.GET.get("owner", '')
  name = request.GET.get('name', '')
  if owner:
    data = data.filter(owner__username__icontains=owner)
  if name:
    data = data.filter(name__icontains=name)
  data = data.order_by('-last_modified')

  return render("list_designs.mako", request, {
    'workflows': list(data),
    'currentuser':request.user,
    'owner': owner,
    'name': name,
  })


def _get_design(wf_id):
  """Raise PopupException if workflow doesn't exist"""
  try:
    return models.OozieWorkflow.objects.get(pk=wf_id)
  except models.OozieWorkflow.DoesNotExist:
    raise PopupException("Job design not found")

def _check_permission(request, owner_name, error_msg):
  """Raise PopupException if user doesn't have permission to modify the workflow"""
  if request.user.username != owner_name and not request.user.is_superuser:
    access_warn(request, error_msg)
    raise PopupException("Permission denied. You are not the owner or a superuser.")


def delete_design(request, wf_id):
  if request.method == 'POST':
    try:
      wf_obj = _get_design(wf_id)
      _check_permission(request, wf_obj.owner.username,
                        "Access denied: delete workflow %s" % (wf_id,))
      wf_obj.root_action.delete()
      wf_obj.delete()

      submit.Submission(wf_obj, request.fs).remove_deployment_dir()
    except models.OozieWorkflow.DoesNotExist:
      LOG.error("Trying to delete non-existent workflow (id %s)" % (wf_id,))
      raise PopupException("Workflow not found")

  return redirect(urlresolvers.reverse(list_designs))


def edit_design(request, wf_id):
  wf_obj = _get_design(wf_id)
  _check_permission(request, wf_obj.owner.username,
                    "Access denied: edit workflow %s" % (wf_id,))

  if request.method == 'POST':
    form = jobsub.forms.workflow_form_by_instance(wf_obj, request.POST)
    if form.is_valid():
      form.action.save()
      form.wf.save()
      return redirect(urlresolvers.reverse(list_designs))
  else:
    form = jobsub.forms.workflow_form_by_instance(wf_obj)

  return _render_design_edit(request,
                               form,
                               wf_obj.root_action.action_type,
                               _STD_PROPERTIES_JSON)


def submit_design(request, wf_id):
  """Submit a workflow to Oozie"""
  wf_obj = _get_design(wf_id)
  _check_permission(request, wf_obj.owner.username,
                    "Access denied: submit workflow %s" % (wf_id,))

  submission = submit.Submission(wf_obj, request.fs)
  jobid = submission.run()

  # Save the submission record
  job_record = models.JobHistory(owner=request.user,
                                 job_id=jobid,
                                 workflow=wf_obj)
  job_record.save()

  # Show oozie job info
  return redirect(urlresolvers.reverse(oozie_job, kwargs={'jobid': jobid}))


# See http://wiki.apache.org/hadoop/JobConfFile
_STD_PROPERTIES = [
  'mapred.input.dir',
  'mapred.output.dir',
  'mapred.job.name',
  'mapred.job.queue.name',
  'mapred.mapper.class',
  'mapred.reducer.class',
  'mapred.combiner.class',
  'mapred.partitioner.class',
  'mapred.map.tasks',
  'mapred.reduce.tasks',
  'mapred.input.format.class',
  'mapred.output.format.class',
  'mapred.input.key.class',
  'mapred.input.value.class',
  'mapred.output.key.class',
  'mapred.output.value.class',
  'mapred.combine.buffer.size',
  'mapred.min.split.size',
  'mapred.map.tasks.speculative.execution',
  'mapred.reduce.tasks.speculative.execution',
  'mapred.queue.default.acl-administer-jobs',
]

_STD_PROPERTIES_JSON = json.dumps(_STD_PROPERTIES)


def bc_test(request):
  __import__("ipdb").set_trace()
  wf = models.OozieWorkflow(owner=request.user, name='Test WF')
  wf.save()

  java_action = models.OozieJavaAction(jar_path="hdfs://somewhere",
                                       main_class="foo.bar.com",
                                       args="-D bulllshit",
                                       job_properties='{ "json": "here" }')
  java_action.action_type = java_action.ACTION_TYPE
  java_action.save()

  wf.root_action = java_action
  wf.save()
