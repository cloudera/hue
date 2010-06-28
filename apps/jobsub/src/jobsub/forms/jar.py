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
from django.template.loader import render_to_string

from jobsub.forms import interface
from jobsub.forms import mixins

from jobsubd.ttypes import LocalizeFilesStep, BinHadoopStep, LocalizedFile, SubmissionPlanStep

class JarForm(interface.JobSubForm, mixins.DjangoFormBasedEditForm, mixins.BasicParameterizationForm):
  """
  Handles "jar" submissions.
  """

  name = "jar"

  def __init__(self, string_repr=None):
    if string_repr:
      self.deserialize_from_string(string_repr)
    else:
      self.django_form = self.DjangoForm()
      self.data = None

  class DjangoForm(forms.Form):
    """
    Form representing a JarSubmission.
    This is a private inner class.
    """
    jarfile = forms.CharField(max_length=300, 
      initial="/user/hue/jobsub/examples/hadoop-0.20.1-dev-examples.jar", 
      help_text="Filename, on the cluster, of jar to launch.")
    arguments = forms.CharField(max_length=300, 
      initial="pi 2 1000", 
      help_text="Arguments to pass to launched jar.")

  def render_edit(self):
    return render_to_string("forms/jar.html", dict(form=self.django_form))

  def get_arguments(self):
    # TODO(philip): This argument handling is bad; need to allow
    # some form of escaping.
    return self.parameterized_data['arguments'].split(" ")

  def to_job_submission_steps(self, _unused_job_design_name):
    lfs = LocalizeFilesStep()
    lf = LocalizedFile(target_name="tmp.jar", path_on_hdfs=self.parameterized_data["jarfile"])
    lfs.localize_files = [ lf ]

    bhs = BinHadoopStep()
    bhs.arguments = ["jar", "tmp.jar"] + self.get_arguments()

    return [
      SubmissionPlanStep(localize_files_step=lfs),
      SubmissionPlanStep(bin_hadoop_step=bhs)
    ]
