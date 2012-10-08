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

import logging

from django import forms
from django.db.models import Q

from desktop.lib.django_forms import MultiForm, SplitDateTimeWidget
from oozie.models import Workflow, Node, Java, Mapreduce, Streaming, Coordinator,\
  Dataset, DataInput, DataOutput, Pig, Link, Hive, Sqoop, Ssh, Shell, DistCp

LOG = logging.getLogger(__name__)


class ParameterForm(forms.Form):
  name = forms.CharField(max_length=40, widget=forms.widgets.HiddenInput())
  value = forms.CharField(max_length=40, required=False)


class WorkflowForm(forms.ModelForm):
  class Meta:
    model = Workflow
    exclude = ('owner', 'start', 'end')
    widgets = {
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'deployment_dir': forms.TextInput(attrs={'class': 'pathChooser', 'style': "width:535px"}),
      'parameters': forms.widgets.HiddenInput(),
      'job_xml': forms.widgets.TextInput(attrs={'class': 'pathChooser span5'}),
      'job_properties': forms.widgets.HiddenInput(),
      'schema_version': forms.widgets.HiddenInput(),
    }

  def __init__(self, *args, **kwargs):
    super(WorkflowForm, self).__init__(*args, **kwargs)


class ImportJobsubDesignForm(forms.Form):
  """Used for specifying what oozie actions to import"""
  def __init__(self, choices=[], *args, **kwargs):
    super(ImportJobsubDesignForm, self).__init__(*args, **kwargs)
    self.fields['action_id'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect(attrs={'class':'radio'}))


class NodeForm(forms.ModelForm):
  class Meta:
    ALWAYS_HIDE = ('workflow', 'children', 'node_type')
    model = Node
    exclude = ALWAYS_HIDE + ('name', 'description')


class JavaForm(forms.ModelForm):
  class Meta:
    model = Java
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'files': forms.HiddenInput(),
      'archives': forms.HiddenInput(),
      'jar_path': forms.TextInput(attrs={'class': 'pathChooser span5'}),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'main_class': forms.TextInput(attrs={'class': 'span5'}),
      'args': forms.TextInput(attrs={'class': 'span5'}),
      'java_opts': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }


class MapreduceForm(forms.ModelForm):
  """Used for specifying a mapreduce action"""
  class Meta:
    model = Mapreduce
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'files': forms.HiddenInput(),
      'archives': forms.HiddenInput(),
      'jar_path': forms.TextInput(attrs={'class': 'pathChooser span5'}),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }


class StreamingForm(forms.ModelForm):
  """Used for specifying a streaming action"""
  class Meta:
    model = Streaming
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'files': forms.widgets.HiddenInput(),
      'archives': forms.widgets.HiddenInput(),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
      'mapper': forms.TextInput(attrs={'class': 'span5'}),
      'reducer': forms.TextInput(attrs={'class': 'span5'}),
    }


class PigForm(forms.ModelForm):
  class Meta:
    model = Pig
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'params': forms.widgets.HiddenInput(),
      'script_path': forms.TextInput(attrs={'class': 'pathChooser span5'}),
      'files': forms.widgets.HiddenInput(),
      'archives': forms.widgets.HiddenInput(),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }


class HiveForm(forms.ModelForm):
  class Meta:
    model = Hive
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'params': forms.widgets.HiddenInput(),
      'script_path': forms.TextInput(attrs={'class': 'pathChooser span5'}),
      'files': forms.widgets.HiddenInput(),
      'archives': forms.widgets.HiddenInput(),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }


class SqoopForm(forms.ModelForm):
  class Meta:
    model = Sqoop
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'params': forms.widgets.HiddenInput(),
      'script_path': forms.Textarea(attrs={'class': 'span8'}),
      'files': forms.widgets.HiddenInput(),
      'archives': forms.widgets.HiddenInput(),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }


class SshForm(forms.ModelForm):
  class Meta:
    model = Ssh
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'params': forms.widgets.HiddenInput(),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'command': forms.TextInput(attrs={'class': 'pathChooser span5'}),
    }


class ShellForm(forms.ModelForm):
  class Meta:
    model = Shell
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'params': forms.widgets.HiddenInput(),
      'command': forms.TextInput(attrs={'class': 'pathChooser span5'}),
      'files': forms.widgets.HiddenInput(),
      'archives': forms.widgets.HiddenInput(),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }


class DistCpForm(forms.ModelForm):
  class Meta:
    model = DistCp
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'prepares': forms.widgets.HiddenInput(),
      'params': forms.widgets.HiddenInput(),
      'command': forms.TextInput(attrs={'class': 'pathChooser span5'}),
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'job_xml': forms.TextInput(attrs={'class': 'span5'}),
    }



