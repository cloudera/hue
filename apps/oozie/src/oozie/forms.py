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
from datetime import datetime,  timedelta

from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms.widgets import TextInput
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _t

from desktop.lib.django_forms import MultiForm, SplitDateTimeWidget
from oozie.models import Workflow, Node, Java, Mapreduce, Streaming, Coordinator,\
  Dataset, DataInput, DataOutput, Pig, Link, Hive, Sqoop, Ssh, Shell, DistCp, Fs,\
  Email, SubWorkflow, Generic, Bundle, BundledCoordinator


LOG = logging.getLogger(__name__)


class ParameterForm(forms.Form):
  name = forms.CharField(max_length=40, widget=forms.widgets.HiddenInput())
  value = forms.CharField(max_length=1024, required=False)

  NON_PARAMETERS = (
      'user.name',
      'oozie.wf.rerun.failnodes',
      'oozie.wf.rerun.skip.nodes',
      'oozie.wf.application.path',
      'oozie.coord.application.path',
      'mapreduce.job.user.name',
      'wf_application_path',
      'jobTracker',
      'nameNode',
      'hue-id-w',
      'hue-id-c',
  )

  @staticmethod
  def get_initial_params(conf_dict):
    params = filter(lambda key: key not in ParameterForm.NON_PARAMETERS, conf_dict.keys())
    return [{'name': name, 'value': conf_dict[name]} for name in params]


class WorkflowForm(forms.ModelForm):
  class Meta:
    model = Workflow
    exclude = ('owner', 'start', 'end')
    widgets = {
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'deployment_dir': forms.TextInput(attrs={'class': 'pathChooser span7'}),
      'parameters': forms.widgets.HiddenInput(),
      'job_xml': forms.widgets.TextInput(attrs={'class': 'pathChooser span7'}),
      'job_properties': forms.widgets.HiddenInput(),
      'schema_version': forms.widgets.HiddenInput(),
    }

  def __init__(self, *args, **kwargs):
    super(WorkflowForm, self).__init__(*args, **kwargs)


SCHEMA_VERSION_CHOICES = ['0.4']

class ImportWorkflowForm(WorkflowForm):
  definition_file = forms.FileField(label=_t("Local workflow.xml file"))
  resource_archive = forms.FileField(label=_t("Workflow resource archive (zip)"), required=False)


class ImportJobsubDesignForm(forms.Form):
  """Used for specifying what oozie actions to import"""
  def __init__(self, choices=[], *args, **kwargs):
    super(ImportJobsubDesignForm, self).__init__(*args, **kwargs)
    self.fields['jobsub_id'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect(attrs={'class':'radio'}))


class NodeForm(forms.ModelForm):
  class Meta:
    ALWAYS_HIDE = ('workflow', 'children', 'node_type')
    model = Node
    exclude = ALWAYS_HIDE


class NodeMetaForm(forms.ModelForm):
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


class FsForm(forms.ModelForm):
  class Meta:
    model = Fs
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'deletes': forms.widgets.HiddenInput(),
      'mkdirs': forms.widgets.HiddenInput(),
      'moves': forms.widgets.HiddenInput(),
      'chmods': forms.widgets.HiddenInput(),
      'touchzs': forms.widgets.HiddenInput(),
    }


class EmailForm(forms.ModelForm):
  class Meta:
    model = Email
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'to': forms.TextInput(attrs={'class': 'span8'}),
      'cc': forms.TextInput(attrs={'class': 'span8'}),
      'subject': forms.TextInput(attrs={'class': 'span8'}),
      'body': forms.Textarea(attrs={'class': 'span8'}),
    }

class SubWorkflowForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    workflow = kwargs.pop('workflow')
    super(SubWorkflowForm, self).__init__(*args, **kwargs)
    choices=((wf.id, wf) for wf in Workflow.objects.available().filter(owner=user).exclude(id=workflow.id))
    self.fields['sub_workflow'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect(attrs={'class':'radio'}))

  class Meta:
    model = SubWorkflow
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
    }

  def clean_sub_workflow(self):
    try:
      return Workflow.objects.get(id=int(self.cleaned_data.get('sub_workflow')))
    except Exception, e:
      raise ValidationError(_('The sub-workflow could not be found: %s' % e))


class GenericForm(forms.ModelForm):
  class Meta:
    model = Generic
    exclude = NodeForm.Meta.ALWAYS_HIDE
    widgets = {
      'xml': forms.Textarea(attrs={'class': 'span8'})
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


class NumberInput(TextInput):
  input_type = 'number'


class CoordinatorForm(forms.ModelForm):
  start = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT],
                                   widget=SplitDateTimeWidget(attrs={'class': 'input-small', 'id': 'coordinator_start'},
                                                              date_format=DATE_FORMAT, time_format=TIME_FORMAT))
  end = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT],
                                 widget=SplitDateTimeWidget(attrs={'class': 'input-small', 'id': 'coordinator_end'},
                                                            date_format=DATE_FORMAT, time_format=TIME_FORMAT))

  class Meta:
    model = Coordinator
    exclude = ('owner', 'deployment_dir')
    widgets = {
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'parameters': forms.widgets.HiddenInput(),
      'job_properties': forms.widgets.HiddenInput(),
      'schema_version': forms.widgets.HiddenInput(),
      'timeout': NumberInput(),
    }

  def __init__(self, *args, **kwargs):
    user = kwargs['user']
    del kwargs['user']
    super(CoordinatorForm, self).__init__(*args, **kwargs)
    qs = Workflow.objects.available().filter(Q(is_shared=True) | Q(owner=user))
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
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'uri': forms.TextInput(attrs={'class': 'span5'}),
    }

  def __init__(self, *args, **kwargs):
    super(DatasetForm, self).__init__(*args, **kwargs)


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
  Fs.node_type: FsForm,
  Email.node_type: EmailForm,
  SubWorkflow.node_type: SubWorkflowForm,
  Generic.node_type: GenericForm,
}


