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

from desktop.lib.django_forms import MultiForm
from jobsub import models

from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)

# This aligns with what Oozie accepts as a workflow name
_OOZIE_WORKFLOW_NAME_REGEX = '^([a-zA-Z_]([\-_a-zA-Z0-9])*){1,39}$'

class WorkflowDesignForm(forms.ModelForm):
  """Used for specifying a design"""
  class Meta:
    model = models.OozieDesign
    exclude = ('root_action', 'owner')

  name = forms.RegexField(
        label=_('Name'),
        max_length=39,
        regex=_OOZIE_WORKFLOW_NAME_REGEX,
        help_text="Name of the design.",
        error_messages={'invalid': _("Allows letters, digits, '_', and '-'. "
                        "The first character must be a letter or '_'.")})


class JavaActionForm(forms.ModelForm):
  """Used for specifying a java action"""
  class Meta:
    model = models.OozieJavaAction
    exclude = ('action_type',)
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'files': forms.HiddenInput(),
      'archives': forms.HiddenInput()
    }

    name = forms.CharField(label=_('Name'))
    description = forms.CharField(label=_('Description'))
    main_class = forms.CharField(label=_('Main class'))
    jar_path = forms.CharField(label=_('Jar path'), widget=forms.TextInput(attrs={'class': 'pathChooser'}))
    args = forms.CharField(label=_('Args'))
    java_opts = forms.CharField(label=_('Java opts'))


class MapreduceActionForm(forms.ModelForm):
  """Used for specifying a mapreduce action"""
  class Meta:
    model = models.OozieMapreduceAction
    exclude = ('action_type',)
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'files': forms.HiddenInput(),
      'archives': forms.HiddenInput()
    }

    name = forms.CharField(label=_('Name'))
    description = forms.CharField(label=_('Description'))
    jar_path = forms.CharField(label=_('Jar path'), widget=forms.TextInput(attrs={'class': 'pathChooser'}))
    mapper = forms.CharField(label=_('Mapper'))
    reducer = forms.CharField(label=_('Reducer'))


class StreamingActionForm(forms.ModelForm):
  """Used for specifying a streaming action"""
  class Meta:
    model = models.OozieStreamingAction
    exclude = ('action_type',)
    widgets = {
      'job_properties': forms.widgets.HiddenInput(),
      'files': forms.widgets.HiddenInput(),
      'archives': forms.widgets.HiddenInput(),
    }

    name = forms.CharField(label=_('Name'))
    description = forms.CharField(label=_('Description'))


_ACTION_TYPE_TO_FORM_CLS = {
  models.OozieMapreduceAction.ACTION_TYPE: MapreduceActionForm,
  models.OozieStreamingAction.ACTION_TYPE: StreamingActionForm,
  models.OozieJavaAction.ACTION_TYPE: JavaActionForm,
}


def design_form_by_type(action_type):
  cls = _ACTION_TYPE_TO_FORM_CLS[action_type]
  return MultiForm(wf=WorkflowDesignForm, action=cls)

def design_form_by_instance(design_obj, data=None):
  action_obj = design_obj.get_root_action()
  cls = _ACTION_TYPE_TO_FORM_CLS[action_obj.action_type]

  instances = dict(wf=design_obj, action=action_obj)

  res = MultiForm(wf=WorkflowDesignForm, action=cls)
  res.bind(data=data, instances=instances)
  return res
