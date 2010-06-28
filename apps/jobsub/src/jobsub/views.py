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
from django.http import HttpResponse
from django.contrib.auth.models import User
from django import forms
from django.core import urlresolvers
from django.db.models import Q

from desktop.views import register_status_bar_view
from desktop.lib import thrift_util
from desktop.lib.django_util import render, MessageException, format_preserving_redirect
from desktop.log.access import access_warn

from jobsub.management.commands import jobsub_setup
from jobsub import conf
from jobsub.forms import interface
from jobsub.models import JobDesign, Submission
from jobsubd.ttypes import SubmissionPlan
from jobsubd import JobSubmissionService
from jobsubd.ttypes import State

JOBSUB_THRIFT_TIMEOUT_SECS=5

class MetadataForm(forms.Form):
  name = forms.CharField(required=True, initial="Untitled", help_text="Name of Job Design")
  description = forms.CharField(required=False, initial="", help_text="Description of Job Design", widget=forms.Textarea)

def edit_design(request, id=None, type=None, force_get=False, clone_design=None):
  """
  Edits a job submission.

  This method has high-ish cyclomatic complexity, in large part,
  because, when handling web forms, validation errors
  on submit receive very similar treatment to a request
  for the form itself.

  This method does double-duty for "new" as well.
  """
  assert id or type

  message=request.GET.get("message")

  if type:
    new = True
    jd = JobDesign()
    form_type = interface.registry.get(type)
    edit_url = urlresolvers.reverse("jobsub.new", kwargs=dict(type=type))
    if form_type is None:
      raise MessageException("Type %s does not exist." % repr(type))
  else:
    new = False
    jd = JobDesign.objects.get(pk=id)
    edit_url = jd.edit_url()
    form_type = interface.registry.get(jd.type)
    if form_type is None:
      raise MessageException("Could not find form type for %s." % str(jd))
    if jd.owner != request.user:
      access_warn(request, 'Insufficient permission')
      raise MessageException("Permission Denied.  You are not the owner of this JobDesign.  "
                             "You may copy the design instead.")

  if not force_get and request.method == 'POST':
    metadata_form = MetadataForm(request.POST)
    form = form_type()
    if metadata_form.is_valid() and form.is_valid_edit(request.POST):
      message = _save_design(request, jd, metadata_form, form)
      if request.POST.get("save_submit") == "on":
        return submit_design(request, jd.id, force_get=True)
      else:
        return list_designs(request, saved=jd.id)
  else:
    if new:
      metadata_form = MetadataForm()
      if clone_design:
        form = form_type(string_repr=clone_design.data)
        metadata_form.initial["name"] = "Copy of %s" % clone_design.name
        metadata_form.initial["description"] = clone_design.description
      else:
        form = form_type()
    else:
      form = form_type(string_repr=jd.data)
      metadata_form = MetadataForm(dict(name=jd.name, description=jd.description))

  # Present edit form for failed POST requests and edits.
  newlinks = [ (type, urlresolvers.reverse("jobsub.new", kwargs=dict(type=type))) for type in interface.registry ]
  request.path = edit_url
  return render("edit.html", request, {
      'newlinks': newlinks,
      'metadata_form': metadata_form,
      'form': form,
      'edit_url': edit_url,
      'message': message
    })

def _save_design(request, jd, metadata_form, form):
  """
  Helper responsible for saving the job design.
  """
  jd.name = metadata_form.cleaned_data["name"]
  jd.description = metadata_form.cleaned_data["description"]
  jd.data = form.serialize_to_string()
  jd.owner = request.user
  jd.type = form.name
  jd.save()

def list_designs(request, saved=None):
  """
  Lists extant job designs.

  Filters can be specified for owners.

  Note: the URL is named "list", but since list is a built-in,
  better to name the method somethign else.
  """
  show_install_examples = request.user.is_superuser and not jobsub_setup.Command().has_been_setup()
  data = JobDesign.objects.order_by('-last_modified')
  owner = request.GET.get("owner")
  name = request.GET.get('name')
  if owner:
    try:
      user = User.objects.get(username=owner)
      data = data.filter(owner=user)
    except User.DoesNotExist:
      data = []
  else:
    owner = ""

  if name:
    data = data.filter(name__icontains=name)
  else:
    name = ''

  newlinks = [ (type, urlresolvers.reverse("jobsub.new", kwargs=dict(type=type))) for type in interface.registry ]

  return render("list.html", request, {
    'jobdesigns': list(data),
    'currentuser':request.user,
    'newlinks': newlinks,
    'owner': owner,
    'name': name,
    'saved': saved,
    'show_install_examples': show_install_examples,
  })

def clone_design(request, id):
  """
  Clone a design.
  """
  try:
    jd = JobDesign.objects.get(pk=id)
  except JobDesign.DoesNotExist:
    raise MessageException("Design not found.")

  return edit_design(request, type=jd.type, clone_design=jd, force_get=True)

