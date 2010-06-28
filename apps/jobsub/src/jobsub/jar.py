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

from django import forms
from desktop.lib.django_util import render

from jobsubd.ttypes import SubmissionType, JarSubmission

class JarEditForm(forms.Form):
  """Form representing a JarSubmission"""
  name = forms.CharField(required=True, 
    initial="Untitled", 
    help_text="Name of Job Design")
  jarfile = forms.CharField(max_length=300, 
    initial="/jobsub/examples/hadoop-0.20.2-dev-examples.jar", 
    help_text="Filename, on the cluster, of jar to launch.")
  arguments = forms.CharField(max_length=300, 
    initial="pi 2 1000", 
    help_text="Arguments to pass to launched jar.")
  title = "Jar Job Design Editor"
  type_str = "jar"

  def get_arguments(self):
    # TODO(philip): This argument handling is bad; need to allow
    # some form of escaping.
    return self.cleaned_data['arguments'].split(" ")

  def dump_to_job_design(self, jd):
    """Takes the form's clean data and dumps to the passed into JobDesign thrift object."""
    if jd.data.jar_submission is None:
      jd.data.jar_submission = JarSubmission()
    jd.data.type = SubmissionType.JAR
    jd.data.jar_submission.jarfile = self.cleaned_data["jarfile"]
    jd.data.jar_submission.arguments = self.get_arguments()
    jd.name = self.cleaned_data["name"]

  def set_initial_from_job_design(self, jd):
    """Sets initial data from a JobDesign thrift object."""
    if jd.data.jar_submission is None:
      return
    self.initial["jarfile"] = jd.data.jar_submission.jarfile
    self.initial["arguments"] = " ".join(jd.data.jar_submission.arguments)
    self.initial["name"] = jd.name

  def render(self, request, message):
    return render("jaredit.html", request, dict(form=self, message=message))