class LinkForm(forms.ModelForm):
  comment = forms.CharField(label='if', max_length=1024, required=True, widget=forms.TextInput(attrs={'class': 'span8'}))

  class Meta:
    model = Link
    exclude = NodeForm.Meta.ALWAYS_HIDE + ('parent', 'child', 'name')


class DefaultLinkForm(forms.ModelForm):
  class Meta:
    model = Link
    exclude = NodeForm.Meta.ALWAYS_HIDE + ('parent', 'comment', 'name')

  def __init__(self, *args, **kwargs):
    workflow = kwargs['action'].workflow
    del kwargs['action']
    super(DefaultLinkForm, self).__init__(*args, **kwargs)
    self.fields['child'].widget = forms.Select(choices=((node.id, node) for node in set(workflow.node_set.all())))


DATE_FORMAT = '%m/%d/%Y'
TIME_FORMAT = '%I:%M %p'

class CoordinatorForm(forms.ModelForm):
  start = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT],
                                   widget=SplitDateTimeWidget(attrs={'class': 'short', 'id': 'coordinator_start'},
                                                              date_format=DATE_FORMAT, time_format=TIME_FORMAT))
  end = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT],
                                 widget=SplitDateTimeWidget(attrs={'class': 'short', 'id': 'coordinator_end'},
                                                            date_format=DATE_FORMAT, time_format=TIME_FORMAT))

  class Meta:
    model = Coordinator
    exclude = ('owner', 'deployment_dir')
    widgets = {
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'parameters': forms.widgets.HiddenInput(),
      'schema_version': forms.widgets.HiddenInput(),
    }

  def __init__(self, *args, **kwargs):
    user = kwargs['user']
    del kwargs['user']
    super(CoordinatorForm, self).__init__(*args, **kwargs)
    qs = Workflow.objects.filter(Q(is_shared=True) | Q(owner=user))
    workflows = []
    for workflow in qs:
      if workflow.is_accessible(user):
        workflows.append(workflow.id)
    qs = qs.filter(id__in=workflows)
    self.fields['workflow'].queryset = qs


class DatasetForm(forms.ModelForm):
  start = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT],
                                   widget=SplitDateTimeWidget(attrs={'class': 'short'},
                                                              date_format=DATE_FORMAT, time_format=TIME_FORMAT))

  class Meta:
    model = Dataset
    exclude = ('coordinator')
    widgets = {
      'uri': forms.TextInput(attrs={'class': 'span5'}),
    }

  def __init__(self, *args, **kwargs):
    super(DatasetForm, self).__init__(*args, **kwargs)


class DataInputSetForm(forms.ModelForm):
  class Meta:
    model = DataInput
    exclude = ('coordinator')


class DataInputForm(forms.ModelForm):
  class Meta:
    model = DataInput
    exclude = ('coordinator')

  def __init__(self, *args, **kwargs):
    coordinator = kwargs['coordinator']
    del kwargs['coordinator']
    super(DataInputForm, self).__init__(*args, **kwargs)
    self.fields['dataset'].queryset = Dataset.objects.filter(coordinator=coordinator)
    if coordinator.workflow:
      self.fields['name'].widget = forms.Select(choices=((param, param) for param in set(coordinator.workflow.find_parameters())))


class DataOutputSetForm(forms.ModelForm):
  class Meta:
    model = DataOutput
    exclude = ('coordinator')


class DataOutputForm(forms.ModelForm):
  class Meta:
    model = DataOutput
    exclude = ('coordinator')

  def __init__(self, *args, **kwargs):
    coordinator = kwargs['coordinator']
    del kwargs['coordinator']
    super(DataOutputForm, self).__init__(*args, **kwargs)
    self.fields['dataset'].queryset = Dataset.objects.filter(coordinator=coordinator)
    if coordinator.workflow:
      self.fields['name'].widget = forms.Select(choices=((param, param) for param in set(coordinator.workflow.find_parameters())))


_node_type_TO_FORM_CLS = {
  Mapreduce.node_type: MapreduceForm,
  Streaming.node_type: StreamingForm,
  Java.node_type: JavaForm,
  Pig.node_type: PigForm,
  Hive.node_type: HiveForm,
  Sqoop.node_type: SqoopForm,
  Ssh.node_type: SshForm,
  Shell.node_type: ShellForm,
  DistCp.node_type: DistCpForm,
}


def design_form_by_type(node_type):
  return _node_type_TO_FORM_CLS[node_type]


def design_form_by_instance(design_obj, data=None):
  action_obj = design_obj.get_root_action()
  cls = _node_type_TO_FORM_CLS[action_obj.node_type]

  instances = dict(wf=design_obj, action=action_obj)

  res = MultiForm(wf=WorkflowForm, action=cls)
  res.bind(data=data, instances=instances)
  return res