def delete_design(request, id):
  """
  Design deletion.

  The url provides the id, but we require a POST
  for deletion to indicate that it's an "action".
  """
  try:
    jd = JobDesign.objects.get(pk=id)
  except JobDesign.DoesNotExist:
    return HttpResponse("Design not found.")

  if jd.owner != request.user:
    access_warn(request, 'Insufficient permission')
    raise MessageException("Permission Denied.  You are not the owner of this JobDesign.")

  if request.method == 'POST':
    jd.delete()
    return list_designs(request)
  else:
    return render("confirm.html", request, dict(url=request.path, title="Delete job design?"))

def submit_design(request, id, force_get=False):
  """
  Job design submission.

  force_get is used when other views chain to this view.
  """
  job_design = JobDesign.objects.get(pk=id)
  form_type = interface.registry.get(job_design.type)
  form = form_type(string_repr=job_design.data)
  if not force_get and request.method == "POST":
    if form.is_valid_parameterization(request.POST):
      return _submit_to_cluster(request, job_design, form)

  return render("parameterize.html", request, dict(form=form, job_design=job_design))

def _submit_to_cluster(request, job_design, form):
  plan = SubmissionPlan()
  plan.name = job_design.name
  plan.user = request.user.username
  plan.groups = request.user.get_groups()
  plan.steps = form.to_job_submission_steps(plan.name)

  submission = Submission(owner=request.user,
    last_seen_state=State.SUBMITTED,
    name=job_design.name,
    submission_plan=plan)

  # Save aggressively in case submit() below triggers an error.
  submission.save()
  try:
    try:
      submission.submission_handle = get_client().submit(plan)
    except Exception:
      submission.last_seen_state=State.ERROR
      raise
  finally:
    submission.save()

  watch_url = submission.watch_url()
  return format_preserving_redirect(request, watch_url)

def watch(request):
  offset = request.GET.get("offset", 0)
  limit = request.GET.get("limit", 20)
  submissions = Submission.objects.order_by('-submission_date')
  limited = submissions[offset:limit]
  more = len(limited) < len(submissions)
  return render("watch.html", request,
    dict(submissions=limited, offset=offset, limit=limit, more=more))

def watch_submission(request, id):
  """
  Views job data for an already submitted job.
  """
  submission = Submission.objects.get(id=int(id))
  handle = submission.submission_handle
  job_data = get_client().get_job_data(handle)
  submission.last_seen_state = job_data.state
  submission.save()

  completed = (job_data.state not in (State.SUBMITTED, State.RUNNING))
  template = "watch_submission.html"
  return render(template, request, dict(
    id=id,
    submission=submission,
    job_data=job_data,
    completed=completed,
    jobs=job_data.hadoop_job_ids
  ))

def setup(request):
  """Installs jobsub examples."""
  if request.method == "GET":
    return render("confirm.html", request, dict(url=request.path, title="Install job design examples?"))
  else:
    jobsub_setup.Command().handle_noargs()
    return format_preserving_redirect(request, "/jobsub")

def status_bar(request):
  """Returns number of pending jobs tied to this user."""
  pending_count = Submission.objects.filter(Q(owner=request.user), 
    Q(last_seen_state=State.SUBMITTED) | Q(last_seen_state=State.RUNNING)).count()
  # Use force_template to avoid returning JSON.
  return render("status_bar.mako", request, dict(pending_count=pending_count), 
    force_template=True)
    
# Disabled, because the state is a bit confusing.
# This is more like a "inbox flag" that there's stuff that
# the user hasn't looked at, but we haven't found a great
# way to expose that.
# register_status_bar_view(status_bar)

CACHED_CLIENT = None
def get_client():
  """
  Returns a stub to talk to the server.
  """
  global CACHED_CLIENT
  if CACHED_CLIENT is None:
    CACHED_CLIENT = thrift_util.get_client(JobSubmissionService.Client,
      conf.JOBSUBD_HOST.get(), conf.JOBSUBD_PORT.get(), service_name="JobSubmission Daemon",
      timeout_seconds=JOBSUB_THRIFT_TIMEOUT_SECS)
  return CACHED_CLIENT

def in_process_jobsubd(conf_dir=None):
  """
  Instead of talking through Thrift, connects
  to jobsub daemon in process.
  """
  import jobsub.server
  import hadoop.conf
  global CACHED_CLIENT
  prev = CACHED_CLIENT
  next = jobsub.server.JobSubmissionServiceImpl()
  finish = hadoop.conf.HADOOP_CONF_DIR.set_for_testing(conf_dir)
  CACHED_CLIENT = next
  class Close(object):
    def __init__(self, client, prev):
      self.client = client
      self._prev = prev

    def exit(self):
      CACHED_CLIENT = self._prev
      finish()
  return Close(next, prev)