class RerunForm(forms.Form):
  skip_nodes = forms.MultipleChoiceField(required=False)

  def __init__(self, *args, **kwargs):
    oozie_workflow = kwargs.pop('oozie_workflow')

    # Build list of skip nodes
    decisions = filter(lambda node: node.type == 'switch', oozie_workflow.get_control_flow_actions())
    working_actions = oozie_workflow.get_working_actions()
    skip_nodes = []

    for action in decisions + working_actions:
      if action.status == 'OK':
        skip_nodes.append((action.name, action.name))
    initial_skip_nodes = oozie_workflow.conf_dict.get('oozie.wf.rerun.skip.nodes', '').split()

    super(RerunForm, self).__init__(*args, **kwargs)

    self.fields['skip_nodes'].choices = skip_nodes
    self.fields['skip_nodes'].initial = initial_skip_nodes


class RerunCoordForm(forms.Form):
  refresh = forms.BooleanField(initial=True, required=False, help_text=_t('Used to indicate if user wants to cleanup output events for given rerun actions'))
  nocleanup = forms.BooleanField(initial=True, required=False, help_text=_t("Used to indicate if user wants to refresh an action's input and output events"))
  actions = forms.MultipleChoiceField(required=True)

  def __init__(self, *args, **kwargs):
    oozie_coordinator = kwargs.pop('oozie_coordinator')

    super(RerunCoordForm, self).__init__(*args, **kwargs)

    self.fields['actions'].choices = [(action.actionNumber, action.title) for action in reversed(oozie_coordinator.get_working_actions())]


class RerunBundleForm(forms.Form):
  refresh = forms.BooleanField(initial=True, required=False, help_text=_t('Used to indicate if user wants to cleanup output events for given rerun actions'))
  nocleanup = forms.BooleanField(initial=True, required=False, help_text=_t("Used to indicate if user wants to refresh an action's input and output events"))
  coordinators = forms.MultipleChoiceField(required=True)
  start = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT], required=False, initial=datetime.today(),
                                   widget=SplitDateTimeWidget(attrs={'class': 'input-small', 'id': 'rerun_start'},
                                                              date_format=DATE_FORMAT, time_format=TIME_FORMAT))
  end = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT], required=False, initial=datetime.today() + timedelta(days=3),
                                 widget=SplitDateTimeWidget(attrs={'class': 'input-small', 'id': 'rerun_end'},
                                                            date_format=DATE_FORMAT, time_format=TIME_FORMAT))

  def __init__(self, *args, **kwargs):
    oozie_bundle = kwargs.pop('oozie_bundle')

    super(RerunBundleForm, self).__init__(*args, **kwargs)

    self.fields['coordinators'].choices = [(action.name, action.name) for action in reversed(oozie_bundle.actions)]
    self.fields['coordinators'].initial = [action.name for action in reversed(oozie_bundle.actions)]


class BundledCoordinatorForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    super(BundledCoordinatorForm, self).__init__(*args, **kwargs)
    self.fields['coordinator'].empty_label = None

  class Meta:
    model = BundledCoordinator
    exclude = ('bundle',)
    widgets = {
      'parameters': forms.widgets.HiddenInput(),
    }


class BundleForm(forms.ModelForm):
  kick_off_time = forms.SplitDateTimeField(input_time_formats=[TIME_FORMAT],
                                           widget=SplitDateTimeWidget(attrs={'class': 'input-small', 'id': 'bundle_kick_off_time'},
                                                                      date_format=DATE_FORMAT, time_format=TIME_FORMAT))

  class Meta:
    model = Bundle
    exclude = ('owner', 'coordinators')
    widgets = {
      'description': forms.TextInput(attrs={'class': 'span5'}),
      'parameters': forms.widgets.HiddenInput(),
      'schema_version': forms.widgets.HiddenInput(),
    }


def design_form_by_type(node_type, user, workflow):
  klass_form = _node_type_TO_FORM_CLS[node_type]

  if node_type == 'subworkflow':
    klass_form = curry(klass_form, user=user, workflow=workflow)

  return klass_form


def design_form_by_instance(design_obj, data=None):
  action_obj = design_obj.get_root_action()
  cls = _node_type_TO_FORM_CLS[action_obj.node_type]

  instances = dict(wf=design_obj, action=action_obj)

  res = MultiForm(wf=WorkflowForm, action=cls)
  res.bind(data=data, instances=instances)
  return res
