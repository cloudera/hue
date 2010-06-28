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

import datetime
import posixpath

from django import forms
from django.forms import CharField, IntegerField
from django.template.loader import render_to_string

from jobsub.forms import interface
from jobsub.forms import mixins
from jobsubd.ttypes import LocalizeFilesStep, BinHadoopStep, LocalizedFile, SubmissionPlanStep, PreFabLocalizedFiles
from desktop.lib.django_forms import MultipleInputField, ChoiceOrOtherField, KeyValueField

class PathListField(MultipleInputField):
  # Could do extra checking to make sure paths are valid, etc.
  pass

class StreamingException(Exception):
  pass

def unique_output():
  return "/tmp/output-" + datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S")

def pair_up(x):
  return x,x

class StreamingForm(interface.JobSubForm, mixins.DjangoFormBasedEditForm, mixins.BasicParameterizationForm):
  name = "streaming"

  def __init__(self, string_repr=None):
    if string_repr:
      self.deserialize_from_string(string_repr)
    else:
      self.django_form = self.DjangoForm()
      self.data = None

  def render_edit(self):
    return render_to_string("forms/streaming.html", dict(form=self.django_form))

  def to_job_submission_steps(self, job_design_name):
    return [
      SubmissionPlanStep(localize_files_step=LocalizeFilesStep(
        localize_files=[
          LocalizedFile(target_name="streaming.jar", pre_fab_localized_file=PreFabLocalizedFiles.STREAMING)])),
      SubmissionPlanStep(bin_hadoop_step=BinHadoopStep(
        arguments = [ "jar", "streaming.jar" ] + self.make_args(job_design_name)))]

  class DjangoForm(forms.Form):
    input = PathListField(required=True,
      initial=["$input"],
      help_text="Input paths (may be files or folders).")
    output = CharField(required=True,
      initial="$output",
      help_text="Output directory.  Must not already exist.")
    mapper_cmd = CharField(required=True,
      initial="<python yourscript.py --map>",
      help_text="Command to execute for map tasks (exclusive with mapper_class).")
    mapper_class = CharField(required=False,
      initial="",
      help_text="Class to execute for map tasks (exclusive with mapper_cmd).")
    combiner_class = CharField(required=False,
      help_text="(Optional) Class to execute as combiner.")
    reducer_cmd = CharField(required=False,
      initial="<python yourscript.py --reduce>",
      help_text="(Optional.)  Command to execute for reduce tasks (exclusive with reducer_class)")
    reducer_class = CharField(required=False,
      initial="",
      help_text="Class to execute for reduce tasks (exclusive with reducer_cmd)")
    inputformat_class = ChoiceOrOtherField(
      required=False,
      initial="org.apache.hadoop.mapred.TextInputFormat",
      choices=(
        pair_up("org.apache.hadoop.mapred.TextInputFormat"),
        pair_up("org.apache.hadoop.mapred.SequenceFileAsTextInputFormat"),
      ),
      help_text="Built-in input format, or class of custom input format."
    )
    outputformat_class = ChoiceOrOtherField(
      required=False,
      initial="org.apache.hadoop.mapred.TextOutputFormat",
      choices=(
        pair_up("org.apache.hadoop.mapred.TextOutputFormat"),
      ),
      help_text="Built-in output format, or class of custom input format."
    )
    partitioner_class = CharField(required=False,
      help_text="(Optional) class name of partitioner.")
    num_reduce_tasks = IntegerField(required=False,
      initial=1,
      help_text="Number of reduce tasks.  Set to 0 to disable reducers.")
    inputreader = CharField(required=False,
      help_text="(Optional) Inputreader spec.")
    cache_files = PathListField(required=False,
      initial= ["<yourscript.py>"],
      label="Required Files",
      help_text="Files (on cluster) to send as part of job.")
    cache_archives = PathListField(required=False,
      help_text="Archives (zip, jar) (on cluster) to send as part of job.")
    hadoop_properties = KeyValueField(required=False,
      help_text='Hadoop options in format property=value.')

  def make_args(self, job_design_name):
    # This is a hacky way to avoid writing 'self.data["foo"]' many times.
    class Proxy(object):
      pass
    s = Proxy()
    s.__dict__ = self.parameterized_data

    errors = []
    args = []

    # First handle Hadoop properties.
    # Convert hadoop properties dict to a string for
    # presentation in the edit box, filtering out properties
    # that are set with dedicated fields.
    filter_props = ['mapred.job.name', 'hadoop.job.ugi']
    hadoop_props = s.hadoop_properties or {}
    filtered_props = dict([ (k,v) for k,v in hadoop_props.items() if k not in filter_props])
    filtered_props['mapred.job.name'] = job_design_name

    for k, v in filtered_props.iteritems():
      args += [ "-D", '%s=%s' % (k,v) ]

    # Handle the rest
    if not s.input:
      errors.append("At least one input is required.")
    elif len([ x for x in s.input if "," in x ]) > 0:
      errors.append("Input paths may not have commas.")
    else:
      args += [ "-input", ",".join(s.input) ]
    
    if not s.output:
      errors.append("Output is required.")
    else:
      args += [ "-output", s.output ]

    if len(filter(None, [s.mapper_cmd, s.mapper_class])) != 1:
      errors.append("Exactly one of map command or map class must be specified.")
    elif s.mapper_cmd:
      args += [ "-mapper", s.mapper_cmd ]
    elif s.mapper_class:
      args += [ "-mapper", s.mapper_class ]
    else:
      assert "Impossible."

    if s.combiner_class:
      args += [ "-combiner", s.combiner_class ]

    if s.reducer_cmd and s.reducer_class:
      errors.append("At most one of reducer command or class may be specified.")
    if s.reducer_cmd:
      args += [ "-reducer", s.reducer_cmd ]
    elif s.reducer_class:
      args += [ "-reducer", s.reducer_class ]

    if s.inputformat_class:
      args += [ "-inputformat", s.inputformat_class ]

    if s.outputformat_class:
      args += [ "-outputformat", s.outputformat_class ]

    if s.partitioner_class:
      args += [ "-partitioner", s.partitioner_class ]

    if s.num_reduce_tasks:
      if s.num_reduce_tasks < 0:
        errors.append("numReduceTasks must be >= 0")
      else:
        args += [ "-numReduceTasks", str(s.num_reduce_tasks) ]

    if s.inputreader:
      args += [ "-inputreader", s.inputreader ]

    for f in s.cache_files or ():
      # Transform to give link path.
      f = f + "#" + posixpath.basename(f)
      args += [ "-cacheFile", f ]

    for f in s.cache_archives or ():
      args += [ "-cacheArchive", f ]

    if errors:
      raise Exception("Errors: " + ", ".join(errors))

    # TODO -file is missing!
    return args
