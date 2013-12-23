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
from django.utils.translation import ugettext_lazy as _t
from desktop.lib.django_forms import MultiForm
from beeswax.forms import SaveForm


class SparkForm(forms.Form):
  params = forms.CharField(label=_t("Script parameters"),
                          required=False)
  classPath = forms.CharField(label=_t("Class path"),
                          required=True)
  appName = forms.ChoiceField(required=True,
                             label='',
                             choices=(('default', 'default'),),
                             initial=0,
                             widget=forms.widgets.Select(attrs={'class': 'input-medium'}))
  autoContext = forms.BooleanField(required=False,
                                   initial=True)
  context = forms.CharField(required=False)


  def __init__(self, *args, **kwargs):
    app_names = kwargs.pop('app_names', [])
    super(SparkForm, self).__init__(*args, **kwargs)
    self.fields['appName'].choices = ((key, key) for key in app_names)


class QueryForm(MultiForm):
  def __init__(self):
    super(QueryForm, self).__init__(
      query=SparkForm,
      saveform=SaveForm
    )


class UploadApp(forms.Form):
  app_name = forms.CharField()
  jar_file = forms.FileField()
